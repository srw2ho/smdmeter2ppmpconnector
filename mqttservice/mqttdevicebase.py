import asyncio
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
from helpers.timespan import TimeSpan
import kebakeycontactP30
import sdm_modbus
from sdm_modbus import meter
from sdm_modbus.meter import registerType
from pymodbus.register_write_message import WriteMultipleRegistersResponse

logger = logging.getLogger("root")

DEVICE_TYPE_CTRL = "homemqttcontrol"
SERVICE_DEVICE_NAME = "homemqttservice"
SERVICE_DEVICE_TYPE = "homemqttservice"
SERVICE_TYPE_VERSION = "homemqttVersion"


class MqttDeviceServiceBase(object):
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
    ):
        self.m_MQTT_NETID = MQTT_NETID

        self.m_INFODEBUGLEVEL = INFODEBUGLEVEL
        self.m_MQTT_REFRESH_TIME = MQTT_REFRESH_TIME
        self.m_MQTT_CONNECT_TIME = MQTT_CONNECT_TIME
        self.m_last_MQTT_timestamp = 0
        self.m_MQTT_QUEUE = Queue(maxsize=0)
        self.m_MQTT_QUEUE_CHANGEDVALUES = Queue(maxsize=0)
        self.m_server_timestamp = -1
        self.m_MetaData = {}
        self.m_metaDataOutFilePath = "./opcua2mqttservice_metadata.json"
        self.m_configControlChannelSettingPath = ""
        self.m_configControlChannel = dict()
        self.m_onMqttConnected = False
        # self.m_SMD_Device = None
        self.m_doReadHoldingRegister = True
        self.m_MQTTPayload = {}
        self.m_lastMQTTPayload = {}
        self.m_lock = threading.RLock()
        self.m_deviceState = DeviceState.UNKNOWN
        self.m_doMQTTConnect = False
        self.m_HoldingBatchRegister = {}
        self.m_TimeSpan = TimeSpan()
        self.m_TimeSpan_Holding = TimeSpan()

        self._mqtt_client = MQTTClient(
            host=MQTT_HOST,
            port=MQTT_PORT,
            user=MQTT_USERNAME,
            password=MQTT_PASSWORD,
            tls_cert=MQTT_TLS_CERT,
        )
        self.m_device = Device(
            additionalData={
                "type": SERVICE_DEVICE_TYPE,
                "hostname": self.m_MQTT_NETID,
                "generalconfig": {
                    "InterfaceType": f"{SERVICE_TYPE_VERSION}",
                    "InterfaceVersion": "V1.0",
                    "MetadataVersion": "V1.0",
                },
            },
        )

        self.m_ctrldevice = Device(
            additionalData={
                "type": DEVICE_TYPE_CTRL,
                "hostname": SERVICE_DEVICE_NAME,
            },
        )
        if self.m_MQTT_NETID != None:
            name = f"{SERVICE_DEVICE_NAME}/{self.m_MQTT_NETID}"
            ctrldevicenetid = f"{SERVICE_DEVICE_NAME}_{self.m_MQTT_NETID}"

            self.m_device.setNetId(name)

            if os.name == "nt":
                self.m_metaDataOutFilePath = (
                    f"./{SERVICE_DEVICE_NAME}_{self.m_MQTT_NETID}_metadata.json"
                )
                self.m_configControlChannelSettingPath = f"./{SERVICE_DEVICE_NAME}_{self.m_MQTT_NETID}_configctrlchannel.json"
            else:
                self.m_metaDataOutFilePath = f"/etc/moehwald/{SERVICE_DEVICE_NAME}_{self.m_MQTT_NETID}_metadata.json"
                self.m_configControlChannelSettingPath = f"/etc/moehwald/{SERVICE_DEVICE_NAME}_{self.m_MQTT_NETID}_configctrlchannel.json"

            self.m_ctrldevice.setNetId(ctrldevicenetid)
            self.m_ctrldevice.sethostNameByNetId(self.m_MQTT_NETID)

        self.readControlChannelFile()

    def connectDevice(self) -> bool:
        return False

    def isDeviceConnected(self) -> bool:
        return False

    def isMQTTConnected(self) -> bool:
        return self.m_onMqttConnected

    def readControlChannelFile(self) -> bool:
        try:

            def getCtrlchannelResultdata(value) -> dict:
                if "ctrlchannel" in value:
                    return {"ctrlchannel": value["ctrlchannel"]}
                return {}

            self.m_configControlChannel = {}

            with open(self.m_configControlChannelSettingPath) as fObj:
                # fObj = open(filename)
                data = json.load(fObj)
                resultdata = {
                    key: getCtrlchannelResultdata(value) for key, value in data.items()
                }

                self.m_configControlChannel = resultdata

                return True
        except Exception as error:
            # logger.error(f"readControlChannelFile Error: {error}")

            return False

    def writeMetaDataToFile(self) -> bool:
        try:
            json_object = json.dumps(self.m_MetaData, indent=4)
            with open(self.m_metaDataOutFilePath, "w") as fObj:
                fObj.write(json_object)
                return True
        except Exception as error:
            logger.error(f"writeMetaDataToFile Error: {error}")
            # logger.info(
            #     f'readSequencerTemplates.writeMetaDataToFile Error: {error}')
            return False

    def getTopicByKey(self, key: str) -> str:

        replaced = key.replace("/", "_")
        topic = f"mh/{SERVICE_DEVICE_NAME}/{self.m_MQTT_NETID}/data/{replaced}"

        return topic

    def doMQTTProcessCommand(self, command):
        """Wait for items in the queue and process these items"""

        try:
            pass

        except Exception as exception:
            logger.error(f"MQTTConsumeQueue Parse error: {exception}")

    def getMetaDataTopic(self) -> str:
        topic = f"mh/{SERVICE_DEVICE_NAME}/{self.m_MQTT_NETID}/metadata"
        return topic

    def subscribeMQTTWriteTopis(self):
        """Publish all values that are currently cached"""

        try:
            self.m_lock.acquire()
            # self._mqtt_client.unsubscribeallTopics()

            subscribetopictupels = [
                value["writetopic"]
                for k, value in self.m_MetaData.items()
                if value["writetopic"] != ""
            ]

            for topic in subscribetopictupels:
                self._mqtt_client.subscribe(topic, self.handle_mqtt_commands)

            retValue = True
        finally:
            self.m_lock.release()
            return retValue

    def handle_mqtt_commands(self, command):
        """Handles commands from the MQTT message broker to the OPC-UA interface

        Arguments:
            command {str} -- command to execute
        """
        try:
            self.m_MQTT_QUEUE.put(command)

        except BaseException as error:
            logger.error(f"handle_mqtt_commands:-->MQTT:{error}")

        finally:
            self.m_MQTT_QUEUE.task_done()

    def MQTTConsumeQueue(self):
        """Wait for items in the queue and process these items"""

        while True:
            try:
                command = self.m_MQTT_QUEUE.get()
                self.doMQTTProcessCommand(command)
            except Exception as exception:
                logger.error(f"MQTTConsumeQueue Parse error: {exception}")

    def on_connect(self, client, userdata, flags, rc):
        return

    def publish_MQTTMetaData(self):
        return

    def getDeviceServicesTopic(self) -> str:
        topic = f"mh/DeviceServices/{self.m_MQTT_NETID}"
        return topic

    def on_disconnect(self, client, userdata, rc):
        self.m_onMqttConnected = False
        logger.info(f"MQTT-Client: on_disconnect")

    def doStartProcessCommandThred(self):
        threading.Thread(target=self.MQTTConsumeQueue).start()

    def doMQTTconnect(self):
        """Establish connection to MQTT-Broker"""

        if not self.m_doMQTTConnect:
            self.m_doMQTTConnect = True
            infoTopic = self.m_device.info_topic()
            self._mqtt_client.last_will(
                infoTopic,
                machine_message_generator(
                    self.m_device, state=DeviceState.ERROR, code="offline"
                ),
                retain=True,
            )
            # connect to MQTT
            self._mqtt_client.connect(
                connectHandler=self.on_connect, disconnectHandler=self.on_disconnect
            )
            self.doStartProcessCommandThred()

    def getMetaKeyByKey(self, key: str) -> str:
        return f"@{self.m_MQTT_NETID}.{key}"

    def getActTime(self):
        timestamp = datetime.now(timezone.utc).astimezone()
        posix_timestamp = datetime.timestamp(timestamp) * 1000
        return posix_timestamp

    def getPayloadfromValue(self, identifier: str, value: any) -> dict:
        try:
            payload = {}
            payload = {
                "metakey": self.getMetaKeyByKey(identifier),
                "identifier": identifier,
                "posix_timestamp": self.getActTime(),
                "value": value,
            }

        finally:
            return payload

    def doPublishPayload(self, jsonpayload: dict, retained: bool = False):
        def isValueChanged(k: str, value: any):
            if k in self.m_lastMQTTPayload:
                return self.m_lastMQTTPayload[k] != value
            return True

        try:
            self.m_lock.acquire()
            if self._mqtt_client.isConnected():
                changedPayload = {
                    k: self.getPayloadfromValue(k, v)
                    for k, v in jsonpayload.items()
                    # if isValueChanged(k, v)
                }

                # write changed Values over MQTT
                for k, v in changedPayload.items():
                    try:
                        self._mqtt_client.publish(
                            self.getTopicByKey(k),
                            json.dumps(v),
                            retain=retained,
                        )
                    except Exception as e:
                        logger.error(f"doPublishPayload: publish : Error->{e}")
                self.m_lastMQTTPayload.update(jsonpayload)       
                # if len(changedPayload.keys()) > 0:
                #     self.m_lastMQTTPayload.update(jsonpayload)
            else:
                logger.error(f"doPublishPayload: error-> MQTT is not connected")
        finally:
            self.m_lock.release()

    def readallRegisters(self) -> dict:
        try:
            return {}
        finally:
            return {}

    def LogInfo(self, jsonpayloadInput: dict) -> dict:
        if self.m_INFODEBUGLEVEL > 0:
            pass

    def readInputRegisters(self) -> dict:
        try:
            return {}

        finally:
            return {}

    def doProcess(self):
        return

    def setDeviceState(self, devicestate: DeviceState = DeviceState.UNKNOWN):
        if self.m_deviceState != devicestate:
            if self._mqtt_client.isConnected():
                self.m_deviceState = devicestate
                self._mqtt_client.publish(
                    self.m_device.info_topic(),
                    machine_message_generator(self.m_device, state=devicestate),
                    retain=True,
                )
                self._mqtt_client.publish(
                    self.m_ctrldevice.info_topic(),
                    machine_message_generator(self.m_ctrldevice, state=devicestate),
                    retain=True,
                )
