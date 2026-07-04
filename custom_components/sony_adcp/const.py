"""Constants for the Sony ADCP integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "sony_adcp"
MANUFACTURER: Final = "Sony"

CONF_PASSWORD: Final = "password"
CONF_PORT: Final = "port"
CONF_SCAN_INTERVAL: Final = "scan_interval"

DEFAULT_ADCP_PORT: Final = 53595
DEFAULT_SDAP_PORT: Final = 53862
DEFAULT_PASSWORD: Final = ""
DEFAULT_SCAN_INTERVAL: Final = 30
DEFAULT_TIMEOUT: Final = 10
SDAP_DISCOVERY_TIMEOUT: Final = 12

POWER_ON_STATES: Final = frozenset({'"on"', "on"})
POWER_OFF_STATES: Final = frozenset({'"standby"', "standby"})
POWER_TRANSITION_STATES: Final = frozenset(
    {'"startup"', '"cooling1"', '"cooling2"', "startup", "cooling1", "cooling2"}
)

PICTURE_MODE_OPTIONS: Final = [
    "cinema_film1",
    "cinema_film2",
    "reference",
    "tv",
    "photo",
    "game",
    "brt_cinema",
    "brt_tv",
    "user",
    "user1",
    "user2",
    "user3",
]

PICTURE_MODE_LABELS: Final = {
    "cinema_film1": "Cinema Film 1",
    "cinema_film2": "Cinema Film 2",
    "reference": "Reference",
    "tv": "TV",
    "photo": "Photo",
    "game": "Game",
    "brt_cinema": "Bright Cinema",
    "brt_tv": "Bright TV",
    "user": "User",
    "user1": "User 1",
    "user2": "User 2",
    "user3": "User 3",
}

INPUT_OPTIONS: Final = ["hdmi1", "hdmi2"]
INPUT_LABELS: Final = {"hdmi1": "HDMI 1", "hdmi2": "HDMI 2"}

ASPECT_OPTIONS: Final = [
    "full1",
    "full2",
    "normal",
    "stretch",
    "v_stretch",
    "squeeze",
    "1.85_1_zoom",
    "2.35_1_zoom",
    "aspect_ratio_scaling",
]

GAMMA_OPTIONS: Final = [
    "1.8",
    "2.0",
    "2.1",
    "2.2",
    "2.4",
    "2.6",
    "gamma7",
    "gamma8",
    "gamma9",
    "gamma10",
    "off",
]

COLOR_TEMP_OPTIONS: Final = [
    "d93",
    "d75",
    "d65",
    "d55",
    "dci",
    "custom1",
    "custom2",
    "custom3",
    "custom4",
    "custom5",
]

MOTIONFLOW_OPTIONS: Final = [
    "off",
    "smooth_high",
    "smooth_low",
    "impulse",
    "combination",
    "true_cinema",
]

LENS_MEMORY_OPTIONS: Final = [
    "1.85_1",
    "2.35_1",
    "custom1",
    "custom2",
    "custom3",
    "custom4",
    "custom5",
]

POLL_ATTRIBUTES: Final = (
    "power_status",
    "input",
    "picture_mode",
    "aspect",
    "gamma_correction",
    "color_temp",
    "hdr_tone_mapping",
    "motionflow",
    "blank",
    "pic_pos_sel",
    "calibration_auto",
)

SERVICE_SEND_COMMAND: Final = "send_command"
ATTR_COMMAND: Final = "command"
