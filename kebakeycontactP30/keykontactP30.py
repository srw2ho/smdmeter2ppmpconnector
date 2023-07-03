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
            "Charging_State": (1000, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, int, "Inverter_Status", "0,1,3", 1, 1),
            "Cable_State": (1004, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Input_power", "W", 1, 0.1),
            "EVSE_Error_Code": (1006, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "PV1 voltage", "V", 1, 0.1),
            "Current_L1": (1008, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "PV1 input current", "A", 1, 0.1),
            "Current_L2": (1010, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "PV1 input power", "W", 1, 0.1),
            "Current_L3": (1012, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "PV2 voltage", "U", 1, 0.1),
            "Serial_Number": (1014, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "PV2 input current", "A", 1, 0.1),
            "Product_Type": (1016, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, " PV2 input power", "W", 1, 0.1),
            "Firmware_Version": (1018, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Output power", "W", 1, 0.1),
            "Active_Power": (1020, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Grid frequency", "Hz", 1, 0.01),

            "Total_Energy": (1036, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Three/single_phase grid voltage", "V", 1, 0.1),
            "Voltage_U1": (1040, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Three/single_phase grid output current", "A", 1, 0.1),
            "Voltage_U2": (1042, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Three/single_phase grid output watt", "W", 1, 0.1),
            "Voltage_U3": (1044, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Today_generate energy", "W", 1, 0.1),
            "Power_Factor": (1046, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Total_generate energy", "W", 1, 0.1),
            "Max_Charging_Current": (1100, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "PV1_Energy today", "W", 1, 0.1),
            "Max_Supported_urrent": (1110, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "PV1_Energy today", "W", 1, 0.1),
            "RFID_Card": (1500, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "PV2_Energy today", "W", 1, 0.1),
            "Charged_Energy": (1502, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "PV_Energy total", "W", 1, 0.1),

            "Phase_Switching_Source": (1552, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Inverter temperature", "°C", 2, 0.1),
            "Phase_Switching_State": (1552, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "System work mode", "", 2, 1),
            "Failsafe_Current_Setting": (1600, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Discharge power", "W", 2, 0.1),
            "Failsafe_Timeout_Setting": (1602, 2, meter.registerType.HOLDING, meter.registerDataType.UINT32, float, "Charge power", "W", 2, 0.1),
            
            # Write Holding-Register
            "Set_Charging_Current": (5004, 2, meter.registerType.WRITE_HOLDING, meter.registerDataType.UINT32, int, "Inverter_Status", "0,1,2,3", 1, 1),
            "Set_Energy": (5010, 2, meter.registerType.WRITE_HOLDING, meter.registerDataType.UINT32, int, "0 :disable,1: enable", "", 1, 1),

            "Unlock_Plug": (5012, 2, meter.registerType.WRITE_HOLDING, meter.registerDataType.UINT32, int, "Set Holding register3,4,5,99", "", 1, 1),

            "Charging_Station_Enable": (5014, 2, meter.registerType.WRITE_HOLDING, meter.registerDataType.UINT32, int, "Inverter Max output active power percent", "%", 1, 0.1),

            "Set_Phase_Switch_Toggle": (5050, 2, meter.registerType.WRITE_HOLDING, meter.registerDataType.UINT32, int, "Inverter max output reactive power percent", "%", 1, 0.1),

            "Trigger_Phase_Switch": (5052, 2, meter.registerType.WRITE_HOLDING, meter.registerDataType.UINT32, int, "Inverter output power factor’s 10000 times", "%", 1, 1000),

            "Failsafe_Current": (5016, 2, meter.registerType.WRITE_HOLDING, meter.registerDataType.UINT32, int, "ExportLimit_En/dis", "0...3", 1, 1),
            "Failsafe_Timeout": (5018, 2, meter.registerType.WRITE_HOLDING, meter.registerDataType.UINT32, int, "ExportLimitPowerRate", "%", 1, 0.1),
            "Failsafe_Persist": (5020, 2, meter.registerType.WRITE_HOLDING, meter.registerDataType.UINT16, int, "SOC_Min", "0", 2, 1),

         

        }
