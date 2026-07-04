"""Switch platform for Sony ADCP."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
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
    async_add_entities([SonyADCPCalibrationAutoSwitch(coordinator)])


class SonyADCPCalibrationAutoSwitch(SonyADCPEntity, SwitchEntity):
    """Toggle automatic color calibration execution."""

    _attr_translation_key = "calibration_auto"

    def __init__(self, coordinator: SonyADCPCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_calibration_auto"

    @property
    def is_on(self) -> bool:
        if not self.projector_data or not self.projector_data.calibration_auto:
            return False
        return self.projector_data.calibration_auto == "on"

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_select("calibration_auto", "on")

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_select("calibration_auto", "off")
