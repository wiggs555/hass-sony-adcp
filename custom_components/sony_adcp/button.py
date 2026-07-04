"""Button platform for Sony ADCP calibration actions."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SonyADCPCoordinator
from .entity import SonyADCPEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SonyADCPCoordinator = entry.runtime_data
    async_add_entities(
        [
            SonyADCPStartCalibrationButton(coordinator),
            SonyADCPResetCalibrationButton(coordinator),
            SonyADCPReturnCalibrationButton(coordinator),
        ]
    )


class SonyADCPStartCalibrationButton(SonyADCPEntity, ButtonEntity):
    """Start projector color calibration."""

    _attr_translation_key = "start_calibration"

    def __init__(self, coordinator: SonyADCPCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_start_calibration"

    async def async_press(self) -> None:
        await self.coordinator.async_execute("calibration_start")


class SonyADCPResetCalibrationButton(SonyADCPEntity, ButtonEntity):
    """Reset projector color calibration."""

    _attr_translation_key = "reset_calibration"

    def __init__(self, coordinator: SonyADCPCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_reset_calibration"

    async def async_press(self) -> None:
        await self.coordinator.async_execute("calibration_reset")


class SonyADCPReturnCalibrationButton(SonyADCPEntity, ButtonEntity):
    """Return projector color calibration to previous values."""

    _attr_translation_key = "return_calibration"

    def __init__(self, coordinator: SonyADCPCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_return_calibration"

    async def async_press(self) -> None:
        await self.coordinator.async_execute("calibration_return")
