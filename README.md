# hass-sony-adcp

[![Validate](https://github.com/wiggs555/hass-sony-adcp/actions/workflows/validate.yml/badge.svg)](https://github.com/wiggs555/hass-sony-adcp/actions/workflows/validate.yml)

Home Assistant custom integration for controlling Sony projectors over **ADCP** (Advanced Display Control Protocol).

Tested against the **Sony VPL-VW295ES**, with support expected for other Sony home cinema projectors that expose ADCP on TCP port **53595**.

## Repository layout

This repository follows the [HACS integration structure](https://www.hacs.xyz/docs/publish/integration/):

```text
hass-sony-adcp/
├── custom_components/sony_adcp/   # Integration code (installed by HACS)
├── hacs.json                      # HACS metadata
├── info.md                        # HACS info panel content
├── tests/                         # Unit tests (not installed)
└── .github/workflows/validate.yml # hassfest + HACS CI checks
```

## Features

- Power on/off and HDMI input selection via `media_player`
- Calibrated picture preset selection
- Picture controls: aspect ratio, gamma, color temperature, motionflow
- Lens memory selection
- Color calibration actions (start, reset, return) and auto-calibration toggle
- Raw ADCP command service for advanced automation
- Optional SDAP-based discovery during setup

## Projector setup

On the projector web UI (`http://<projector-ip>`):

1. Set **Standby Mode** to **Standard** (Low disables network control in standby).
2. Ensure **ADCP** is enabled (default ON).
3. Note the ADCP password (Web UI password) or disable authentication under **Setup → Advanced → ADCP**.
4. Restart the ADCP service after changing authentication settings.

## HACS installation

1. Open **HACS → Integrations → Custom repositories**.
2. Add `https://github.com/wiggs555/hass-sony-adcp` as an **Integration** repository.
3. Install **Sony ADCP Projector**.
4. Restart Home Assistant.
5. Go to **Settings → Devices & Services → Add Integration** and search for **Sony ADCP Projector**.

To publish as a default HACS repository later, register the integration in [home-assistant/brands](https://github.com/home-assistant/brands) and remove the `ignore: brands` line from `.github/workflows/validate.yml`.

## Manual installation

Copy `custom_components/sony_adcp` into your Home Assistant `custom_components` directory and restart Home Assistant.

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Host | required | Projector IP address |
| Password | empty | ADCP/Web UI password when authentication is enabled |
| Port | 53595 | ADCP TCP port |
| Scan interval | 30 | Polling interval in seconds |

## Entities

| Entity | Description |
|--------|-------------|
| `media_player` | Power and HDMI input |
| `select.picture_preset` | Calibrated picture mode |
| `select.aspect` | Aspect ratio |
| `select.gamma` | Gamma correction |
| `select.color_temperature` | Color temperature |
| `select.motionflow` | Motionflow mode |
| `select.lens_memory` | Lens position memory |
| `switch.calibration_auto` | Auto color calibration |
| `button.start_calibration` | Start color calibration |
| `button.reset_calibration` | Reset color calibration |
| `button.return_calibration` | Revert calibration changes |
| `sensor.power_status` | Current power state |
| `sensor.model` | Projector model name |

## Service: `sony_adcp.send_command`

Send any raw ADCP command:

```yaml
service: sony_adcp.send_command
data:
  command: 'picture_mode "reference"'
```

## Automation example

```yaml
alias: Theater off
trigger:
  - platform: state
    entity_id: input_boolean.theater_mode
    to: "off"
action:
  - service: media_player.turn_off
    target:
      entity_id: media_player.sony_projector
```

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## Protocol references

- [Sony Protocol Manual (Common)](https://www.sony.com/electronics/support/res/manuals/9932/56e8960c34dfa2b9a3c29caae4b87340/99327515M.pdf)
- [VPL-VW295ES Protocol Manual (Supported Commands)](https://www.sony.com/electronics/support/res/manuals/9932/68bf8c3b38750c56cb60dcb8f1dfa909/99327615M.pdf)

## License

MIT
