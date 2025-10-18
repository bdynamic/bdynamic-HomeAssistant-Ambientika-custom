# Ambientika Smart - Home Assistant Custom Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/bdynamic/HomeAssistant-Ambientika-custom.svg)](https://github.com/bdynamic/HomeAssistant-Ambientika-custom/releases)

A Home Assistant custom integration for **Südwind Ambientika smart** single-room heat recovery ventilation systems.

This custom integration provides a modern, user-friendly alternative to the original YAML package, offering:

- **UI-based configuration** through Home Assistant's integration setup
- **Automatic device discovery** and configuration
- **Clean entity management** with proper device grouping
- **Service-based controls** for advanced automation
- **Robust error handling** and automatic token refresh

## Features

### Supported Devices
- **Master devices**: Full control including operating modes, fan speed, humidity levels
- **Slave devices**: Monitoring capabilities with temperature, humidity, and status sensors

### Entity Types
- **Sensors**: Temperature, humidity, air quality, filter status, signal strength
- **Binary Sensors**: Humidity alarms, night alarms
- **Switch**: Master device on/off control
- **Number**: Fan speed, humidity level, light sensor level controls
- **Select**: Operating mode selection

### Services
- `ambientika.reset_filter`: Reset device filter status
- `ambientika.change_mode`: Change operating mode with full parameter control

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu and select "Custom repositories"
4. Add `https://github.com/bdynamic/HomeAssistant-Ambientika-custom` as a custom repository
5. Select "Integration" as the category
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub](https://github.com/bdynamic/HomeAssistant-Ambientika-custom/releases)
2. Extract the `custom_components/ambientika` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for "Ambientika Smart"
4. Enter your Ambientika account credentials
5. Configure each device with its serial number (MAC address) and role

## Migration from YAML Package

If you're migrating from the original YAML package:

1. Remove the YAML package configuration from your `configuration.yaml`
2. Delete the package files from your `packages` directory
3. Restart Home Assistant
4. Install this custom integration
5. Configure your devices through the UI

Your automation and dashboard configurations may need updates to use the new entity IDs.

## Requirements

- Home Assistant 2023.1.0 or newer
- Active internet connection (cloud-based API)
- Valid Ambientika account with registered devices

## Support

- **Issues**: [GitHub Issues](https://github.com/bdynamic/HomeAssistant-Ambientika-custom/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bdynamic/HomeAssistant-Ambientika-custom/discussions)

## Credits

Based on the original reverse-engineering work and YAML package by [Flo-R1der](https://github.com/Flo-R1der/ambientika-smart_4_home-assistant).

## License

This project is licensed under the same terms as the original package.