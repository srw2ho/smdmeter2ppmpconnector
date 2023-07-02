import json
import sys
import logging
from logging.handlers import RotatingFileHandler
import os
import configparser
from queue import Queue
from threading import Thread
from mqttservice.mqttdeviceservicebase import MqttDeviceServiceBase
import sdm_modbus


# from time import time
import time
from pathlib import Path
from mqttconnector.client import MQTTClient
from ppmpmessage.v3.device_state import DeviceState
from ppmpmessage.v3.device import Device
from ppmpmessage.v3.util import machine_message_generator
from ppmpmessage.v3.util import local_now
from ppmpmessage.convertor.simple_variables import SimpleVariables
from ppmpmessage.v3.device import Device
from ppmpmessage.v3.device import iotHubDevice


from tomlconfig.tomlutils import TomlParser

PROJECT_NAME = 'sdmmeter2ppmpconnector'

LOGFOLDER = "./logs/"

# configure logging
logger = logging.getLogger('root')
logger.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

# fl = logging.FileHandler(f'{PROJECT_NAME}.log')
# Rotation file handler mit 200 000 bytes pro file und 10 files in rotation


try:
    os.mkdir(LOGFOLDER)
    logger.info(f'create logfolder: {LOGFOLDER}')
except OSError as error:
    logger.info(f'create logfolder: {LOGFOLDER}:{error}')

fl = RotatingFileHandler(
    f'{LOGFOLDER}{PROJECT_NAME}.log', mode='a', maxBytes=2*(10**5), backupCount=10)

fl.setLevel(logging.ERROR)
fl.setFormatter(formatter)
logger.addHandler(fl)

toml = TomlParser(f'{PROJECT_NAME}.toml')

MQTT_NETWORK_NAME = toml.get('mqtt.network_name', 'mh')
MQTT_TOPIC_PPMP = MQTT_NETWORK_NAME + '/+/' + 'ppmp'
MQTT_TOPIC_INFO = MQTT_NETWORK_NAME + '/+/' + 'ppmp'
MQTT_HOST = toml.get('mqtt.host', 'localhost')
MQTT_PORT = toml.get('mqtt.port', 1883)
MQTT_USERNAME = toml.get('mqtt.username', '')
MQTT_PASSWORD = toml.get('mqtt.password', '')
MQTT_TLS_CERT = toml.get('mqtt.tls_cert', '')


# create distributed queues for all threads
# QUEUE_MQTT = Queue(maxsize=0)
# QUEUE_INFLUX = Queue(maxsize=0)




def run_SMD_meter(alias, modbushost, modbusport, devid, metertype, timeout, refresrate, readholding):
    
    mqttDeviceService = MqttDeviceServiceBase(
        MQTT_HOST=MQTT_HOST,
        MQTT_PORT=MQTT_PORT,
        MQTT_USERNAME=MQTT_USERNAME,
        MQTT_PASSWORD=MQTT_PASSWORD,
        MQTT_TLS_CERT=MQTT_TLS_CERT,
        INFODEBUGLEVEL=1,
        MQTT_REFRESH_TIME=refresrate,
        MQTT_NETID=alias,
    )
    
    mqttDeviceService.createtMeterByType(metertype=metertype,modbushost=modbushost,modbusport=modbusport,timeout=timeout,devid=devid)
    
    isConnected = mqttDeviceService.connectMeter()
    
      # doJson: bool = False
    RefreshTime: int = refresrate
    connectTime: int = timeout

    while True:

        isMQTTConnected = mqttDeviceService.isMQTTConnected()
        IsConnected: bool = mqttDeviceService.isMeterConnected()
        
 
        if not IsConnected:
            mqttDeviceService.connectMeter()
            time.sleep(connectTime)
            logger.error(
                f'device: {alias} error: Disconnected -> Try Reconnect')
            logger.info(f'device: {alias} error: Disconnected -> Try Reconnect')

        if isMQTTConnected:
            mqttDeviceService.doProcess()
        time.sleep(RefreshTime)


def start_smdmeters():

    SMDMETERS_MODBUSHOST = toml.get('sdmmeters.tcpmodbushost', ['localhost'])
    SMDMETERS_MODBUSALIAS = toml.get('sdmmeters.tcpmodbusalias', ['SDM630_1'])
    SDMMETERS_MODBUSPORT = toml.get('sdmmeters.tcpmodbusport', [8086])
    SMDMETERS_TYPE = toml.get('sdmmeters.metertype', ['SDM630'])
    SDMMETETERS_REFRESHRATE = toml.get('sdmmeters.refreshrate', [2])
    SDMMETETERS_CONNECTIONTIMEOUT = toml.get(
        'sdmmeters.connectiontimeout', [2])
    SDMMETERS_DEVICEID = toml.get('sdmmeters.deviceid', [2])
    SDMMETERS_READHOLDING = toml.get('sdmmeters.readholding', [0])

    # create own thread for each SMD-device
    for alias, host, port, devid, metertypes, timeout, refresrate, readholding in zip(SMDMETERS_MODBUSALIAS, SMDMETERS_MODBUSHOST, SDMMETERS_MODBUSPORT, SDMMETERS_DEVICEID, SMDMETERS_TYPE, SDMMETETERS_CONNECTIONTIMEOUT, SDMMETETERS_REFRESHRATE, SDMMETERS_READHOLDING):
        # create new thread for each OPC-UA client
        thread = Thread(target=run_SMD_meter, args=(alias,
                                                    host, port, devid, metertypes, timeout, refresrate, readholding))

        thread.start()


def main():

    start_smdmeters()

    # mqtt_client.start()


if __name__ == '__main__':
    main()
