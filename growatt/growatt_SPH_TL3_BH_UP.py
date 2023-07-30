from sdm_modbus import meter
from sdm_modbus.sdm import SDM630
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
import struct
from pymodbus.pdu import ModbusRequest, ModbusResponse, ModbusExceptions


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

        self.registers = {
            "Inverter_Status": (0, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "Inverter_Status", "0,1,3", 1, 1),
            "Ppv": (2, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Input_power", "W", 1, 0.1),
            "Vpv1": (6, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "PV1 voltage", "V", 1, 0.1),
            "PV1Curr": (8, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "PV1 input current", "A", 1, 0.1),
            "Ppv1": (10, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV1 input power", "W", 1, 0.1),
            "Vpv2": (14, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "PV2 voltage", "U", 1, 0.1),
            "PV2Curr": (16, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "PV2 input current", "A", 1, 0.1),
            "Ppv2": (18, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, " PV2 input power", "W", 1, 0.1),
            
            "Pac": (70, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Output power", "W", 2, 0.1),
            "Fac": (74, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Grid frequency", "Hz", 2, 0.01),
            "Vac1": (76, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 1 grid voltage", "V", 2, 0.1),
            "Iac1": (78, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 1 grid output current", "A", 2, 0.1),
            "Pac1": (80, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Three/single_phase 1 grid output watt", "VA", 2, 0.1),
            
            "Vac2": (84, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 2 grid voltage", "V", 2, 0.1),
            "Iac2": (86, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 2 grid output current", "A", 2, 0.1),
            "Pac2": (88, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Three/single_phase 2 grid output watt", "VA", 2, 0.1),
       
            "Vac3": (92, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 3 grid voltage", "V", 2, 0.1),
            "Iac3": (94, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 3 grid output current", "A", 2, 0.1),
            "Pac3": (96, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Three/single_phase 3 grid output watt", "VA", 2, 0.1),
            "Vac_RS": (100, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three phase grid voltage", "V", 2, 0.1),
            "Vac_ST": (102, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three phase grid voltage", "V", 2, 0.1),     
            "Vac_TR": (104, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three phase grid voltage", "V", 2, 0.1),                   
            "Eactoday": (106, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Today_generate energy", "kW", 2, 0.1),
            "Eactotal": (110, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Total_generate energy", "kW", 2, 0.1),
            "Time_total": (114, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Time total", "s", 2, 0.5),
            "Epv1_today": (118, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV1_Energy today", "kW", 2, 0.1),
            "Epv1_total": (122, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV1_Energy total", "kW", 2, 0.1),
            "Epv2_today": (126, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV2_Energy today", "kW", 2, 0.1),
            "Epv2_total": (130, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV2_Energy total", "kW", 2, 0.1),


            "Temp1": (186, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Inverter temperature", "°C", 3, 0.1),
            "Temp2": (188, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "inside IPM in inverter Temperature", "°C", 3, 0.1),
            "Temp3": (190, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Boost temperature", "°C", 3, 0.1),
            
            "uwSysWorkMode": (1000, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "System work mode", "", 4, 1),
            "Pdischarge1": (1018, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Discharge power", "W", 4, 0.1),
            "Pcharge1": (1022, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Charge power", "W", 4, 0.1),
            "Vbat": (1026, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Battery voltage", "V", 4, 0.1),
            "SOC": (1028, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "State of charge Capacity", "%", 4, 0.1),
            "Pactouser R": (1030, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "AC power to user", "W", 4, 0.1),
            "Pactouser S": (1034, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Pactouser", "W", 4, 0.1),
            "Pactouser T": (1038, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "AC power to user total", "W", 4, 0.1),
            "Pactogrid total": (1042, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "AC_power to grid total", "W", 4, 0.1),

            "LocalLoad total": (1074, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "INV_power to local load total", "W", 5, 0.1),
            "Etouser_today": (1088, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Energy_to user today", "W", 5, 0.1),
            "Etouser_total": (1092, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Energy_to user total", "W", 5, 0.1),
            "Etogrid_today": (1096, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Energy_to grid today", "W", 5, 0.1),
            "Etogrid_total": (1100, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Energy_to grid total", "W", 5, 0.1),
            "Edischarge1_today": (1104, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Discharge_energy1 today", "W", 5, 0.1),
            "Edischarge1_total": (1108, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Discharge_energy1 total", "W", 5, 0.1),
            "Echarge1_today": (1112, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, " Charge1_energy today", "W", 5, 0.1),
            "Echarge1_total": (1116, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Charge1_energy total", "W", 5, 0.1),
            "ELocalLoad_Today": (1120, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Local_load energy today", "W", 5, 0.1),
            "ELocalLoad_Total": (1124, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Local_load energy total", "W", 5, 0.1),
            "dwExportLimitApparentPower": (1128, 4, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "ExportLimitApparentPower", "W", 5, 0.1),
            
            "BMS_Status": (1166, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "Status from BMS", "", 6, 1),
            "BMS_Error": (1170, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "Error infomation from BMS", "", 6, 1),
            "BMS_SOC": (1172, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "SOC from BM", "%", 6, 1),
            "BMS_BatteryVolt": (1174, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "Battery voltage from BMS", "V", 6, 1),
            "BMS_BatteryCurrent": (1176, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "Battery current from BMS", "A", 6, 1),
            "BMS_BatteryTemp": (1176, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "Battery temperature from BMS", "°C", 6, 1),
            
            "BMS_SOH": (1192, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "BMS_SOH", "", 6, 1),
            "uwMaxCellVolt": (1216, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Maximum single battery voltage", "V", 6, 0.001),
            "uwMinCellVolt": (1218, 2, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Lowest single battery voltage", "V", 6, 0.001),
            
            # Holding-Register
            "OnOff": (0, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Inverter_Status", "0,1,2,3", 1, 1),
            #         Set Holding  register3,4,5,99 CMD  will be memory or  not(1/0), if not, these settings are the  initial     #
            "SaftyFuncEn": (2, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "0 :disable,1: enable", "", 1, 1),

            "PF_CMD_memory_state": (4, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Set Holding register3,4,5,99", "", 1, 1),

            "Active_P_Rate": (6, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Inverter Max output active power percent", "%", 1, 0.1),

            "Reactive_P_Rate": (8, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Inverter max output reactive power percent", "%", 1, 0.1),

            "Power_factor": (10, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Inverter output power factor’s 10000 times", "%", 1, 1000),

            "ExportLimit_EN_Dis": (244, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "ExportLimit_En/dis", "0...3", 2, 1),
            "ExportLimitPowerRate": (246, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "ExportLimitPowerRate", "%", 2, 0.1),

         
            # 2:METER
            # 1:cWirele ssCT
            # 0:cWiredCT
            "bCTMode": (1074, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "2:METER 1:cWirelessCT 0:cWiredCT", "0,1,2", 3, 1),

            # ForceChrEn/ForceDischrEn
            # Load first=0/bat first=1 /grid first=3
            "Load_Priority": (1176, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Load first/bat first /grid first", "0,1,2", 3, 1),


            # SET SOC-Min: Register 608
            "SOC_Min": (616, 2, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "SOC_Min", "0", 4, 1),

        }
