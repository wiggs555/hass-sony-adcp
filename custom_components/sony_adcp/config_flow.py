"""Config flow for Sony ADCP."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.helpers import selector

from .adcp_client import ADCPAuthError, ADCPClient, ADCPError
from .const import (
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    DEFAULT_ADCP_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MANUFACTURER,
    SDAP_DISCOVERY_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class SonyADCPConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sony ADCP."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovered: list[dict[str, Any]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle manual setup."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            password = user_input.get(CONF_PASSWORD, "")
            port = user_input.get(CONF_PORT, DEFAULT_ADCP_PORT)
            try:
                await self._async_validate_connection(host, port, password)
            except ADCPAuthError:
                errors["base"] = "invalid_auth"
            except ADCPError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, f"Sony Projector ({host})"),
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_PASSWORD: password,
                        CONF_SCAN_INTERVAL: user_input.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): selector.TextSelector(),
                    vol.Optional(CONF_NAME): selector.TextSelector(),
                    vol.Optional(CONF_PASSWORD, default=""): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                    ),
                    vol.Optional(CONF_PORT, default=DEFAULT_ADCP_PORT): selector.NumberSelector(
                        selector.NumberSelectorConfig(min=1, max=65535, mode=selector.NumberSelectorMode.BOX)
                    ),
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(min=10, max=300, mode=selector.NumberSelectorMode.BOX)
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_discover(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Discover projectors via SDAP."""
        if user_input is not None:
            host = user_input[CONF_HOST]
            return await self.async_step_user(
                {
                    CONF_HOST: host,
                    CONF_PASSWORD: "",
                    CONF_PORT: DEFAULT_ADCP_PORT,
                    CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
                }
            )

        try:
            devices = await ADCPClient.discover(timeout=SDAP_DISCOVERY_TIMEOUT)
        except ADCPError as err:
            _LOGGER.debug("Discovery failed: %s", err)
            return self.async_abort(reason="discovery_failed")

        if not devices:
            return self.async_abort(reason="no_devices_found")

        self._discovered = [
            {
                CONF_HOST: device.ip,
                "model": device.model,
                "serial": str(device.serial),
            }
            for device in devices
        ]

        if len(self._discovered) == 1:
            device = self._discovered[0]
            return await self.async_step_user(
                {
                    CONF_HOST: device[CONF_HOST],
                    CONF_NAME: f"{MANUFACTURER} {device['model']}",
                    CONF_PASSWORD: "",
                    CONF_PORT: DEFAULT_ADCP_PORT,
                    CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
                }
            )

        return self.async_show_form(
            step_id="discover",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value=item[CONF_HOST],
                                    label=f"{item['model']} ({item[CONF_HOST]})",
                                )
                                for item in self._discovered
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            ),
        )

    async def _async_validate_connection(
        self, host: str, port: int, password: str
    ) -> None:
        client = ADCPClient(host, port=port, password=password)
        await client.query("power_status")
