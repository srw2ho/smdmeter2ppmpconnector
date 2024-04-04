import json
import logging
import os
import re
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


class MqttDeviceESPAltherma(MqttDeviceServiceBase):
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
        MQTT_CONNECT_TIME=5

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

     

   
    def doStartProcessCommandThred(self):
        pass

            
    def connectDevice(self) -> bool:

        self.doMQTTconnect()
        # self.setDeviceState(DeviceState.OK)
                
    


    def isMQTTConnected(self) -> bool:
        return self.m_onMqttConnected


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

    def handle_espaltherma_attr(self, topic: str, payload: any):
        """ Subscribe to MQTT changes and write payload into queue

        Arguments:
            payload {obj} -- JSON payload in PPMP format
        """
        def filter(key:str, value:any) -> any:
            if key =="[HPSU] Bypass valve position (0:Bypass 100:Emitter)":
                a = 1
            if isinstance(value, str):
                x= re.match(r'^[-0-9.]+', value)
                if x: 
                    value = float(x.group())
                return value
            return float(value)
        
        try:
            actions:dict = json.loads(payload)
            filteredpayload = {key: filter(key, value) for key,value in actions.items()}
            self.doPublishPayload(filteredpayload,retained=True)
            
            acttime = local_now()
            simplevars = SimpleVariables(
                        self.m_ctrldevice, filteredpayload, acttime
                    )

            ppmppayload = simplevars.to_ppmp()
            self._mqtt_client.publish(
                        self.m_ctrldevice.ppmp_topic(), ppmppayload, retain=False
                    )
    

        # logger.info(f'MQTT Queue size: {QUEUE_MQTT.qsize()}')
        except (Exception) as error:
            logger.info(
                f'MQTTServiceDevice.handle_espaltherma_attr!{error}')
            logger.error(
                f'MQTTServiceDevice.handle_espaltherma_attr!{error}')

    def handle_espaltherma_lwt(self, topic: str, payload: any):
        """ Subscribe to MQTT changes and write payload into queue

        Arguments:
            payload {obj} -- JSON payload in PPMP format
        """
        try:
            action:dict = json.loads(payload)
            if action == "Online":
                self.setDeviceState(devicestate=DeviceState.OK)
            else:
                self.setDeviceState(devicestate=DeviceState.ERROR)
                
        # logger.info(f'MQTT Queue size: {QUEUE_MQTT.qsize()}')
        except (Exception) as error:
            logger.info(
                f'MQTTServiceDevice.handle_espaltherma_lwt!{error}')
            logger.error(
                f'MQTTServiceDevice.handle_espaltherma_lwt!{error}')

    def handle_espaltherma_log(self, topic: str, payload: any):
        """ Subscribe to MQTT changes and write payload into queue

        Arguments:
            payload {obj} -- JSON payload in PPMP format
        """
        try:
            out = payload.decode("utf-8")

            # action:dict = json.loads(payload)
  

        # logger.info(f'MQTT Queue size: {QUEUE_MQTT.qsize()}')
        except (Exception) as error:
            logger.info(
                f'MQTTServiceDevice.handle_espaltherma_log!{error}')
            logger.error(
                f'MQTTServiceDevice.handle_espaltherma_log!{error}')



    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"MQTT-Client: on_connect -> publish_MQTTMetaData()")

        # delete previous Topic
        self._mqtt_client.publish(self.getDeviceServicesTopic(), None, retain=True)
        # self._mqtt_client.publish(self.m_device.info_topic(), None, retain=True)
        
        self._mqtt_client.subscribe("espaltherma/ATTR", self.handle_espaltherma_attr)
        self._mqtt_client.subscribe("espaltherma/LWT", self.handle_espaltherma_lwt)
        self._mqtt_client.subscribe("espaltherma/log", self.handle_espaltherma_log)
        
                
        self.setDeviceState(devicestate=DeviceState.ERROR)
       

        # allregisterPayload = self.readallRegisters()
        # bei start alle retained Senden
        # self.doPublishPayload(allregisterPayload, retained=True)

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
            return ""

        def getReadTopic(k: any) -> str:
            return self.getTopicByKey(k)

        def getWriteTopic(k: any) -> str:
            return ""

        def getVarType(k: any) -> str:
            return ""

        def getStructure(k: any) -> dict:
            return {}

        def getUnit(k: any) -> str:
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




    def doProcess(self):
        try:
           pass
        except Exception as e:
            logger.error(f"device: {self.m_MQTT_NETID}  doProcess : error:{e}")
            logger.info(f"device: {self.m_MQTT_NETID}  doProcess : error:{e}")
