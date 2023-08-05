from sdm_modbus import meter
# from sdm_modbus.sdm import SDM630
# from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
import struct
# from pymodbus.pdu import ModbusRequest, ModbusResponse, ModbusExceptions
# from pymodbus.constants import Endian




# Storage(SPH Type)：
# Input-Register: 03 register range：0~124,1000~1124；
# Holding Register: 04 register range：0~124,1000~1124，1125~1249
# SOC-Min: Register 608

# rading no more than 125 register words in one call

class Growatt(meter.Meter):
    pass


class SPH_TL3_BH_UP(Growatt):

    def __init__(self, *args, **kwargs):
        self.model = "SPH_TL3_BH_UP"
        self.baud = 9600

        super().__init__(*args, **kwargs)


        self.registers = {

            "Inverter_Status": (0, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "Inverter_Status", "0,1,3", 1, 1),
            "Ppv": (1, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Input_power", "W", 1, 0.1),
            "Vpv1": (3, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "PV1 voltage", "V", 1, 0.1),
            "PV1Curr": (4, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "PV1 input current", "A", 1, 0.1),
            "Ppv1": (5, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV1 input power", "W", 1, 0.1),
            "Vpv2": (7, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "PV2c2 voltage", "U", 1, 0.1),
            "PV2Curr": (8, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "PV2 input current", "A", 1, 0.1),
            "Ppv2": (9, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, " PV2 input power", "W", 1, 0.1),
           
            "Pac": (35, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Output power", "W", 1, 0.1),
            "Fac": (37, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Grid frequency", "Hz", 1, 0.01),
            "Vac1": (38, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 1 grid voltage", "V", 1, 0.1),
            "Iac1": (39, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 1 grid output current", "A", 1, 0.1),
            "Pac1": (40, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Three/single_phase 1 grid output watt", "VA", 1, 0.1),   
            "Vac2": (42, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 2 grid voltage", "V", 1, 0.1),
            "Iac2": (43, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 2 grid output current", "A", 1, 0.1),
            "Pac2": (44, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Three/single_phase 2 grid output watt", "VA", 1, 0.1),
       

            "Vac3": (46, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 3 grid voltage", "V", 1, 0.1),
            "Iac3": (47, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three/single_phase 3 grid output current", "A", 1, 0.1),
            "Pac3": (48, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Three/single_phase 3 grid output watt", "VA", 1, 0.1),
            "Vac_RS": (50, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three phase grid voltage", "V", 1, 0.1),
            "Vac_ST": (51, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three phase grid voltage", "V", 1, 0.1),     
            "Vac_TR": (52, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Three phase grid voltage", "V", 1, 0.1),                   
         
            "Eactoday": (53, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Today_generate energy", "kW", 1, 0.1),
            "Eactotal": (55, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Total_generate energy", "kW", 1, 0.1),
            "Time_total": (57, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Time total", "s", 1, 0.5),
            "Epv1_today": (59, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV1_Energy today", "kW", 1, 0.1),
            "Epv1_total": (61, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV1_Energy total", "kW", 1, 0.1),
            "Epv2_today": (63, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV2_Energy today", "kW", 1, 0.1),
            "Epv2_total": (65, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV2_Energy total", "kW", 1, 0.1),
            "Epv_total": (91, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "PV Energy total", "kW", 1, 0.1),
            "Temp1": (93, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Inverter temperature", "°C", 1, 0.1),
            "Temp2": (94, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "inside IPM in inverter Temperature", "°C", 1, 0.1),
            "Temp3": (95, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Boost temperature", "°C", 1, 0.1),
            
            
            "uwSysWorkMode": (1000, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "System work mode", "", 2, 1),
        
            "Pdischarge1": (1009, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Discharge power", "W", 2, 0.1),
            "Pcharge1": (1011, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Charge power", "W", 2, 0.1),
            "Vbat": (1013, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Battery voltage", "V", 2, 0.1),
            "SOC": (1014, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "State of charge Capacity", "%", 2, 1),
            "Pactouser_R": (1015, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "AC power to user R", "W", 2, 0.1),
            "Pactouser_S": (1017, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "AC power to user S", "W", 2, 0.1),
            "Pactouser_T": (1019, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "AC power to user T", "W", 2, 0.1),
            "Pactouser_total": (1021, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "AC power to user total", "W", 2, 0.1),
            "Pactogrid_R": (1023, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "AC power to grid R", "W", 2, 0.1),
            "Pactogrid_S": (1025, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "AC power to grid S", "W", 2, 0.1),
            "Pactogrid_T": (1027, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "AC power to grid T", "W", 2, 0.1),
            "Pactogrid_total": (1029, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "AC power to grid total", "W", 2, 0.1),
            "PLocalLoad_R": (1031, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "INV power to local load R", "W", 2, 0.1),
            "PLocalLoad_S": (1033, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "INV power to local load S", "W", 2, 0.1),
            "PLocalLoad_T": (1035, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "INV power to local load T", "W", 2, 0.1),
            "PLocalLoad_total": (1037, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "INV power to local load total", "W", 2, 0.1),

               
            "Etouser_today": (1044, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Energy_to user today", "KWh", 2, 0.1),
            "Etouser_total": (1046, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Energy_to user total", "KWh", 2, 0.1),
            "Etogrid_today": (1048, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Energy_to grid today", "KWh", 2, 0.1),
           
            "Etogrid_total": (1050, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Energy_to grid total", "KWh", 2, 0.1),
            "Edischarge1_today": (1052, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Discharge_energy1 today", "KWh", 2, 0.1),
            "Edischarge1_total": (1054, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Discharge_energy1 total", "KWh", 2, 0.1),
            "Echarge1_today": (1056, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, " Charge1_energy today", "KWh", 2, 0.1),
            "Echarge1_total": (1058, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Charge1_energy total", "KWh", 2, 0.1),
            "ELocalLoad_Today": (1060, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Local_load energy today", "KWh", 2, 0.1),
            "ELocalLoad_Total": (1062, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "Local_load energy total", "KWh", 2, 0.1),
            "dwExportLimitApparentPower": (1064, 2, meter.registerType.INPUT, meter.registerDataType.UINT32, float, "ExportLimitApparentPower", "W", 2, 0.1),
            
            "BMS_StatusOld": (1082, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "old Status from BMS", "", 2, 1),
            "BMS_Status": (1083, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "Status from BMS", "", 2, 1),
            "BMS_ErrorOld": (1084, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "Old Error infomation from BMS", "", 2, 1),
            "BMS_Error": (1085, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, int, "Error infomation from BMS", "", 2, 1),
            "BMS_SOC": (1086, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "SOC from BM", "%", 2, 1),
            "BMS_BatteryVolt": (1087, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Battery voltage from BMS", "V", 2, 0.1),
            "BMS_BatteryCurrent": (1088, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Battery current from BMS", "A", 2, 1),
            "BMS_BatteryTemp": (1089, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Battery temperature from BMS", "°C", 2, 0.1),
            "BMS_MaxCurrent": (1090, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "Max. charge/discharge current from BMS (pylon)", "A", 2, 1),
      
            "BMS_SOH": (1096, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_SOH", "", 2, 1),
            "BMS_CELL1Volt": (1108, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 1 Voltage", "V", 2, 0.01),
            "BMS_CELL2Volt": (1109, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 2 Voltage", "V", 2, 0.01),
            "BMS_CELL3Volt": (1110, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 3 Voltage", "V", 2, 0.01), 
            "BMS_CELL4Volt": (1111, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 4 Voltage", "V", 2, 0.01), 
            "BMS_CELL5Volt": (1112, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 5 Voltage", "V", 2, 0.01), 
            "BMS_CELL6Volt": (1113, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 6 Voltage", "V", 2, 0.01), 
            "BMS_CELL7Volt": (1114, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 7 Voltage", "V", 2, 0.01), 
            "BMS_CELL8Volt": (1115, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 8 Voltage", "V", 2, 0.01), 
            "BMS_CELL9Volt": (1116, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 9 Voltage", "V", 2, 0.01), 
            "BMS_CELL10Volt": (1117, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 10 Voltage", "V", 2, 0.01), 
            "BMS_CELL11Volt": (1118, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 11 Voltage", "V", 2, 0.01), 
            "BMS_CELL12Volt": (1119, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 12 Voltage", "V", 2, 0.01), 
            "BMS_CELL13Volt": (1120, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 13 Voltage", "V", 2, 0.01), 
            "BMS_CELL14Volt": (1121, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 14 Voltage", "V", 2, 0.01), 
            "BMS_CELL15Volt": (1122, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 15 Voltage", "V", 2, 0.01), 
            "BMS_CELL16Volt": (1123, 1, meter.registerType.INPUT, meter.registerDataType.UINT16, float, "BMS_Cell 16 Voltage", "V", 2, 0.01), 
            
            
            # # Holding-Register
            "OnOff": (0, 1, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Inverter_Status", "0,1,2,3", 1, 1),
            #         Set Holding  register3,4,5,99 CMD  will be memory or  not(1/0), if not, these settings are the  initial     #
            "SaftyFuncEn": (1, 1, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "0 :disable,1: enable", "", 1, 1),

            "PF_CMD_memory_state": (2, 1, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Set Holding register3,4,5,99", "", 1, 1),

            "Active_P_Rate": (3, 1, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Inverter Max output active power percent", "%", 1, 0.1),

            "Reactive_P_Rate": (4, 1, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Inverter max output reactive power percent", "%", 1, 0.1),

            "Power_factor": (5, 1, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Inverter output power factor’s 10000 times", "%", 1, 1),

            "ExportLimit_EN_Dis": (122, 1, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "ExportLimit_En/dis", "0...3", 2, 1),
            "ExportLimitPowerRate": (123, 1, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "ExportLimitPowerRate", "%", 2, 0.1),

         
            # 2:METER
            # 1:cWirele ssCT
            # 0:cWiredCT
            "bCTMode": (1037, 1, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "2:METER 1:cWirelessCT 0:cWiredCT", "0,1,2", 3, 1),

            # ForceChrEn/ForceDischrEn
            # Load first=0/bat first=1 /grid first=3
            "Load_Priority": (1044, 1, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "Load first/bat first /grid first", "0,1,2", 3, 1),


            # SET SOC-Min: Register 608
            "SOC_Min": (608, 1, meter.registerType.HOLDING, meter.registerDataType.UINT16, int, "SOC_Min", "0", 4, 1),

        }
