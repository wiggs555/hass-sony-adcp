"""Data update coordinator for Sony ADCP."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .adcp_client import ADCPAuthError, ADCPClient, ADCPError
from .const import (
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    DEFAULT_ADCP_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    POLL_ATTRIBUTES,
)

if TYPE_CHECKING:
    from . import SonyADCPConfigEntry

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class SonyADCPData:
    """Coordinator data."""

    power_status: str | None = None
    input: str | None = None
    picture_mode: str | None = None
    aspect: str | None = None
    gamma_correction: str | None = None
    color_temp: str | None = None
    hdr_tone_mapping: str | None = None
    motionflow: str | None = None
    blank: str | None = None
    pic_pos_sel: str | None = None
    calibration_auto: str | None = None
    model: str | None = None
    serial: str | None = None
    ranges: dict[str, list[str]] = field(default_factory=dict)
    available: bool = True


class SonyADCPCoordinator(DataUpdateCoordinator[SonyADCPData]):
    """Poll Sony projector state via ADCP."""

    config_entry: SonyADCPConfigEntry

    def __init__(self, hass: HomeAssistant, entry: SonyADCPConfigEntry) -> None:
        self.entry = entry
        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        self.client = ADCPClient(
            entry.data["host"],
            port=entry.data.get(CONF_PORT, DEFAULT_ADCP_PORT),
            password=entry.data.get(CONF_PASSWORD, ""),
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
            config_entry=entry,
        )
        self._device_info_loaded = False

    async def _async_update_data(self) -> SonyADCPData:
        data = SonyADCPData()
        try:
            if not self._device_info_loaded:
                info = await self.client.get_device_info()
                data.model = info["model"]
                data.serial = info["serial"]
                self._device_info_loaded = True
            else:
                data.model = self.data.model if self.data else None
                data.serial = self.data.serial if self.data else None

            for attribute in POLL_ATTRIBUTES:
                try:
                    value = await self.client.query(attribute)
                except ADCPError as err:
                    _LOGGER.debug("Skipping attribute %s: %s", attribute, err)
                    continue
                setattr(data, attribute, value)

            data.available = True
            return data
        except ADCPAuthError as err:
            raise UpdateFailed("Authentication failed; check projector password") from err
        except ADCPError as err:
            raise UpdateFailed(str(err)) from err

    async def async_send_command(self, command: str) -> str | list[str] | bool:
        """Send a raw ADCP command and refresh state."""
        result = await self.client.send_command(command)
        await self.async_request_refresh()
        return result

    async def async_set_select(self, command: str, value: str) -> None:
        """Set a select-style ADCP value."""
        await self.client.set_value(command, value)
        await self.async_request_refresh()

    async def async_execute(self, command: str) -> None:
        """Execute an ADCP action."""
        await self.client.execute(command)
        await self.async_request_refresh()

    async def async_get_range(self, command: str) -> list[str]:
        """Return allowed values, caching in coordinator data."""
        if self.data and command in self.data.ranges:
            return self.data.ranges[command]
        try:
            values = await self.client.query_range(command)
        except ADCPError:
            return []
        if self.data is not None:
            self.data.ranges[command] = values
        return values


async def async_create_coordinator(
    hass: HomeAssistant, entry: ConfigEntry
) -> SonyADCPCoordinator:
    """Create and prime the coordinator."""
    coordinator = SonyADCPCoordinator(hass, entry)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(str(err)) from err
    return coordinator
