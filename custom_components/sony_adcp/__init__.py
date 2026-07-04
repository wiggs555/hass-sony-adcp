"""Sony ADCP Home Assistant integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import voluptuous as vol

from homeassistant.const import Platform
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant, ServiceCall

from .const import ATTR_COMMAND, DOMAIN, SERVICE_SEND_COMMAND
from .coordinator import async_create_coordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .coordinator import SonyADCPCoordinator

    SonyADCPConfigEntry = ConfigEntry[SonyADCPCoordinator]

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.MEDIA_PLAYER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.BUTTON,
    Platform.SWITCH,
]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register integration-level services."""

    async def handle_send_command(call: ServiceCall) -> None:
        entry_id = call.data.get("entry_id")
        command = call.data[ATTR_COMMAND]
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry_id and entry.entry_id != entry_id:
                continue
            coordinator: SonyADCPCoordinator = entry.runtime_data
            await coordinator.async_send_command(command)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_COMMAND,
        handle_send_command,
        schema=vol.Schema(
            {
                vol.Required(ATTR_COMMAND): cv.string,
                vol.Optional("entry_id"): cv.string,
            }
        ),
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: SonyADCPConfigEntry) -> bool:
    """Set up Sony ADCP from a config entry."""
    coordinator = await async_create_coordinator(hass, entry)
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SonyADCPConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
