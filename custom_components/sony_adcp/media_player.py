"""Media player platform for Sony ADCP."""

from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import INPUT_LABELS, INPUT_OPTIONS, POWER_OFF_STATES, POWER_ON_STATES, POWER_TRANSITION_STATES
from .coordinator import SonyADCPCoordinator
from .entity import SonyADCPEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SonyADCPCoordinator = entry.runtime_data
    async_add_entities([SonyADCPMediaPlayer(coordinator)])


class SonyADCPMediaPlayer(SonyADCPEntity, MediaPlayerEntity):
    """Representation of a Sony projector."""

    _attr_device_class = MediaPlayerDeviceClass.TV
    _attr_name = None
    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(self, coordinator: SonyADCPCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_media_player"

    @property
    def state(self) -> MediaPlayerState:
        status = self.projector_data.power_status if self.projector_data else None
        if status in POWER_ON_STATES:
            return MediaPlayerState.ON
        if status in POWER_OFF_STATES:
            return MediaPlayerState.OFF
        if status in POWER_TRANSITION_STATES:
            return MediaPlayerState.IDLE
        return MediaPlayerState.OFF

    @property
    def source(self) -> str | None:
        if not self.projector_data or not self.projector_data.input:
            return None
        return INPUT_LABELS.get(self.projector_data.input, self.projector_data.input)

    @property
    def source_list(self) -> list[str]:
        return [INPUT_LABELS.get(option, option) for option in INPUT_OPTIONS]

    async def async_turn_on(self) -> None:
        await self.coordinator.client.set_value("power", "on")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        await self.coordinator.client.set_value("power", "off")
        await self.coordinator.async_request_refresh()

    async def async_select_source(self, source: str) -> None:
        for key, label in INPUT_LABELS.items():
            if source in {key, label}:
                await self.coordinator.async_set_select("input", key)
                return
        await self.coordinator.async_set_select("input", source)
