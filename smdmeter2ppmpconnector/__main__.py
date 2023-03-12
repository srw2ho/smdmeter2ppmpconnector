import json
import sys
import logging
from logging.handlers import RotatingFileHandler
import os
import configparser
from queue import Queue
from threading import Thread
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
QUEUE_MQTT = Queue(maxsize=0)
QUEUE_INFLUX = Queue(maxsize=0)

threads = []

globMQTTClient = None


def run_SMD_meter(alias, modbushost, modbusport, devid, metertype, timeout, refresrate):

    global globMQTTClient
    def getMeterByType(x):
        if x == "SDM630":
            return sdm_modbus.SDM630(host=modbushost, port=modbusport, timeout=timeout, framer=None, unit=devid, udp=False)
        if x == "SDM230":
            return sdm_modbus.SDM230(host=modbushost, port=modbusport, timeout=timeout, framer=None, unit=devid, udp=False)
        if x == "SDM120":
            return sdm_modbus.SDM120(host=modbushost, port=modbusport, timeout=timeout, framer=None, unit=devid, udp=False)
        if x == "SDM72":
            return sdm_modbus.SDM72(host=modbushost, port=modbusport, timeout=timeout, framer=None, unit=devid, udp=False)
        if x == "SDM72V2":
            return sdm_modbus.SDM72V2(host=modbushost, port=modbusport, timeout=timeout, framer=None, unit=devid, udp=False)
        return None

    meter = getMeterByType(metertype)
    if (meter == None):
        return

    doJson: bool = False
    RefreshTime: int = refresrate
    connectTime: int = timeout
    doReadHoldingRegister: bool = False

    iotDevice = iotHubDevice(net_name='mh', devideid=alias, additionalData={
                             'type': 'smdmeter', },)
    if globMQTTClient:
        globMQTTClient.publish(iotDevice.info_topic(),
                               machine_message_generator(iotDevice), retain=True)

    while True:

        IsConnected: bool = meter.connected()
        if not IsConnected:
            meter.connect()
            time.sleep(connectTime)
            print("Disconnected -> Try Rconnect")

        if IsConnected:
            if doJson:
                print(json.dumps(meter.read_all(scaling=True), indent=4))
            else:
                # print(f"{meter}:")
                print("\nInput Registers:")

                # jsonpayload = {k: v for k, v in meter.read_all(
                #     sdm_modbus.registerType.INPUT).items() if k != ""}

                jsonpayload =  meter.read_all(sdm_modbus.registerType.INPUT)
               
                for k, v in jsonpayload.items():
                    address, length, rtype, dtype, vtype, label, fmt, batch, sf = meter.registers[
                        k]

                    if type(fmt) is list or type(fmt) is dict:
                        print(f"\t{label}: {fmt[str(v)]}")
                    elif vtype is float:
                        print(f"\t{label}: {v:.2f}{fmt}")
                    else:
                        print(f"\t{label}: {v}{fmt}")

                if globMQTTClient and globMQTTClient.isConnected():
                    acttime = local_now()
                    simplevars = SimpleVariables(
                        iotDevice, jsonpayload, acttime)
                    ppmppayload = simplevars.to_ppmp()
                    globMQTTClient.publish(
                        iotDevice.ppmp_topic(), ppmppayload, retain=False)

                if doReadHoldingRegister:
                    print("\nHolding Registers:")

                    for k, v in meter.read_all(sdm_modbus.registerType.HOLDING).items():
                        address, length, rtype, dtype, vtype, label, fmt, batch, sf = meter.registers[
                            k]

                        if type(fmt) is list:
                            print(f"\t{label}: {fmt[v]}")
                        elif type(fmt) is dict:
                            print(f"\t{label}: {fmt[str(v)]}")
                        elif vtype is float:
                            print(f"\t{label}: {v:.2f}{fmt}")
                        else:
                            print(f"\t{label}: {v}{fmt}")

        time.sleep(RefreshTime)


def start_smdmeters():
    ll = []

    SMDMETERS_MODBUSHOST = toml.get('sdmmeters.tcpmodbushost', ['localhost'])
    SMDMETERS_MODBUSALIAS = toml.get('sdmmeters.tcpmodbusalias', ['SDM630_1'])
    SDMMETERS_MODBUSPORT = toml.get('sdmmeters.tcpmodbusport', [8086])
    SMDMETERS_TYPE = toml.get('sdmmeters.metertype', ['SDM630'])
    SDMMETETERS_REFRESHRATE = toml.get('sdmmeters.refreshrate', [2])
    SDMMETETERS_CONNECTIONTIMEOUT = toml.get(
        'sdmmeters.connectiontimeout', [2])
    SDMMETERS_DEVICEID = toml.get('sdmmeters.deviceid', [2])

    # registers = {k: v for k, v in self.registers.items() if (v[2] == rtype)}

    # for host, port, path in zip(hosts, ports, paths):

    # create own thread for each PLC device
    for alias, host, port, devid, metertypes, timeout, refresrate in zip(SMDMETERS_MODBUSALIAS, SMDMETERS_MODBUSHOST, SDMMETERS_MODBUSPORT, SDMMETERS_DEVICEID, SMDMETERS_TYPE, SDMMETETERS_CONNECTIONTIMEOUT, SDMMETETERS_REFRESHRATE):
        # create new thread for each OPC-UA client
        thread = Thread(target=run_SMD_meter, args=(alias,
                                                    host, port, devid, metertypes, timeout, refresrate))
        threads.append(thread)
        thread.start()


def main():
    global globMQTTClient
    
    # connect to MQTT and InfluxDB
    mqtt_client = MQTTClient(host=MQTT_HOST, port=MQTT_PORT,
                             user=MQTT_USERNAME, password=MQTT_PASSWORD, tls_cert=MQTT_TLS_CERT)
    mqtt_client.connect(forever=True)

    globMQTTClient = mqtt_client
    # # create and start convertor thread
    # Thread(target=convertor).start()

    # # create and start InfluxDB consumer thread
    # Thread(target=influx_consumer).start()
    start_smdmeters()

    mqtt_client.start()


def mqtt_producer(payload):
    """ Subscribe to MQTT changes and write payload into queue

    Arguments:
        payload {obj} -- JSON payload in PPMP format
    """
    QUEUE_MQTT.put(payload)
    # logger.info(f'MQTT Queue size: {QUEUE_MQTT.qsize()}')


if __name__ == '__main__':
    main()
