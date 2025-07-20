import asyncio
from datetime import datetime, timezone
import json
import sys
import logging
from logging.handlers import RotatingFileHandler
import os
import configparser
from queue import Queue
from threading import Thread
from daikin_residential.daikinaltherma.climate import DaikinClimate
from daikin_residential.daikinaltherma.daikin_api import DaikinApi
from daikin_residential.daikinaltherma.daikin_base import Appliance
from daikin_residential.daikinaltherma.sensor import DaikinSensor
from daikin_residential.daikinaltherma.water_heater import DaikinWaterTank
from mqttservice.mqttdeviceespaltherma import MqttDeviceESPAltherma
from mqttservice.mqttdevicedaikinservice import MqttDeviceDaikinService
from mqttservice.mqttdevicemodbusservice import MqttDeviceModbusService
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

PROJECT_NAME = "sdmmeter2ppmpconnector"

LOGFOLDER = "./logs/"

# configure logging
logger = logging.getLogger("root")
logger.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

# fl = logging.FileHandler(f'{PROJECT_NAME}.log')
# Rotation file handler mit 200 000 bytes pro file und 10 files in rotation


try:
    if not os.path.exists(LOGFOLDER):
        os.mkdir(LOGFOLDER)
        logger.info(f"create logfolder: {LOGFOLDER}")
except OSError as error:
    logger.info(f"create logfolder: {LOGFOLDER}:{error}")

fl = RotatingFileHandler(
    f"{LOGFOLDER}{PROJECT_NAME}.log", mode="a", maxBytes=2 * (10**5), backupCount=10
)

fl.setLevel(logging.ERROR)
fl.setFormatter(formatter)
logger.addHandler(fl)

toml = TomlParser(f"{PROJECT_NAME}.toml")

MQTT_NETWORK_NAME = toml.get("mqtt.network_name", "mh")
MQTT_TOPIC_PPMP = MQTT_NETWORK_NAME + "/+/" + "ppmp"
MQTT_TOPIC_INFO = MQTT_NETWORK_NAME + "/+/" + "ppmp"
MQTT_HOST = toml.get("mqtt.host", "localhost")
MQTT_PORT = toml.get("mqtt.port", 1883)
MQTT_USERNAME = toml.get("mqtt.username", "")
MQTT_PASSWORD = toml.get("mqtt.password", "")
MQTT_TLS_CERT = toml.get("mqtt.tls_cert", "")


# create distributed queues for all threads
# QUEUE_MQTT = Queue(maxsize=0)
# QUEUE_INFLUX = Queue(maxsize=0)


def run_ESPAltherma(alias, timeout, refresrate, infolog):
    mqttDeviceService = MqttDeviceESPAltherma(
        MQTT_HOST=MQTT_HOST,
        MQTT_PORT=MQTT_PORT,
        MQTT_USERNAME=MQTT_USERNAME,
        MQTT_PASSWORD=MQTT_PASSWORD,
        MQTT_TLS_CERT=MQTT_TLS_CERT,
        INFODEBUGLEVEL=infolog,
        MQTT_REFRESH_TIME=refresrate,
        MQTT_NETID=alias,
        MQTT_CONNECT_TIME=timeout,
    )

    isConnected = mqttDeviceService.connectDevice()
    # time.sleep(1)

    # doJson: bool = False
    RefreshTime: float = 1.0
    connectTime: int = timeout

    while True:
        isMQTTConnected = mqttDeviceService.isMQTTConnected()

        if isMQTTConnected:
            mqttDeviceService.doProcess()
        # time.sleep(0.2)
        time.sleep(RefreshTime)


def run_SMD_meter(
    alias,
    modbushost,
    modbusport,
    devid,
    metertype,
    timeout,
    refresrate,
    modbusbatchsleepinsec,
    infolog,
):
    mqttDeviceService = MqttDeviceModbusService(
        MQTT_HOST=MQTT_HOST,
        MQTT_PORT=MQTT_PORT,
        MQTT_USERNAME=MQTT_USERNAME,
        MQTT_PASSWORD=MQTT_PASSWORD,
        MQTT_TLS_CERT=MQTT_TLS_CERT,
        INFODEBUGLEVEL=infolog,
        MQTT_REFRESH_TIME=refresrate,
        MQTT_NETID=alias,
        MQTT_CONNECT_TIME=timeout,
        MODBUS_BATCH_SLEEP=modbusbatchsleepinsec,
    )

    mqttDeviceService.createtMeterByType(
        metertype=metertype,
        modbushost=modbushost,
        modbusport=modbusport,
        timeout=timeout,
        devid=devid,
    )

    isConnected = mqttDeviceService.connectDevice()
    # time.sleep(1)

    # doJson: bool = False
    RefreshTime: float = 0.2
    # connectTime: int = timeout
    # trigger: int = 1

    while True:
        isMQTTConnected = mqttDeviceService.isMQTTConnected()
        IsConnected: bool = mqttDeviceService.isDeviceConnected()

        if isMQTTConnected:
            mqttDeviceService.doProcess()
            # Improved trigger handling using match-case
            # match trigger:
            #     case 1:
            #         trigger += 1
            #         response = mqttDeviceService.getMeter().write("Set_Phase_Switch_Toggle", 3)
            #         if response.isError ():
            #             logger.error(f"Error writing Set_Phase_Switch_Toggle: {response.error}")
            #         response = mqttDeviceService.getMeter().write("Trigger_Phase_Switch", 0)
            #         if response.isError ():
            #             logger.error(f"Error writing Set_Phase_Switch_Toggle: {response.error}")
                        
            #         response=mqttDeviceService.getMeter().write("Failsafe_Current",8)
            #         if response.isError ():
            #             logger.error(f"Error writing Set_Phase_Switch_Toggle: {response.error}")
            #         response=mqttDeviceService.getMeter().write("Failsafe_Timeout",8)
            #         if response.isError ():
            #             logger.error(f"Error writing Set_Phase_Switch_Toggle: {response.error}")
            #         logger.info("Option 1 selected: Phase switch toggled and trigger reset.")
            #         timestamp = datetime.now(timezone.utc).astimezone()
            #     case 2:
            #         if timestamp is not None and (datetime.now(timezone.utc).astimezone() - timestamp).total_seconds() > 300:
            #             timestamp = datetime.now(timezone.utc).astimezone()
            #             trigger += 1
            #             response = mqttDeviceService.getMeter().write("Set_Phase_Switch_Toggle", 3)
            #             response = mqttDeviceService.getMeter().write("Trigger_Phase_Switch", 1)
            #             if response.isError ():
            #                 logger.error(f"Error writing Set_Phase_Switch_Toggle: {response.error}")
            #             logger.info("Option 2 selected: Phase switch triggered.")
            #     case 3:
            #         if timestamp is not None and (datetime.now(timezone.utc).astimezone() - timestamp).total_seconds() > 3:
            #             trigger += 1  
            #             timestamp = datetime.now(timezone.utc).astimezone()
            #             response=mqttDeviceService.getMeter().write("Charging_Station_Enable",1)
            #             if response.isError ():
            #                 logger.error(f"Error writing Set_Phase_Switch_Toggle: {response.error}")
            #                 # 8 A
            #             response=mqttDeviceService.getMeter().write("Set_Charging_Current",8)
            #             if response.isError ():
            #                 logger.error(f"Error writing Set_Phase_Switch_Toggle: {response.error}")
            #             logger.info("Option 3 selected.")
            #     case _:
            #         if timestamp is not None and (datetime.now(timezone.utc).astimezone() - timestamp).total_seconds() > 300:
            #             trigger =1
            #             timestamp = datetime.now(timezone.utc).astimezone()
            #             logger.warning("Invalid trigger option selected.")


        # time.sleep(0.2)
        time.sleep(RefreshTime)


async def start_ESPAltherma():
    EPSALTHERMA_ALIAS = toml.get("espsaltherma.alias", "ESPAltherma")

    EPSALTHERMA_REFRESHRATE = toml.get("espsaltherma.refreshrate", 2)
    EPSALTHERMA_CONNECTIONTIMEOUT = toml.get("espsaltherma.connectiontimeout", 2)
    EPSALTHERMA_INFOLOG = toml.get("espsaltherma.infolog", 1)

    # create own thread for each SMD-device
    # for (
    #     alias,
    #     host,
    #     port,
    #     devid,
    #     metertypes,
    #     timeout,
    #     refresrate,

    # ) in zip(
    #     SMDMETERS_MODBUSALIAS,
    #     SMDMETERS_MODBUSHOST,
    #     SDMMETERS_MODBUSPORT,
    #     SDMMETERS_DEVICEID,
    #     SMDMETERS_TYPE,
    #     SDMMETETERS_CONNECTIONTIMEOUT,
    #     SDMMETETERS_REFRESHRATE,

    # ):
    # create new thread for each OPC-UA client
    thread = Thread(
        target=run_ESPAltherma,
        args=(
            EPSALTHERMA_ALIAS,
            EPSALTHERMA_CONNECTIONTIMEOUT,
            EPSALTHERMA_REFRESHRATE,
            EPSALTHERMA_INFOLOG,
        ),
    )

    thread.start()


async def start_smdmeters():
    SMDMETERS_MODBUSHOST = toml.get("sdmmeters.tcpmodbushost", ["localhost"])
    SMDMETERS_MODBUSALIAS = toml.get("sdmmeters.tcpmodbusalias", ["SDM630_1"])
    SDMMETERS_MODBUSPORT = toml.get("sdmmeters.tcpmodbusport", [8086])
    SMDMETERS_TYPE = toml.get("sdmmeters.metertype", ["SDM630"])
    SDMMETETERS_REFRESHRATE = toml.get("sdmmeters.refreshrate", [2])
    SDMMETETERS_CONNECTIONTIMEOUT = toml.get("sdmmeters.connectiontimeout", [2])
    MODBUS_BATCH_SLEEPINSCS = toml.get("sdmmeters.modbusbatchsleepinsec", [0])
    SDMMETERS_DEVICEID = toml.get("sdmmeters.deviceid", [2])
    SDMMETERS_INFOLOG = toml.get("sdmmeters.infolog", [1])

    # create own thread for each SMD-device
    for (
        alias,
        host,
        port,
        devid,
        metertypes,
        timeout,
        refresrate,
        modbusbatchsleepinsec,
        infolog,
    ) in zip(
        SMDMETERS_MODBUSALIAS,
        SMDMETERS_MODBUSHOST,
        SDMMETERS_MODBUSPORT,
        SDMMETERS_DEVICEID,
        SMDMETERS_TYPE,
        SDMMETETERS_CONNECTIONTIMEOUT,
        SDMMETETERS_REFRESHRATE,
        MODBUS_BATCH_SLEEPINSCS,
        SDMMETERS_INFOLOG,
    ):
        # create new thread for each OPC-UA client
        thread = Thread(
            target=run_SMD_meter,
            args=(
                alias,
                host,
                port,
                devid,
                metertypes,
                timeout,
                refresrate,
                modbusbatchsleepinsec,
                infolog,
            ),
        )

        thread.start()


async def runDaikin():
    # await self.m_daikinAPI.retrieveAccessToken("wilschneider@kabelmail.de", "niknak@01W")

    DAIKINUSER = toml.get("daikin.user", "")
    DAIKINPW = toml.get("daikin.password", "")
    DAIKINREFRESHRATE = toml.get("daikin.refreshrate", 5)
    DAIKINCONNCTIONTIMEOUT = toml.get("daikin.connectiontimeout", 5)
    DAIKIN_INFOLOG = toml.get("daikin.infolog", 1)
    RefreshTime: float = 0.2

    mqttDeviceService = MqttDeviceDaikinService(
        MQTT_HOST=MQTT_HOST,
        MQTT_PORT=MQTT_PORT,
        MQTT_USERNAME=MQTT_USERNAME,
        MQTT_PASSWORD=MQTT_PASSWORD,
        MQTT_TLS_CERT=MQTT_TLS_CERT,
        INFODEBUGLEVEL=DAIKIN_INFOLOG,
        MQTT_REFRESH_TIME=DAIKINREFRESHRATE,
        MQTT_CONNECT_TIME=DAIKINCONNCTIONTIMEOUT,
        MQTT_NETID="DaikinWP",
        DAIKINUSER=DAIKINUSER,
        DAIKINPW=DAIKINPW,
    )

    await mqttDeviceService.connectDevice()

    while True:
        await mqttDeviceService.doProcess()
        time.sleep(RefreshTime)


def main():
    # start_smdmeters()
    loop = asyncio.get_event_loop()

    enable_altherma = toml.get("espsaltherma.enable", 1)
    if enable_altherma > 0:
        loop.run_until_complete(start_ESPAltherma())

    enable_sdmmeters = toml.get("sdmmeters.enable", 1)
    if enable_sdmmeters > 0:
        loop.run_until_complete(start_smdmeters())

    enable_daikin = toml.get("daikin.enable", 1)
    if enable_daikin > 0:
        loop.run_until_complete(runDaikin())
    else:
        while True:
            time.sleep(0.5)

    logger.error(f"runDaikin.loop.run_until_complete -closed")

    loop.close()


if __name__ == "__main__":
    main()
