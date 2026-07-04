"""Select platform for Sony ADCP."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ASPECT_OPTIONS,
    COLOR_TEMP_OPTIONS,
    GAMMA_OPTIONS,
    INPUT_LABELS,
    INPUT_OPTIONS,
    LENS_MEMORY_OPTIONS,
    MOTIONFLOW_OPTIONS,
    PICTURE_MODE_LABELS,
    PICTURE_MODE_OPTIONS,
)
from .coordinator import SonyADCPCoordinator
from .entity import SonyADCPEntity


@dataclass(frozen=True, slots=True)
class SelectDefinition:
    """Definition for an ADCP select entity."""

    key: str
    command: str
    translation_key: str
    fallback_options: list[str]
    option_labels: dict[str, str] | None = None


SELECT_DEFINITIONS: tuple[SelectDefinition, ...] = (
    SelectDefinition(
        key="picture_mode",
        command="picture_mode",
        translation_key="picture_mode",
        fallback_options=PICTURE_MODE_OPTIONS,
        option_labels=PICTURE_MODE_LABELS,
    ),
    SelectDefinition(
        key="input",
        command="input",
        translation_key="input",
        fallback_options=INPUT_OPTIONS,
        option_labels=INPUT_LABELS,
    ),
    SelectDefinition(
        key="aspect",
        command="aspect",
        translation_key="aspect",
        fallback_options=ASPECT_OPTIONS,
    ),
    SelectDefinition(
        key="gamma_correction",
        command="gamma_correction",
        translation_key="gamma",
        fallback_options=GAMMA_OPTIONS,
    ),
    SelectDefinition(
        key="color_temp",
        command="color_temp",
        translation_key="color_temperature",
        fallback_options=COLOR_TEMP_OPTIONS,
    ),
    SelectDefinition(
        key="motionflow",
        command="motionflow",
        translation_key="motionflow",
        fallback_options=MOTIONFLOW_OPTIONS,
    ),
    SelectDefinition(
        key="pic_pos_sel",
        command="pic_pos_sel",
        translation_key="lens_memory",
        fallback_options=LENS_MEMORY_OPTIONS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SonyADCPCoordinator = entry.runtime_data
    async_add_entities(
        SonyADCPSelectEntity(coordinator, definition) for definition in SELECT_DEFINITIONS
    )


class SonyADCPSelectEntity(SonyADCPEntity, SelectEntity):
    """ADCP-backed select entity."""

    def __init__(self, coordinator: SonyADCPCoordinator, definition: SelectDefinition) -> None:
        super().__init__(coordinator)
        self._definition = definition
        self._attr_translation_key = definition.translation_key
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{definition.key}"

    @property
    def current_option(self) -> str | None:
        if not self.projector_data:
            return None
        return getattr(self.projector_data, self._definition.key, None)

    @property
    def options(self) -> list[str]:
        if self.projector_data and self._definition.command in self.projector_data.ranges:
            return self.projector_data.ranges[self._definition.command]
        return self._definition.fallback_options

    @property
    def option_labels(self) -> dict[str, str] | None:
        return self._definition.option_labels

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_select(self._definition.command, option)
