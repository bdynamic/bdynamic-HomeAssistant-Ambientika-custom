# Ambientika Smart Custom Component

This directory contains the **Home Assistant Custom Integration** version of the Ambientika Smart package.

## What Changed

This project has been converted from a YAML-based package to a full Home Assistant custom integration, providing:

### Benefits
- **UI Configuration**: No more manual YAML editing - configure through Home Assistant's integration UI
- **Automatic Setup**: Devices are automatically discovered and configured
- **Better Organization**: All entities are properly grouped under device entries
- **Robust Error Handling**: Automatic token refresh and connection retry logic
- **Service Integration**: Type-safe service calls with proper validation
- **HACS Support**: Easy installation and updates through HACS

### Architecture

```
custom_components/ambientika/
├── __init__.py          # Main integration setup
├── api.py              # REST API client with authentication
├── config_flow.py      # UI configuration flow
├── coordinator.py      # Data update coordinator
├── const.py           # Constants and configuration
├── manifest.json      # Integration metadata
├── services.yaml      # Service definitions
├── strings.json       # UI text translations
├── sensor.py          # Sensor platform (temperature, humidity, etc.)
├── binary_sensor.py   # Binary sensor platform (alarms)
├── switch.py          # Switch platform (master on/off)
├── number.py          # Number platform (fan speed, humidity level)
└── select.py          # Select platform (operating mode)
```

### Migration from YAML Package

If you were using the original YAML package:

1. **Backup your configuration** before proceeding
2. **Remove the YAML package**:
   - Delete package references from `configuration.yaml`
   - Remove package files from `/config/packages/ambientika_smart/`
3. **Install this custom integration**:
   - Copy to `/config/custom_components/ambientika/` or install via HACS
4. **Restart Home Assistant**
5. **Add the integration**:
   - Go to Settings > Devices & Services
   - Add "Ambientika Smart" integration
   - Configure with your credentials and devices
6. **Update automations and dashboards** to use new entity IDs

### Entity ID Changes

The entity naming convention has changed:

**Old (YAML Package):**
- `sensor.ambientika_master_1_temperature_raw`
- `switch.ambientika_master_1`
- `input_number.ambientika_master_1_fanspeed`

**New (Custom Integration):**
- `sensor.ambientika_master_temperature`
- `switch.ambientika_master`
- `number.ambientika_master_fan_speed`

### Services

The integration provides two services:

1. **`ambientika.reset_filter`**: Reset device filter status
2. **`ambientika.change_mode`**: Change operating mode with full parameter control

### Configuration

All configuration is done through the UI:
- **Username/Password**: Your Ambientika account credentials
- **Device Serial**: Device MAC address (same as before)
- **Device Role**: Master or Slave

### Features Preserved

All functionality from the original package is preserved:
- Master/Slave device support
- All sensor types (temperature, humidity, air quality, etc.)
- Operating mode control
- Fan speed and humidity level settings
- Filter status monitoring and reset
- Alarm sensors

### New Features

- Automatic token refresh (no more manual token management)
- Device grouping in Home Assistant UI
- Better error handling and recovery
- Service-based automation (no more REST command templates)
- Proper device information and diagnostics

## Installation

See the main [HACS_README.md](HACS_README.md) for installation instructions.

## Support

For issues specific to the custom integration, please use the [GitHub Issues](https://github.com/bdynamic/HomeAssistant-Ambientika-custom/issues) page.