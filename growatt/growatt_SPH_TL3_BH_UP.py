from sdm_modbus import meter
from sdm_modbus.sdm import SDM630
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
import struct
from pymodbus.pdu import ModbusRequest, ModbusResponse, ModbusExceptions
from pymodbus.constants import Endian

# SOC-Min: Register 608


# Storage(SPH Type)：
# Input-Register: 03 register range：0~124,1000~1124；
# Holding Register: 04 register range：0~124,1000~1124，1125~1249

class Growatt(meter.Meter):
    pass


class SPH_TL3_BH_UP(Growatt):

    def __init__(self, *args, **kwargs):
        self.model = "SPH_TL3_BH_UP"
        self.baud = 9600

        super().__init__(*args, **kwargs)

        # self.wordorder = Endian.Little
        # self.byteorder = Endian.Little
        self.registers = {
            "Inverter_Status": (0, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "Inverter_Status", "0,1,3", 1, 1),
            "Ppv": (2, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Input_power", "W", 1, 0.1),
            "Vpv1": (6, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "PV1 voltage", "V", 1, 0.1),
            "PV1Curr": (8, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "PV1 input current", "A", 1, 0.1),
            "Ppv1": (10, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV1 input power", "W", 1, 0.1),
            "Vpv2": (14, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "PV2c2 voltage", "U", 1, 0.1),
            "PV2Curr": (16, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "PV2 input current", "A", 1, 0.1),
            "Ppv2": (18, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, " PV2 input power", "W", 1, 0.1),
            
            "Pac": (35, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Output power", "W", 2, 0.1),
            "Fac": (37, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Grid frequency", "Hz", 2, 0.01),
            "Vac1": (38, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 1 grid voltage", "V", 2, 0.1),
            "Iac1": (39, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 1 grid output current", "A", 2, 0.1),
            "Pac1": (40, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Three/single_phase 1 grid output watt", "VA", 2, 0.1),
            
            "Vac2": (42, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 2 grid voltage", "V", 2, 0.1),
            "Iac2": (43, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 2 grid output current", "A", 2, 0.1),
            "Pac2": (44, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Three/single_phase 2 grid output watt", "VA", 2, 0.1),
       
            "Vac3": (46, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 3 grid voltage", "V", 2, 0.1),
            "Iac3": (47, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 3 grid output current", "A", 2, 0.1),
            "Pac3": (48, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Three/single_phase 3 grid output watt", "VA", 2, 0.1),
            "Vac_RS": (50, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three phase grid voltage", "V", 2, 0.1),
            "Vac_ST": (51, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three phase grid voltage", "V", 2, 0.1),     
            "Vac_TR": (52, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three phase grid voltage", "V", 2, 0.1),                   
            "Eactoday": (53, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Today_generate energy", "kW", 2, 0.1),
            "Eactotal": (55, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Total_generate energy", "kW", 2, 0.1),
            "Time_total": (57, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Time total", "s", 2, 0.5),
            "Epv1_today": (59, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV1_Energy today", "kW", 2, 0.1),
            "Epv1_total": (61, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV1_Energy total", "kW", 2, 0.1),
            "Epv2_today": (63, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV2_Energy today", "kW", 2, 0.1),
            "Epv2_total": (65, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV2_Energy total", "kW", 2, 0.1),

            "Epv_total": (91, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV Energy total", "kW", 3, 0.1),
            "Temp1": (93, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Inverter temperature", "°C", 3, 0.1),
            "Temp2": (94, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "inside IPM in inverter Temperature", "°C", 3, 0.1),
            "Temp3": (95, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Boost temperature", "°C", 3, 0.1),
            

            "Pdischarge1": (1009, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Discharge power", "W", 4, 0.1),
            "Pcharge1": (1011, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Charge power", "W", 4, 0.1),
            "Vbat": (1013, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Battery voltage", "V", 4, 0.1),
            "SOC": (1014, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "State of charge Capacity", "%", 4, 1),
            "Pactouser_R": (1015, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "AC power to user", "W", 4, 0.1),
            "Pactouser_S": (1017, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Pactouser", "W", 4, 0.1),
            "Pactouser_T": (1019, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "AC power to user total", "W", 4, 0.1),
            "Pactouser_Total": (1021, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "AC power to user total", "W", 4, 0.1),
            "Pac_to_grid_R": (1023, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "AC power to grid", "W", 4, 0.1),
           
            "uwSysWorkMode": (1000, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "System work mode", "", 5, 1),
            "PLocalLoad_total": (1037, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "INV_power to local load total", "W", 6, 0.1),
         
            "Etouser_today": (1044, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Energy_to user today", "KWh", 6, 0.1),
            "Etouser_total": (1046, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Energy_to user total", "KWh", 6, 0.1),
            "Etogrid_today": (1048, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Energy_to grid today", "KWh", 6, 0.1),
           
            "Etogrid_total": (1050, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Energy_to grid total", "W", 6, 0.1),
            "Edischarge1_today": (1052, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Discharge_energy1 today", "W", 6, 0.1),
            "Edischarge1_total": (1054, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Discharge_energy1 total", "W", 6, 0.1),
            "Echarge1_today": (1056, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, " Charge1_energy today", "W", 6, 0.1),
            "Echarge1_total": (1058, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Charge1_energy total", "W", 6, 0.1),
            "ELocalLoad_Today": (1060, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Local_load energy today", "W", 6, 0.1),
            "ELocalLoad_Total": (1062, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Local_load energy total", "W", 6, 0.1),
            "dwExportLimitApparentPower": (1064, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "ExportLimitApparentPower", "W", 6, 0.1),
            
            "BMS_StatusOld": (1082, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "old Status from BMS", "", 7, 1),
            "BMS_Status": (1083, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "Status from BMS", "", 7, 1),
            "BMS_ErrorOld": (1084, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "Old Error infomation from BMS", "", 7, 1),
            "BMS_Error": (1085, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "Error infomation from BMS", "", 7, 1),
            "BMS_SOC": (1086, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "SOC from BM", "%", 7, 1),
            "BMS_BatteryVolt": (1087, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Battery voltage from BMS", "V", 7, 0.1),
            "BMS_BatteryCurrent": (1088, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Battery current from BMS", "A", 7, 0.001),
            "BMS_BatteryTemp": (1089, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Battery temperature from BMS", "°C", 7, 0.1),
            
            "BMS_SOH": (1096, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_SOH", "", 8, 1),
            "uwMaxCellVolt": (1108, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Maximum single battery voltage", "V", 9, 0.001),
            "uwMinCellVolt": (1109, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Lowest single battery voltage", "V", 9, 0.001),
            
            # # Holding-Register
            "OnOff": (0, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Inverter_Status", "0,1,2,3", 1, 1),
            #         Set Holding  register3,4,5,99 CMD  will be memory or  not(1/0), if not, these settings are the  initial     #
            "SaftyFuncEn": (1, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "0 :disable,1: enable", "", 1, 1),

            "PF_CMD_memory_state": (2, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Set Holding register3,4,5,99", "", 1, 1),

            "Active_P_Rate": (3, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Inverter Max output active power percent", "%", 1, 0.1),

            "Reactive_P_Rate": (4, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Inverter max output reactive power percent", "%", 1, 0.1),

            "Power_factor": (5, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Inverter output power factor’s 10000 times", "%", 1, 1),

            "ExportLimit_EN_Dis": (122, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "ExportLimit_En/dis", "0...3", 2, 1),
            "ExportLimitPowerRate": (123, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "ExportLimitPowerRate", "%", 2, 0.1),

         
            # 2:METER
            # 1:cWirele ssCT
            # 0:cWiredCT
            "bCTMode": (1037, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "2:METER 1:cWirelessCT 0:cWiredCT", "0,1,2", 3, 1),

            # ForceChrEn/ForceDischrEn
            # Load first=0/bat first=1 /grid first=3
            "Load_Priority": (1044, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Load first/bat first /grid first", "0,1,2", 3, 1),


            # SET SOC-Min: Register 608
            "SOC_Min": (608, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "SOC_Min", "0", 4, 1),

        }
