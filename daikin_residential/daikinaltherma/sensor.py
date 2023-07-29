"""Support for Daikin AC sensors."""

from unicodedata import name

# from homeassistant.const import (
#     CONF_DEVICE_CLASS,
#     CONF_ICON,
#     CONF_NAME,
#     CONF_TYPE,
#     CONF_UNIT_OF_MEASUREMENT,
# )

# from homeassistant.components.sensor import (
#     SensorEntity,
#     STATE_CLASS_MEASUREMENT,
#     STATE_CLASS_TOTAL_INCREASING,
# )

# from homeassistant.helpers.entity import EntityCategory

# from .const import (
#     SensorEntity,
#     STATE_CLASS_MEASUREMENT,
#     STATE_CLASS_TOTAL_INCREASING,
# )

from .const import (
    CONF_DEVICE_CLASS,
    CONF_ICON,
    CONF_NAME,
    CONF_TYPE,
    CONF_UNIT_OF_MEASUREMENT,
)

from .daikin_base import Appliance

from .const import (
    DOMAIN as DAIKIN_DOMAIN,
    DAIKIN_DEVICES,
    ATTR_COOL_ENERGY,
    ATTR_HEAT_ENERGY,
    ATTR_HEAT_TANK_ENERGY,
    ATTR_LEAVINGWATER_TEMPERATURE,
    ATTR_LEAVINGWATER_OFFSET,
    ATTR_OUTSIDE_TEMPERATURE,
    ATTR_ROOM_TEMPERATURE,
    ATTR_TANK_TEMPERATURE,
    ATTR_SETPOINT_MODE,
    ATTR_OPERATION_MODE,
    ATTR_TANK_SETPOINT_MODE,
    ATTR_CONTROL_MODE,
    ATTR_IS_HOLIDAY_MODE_ACTIVE,
    ATTR_IS_IN_EMERGENCY_STATE,
    ATTR_IS_IN_ERROR_STATE,
    ATTR_IS_IN_INSTALLER_STATE,
    ATTR_IS_IN_WARNING_STATE,
    ATTR_ERROR_CODE,
    ATTR_ENERGY_CONSUMPTION,
    # TANK
    ATTR_TANK_OPERATION_MODE,
    ATTR_TANK_HEATUP_MODE,
    ATTR_TANK_IS_HOLIDAY_MODE_ACTIVE,
    ATTR_TANK_IS_IN_EMERGENCY_STATE,
    ATTR_TANK_IS_IN_ERROR_STATE,
    ATTR_TANK_IS_IN_INSTALLER_STATE,
    ATTR_TANK_IS_IN_WARNING_STATE,
    ATTR_TANK_IS_POWERFUL_MODE_ACTIVE,
    ATTR_TANK_ERROR_CODE,
    ATTR_ENERGY_CONSUMPTION_TANK,
    SENSOR_TYPE_ENERGY,
    SENSOR_TYPE_POWER,
    SENSOR_TYPE_TEMPERATURE,
    SENSOR_TYPE_INFO,
    SENSOR_TYPE_GATEWAY_DIAGNOSTIC,
    SENSOR_PERIODS,
    SENSOR_TYPES,
    ATTR_WIFI_STRENGTH,
    ATTR_WIFI_SSID,
    ATTR_LOCAL_SSID,
    ATTR_MAC_ADDRESS,
    ATTR_SERIAL_NUMBER,
)

import logging

_LOGGER = logging.getLogger(__name__)


def createSensorsByDaikinAPI(data: dict) -> dict:
    """Set up Daikin climate based on config_entry."""
    sensors = {}
    prog = 0

    for dev_id, device in data[DAIKIN_DOMAIN][DAIKIN_DEVICES].items():
        if device.getData(ATTR_LEAVINGWATER_TEMPERATURE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_LEAVINGWATER_TEMPERATURE, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'",
                device.name,
                ATTR_LEAVINGWATER_TEMPERATURE,
            )

        if device.getData(ATTR_LEAVINGWATER_OFFSET) is not None:
            sensor = DaikinSensor.factory(device, ATTR_LEAVINGWATER_OFFSET, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_LEAVINGWATER_OFFSET
            )

        if device.getData(ATTR_ROOM_TEMPERATURE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_ROOM_TEMPERATURE, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_ROOM_TEMPERATURE
            )

        if device.getData(ATTR_TANK_TEMPERATURE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_TANK_TEMPERATURE, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_TANK_TEMPERATURE
            )

        if device.getData(ATTR_OUTSIDE_TEMPERATURE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_OUTSIDE_TEMPERATURE, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_OUTSIDE_TEMPERATURE
            )

        for period in SENSOR_PERIODS:
            if device.getDataEC(ATTR_ENERGY_CONSUMPTION, "cooling", period) is not None:
                sensor = DaikinSensor.factory(device, ATTR_COOL_ENERGY, "", period)
                sensors[sensor.Key] = sensor                
                # sensors.append(sensor)
            else:
                _LOGGER.info(
                    "Device '%s' NOT supports %s cooling energy consumption",
                    device.name,
                    period,
                )

            if device.getDataEC(ATTR_ENERGY_CONSUMPTION, "heating", period) is not None:
                sensor = DaikinSensor.factory(device, ATTR_HEAT_ENERGY, "", period)
                sensors[sensor.Key] = sensor
                # sensors.append(sensor)
            else:
                _LOGGER.info(
                    "Device '%s' NOT supports %s heating energy consumption",
                    device.name,
                    period,
                )

            if (
                device.getDataEC(ATTR_ENERGY_CONSUMPTION_TANK, "heating", period)
                is not None
            ):
                sensor = DaikinSensor.factory(device, ATTR_HEAT_TANK_ENERGY, "", period)
                sensors[sensor.Key] = sensor
                # sensors.append(sensor)
            else:
                _LOGGER.info("Device NOT supports %s tank energy consumption", period)

        if device.getData(ATTR_OPERATION_MODE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_OPERATION_MODE, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_OPERATION_MODE
            )

        if device.getData(ATTR_SETPOINT_MODE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_SETPOINT_MODE, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_SETPOINT_MODE
            )

        if device.getData(ATTR_TANK_SETPOINT_MODE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_TANK_SETPOINT_MODE, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_TANK_SETPOINT_MODE
            )

        if device.getData(ATTR_CONTROL_MODE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_CONTROL_MODE, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_CONTROL_MODE
            )

        if device.getData(ATTR_IS_HOLIDAY_MODE_ACTIVE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_IS_HOLIDAY_MODE_ACTIVE, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'",
                device.name,
                ATTR_IS_HOLIDAY_MODE_ACTIVE,
            )

        if device.getData(ATTR_IS_IN_EMERGENCY_STATE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_IS_IN_EMERGENCY_STATE, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_IS_IN_EMERGENCY_STATE
            )

        if device.getData(ATTR_IS_IN_ERROR_STATE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_IS_IN_ERROR_STATE, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_IS_IN_ERROR_STATE
            )

        if device.getData(ATTR_IS_IN_INSTALLER_STATE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_IS_IN_INSTALLER_STATE, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_IS_IN_INSTALLER_STATE
            )

        if device.getData(ATTR_IS_IN_WARNING_STATE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_IS_IN_WARNING_STATE, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_IS_IN_WARNING_STATE
            )

        if device.getData(ATTR_ERROR_CODE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_ERROR_CODE, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info("Device '%s' NOT supports '%s'", device.name, ATTR_ERROR_CODE)

        if device.getData(ATTR_WIFI_STRENGTH) is not None:
            sensor = DaikinSensor.factory(device, ATTR_WIFI_STRENGTH, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_WIFI_STRENGTH
            )

        if device.getData(ATTR_WIFI_SSID) is not None:
            sensor = DaikinSensor.factory(device, ATTR_WIFI_SSID, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_WIFI_STRENGTH
            )

        if device.getData(ATTR_LOCAL_SSID) is not None:
            sensor = DaikinSensor.factory(device, ATTR_LOCAL_SSID, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info("Device '%s' NOT supports '%s'", device.name, ATTR_LOCAL_SSID)

        if device.getData(ATTR_MAC_ADDRESS) is not None:
            sensor = DaikinSensor.factory(device, ATTR_MAC_ADDRESS, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info("Device '%s' NOT supports '%s'", device.name, ATTR_MAC_ADDRESS)

        if device.getData(ATTR_SERIAL_NUMBER) is not None:
            sensor = DaikinSensor.factory(device, ATTR_SERIAL_NUMBER, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_SERIAL_NUMBER
            )

        if device.getData(ATTR_TANK_HEATUP_MODE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_TANK_HEATUP_MODE, "")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_TANK_HEATUP_MODE
            )

        if device.getData(ATTR_TANK_OPERATION_MODE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_TANK_OPERATION_MODE, "TANK")
            sensors[sensor.Key] = sensor            
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_TANK_OPERATION_MODE
            )

        if device.getData(ATTR_TANK_IS_HOLIDAY_MODE_ACTIVE) is not None:
            sensor = DaikinSensor.factory(
                device, ATTR_TANK_IS_HOLIDAY_MODE_ACTIVE, "TANK"
            )
            sensors[sensor.Key] = sensor            
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'",
                device.name,
                ATTR_TANK_IS_HOLIDAY_MODE_ACTIVE,
            )

        if device.getData(ATTR_TANK_IS_IN_EMERGENCY_STATE) is not None:
            sensor = DaikinSensor.factory(
                device, ATTR_TANK_IS_IN_EMERGENCY_STATE, "TANK"
            )
            sensors[sensor.Key] = sensor  
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'",
                device.name,
                ATTR_TANK_IS_IN_EMERGENCY_STATE,
            )

        if device.getData(ATTR_TANK_IS_IN_ERROR_STATE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_TANK_IS_IN_ERROR_STATE, "TANK")
            sensors[sensor.Key] = sensor            
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'",
                device.name,
                ATTR_TANK_IS_IN_ERROR_STATE,
            )

        if device.getData(ATTR_TANK_IS_IN_INSTALLER_STATE) is not None:
            sensor = DaikinSensor.factory(
                device, ATTR_TANK_IS_IN_INSTALLER_STATE, "TANK"
            )
            sensors[sensor.Key] = sensor            
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'",
                device.name,
                ATTR_TANK_IS_IN_INSTALLER_STATE,
            )

        if device.getData(ATTR_TANK_IS_IN_WARNING_STATE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_TANK_IS_IN_WARNING_STATE, "TANK")
            sensors[sensor.Key] = sensor            
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'",
                device.name,
                ATTR_TANK_IS_IN_WARNING_STATE,
            )

        if device.getData(ATTR_TANK_IS_POWERFUL_MODE_ACTIVE) is not None:
            sensor = DaikinSensor.factory(
                device, ATTR_TANK_IS_POWERFUL_MODE_ACTIVE, "TANK"
            )
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'",
                device.name,
                ATTR_TANK_IS_POWERFUL_MODE_ACTIVE,
            )

        if device.getData(ATTR_TANK_ERROR_CODE) is not None:
            sensor = DaikinSensor.factory(device, ATTR_TANK_ERROR_CODE, "TANK")
            sensors[sensor.Key] = sensor
            # sensors.append(sensor)
        else:
            _LOGGER.info(
                "Device '%s' NOT supports '%s'", device.name, ATTR_TANK_ERROR_CODE
            )
    return sensors


class DaikinSensor(object):
    """Representation of a Sensor."""

    @staticmethod
    def factory(device: Appliance, monitored_state: str, type, period=""):
        """Initialize any DaikinSensor."""
        try:
            cls = {
                SENSOR_TYPE_TEMPERATURE: DaikinClimateSensor,
                SENSOR_TYPE_POWER: DaikinEnergySensor,
                SENSOR_TYPE_ENERGY: DaikinEnergySensor,
                SENSOR_TYPE_INFO: DaikinInfoSensor,
                SENSOR_TYPE_GATEWAY_DIAGNOSTIC: DaikinGatewaySensor,
            }[SENSOR_TYPES[monitored_state][CONF_TYPE]]
            return cls(device, monitored_state, type, period)
        except Exception as error:
            # print("error: " + error)
            _LOGGER.error("%s", format(error))
            return

    def __init__(
        self, device: Appliance, monitored_state: str, type, period=""
    ) -> None:
        """Initialize the sensor."""
        self._device = device
        self._sensor = SENSOR_TYPES[monitored_state]
        self._period = period
        self._Key = ""
        if period != "":
            periodName = SENSOR_PERIODS[period]
            self._name = f"{device.name} {periodName} {self._sensor[CONF_NAME]}"
            self._Key = f"{device.name}.{periodName}.{self._sensor[CONF_NAME]}"
        else:
            if type == "":
                # Name for Heat Pump Flags
                self._name = f"{device.name} {self._sensor[CONF_NAME]}"
                self._Key = f"{device.name}.{self._sensor[CONF_NAME]}"
            elif type == "TANK":
                # Name for Hot Water Tank Flags
                # self._name = f"{device.name} TANK {self._sensor[CONF_NAME]}"
                self._name = f"{device.name} {self._sensor[CONF_NAME]}"
                self._Key = f"{device.name}.{self._sensor[CONF_NAME]}"
        self._device_attribute = monitored_state
        key = self._Key.replace(" ", "")
        self._Key = f"sensor.{key}"
        _LOGGER.info("Device '%s' supports sensor '%s' (key: '%s')", device.name, self._name,self._Key)

    @property
    def available(self):
        """Return the availability of the underlying device."""
        return self._device.available

    @property
    def unique_id(self):
        """Return a unique ID."""
        devID = self._device.getId()
        if self._period != "":
            return f"{devID}_{self._device_attribute}_{self._period}"
        return f"{devID}_{self._device_attribute}"

    @property
    def Key(self):
        """Return a unique ID."""
        return self._Key

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        raise NotImplementedError

    @property
    def device_class(self):
        """Return the class of this device."""
        return self._sensor.get(CONF_DEVICE_CLASS)

    @property
    def icon(self):
        """Return the icon of this device."""
        return self._sensor.get(CONF_ICON)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        uom = self._sensor[CONF_UNIT_OF_MEASUREMENT]
        return uom

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._device.device_info()

    # @property
    # def entity_category(self):
    #     """
    #     Return the entity_category the sensor.
    #     CONFIG:Set to config for an entity which allows changing the configuration
    #      of a device, for example a switch entity making it possible to turn the
    #      background illumination of a switch on and off.

    #     DIAGNOSTIC: Set to diagnostic for an entity exposing some configuration
    #      parameter or diagnostics of a device but does not allow changing it,

    #     SYSTEM: Set to system for an entity which is not useful for the user
    #      to interact with."""

    #     configList = [
    #         ATTR_SETPOINT_MODE,
    #         ATTR_OPERATION_MODE,
    #         ATTR_TANK_SETPOINT_MODE,
    #         ATTR_TANK_OPERATION_MODE,
    #         ATTR_CONTROL_MODE,
    #         ATTR_IS_HOLIDAY_MODE_ACTIVE,
    #         ATTR_TANK_HEATUP_MODE,
    #         ATTR_TANK_IS_HOLIDAY_MODE_ACTIVE,
    #         ATTR_TANK_IS_POWERFUL_MODE_ACTIVE,
    #     ]
    #     diagnosticList = [
    #         ATTR_IS_IN_EMERGENCY_STATE,
    #         ATTR_IS_IN_ERROR_STATE,
    #         ATTR_IS_IN_INSTALLER_STATE,
    #         ATTR_IS_IN_WARNING_STATE,
    #         ATTR_ERROR_CODE,
    #         ATTR_TANK_IS_IN_EMERGENCY_STATE,
    #         ATTR_TANK_IS_IN_ERROR_STATE,
    #         ATTR_TANK_IS_IN_INSTALLER_STATE,
    #         ATTR_TANK_IS_IN_WARNING_STATE,
    #         ATTR_TANK_ERROR_CODE,
    #         ATTR_WIFI_STRENGTH,
    #         ATTR_WIFI_SSID,
    #         ATTR_LOCAL_SSID,
    #         ATTR_MAC_ADDRESS,
    #         ATTR_SERIAL_NUMBER,
    #     ]
    #     try:
    #         if self._device_attribute in configList:
    #             self._entity_category = EntityCategory.CONFIG
    #             return self._entity_category
    #         elif self._device_attribute in diagnosticList:
    #             self._entity_category = EntityCategory.DIAGNOSTIC
    #             return self._entity_category

    #         else:
    #             return None
    #     except Exception as e:
    #         _LOGGER.info(
    #             "entity_category not supported by this Home Assistant. /n \
    #                 Try to update"
    #         )
    #         return None

    async def async_update(self):
        """Retrieve latest state."""
        await self._device.api.async_update()


class DaikinInfoSensor(DaikinSensor):
    """Representation of a Climate Sensor."""

    @property
    def state(self):
        """Return the internal state of the sensor."""
        return self._device.getValue(self._device_attribute)

    # @property
    # def state_class(self):
    #     return STATE_CLASS_MEASUREMENT


class DaikinClimateSensor(DaikinSensor):
    """Representation of a Climate Sensor."""

    @property
    def state(self):
        """Return the internal state of the sensor."""
        return self._device.getValue(self._device_attribute)

    # @property
    # def state_class(self):
    #     return STATE_CLASS_MEASUREMENT


class DaikinEnergySensor(DaikinSensor):
    """Representation of a power/energy consumption sensor."""

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._device_attribute == ATTR_COOL_ENERGY:
            return round(
                self._device.energy_consumption(
                    ATTR_ENERGY_CONSUMPTION, "cooling", self._period
                ),
                3,
            )

        if self._device_attribute == ATTR_HEAT_ENERGY:
            return round(
                self._device.energy_consumption(
                    ATTR_ENERGY_CONSUMPTION, "heating", self._period
                ),
                3,
            )

        # DAMIANO
        if self._device_attribute == ATTR_HEAT_TANK_ENERGY:
            return round(
                self._device.energy_consumption(
                    ATTR_ENERGY_CONSUMPTION_TANK, "heating", self._period
                ),
                3,
            )
        return None

    # @property
    # def state_class(self):
    #     return STATE_CLASS_TOTAL_INCREASING


class DaikinGatewaySensor(DaikinSensor):
    """Representation of a WiFi Sensor."""

    # set default category for these entities
    # _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def state(self):
        """Return the internal state of the sensor."""
        return self._device.getValue(self._device_attribute)

    # @property
    # def state_class(self):
    #     if self._device_attribute == ATTR_WIFI_STRENGTH:
    #         return STATE_CLASS_MEASUREMENT
    #     else:
    #         return None

    @property
    def entity_registry_enabled_default(self):
        # auto disable these entities when added for the first time
        # except the wifi signal
        return self._device_attribute == ATTR_WIFI_STRENGTH
