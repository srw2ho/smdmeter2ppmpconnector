import json
import logging
import os
import threading
from mqttconnector.client import MQTTClient
from ppmpmessage.v3.device_state import DeviceState
from ppmpmessage.v3.device import Device
from ppmpmessage.v3.util import machine_message_generator
from ppmpmessage.v3.util import local_now
from ppmpmessage.convertor.simple_variables import SimpleVariables
from ppmpmessage.v3.device import Device
from ppmpmessage.v3.device import iotHubDevice
from queue import Queue
import time
from datetime import datetime, timezone
import growatt
import kebakeycontactP30
from mqttservice.mqttdevicebase import (
    SERVICE_DEVICE_NAME,
    SERVICE_DEVICE_TYPE,
    MqttDeviceServiceBase,
)

# from mqttservice.mqttdevicedaikinservice import MqttDeviceService
import sdm_modbus
from sdm_modbus import meter
from sdm_modbus.meter import registerType
from pymodbus.register_write_message import WriteMultipleRegistersResponse


# DEVICE_TYPE = "homemqtt"


logger = logging.getLogger("root")


class MqttDeviceModbusService(MqttDeviceServiceBase):
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
        MQTT_CONNECT_TIME=5,
        MODBUS_BATCH_SLEEP=0,
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
            MQTT_CONNECT_TIME=MQTT_CONNECT_TIME,
        )
        self.m_SMD_Device = None
        self.m_MODBUS_BATCH_SLEEP = MODBUS_BATCH_SLEEP
        # self.m_MQTT_NETID = MQTT_NETID

        # self.m_INFODEBUGLEVEL = INFODEBUGLEVEL
        # self.m_MQTT_REFRESH_TIME = MQTT_REFRESH_TIME

        # self.m_last_MQTT_timestamp = 0
        # self.m_MQTT_QUEUE = Queue(maxsize=0)
        # self.m_MQTT_QUEUE_CHANGEDVALUES = Queue(maxsize=0)
        # self.m_server_timestamp = -1
        # self.m_MetaData = {}
        # self.m_metaDataOutFilePath = "./opcua2mqttservice_metadata.json"
        # self.m_configControlChannelSettingPath = ""
        # self.m_configControlChannel = dict()
        # self.m_onMqttConnected = False
        # self.m_SMD_Device = None
        # self.m_doReadHoldingRegister = True
        # self.m_MQTTPayload = {}
        # self.m_lastMQTTPayload = {}
        # self.m_lock = threading.RLock()
        # self.m_deviceState = DeviceState.UNKNOWN
        # self.m_doMQTTConnect = False
        # self.m_HoldingBatchRegister = {}

        # self._mqtt_client = MQTTClient(
        #     host=MQTT_HOST,
        #     port=MQTT_PORT,
        #     user=MQTT_USERNAME,
        #     password=MQTT_PASSWORD,
        #     tls_cert=MQTT_TLS_CERT,
        # )
        # self.m_device = Device(
        #     additionalData={
        #         "type": SERVICE_DEVICE_TYPE,
        #         "hostname": self.m_MQTT_NETID,
        #         "generalconfig": {
        #             "InterfaceType": f"{SERVICE_TYPE_VERSION}",
        #             "InterfaceVersion": "V1.0",
        #             "MetadataVersion": "V1.0",
        #         },
        #     },
        # )

        # self.m_ctrldevice = Device(
        #     additionalData={
        #         "type": DEVICE_TYPE_CTRL,
        #         "hostname": SERVICE_DEVICE_NAME,
        #     },
        # )
        # if self.m_MQTT_NETID != None:
        #     name = f"{SERVICE_DEVICE_NAME}/{self.m_MQTT_NETID}"
        #     ctrldevicenetid = f"{SERVICE_DEVICE_NAME}_{self.m_MQTT_NETID}"

        #     self.m_device.setNetId(name)

        #     if os.name == "nt":
        #         self.m_metaDataOutFilePath = (
        #             f"./{SERVICE_DEVICE_NAME}_{self.m_MQTT_NETID}_metadata.json"
        #         )
        #         self.m_configControlChannelSettingPath = f"./{SERVICE_DEVICE_NAME}_{self.m_MQTT_NETID}_configctrlchannel.json"
        #     else:
        #         self.m_metaDataOutFilePath = f"/etc/moehwald/{SERVICE_DEVICE_NAME}_{self.m_MQTT_NETID}_metadata.json"
        #         self.m_configControlChannelSettingPath = f"/etc/moehwald/{SERVICE_DEVICE_NAME}_{self.m_MQTT_NETID}_configctrlchannel.json"

        #     self.m_ctrldevice.setNetId(ctrldevicenetid)
        #     self.m_ctrldevice.sethostNameByNetId(self.m_MQTT_NETID)

        # self.readControlChannelFile()

    def getMeter(self) -> meter.Meter:
        return self.m_SMD_Device

    def createtMeterByType(
        self,
        metertype: str = "",
        modbushost: str = "",
        modbusport: int = 0,
        timeout: int = 2,
        devid: int = 1,
    ):
        if metertype == "SDM630":
            self.m_SMD_Device = sdm_modbus.SDM630(
                host=modbushost,
                port=modbusport,
                timeout=timeout,
                retry_on_empty=True,
                retries=3,
                framer=None,
                unit=devid,
                udp=False,
            )
        if metertype == "SDM630_V3":
            self.m_SMD_Device = sdm_modbus.SDM630_V3(
                host=modbushost,
                port=modbusport,
                timeout=timeout,
                retry_on_empty=True,
                retries=3,
                framer=None,
                unit=devid,
                udp=False,
            )

        if metertype == "SDM230":
            self.m_SMD_Device = sdm_modbus.SDM230(
                host=modbushost,
                port=modbusport,
                timeout=timeout,
                retry_on_empty=True,
                retries=3,
                framer=None,
                unit=devid,
                udp=False,
            )
        if metertype == "SDM120":
            self.m_SMD_Device = sdm_modbus.SDM120(
                host=modbushost,
                port=modbusport,
                timeout=timeout,
                retry_on_empty=True,
                retries=3,
                framer=None,
                unit=devid,
                udp=False,
            )
        if metertype == "SDM72":
            self.m_SMD_Device = sdm_modbus.SDM72(
                host=modbushost,
                port=modbusport,
                timeout=timeout,
                retry_on_empty=True,
                retries=3,
                framer=None,
                unit=devid,
                udp=False,
            )
        if metertype == "SDM72V2":
            self.m_SMD_Device = sdm_modbus.SDM72V2(
                host=modbushost,
                port=modbusport,
                timeout=timeout,
                retry_on_empty=True,
                retries=3,
                framer=None,
                unit=devid,
                udp=False,
            )
        if metertype == "SPH_TL3_BH_UP":
            self.m_SMD_Device = growatt.SPH_TL3_BH_UP(
                host=modbushost,
                port=modbusport,
                timeout=timeout,
                retry_on_empty=True,
                retries=3,
                framer=None,
                unit=devid,
                udp=False,
            )
        if metertype == "SPH_TL3_BH_UP_Meter":
            self.m_SMD_Device = growatt.SPH_TL3_BH_UP_Meter(
                host=modbushost,
                port=modbusport,
                timeout=timeout,
                retry_on_empty=True,
                retries=3,
                framer=None,
                unit=devid,
                udp=False,
            )
        if metertype == "KeContactP30":
            self.m_SMD_Device = kebakeycontactP30.KeContactP30(
                host=modbushost,
                port=modbusport,
                timeout=timeout,
                retry_on_empty=True,
                retries=3,
                framer=None,
                unit=devid,
                udp=False,
            )
        if self.m_SMD_Device != None:
            self.storeBatchfordallHoldingRegisters()

    def connectDevice(self) -> bool:
        connectTryCounter = 3

        while True:
            self.m_SMD_Device.connect()
            if self.m_SMD_Device.connected():
                self.doMQTTconnect()
                self.setDeviceState(DeviceState.OK)
                break
            else:
                self.setDeviceState(DeviceState.ERROR)
                if connectTryCounter > 0:
                    time.sleep(0.5)
                    self.m_SMD_Device.connect()

                else:
                    break
                connectTryCounter = connectTryCounter - 1

        return self.m_SMD_Device.connected()

    def isDeviceConnected(self) -> bool:
        return self.m_SMD_Device.connected()

    def isMQTTConnected(self) -> bool:
        return self.m_onMqttConnected

    # def readControlChannelFile(self) -> bool:
    #     try:

    #         def getCtrlchannelResultdata(value) -> dict:
    #             if "ctrlchannel" in value:
    #                 return {"ctrlchannel": value["ctrlchannel"]}
    #             return {}

    #         self.m_configControlChannel = {}

    #         with open(self.m_configControlChannelSettingPath) as fObj:
    #             # fObj = open(filename)
    #             data = json.load(fObj)
    #             resultdata = {
    #                 key: getCtrlchannelResultdata(value) for key, value in data.items()
    #             }

    #             self.m_configControlChannel = resultdata

    #             return True
    #     except Exception as error:
    #         # logger.error(f"readControlChannelFile Error: {error}")

    #         return False

    # def writeMetaDataToFile(self) -> bool:
    #     try:
    #         json_object = json.dumps(self.m_MetaData, indent=4)
    #         with open(self.m_metaDataOutFilePath, "w") as fObj:
    #             fObj.write(json_object)
    #             return True
    #     except Exception as error:
    #         logger.error(f"writeMetaDataToFile Error: {error}")
    #         # logger.info(
    #         #     f'readSequencerTemplates.writeMetaDataToFile Error: {error}')
    #         return False

    # def getTopicByKey(self, key: str) -> str:
    #     replaced = key
    #     topic = f"mh/{SERVICE_DEVICE_NAME}/{self.m_MQTT_NETID}/data/{replaced}"

    #     return topic

    def doMQTTProcessCommand(self, command):
        """Wait for items in the queue and process these items"""

        try:
            doSetting = False
            action = json.loads(command)
            if "identifier" in action:
                identifier = action["identifier"]
                if "value" in action:
                    value = action["value"]
                    doSetting = True
                    errorMessage = ""
                    doUpdate = False
                    try:
                        response: WriteMultipleRegistersResponse = (
                            self.m_SMD_Device.write(identifier, value)
                        )
                        if response.isError():
                            doUpdate = False
                        else:
                            # Holding-Register beim nächsten Lesen auslesen
                            self.m_SMD_Device.setBatchForRegisterByKey(identifier, 1)
                            doUpdate = True
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

    # def getMetaDataTopic(self) -> str:
    #     topic = f"mh/{SERVICE_DEVICE_NAME}/{self.m_MQTT_NETID}/metadata"
    #     return topic

    # def MQTTConsumeQueue(self):
    #     """Wait for items in the queue and process these items"""
    #     while True:
    #         try:
    #             # self._MQTT_QUEUE.empty
    #             command = self.m_MQTT_QUEUE.get()
    #             self.doMQTTProcessCommand(command)
    #             # sleep(0.05)

    #         except Exception as exception:
    #             logger.error(f"MQTTConsumeQueue Parse error: {exception}")

    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"MQTT-Client: on_connect -> publish_MQTTMetaData()")

        # delete previous Topic
        self._mqtt_client.publish(self.getDeviceServicesTopic(), None, retain=True)
        # self._mqtt_client.publish(self.m_device.info_topic(), None, retain=True)

        self.restoreBatchfordallHoldingRegisters()
        allregisterPayload = self.readallRegisters()
        # bei start alle retained Senden
        self.doPublishPayload(allregisterPayload, retained=True)

        self.publish_MQTTMetaData()
        self.subscribeMQTTWriteTopis()


        logger.info(f"MQTT-Client: on_connect -> publish_cached_values()")

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

    def publish_MQTTMetaData(self):
        """Publish all MetaData values that are currently cached"""
        #    topic = f"mh/opcua2mqtt/{self.MQTT_NETID}/data/{replaced}"

        def getViename(k: any) -> str:
            if k in self.m_SMD_Device.registers:
                v = self.m_SMD_Device.registers[k]
                return v[5]
            return ""

        def getReadTopic(k: any) -> str:
            if k in self.m_SMD_Device.registers:
                v = self.m_SMD_Device.registers[k]
                # if v[2] == registerType.INPUT :
                return self.getTopicByKey(k)

            return ""

        def getWriteTopic(k: any) -> str:
            def isWriteTopic(register: registerType):
                regs = [registerType.HOLDING, registerType.SINGLE_HOLDING]
                if register in regs:
                    return True
                return False

            if k in self.m_SMD_Device.registers:
                v = self.m_SMD_Device.registers[k]
                if isWriteTopic(v[2]):
                    # if v[2] == registerType.HOLDING:
                    return f"{self.getTopicByKey(k)}/set"

            return ""

        def getVarType(k: any) -> str:
            if k in self.m_SMD_Device.registers:
                v = self.m_SMD_Device.registers[k]
                return str(v[3])

            return ""

        def getStructure(k: any) -> dict:
            return {}

        def getUnit(k: any) -> str:
            if k in self.m_SMD_Device.registers:
                v = self.m_SMD_Device.registers[k]
                return str(v[6])
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

            values = json.dumps(jsondatapayload)

            self._mqtt_client.publish(topic, values, retain=True)

            self.writeMetaDataToFile()

            # mqtt_client.subscribe(DEVICE_GATEWAY.control_set_topic(), handle_mqtt_commands)
            retValue = True
        finally:
            self.m_lock.release()
            return retValue

    # def getDeviceServicesTopic(self) -> str:
    #     topic = f"mh/DeviceServices/{self.m_MQTT_NETID}"
    #     return topic

    # def on_disconnect(self, client, userdata, rc):
    #     self.m_onMqttConnected = False
    #     logger.info(f"MQTT-Client: on_disconnect")

    def doSMDDeviceconnect(self):
        IsConnected: bool = self.m_SMD_Device.connected()
        if not IsConnected:
            self.m_SMD_Device.connect()
            # time.sleep(connectTime)
            logger.error(
                f"device: {self.m_MQTT_NETID} error: Disconnected -> Try Rconnect"
            )
            logger.info(
                f"device: {self.m_MQTT_NETID} error: Disconnected -> Try Rconnect"
            )

    # def doMQTTconnect(self):
    #     """Establish connection to MQTT-Broker"""

    #     if not self.m_doMQTTConnect:
    #         self.m_doMQTTConnect = True
    #         infoTopic = self.m_device.info_topic()
    #         self._mqtt_client.last_will(
    #             infoTopic,
    #             machine_message_generator(
    #                 self.m_device, state=DeviceState.ERROR, code="offline"
    #             ),
    #             retain=True,
    #         )
    #         # connect to MQTT
    #         self._mqtt_client.connect(
    #             connectHandler=self.on_connect, disconnectHandler=self.on_disconnect
    #         )

    #         # delete previous Topic
    #         # self._mqtt_client.publish(self.getMetaDataTopic(), None, retain=True)

    #         threading.Thread(target=self.MQTTConsumeQueue).start()

    # def getMetaKeyByKey(self, key: str) -> str:
    #     return f"@{self.m_MQTT_NETID}.{key}"

    # def getActTime(self):
    #     timestamp = datetime.now(timezone.utc).astimezone()
    #     posix_timestamp = datetime.timestamp(timestamp) * 1000
    #     return posix_timestamp

    # def getPayloadfromValue(self, identifier: str, value: any) -> dict:
    #     try:
    #         payload = {}
    #         payload = {
    #             "metakey": self.getMetaKeyByKey(identifier),
    #             "identifier": identifier,
    #             "posix_timestamp": self.getActTime(),
    #             "value": value,
    #         }

    #     finally:
    #         return payload

    # def doPublishPayload(self, jsonpayload: dict, retained: bool = False):
    #     def isValueChanged(k: str, value: any):
    #         if k in self.m_lastMQTTPayload:
    #             return self.m_lastMQTTPayload[k] != value
    #         return True

    #     try:
    #         self.m_lock.acquire()
    #         if self._mqtt_client.isConnected():
    #             changedPayload = {
    #                 k: self.getPayloadfromValue(k, v)
    #                 for k, v in jsonpayload.items()
    #                 if isValueChanged(k, v)
    #             }

    #             # write changed Values over MQTT
    #             for k, v in changedPayload.items():
    #                 self._mqtt_client.publish(
    #                     self.getTopicByKey(k),
    #                     json.dumps(v),
    #                     retain=retained,
    #                 )
    #             self.m_lastMQTTPayload.update(jsonpayload)
    #         else:
    #             logger.error(
    #                 f"publish_single_cached_value: error-> MQTT is not connected"
    #             )
    #     finally:
    #         self.m_lock.release()

    def storeBatchfordallHoldingRegisters(self) -> None:
        self.m_HoldingBatchRegister = {
            k: self.m_SMD_Device.getBatchForRegisterByKey(k)
            for k, v in self.m_SMD_Device.registers.items()
            if (v[2] == sdm_modbus.registerType.HOLDING)
        }

    def restoreBatchfordallHoldingRegisters(self) -> None:
        for k, v in self.m_HoldingBatchRegister.items():
            self.m_SMD_Device.setBatchForRegisterByKey(k, v)

    def setBatchfordallHoldingRegisters(self, batch: int) -> None:
        for k, v in self.m_HoldingBatchRegister.items():
            self.m_SMD_Device.setBatchForRegisterByKey(k, batch)

    def readallRegisters(self) -> dict:
        try:
            self.m_lock.acquire()

            jsonpayloadInput = self.m_SMD_Device.read_all(
                sdm_modbus.registerType.INPUT,
                scaling=True,
                batchsleepinSecs=self.m_MODBUS_BATCH_SLEEP,
            )
            jsonpayloadHolding = self.m_SMD_Device.read_all(
                sdm_modbus.registerType.HOLDING,
                scaling=True,
                batchsleepinSecs=self.m_MODBUS_BATCH_SLEEP,
            )

            # Holding-Register nur einmal lesen und dann nicht mit batch=0 ausblenden
            # Achtung, bei KebakeycontactP30 sind die Holding Registers die Input-Register
            # hier müssen die Holding-Registers bleiben!!
            # die Batch-Register müssen daher bleiben
            self.setBatchfordallHoldingRegisters(0)

            self.m_MQTTPayload.update(jsonpayloadInput)
            self.m_MQTTPayload.update(jsonpayloadHolding)

        finally:
            self.m_lock.release()
            return self.m_MQTTPayload

    def LogInfo(self, jsonpayloadInput: dict) -> dict:
        if self.m_INFODEBUGLEVEL > 0:
            logger.info(f"device: {self.m_MQTT_NETID} Read Input Registers:")

            for k, v in jsonpayloadInput.items():
                (
                    address,
                    length,
                    rtype,
                    dtype,
                    vtype,
                    label,
                    fmt,
                    batch,
                    sf,
                ) = self.m_SMD_Device.registers[k]

                if type(fmt) is list or type(fmt) is dict:
                    logger.info(f"\t{k} :{rtype}- {label}: {fmt[str(v)]}")
                elif vtype is float:
                    logger.info(f"\t{k} :{rtype}- {label}: {v:.2f} {fmt}")
                else:
                    logger.info(f"\t{k} :{rtype}- {label}: {v} {fmt}")

    def readInputRegisters(self) -> dict:
        try:
            self.m_lock.acquire()
            jsonpayloadInput = self.m_SMD_Device.read_all(
                sdm_modbus.registerType.INPUT,
                scaling=True,
                batchsleepinSecs=self.m_MODBUS_BATCH_SLEEP,
            )

            jsonpayloadHold = self.m_SMD_Device.read_all(
                sdm_modbus.registerType.HOLDING,
                scaling=True,
                batchsleepinSecs=self.m_MODBUS_BATCH_SLEEP,
            )

            if len(jsonpayloadHold.keys()) > 0:
                jsonpayloadInput.update(jsonpayloadHold)
                for k in jsonpayloadHold.keys():
                    # Read Holding-Register nicht ausführen : Batch = 0
                    self.m_SMD_Device.setBatchForRegisterByKey(k, 0)

            self.LogInfo(jsonpayloadInput)

            if self._mqtt_client and self._mqtt_client.isConnected():
                if len(jsonpayloadInput.keys()) > 0:
                    acttime = local_now()
                    simplevars = SimpleVariables(
                        self.m_ctrldevice, jsonpayloadInput, acttime
                    )
                    ppmppayload = simplevars.to_ppmp()
                    self._mqtt_client.publish(
                        self.m_ctrldevice.ppmp_topic(), ppmppayload, retain=False
                    )
                    self.doPublishPayload(jsonpayloadInput)

            # jsonpayloadHold = self.m_SMD_Device.read_all(
            #     sdm_modbus.registerType.HOLDING, scaling=True
            # )
            # if len(jsonpayloadHold.keys()) > 0:
            #     self.LogInfo(jsonpayloadHold)
            #     # logger.info(f"device: {self.m_MQTT_NETID} Read Holding Registers:")
            #     if self._mqtt_client and self._mqtt_client.isConnected():
            #         #    Holding-Register nur einmal bei Änderungen lesen
            #         for k in jsonpayloadHold.keys():
            #             # Read Holding-Register nicht ausführen : Batch = 0
            #             self.m_SMD_Device.setBatchForRegisterByKey(k, 0)

            #         self.m_MQTTPayload.update(jsonpayloadHold)
            #         self.doPublishPayload(jsonpayloadHold)

            self.m_MQTTPayload.update(jsonpayloadInput)
        finally:
            self.m_lock.release()
            return self.m_MQTTPayload

    def doProcess(self):
        try:
            IsConnected: bool = self.m_SMD_Device.connected()

            timestamp = datetime.now(timezone.utc).astimezone()
            difference_act = self.m_TimeSpan.getTimeSpantoActTime()
            hours_actsecs = self.m_TimeSpan.getTimediffernceintoSecs(difference_act)
            difference_act_holding = self.m_TimeSpan_Holding.getTimeSpantoActTime()
            hours_actsecs_holding = self.m_TimeSpan_Holding.getTimediffernceintoSecs(difference_act_holding)

            if IsConnected:
                if hours_actsecs_holding >= self.m_MQTT_REFRESH_TIME*30:
                    self.restoreBatchfordallHoldingRegisters()
                    self.m_TimeSpan_Holding.setActTime(timestamp)
                    
                if hours_actsecs >= self.m_MQTT_REFRESH_TIME:
                    self.setDeviceState(DeviceState.OK)
                    self.m_TimeSpan.setActTime(timestamp)
                    self.readInputRegisters()

            else:
                if hours_actsecs >= self.m_MQTT_CONNECT_TIME:
                    self.setDeviceState(DeviceState.ERROR)
                    self.m_TimeSpan.setActTime(timestamp)
                    self.doSMDDeviceconnect()

                    logger.error(
                        f"device: {self.m_MQTT_NETID} error: Disconnected -> Try Reconnect"
                    )
                    logger.info(
                        f"device: {self.m_MQTT_NETID} error: Disconnected -> Try Reconnect"
                    )
        except Exception as e:
            logger.error(f"device: {self.m_MQTT_NETID}  doProcess : error:{e}")
            logger.info(f"device: {self.m_MQTT_NETID}  doProcess : error:{e}")
