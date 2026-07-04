"""Shared entity helpers."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, POWER_OFF_STATES, POWER_ON_STATES, POWER_TRANSITION_STATES
from .coordinator import SonyADCPCoordinator, SonyADCPData


class SonyADCPEntity(CoordinatorEntity[SonyADCPCoordinator]):
    """Base Sony ADCP entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SonyADCPCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            manufacturer=MANUFACTURER,
            model=coordinator.data.model if coordinator.data else None,
            name=coordinator.entry.title,
            serial_number=coordinator.data.serial if coordinator.data else None,
        )

    @property
    def projector_data(self) -> SonyADCPData | None:
        return self.coordinator.data

    @property
    def is_powered_on(self) -> bool:
        status = self.projector_data.power_status if self.projector_data else None
        return status in POWER_ON_STATES

    @property
    def is_powered_off(self) -> bool:
        status = self.projector_data.power_status if self.projector_data else None
        return status in POWER_OFF_STATES

    @property
    def is_transitioning(self) -> bool:
        status = self.projector_data.power_status if self.projector_data else None
        return status in POWER_TRANSITION_STATES
