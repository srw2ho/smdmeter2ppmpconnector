import asyncio

# import datetime
import json
import logging
import time
from ppmpmessage.v3.device_state import DeviceState
from ppmpmessage.v3.util import local_now
from ppmpmessage.convertor.simple_variables import SimpleVariables
from daikin_residential.daikinaltherma.climate import DaikinClimate
from daikin_residential.daikinaltherma.daikin_api import DaikinApi
from daikin_residential.daikinaltherma.daikin_base import Appliance
from daikin_residential.daikinaltherma.sensor import DaikinSensor
from daikin_residential.daikinaltherma.water_heater import DaikinWaterTank
from helpers.timespan import TimeSpan

from datetime import datetime, timedelta, timezone
from dateutil import parser, relativedelta

from mqttservice.mqttdevicebase import (
    SERVICE_DEVICE_NAME,
    SERVICE_DEVICE_TYPE,
    MqttDeviceServiceBase,
)

# from mqttservice.mqttdevicemodbusservice import MqttDeviceModbusService


logger = logging.getLogger("root")


class MqttDeviceDaikinService(MqttDeviceServiceBase):
    """OPC-UA Client that provides publish/subscribe as well as polling capabilities

    Arguments:
        object {} --
    """

    def __init__(
        self,
        MQTT_HOST="localhost",
        MQTT_PORT=1883,
        MQTT_USERNAME="",
        MQTT_PASSWORD="",
        MQTT_TLS_CERT="",
        INFODEBUGLEVEL=1,
        MQTT_REFRESH_TIME=1.0,
        MQTT_NETID="PLC1",
        DAIKINUSER="",
        DAIKINPW="",
    ):
        super().__init__(
            MQTT_HOST=MQTT_HOST,
            MQTT_PORT=MQTT_PORT,
            MQTT_USERNAME=MQTT_USERNAME,
            MQTT_PASSWORD=MQTT_PASSWORD,
            MQTT_TLS_CERT=MQTT_TLS_CERT,
            INFODEBUGLEVEL=INFODEBUGLEVEL,
            MQTT_REFRESH_TIME=MQTT_REFRESH_TIME,
            MQTT_NETID=MQTT_NETID,
        )
        self.m_daikinAPI = DaikinApi()
        self.m_daikinUser = DAIKINUSER
        self.m_daikinPW = DAIKINPW

        # self._MQTT_REFRESH_TIME = MQTT_REFRESH_TIME

    def LogInfo(self, jsonpayloadInput: dict) -> dict:
        if self.m_INFODEBUGLEVEL > 0:
            logger.info(f"device: {self.m_MQTT_NETID} Read Input Registers:")

            for k, v in jsonpayloadInput.items():
                value: any = v
                unit: str = ""
                # if v is isinstance (DaikinSensor):
                #     sensor: DaikinSensor = self.m_Sensors[k]
                #     value = sensor.state
                #     unit=sensor.unit_of_measurement
                # if v is isinstance (DaikinSensor):
                #     sensor: DaikinSensor = self.m_Sensors[k]
                #     value = sensor.state
                #     unit=sensor.unit_of_measurement

                if type(value) is list or type(value) is dict:
                    logger.info(f"\t{k}: {str(value)} {unit}")
                elif type(value) is float:
                    logger.info(f"\t{k}: {value:.2f} {unit}")
                else:
                    logger.info(f"\t{k}: {value} {unit}")

    async def connectDevice(self) -> bool:
        connectTryCounter = 3

        while True:
            try:
                await self.m_daikinAPI.retrieveAccessToken(
                    self.m_daikinUser, self.m_daikinPW
                )
                if self.m_daikinAPI.isTokenretrieved():
                    apinfo = await self.m_daikinAPI.getApiInfo()
                    daikindevices: dict[
                        Appliance
                    ] = await self.m_daikinAPI.getCloudDevices()
                    await self.m_daikinAPI.async_update()
                    for value in daikindevices.values():
                        dev: Appliance = value

                        # await dev.updateData()
                        self.m_daikinclimate = DaikinClimate(dev)
                        self.m_daikinwater = DaikinWaterTank(dev)
                        # temp = daikinclimate.current_temperature
                        # watertemp=daikinwater.current_temperature
                        # watertargettemp=daikinwater.target_temperature
                        # print(temp)

                    self.m_Sensors = self.m_daikinAPI.createSensors()

                    self.doMQTTconnect()
                    self.setDeviceState(DeviceState.OK)
                    break
                else:
                    self.setDeviceState(DeviceState.ERROR)
                    if connectTryCounter > 0:
                        time.sleep(3)
                    else:
                        break
                    connectTryCounter = connectTryCounter - 1
            except Exception as error:
                logger.error(f"connectDevice Error: {str(error)}")

        return self.m_daikinAPI.isTokenretrieved()

    def isDeviceConnected(self) -> bool:
        return self.m_daikinAPI.isTokenretrieved()

    async def doWriteMQTTProcessCommand(self, identifier: str, value: any) -> bool:
        doUpdate = False

        if identifier == "WATER.target_temperature":
            await self.m_daikinwater.async_set_tank_temperature(value)
            doUpdate = True

        if identifier == "WATER.tank_state":
            await self.m_daikinwater.async_set_tank_state(value)
            doUpdate = True

        if identifier == "CLIMATE.hvac_mode":
            await self.m_daikinclimate.async_set_hvac_mode(value)
            doUpdate = True

        if identifier == "CLIMATE.preset_mode":
            await self.m_daikinclimate.async_set_preset_mode(value)

            doUpdate = True

        if identifier == "CLIMATE.target_temperature":
            await self.m_daikinclimate.async_set_temperature(
                hvac_mode=self.m_daikinclimate.hvac_mode, temperature=value
            )

            doUpdate = True

        if identifier == "CLIMATE.turn_on":
            await self.m_daikinclimate.async_turn_on()
            doUpdate = True

        if identifier == "CLIMATE.turn_off":
            await self.m_daikinclimate.async_turn_off()
            doUpdate = True

        if identifier == "WATER.turn_on":
            await self.m_daikinwater.async_turn_on()
            doUpdate = True

        if identifier == "WATER.turn_off":
            await self.m_daikinwater.async_turn_off()
            doUpdate = True

        return doUpdate

    async def doMQTTProcessCommand(self, command):
        """Wait for items in the queue and process these items"""

        try:
            doSetting = False
            action = json.loads(command)

            if "identifier" in action:
                identifier = action["identifier"]
                metaKey = action["metakey"]
                if "value" in action:
                    value = action["value"]
                    doSetting = True
                    errorMessage = ""
                    doUpdate = False
                    try:
                        if metaKey in self.m_MetaData.keys():
                            metaValue = self.m_MetaData[metaKey]
                            if metaValue["writetopic"] != "":
                                doUpdate = await self.doWriteMQTTProcessCommand(
                                    identifier, value
                                )

                        if not doUpdate:
                            if self.m_INFODEBUGLEVEL > 0:
                                logger.info(
                                    f"doMQTTProcessCommand:-->MQTT failed: {identifier} = {value} !"
                                )

                    except BaseException as ex:
                        errorMessage = str(ex)
                        doUpdate = False
                    if "notifyid" in action and "notifytopic" in action:
                        # notivy results to requester
                        result = 1
                        if not doUpdate:
                            result = -1
                        if len(errorMessage) > 0:
                            result = -1

                        notifyID = action["notifyid"]
                        notifytopic = action["notifytopic"]
                        notifypayload = {
                            "metakey": action["metakey"],
                            "identifier": identifier,
                            "notifyid": notifyID,
                            "result": result,
                            "errormsg": errorMessage,
                            "setvalue": value,
                            "posix_timestamp": self.getActTime(),
                        }
                        try:
                            if self._mqtt_client.isConnected():
                                self._mqtt_client.publish(
                                    notifytopic, json.dumps(notifypayload), retain=False
                                )
                            else:
                                logger.error(
                                    f"doMQTTProcessCommand:--> MQTT not connected"
                                )

                        except BaseException as ex:
                            logger.error(
                                f"doMQTTProcessCommand:-->json.dumps failed!: {ex}"
                            )

            if not doSetting:
                logger.error(
                    f"doMQTTProcessCommand:-->MQTT:Invalid command structure!: {action}"
                )

        except Exception as exception:
            logger.error(f"MQTTConsumeQueue Parse error: {exception}")

    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"MQTT-Client: on_connect -> publish_MQTTMetaData()")

        # delete previous Topic
        self._mqtt_client.publish(self.getDeviceServicesTopic(), None, retain=True)
        # self._mqtt_client.publish(self.m_device.info_topic(), None, retain=True)

        allregisterPayload = self.readallRegisters()
        # bei start alle retained Senden
        self.doPublishPayload(allregisterPayload, retained=True)

        self.publish_MQTTMetaData()
        logger.info(f"MQTT-Client: on_connect -> publish_cached_values()")

        logger.info(f"MQTT-Client: on_connect -> subscribeMQTTWriteTopis()")

        self.subscribeMQTTWriteTopis()
        # self.publish_cached_values()

        self.setDeviceState(devicestate=DeviceState.OK)

        # devicekey = f"{DEVICE_NAME}.{self._MQTT_NETID}"
        devicekey = f"{self.m_MQTT_NETID}"
        devicetopic = f"mh/{SERVICE_DEVICE_NAME}/{self.m_MQTT_NETID}"
        devicepayload = {
            devicekey: {
                "type": f"{SERVICE_DEVICE_TYPE}",
                "topic": devicetopic,
            }
        }
        deviceservicestopic = self.getDeviceServicesTopic()
        self._mqtt_client.publish(
            deviceservicestopic,
            json.dumps(devicepayload),
            retain=True,
        )

        self.m_onMqttConnected = True

    def getClimateMetaData(self) -> dict:
        ClimateTopics = {
            "CLIMATE.turn_on": {
                "view": "CLIMATE.turn_on",
                "vartype": "bool",
                "writable": True,
                "unit": "",
                "value": self.m_daikinclimate.hvac_mode != "off",
            },
            "CLIMATE.turn_off": {
                "view": "CLIMATE.turn_off",
                "vartype": "bool",
                "writable": True,
                "unit": "",
                "value": self.m_daikinclimate.hvac_mode == "off",
            },
            "CLIMATE.preset_mode": {
                "view": "CLIMATE.preset_mode",
                "vartype": "str",
                "writable": True,
                "unit": "",
                "value": self.m_daikinclimate.preset_mode,
            },
            "CLIMATE.hvac_modes": {
                "view": "CLIMATE.hvac_modes",
                "vartype": "double",
                "writable": False,
                "unit": "",
                "value": self.m_daikinclimate.hvac_modes,
            },
            "CLIMATE.hvac_mode": {
                "view": "CLIMATE.hvac_mode",
                "vartype": "str",
                "writable": True,
                "unit": "",
                "value": self.m_daikinclimate.hvac_mode,
            },
            "CLIMATE.temperature": {
                "view": "CLIMATE.temperature",
                "vartype": "double",
                "writable": True,
                "unit": self.m_daikinclimate.temperature_unit,
                "value": self.m_daikinclimate.current_temperature,
            },
            "CLIMATE.target_temperature_step": {
                "view": "CLIMATE.target_temperature_step",
                "vartype": "double",
                "writable": False,
                "unit": self.m_daikinclimate.temperature_unit,
                "value": self.m_daikinclimate.target_temperature_step,
            },
            "CLIMATE.target_temperature": {
                "view": "CLIMATE.target_temperature",
                "vartype": "double",
                "writable": True,
                "unit": "",
                "value": self.m_daikinclimate.target_temperature,
            },
            "CLIMATE.min_temp": {
                "view": "CLIMATE.min_temp",
                "vartype": "double",
                "writable": False,
                "unit": self.m_daikinclimate.temperature_unit,
                "value": self.m_daikinclimate.min_temp,
            },
            "CLIMATE.max_temp": {
                "view": "CLIMATE.max_temp",
                "vartype": "double",
                "writable": False,
                "unit": self.m_daikinclimate.temperature_unit,
                "value": self.m_daikinclimate.max_temp,
            },
            # "CLIMATE.temperature_unit": {
            #     "view": "CLIMATE.temperature_unit",
            #     "vartype": "str",
            #     "writable": False,
            #     "unit": "",
            #     "value": self.m_daikinclimate.temperature_unit,
            # },
        }

        return ClimateTopics

    def getWaterMetaData(self) -> dict:
        WaterTopics = {
            "WATER.extra_state_attributes": {
                "view": "WATER.extra_state_attributes",
                "vartype": "dict",
                "writable": False,
                "unit": "",
                "value": self.m_daikinwater.extra_state_attributes,
            },
            "WATER.operation_list": {
                "view": "WATER.operation_list",
                "vartype": "list[str]",
                "writable": False,
                "unit": "",
                "value": self.m_daikinwater.operation_list,
            },
            "WATER.temperature": {
                "view": "WATER.temperature",
                "vartype": "double",
                "writable": True,
                "unit": self.m_daikinwater.temperature_unit,
                "value": self.m_daikinwater.current_temperature,
            },
            "WATER.tank_state": {
                "view": "WATER.tank_state",
                "vartype": "double",
                "writable": True,
                "unit": "",
                "value": self.m_daikinwater.current_operation,
            },
            "WATER.target_temperature": {
                "view": "WATER.target_temperature",
                "vartype": "double",
                "writable": True,
                "unit": self.m_daikinwater.temperature_unit,
                "value": self.m_daikinwater.target_temperature,
            },
            "WATER.min_temp": {
                "view": "WATER.min_temp",
                "vartype": "double",
                "writable": False,
                "unit": self.m_daikinwater.temperature_unit,
                "value": self.m_daikinwater.min_temp,
            },
            "WATER.max_temp": {
                "view": "WATER.max_temp",
                "vartype": "double",
                "writable": False,
                "unit": self.m_daikinwater.temperature_unit,
                "value": self.m_daikinwater.max_temp,
            },
            "WATER.turn_off": {
                "view": "WATER.turn_off",
                "vartype": "bool",
                "writable": True,
                "unit": "",
                "value": self.m_daikinwater.current_operation == "off",
            },
            "WATER.turn_on": {
                "view": "WATER.turn_on",
                "vartype": "bool",
                "writable": True,
                "unit": "",
                "value": self.m_daikinwater.current_operation != "off",
            },
        }

        return WaterTopics

    def publish_MQTTMetaData(self):
        """Publish all MetaData values that are currently cached"""
        #    topic = f"mh/opcua2mqtt/{self.MQTT_NETID}/data/{replaced}"

        def getViename(k: any) -> str:
            if k in self.m_Sensors.keys():
                v = self.m_Sensors[k]
                return v.name
            return ""

        def getReadTopic(k: any) -> str:
            if k in self.m_Sensors.keys():
                #  v = self.m_Sensors[k]
                # if v[2] == registerType.INPUT :
                return self.getTopicByKey(k)

            return ""

        def getWriteTopic(k: any) -> str:
            def isWriteTopic(k: any):
                # regs = [registerType.HOLDING, registerType.SINGLE_HOLDING]
                # if register in regs:
                #     return True
                return False

            if k in self.m_Sensors.keys():
                v = self.m_Sensors[k]
                if isWriteTopic(k):
                    # if v[2] == registerType.HOLDING:
                    return f"{self.getTopicByKey(k)}/set"

            return ""

        def getVarType(k: any) -> str:
            if k in self.m_Sensors.keys():
                v = self.m_Sensors[k]
                return "double"

            return ""

        def getStructure(k: any) -> dict:
            return {}

        def getUnit(k: any) -> str:
            if k in self.m_Sensors.keys():
                v = self.m_Sensors[k]
                return v.unit_of_measurement
            return ""

        try:
            self.m_lock.acquire()
            self.m_MetaData = {}
            retValue = False

            topic = self.getMetaDataTopic()

            # self.readallRegisters()
            jsondatapayload = {
                self.getMetaKeyByKey(k): {
                    "identifier": k,
                    "viewname": getViename(k),
                    "vartype": getVarType(k),
                    "readtopic": getReadTopic(k),
                    "writetopic": getWriteTopic(k),
                    "devicekey": self.m_MQTT_NETID,
                    "structure": getStructure(k),
                    "unit": getUnit(k),
                    "value": v,
                    "ctrlchannel": "",
                }
                for k, v in self.m_MQTTPayload.items()
            }

            self.m_MetaData = jsondatapayload

            # for k, v in self.getMQTTClimateTopics().items():

            climatedatapayload = {
                self.getMetaKeyByKey(k): {
                    "identifier": k,
                    "viewname": v["view"],
                    "vartype": v["vartype"],
                    "readtopic": f"{self.getTopicByKey(k)}",
                    "writetopic": f"{self.getTopicByKey(k)}/set",
                    "devicekey": self.m_MQTT_NETID,
                    "structure": {},
                    "unit": v["unit"],
                    "value": v["value"],
                    "ctrlchannel": "",
                }
                for k, v in self.getClimateMetaData().items()
            }

            waterdatapayload = {
                self.getMetaKeyByKey(k): {
                    "identifier": k,
                    "viewname": v["view"],
                    "vartype": v["vartype"],
                    "readtopic": f"{self.getTopicByKey(k)}",
                    "writetopic": f"{self.getTopicByKey(k)}/set",
                    "devicekey": self.m_MQTT_NETID,
                    "structure": {},
                    "unit": v["unit"],
                    "value": v["value"],
                    "ctrlchannel": "",
                }
                for k, v in self.getWaterMetaData().items()
            }
            self.m_MetaData.update(climatedatapayload)

            self.m_MetaData.update(waterdatapayload)

            values = json.dumps(self.m_MetaData)

            self._mqtt_client.publish(topic, values, retain=True)

            self.writeMetaDataToFile()

            # mqtt_client.subscribe(DEVICE_GATEWAY.control_set_topic(), handle_mqtt_commands)
            retValue = True
        finally:
            self.m_lock.release()
            return retValue

    def readallRegisters(self) -> dict:
        try:
            self.m_lock.acquire()

            jsonpayloadInput = {}
            for key, value in self.m_Sensors.items():
                sensor: DaikinSensor = value
                jsonpayloadInput[key] = sensor.state

            jsonclimatepayload = {
                k: v["value"]
                for k, v in self.getClimateMetaData().items()
                # if v["writable"]
            }
            jsonwaterpayload = {
                k: v["value"]
                for k, v in self.getWaterMetaData().items()
                # if v["writable"]
            }

            jsonpayloadInput.update(jsonclimatepayload)
            jsonpayloadInput.update(jsonwaterpayload)

            self.m_MQTTPayload.update(jsonpayloadInput)
            # self.m_MQTTPayload.update(jsonclimatepayload)

        finally:
            self.m_lock.release()
            return self.m_MQTTPayload

    def readInputRegisters(self) -> dict:
        def filteredpayload(value: any) -> bool:
            if type(value) is list or type(value) is dict or type(value) is str:
                return False

            return True

        try:
            self.m_lock.acquire()
            jsonpayloadInput = {}
            for key, value in self.m_Sensors.items():
                sensor: DaikinSensor = value
                jsonpayloadInput[key] = sensor.state

            jsonclimatepayload = {
                k: v["value"]
                for k, v in self.getClimateMetaData().items()
                # if not v["writable"]
            }

            jsonwaterepayload = {
                k: v["value"]
                for k, v in self.getWaterMetaData().items()
                # if not v["writable"]
            }

            jsonpayloadInput.update(jsonclimatepayload)
            jsonpayloadInput.update(jsonwaterepayload)

            self.LogInfo(jsonpayloadInput)

            if self._mqtt_client and self._mqtt_client.isConnected():
                if len(jsonpayloadInput.keys()) > 0:
                    acttime = local_now()
                    filteredjsonpayloadInput = {
                        k: v for k, v in jsonpayloadInput.items() if filteredpayload(v)
                    }
                    simplevars = SimpleVariables(
                        self.m_ctrldevice, filteredjsonpayloadInput, acttime
                    )
                    ppmppayload = simplevars.to_ppmp()
                    self._mqtt_client.publish(
                        self.m_ctrldevice.ppmp_topic(), ppmppayload, retain=False
                    )
                    self.doPublishPayload(jsonpayloadInput)

            self.m_MQTTPayload.update(jsonpayloadInput)

        finally:
            self.m_lock.release()
            return self.m_MQTTPayload

    async def doProcess(self):
        # timestamp = datetime.now(timezone.utc).astimezone()

        IsConnected: bool = self.isDeviceConnected()
        
        if not self.m_MQTT_QUEUE.empty():
            command = self.m_MQTT_QUEUE.get()
            await self.doMQTTProcessCommand(command)

        if IsConnected:
            difference_act = self.m_TimeSpan.getTimeSpantoActTime()

            hours_actsecs = self.m_TimeSpan.getTimediffernceintoSecs(difference_act)
            if hours_actsecs >= self.m_MQTT_REFRESH_TIME:
                if IsConnected:
                    await self.m_daikinAPI.async_update()
                    self.readInputRegisters()
                    timestamp = datetime.now(timezone.utc).astimezone()
                    self.m_TimeSpan.setActTime(timestamp)
                else:
                    await self.connectDevice()
                    self.setDeviceState(DeviceState.ERROR)
                    logger.error(
                        f"device: {self.m_MQTT_NETID} error: Disconnected -> Try Reconnect"
                    )
                    logger.info(
                        f"device: {self.m_MQTT_NETID} error: Disconnected -> Try Reconnect"
                    )


    def doStartProcessCommandThred(self):
        pass
