from mqttservice.mqttdeviceservicebase import MqttDeviceServiceBase


class MqttDeviceService(MqttDeviceServiceBase):
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
    ):
        super.__init__(
            MQTT_HOST=MQTT_HOST,
            MQTT_PORT=MQTT_PORT,
            MQTT_USERNAME=MQTT_USERNAME,
            MQTT_PASSWORD=MQTT_PASSWORD,
            MQTT_TLS_CERT=MQTT_TLS_CERT,
            INFODEBUGLEVEL=INFODEBUGLEVEL,
            MQTT_REFRESH_TIME=MQTT_REFRESH_TIME,
            MQTT_NETID=MQTT_NETID,
        )
        self._MQTT_REFRESH_TIME = MQTT_REFRESH_TIME
