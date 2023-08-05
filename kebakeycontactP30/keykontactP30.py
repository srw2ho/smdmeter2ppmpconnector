from sdm_modbus import meter
from sdm_modbus.sdm import SDM630
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
import struct
from pymodbus.pdu import ModbusRequest, ModbusResponse, ModbusExceptions


# SOC-Min: Register 608


# Storage(SPH Type)：
# Input-Register: 03 register range：0~124,1000~1124；
# Holding Register: 04 register range：0~124,1000~1124，1125~1249

class Keba(meter.Meter):
    pass


class KeContactP30(Keba):

    def __init__(self, *args, **kwargs):
        self.model = "KeContactP30"
        self.baud = 9600

        super().__init__(*args, **kwargs)

        self.registers = {
            "Charging_State": (1000, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, int, "Charging State", "0,1,2,3,4,5", 1, 1),
            "Cable_State": (1004, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, int, "Cable state", "0,1,3,5,7", 2, 1),
            "EVSE_Error_Code": (1006, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, int, "EVSE Error Code", "V", 3, 1),
            "Current_L1": (1008, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Current L1", "A", 4, 0.001),
            "Current_L2": (1010, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Current L2", "A", 5, 0.001),
            "Current_L3": (1012, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Current L3", "A", 6, 0.001),
            "Serial_Number": (1014, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, int, "Serial Number", "", 7, 1),
            "Product_Type": (1016, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, int, "Product Type", "", 8, 1),
            "Firmware_Version": (1018, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, int, "Firmware Version", "", 9, 1),
            "Active_Power": (1020, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Active Power", "W", 10, 0.001),

            "Total_Energy": (1036, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Total Energy", "KWh", 11, 0.001),
            "Voltage_U1": (1040, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Voltage U1", "U", 12, 1),
            "Voltage_U2": (1042, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Voltage U2", "U", 13, 1),
            "Voltage_U3": (1044, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Voltage U3", "U", 14, 1),
            "Power_Factor": (1046, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Power Factor", "%", 15, 0.1),
            "Max_Charging_Current": (1100, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Max Charging Current", "A", 16, 0.001),
            "Max_Supported_Current": (1110, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Max Supported Current", "A", 17, 0.001),
            "RFID_Card": (1500, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, int, "RFID_ Card", "", 18, 1),
            "Charged_Energy": (1502, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Charged Energy", "Wh", 19, 1),

            "Phase_Switching_Source": (1552, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, int, "Phase Switching Source", "", 20, 1),
            "Phase_Switching_State": (1552, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, int, "Phase Switching State", "", 21, 1),
            "Failsafe_Current_Setting": (1600, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Failsafe Current Setting", "A", 22, 0.001),
            "Failsafe_Timeout_Setting": (1602, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, int, "Failsafe_Timeout_Setting", "sec", 23, 1),
            
            # Write Single Holding-Register
            "Set_Charging_Current": (5004, 1, meter.registerType.SINGLE_HOLDING, meter.registerDataType.UINT16, float, "Set Charging Current", "A", 1, 0.001),
            "Set_Energy": (5010, 1, meter.registerType.SINGLE_HOLDING, meter.registerDataType.UINT16, float, "Set Energy", "kWh", 2, 0.001),

            "Unlock_Plug": (5012, 1, meter.registerType.SINGLE_HOLDING, meter.registerDataType.UINT16, int, "Unlock Plug", "", 3, 1),

            "Charging_Station_Enable": (5014, 1, meter.registerType.SINGLE_HOLDING, meter.registerDataType.UINT16, int, "Charging Station Enable", "", 4, 1),

            "Set_Phase_Switch_Toggle": (5050, 1, meter.registerType.SINGLE_HOLDING, meter.registerDataType.UINT16, int, "Set Phase Switch Toggle", "0,1,2,3,4", 5, 1),

            "Trigger_Phase_Switch": (5052, 1, meter.registerType.SINGLE_HOLDING, meter.registerDataType.UINT16, int, "Trigger_Phase_Switch", "0,1", 6, 1),

            "Failsafe_Current": (5016, 1, meter.registerType.SINGLE_HOLDING, meter.registerDataType.UINT16, float, "Failsafe Current", "A", 7, 0.001),
            "Failsafe_Timeout": (5018, 1, meter.registerType.SINGLE_HOLDING, meter.registerDataType.UINT16, int, "Failsafe_Timeout", "sec", 8, 1),
            "Failsafe_Persist": (5020, 1, meter.registerType.SINGLE_HOLDING, meter.registerDataType.UINT16, int, "Failsafe_Persist", "", 9, 1),

         

        }

# Batch nicht disable
    def setBatchForRegisterByKey(self, key: str, setbatch: int = 0) -> bool:
       
        return False
