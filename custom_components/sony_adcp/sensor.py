"""Sensor platform for Sony ADCP."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
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
            SonyADCPPowerStatusSensor(coordinator),
            SonyADCPModelSensor(coordinator),
        ]
    )


class SonyADCPPowerStatusSensor(SonyADCPEntity, SensorEntity):
    """Expose projector power status."""

    _attr_translation_key = "power_status"
    _attr_unique_id = None

    def __init__(self, coordinator: SonyADCPCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_power_status"

    @property
    def native_value(self) -> str | None:
        return self.projector_data.power_status if self.projector_data else None


class SonyADCPModelSensor(SonyADCPEntity, SensorEntity):
    """Expose projector model name."""

    _attr_translation_key = "model"
    _attr_unique_id = None

    def __init__(self, coordinator: SonyADCPCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_model"

    @property
    def native_value(self) -> str | None:
        return self.projector_data.model if self.projector_data else None
