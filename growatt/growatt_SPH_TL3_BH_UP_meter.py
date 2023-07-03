from sdm_modbus import meter
from sdm_modbus.sdm import SDM630
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
import struct
from pymodbus.pdu import ModbusRequest, ModbusResponse, ModbusExceptions


# SOC-Min: Register 608


# Storage(SPH Type)：
# 03 register range：0~124,1000~1124；
# 04 register range：0~124,1000~1124，1125~1249

class Growatt(meter.Meter):
    pass


class CustomModbusResponse(ModbusResponse):
    """Custom modbus response."""

    function_code = 0x20
    _rtu_byte_count_pos = 2

    def __init__(self, values=None, **kwargs):
        """Initialize."""
        ModbusResponse.__init__(self, **kwargs)
        self.values = values or []

    def encode(self):
        """Encode response pdu

        :returns: The encoded packet message
        """
        res = struct.pack(">B", len(self.values) * 2)
        for register in self.values:
            res += struct.pack(">H", register)
        return res

    def decode(self, data):
        """Decode response pdu

        :param data: The packet data to decode
        """
        byte_count = int(data[0])
        self.values = []
        for i in range(1, byte_count + 1, 2):
            self.values.append(struct.unpack(">H", data[i: i + 2])[0])


class CustomModbusRequest(ModbusRequest):
    """Custom modbus request."""
# Modbus request for reading
# 01 20 00 00 00 64 81 E6

    function_code = 0x20
    _rtu_frame_size = 8

    def __init__(self, address=None, **kwargs):
        """Initialize."""
        ModbusRequest.__init__(self, **kwargs)
        self.address = address
        self.count = 100

    def encode(self):
        """Encode."""
        return struct.pack(">HH", self.address, self.count)

    def decode(self, data):
        """Decode."""
        self.address, self.count = struct.unpack(">HH", data)

    def execute(self, context):
        """Execute."""
        if not 1 <= self.count <= 0x7D0:
            return self.doException(ModbusExceptions.IllegalValue)
        if not context.validate(self.function_code, self.address, self.count):
            return self.doException(ModbusExceptions.IllegalAddress)
        values = context.getValues(
            self.function_code, self.address, self.count)
        return CustomModbusResponse(values)


# Engineering die Lösung gefunden.


# Es geht um folgendes Szenario:

# Das Smart-Meter SDM630-Modus ist über ein Modbus direkt mit einem Growatt Wechselrichter verbunden. D.h. das die Modbusschnittstelle des Smart-Meters bereits belegt ist. Da der Wechselrichter der Master ist, kann man hier auch nicht einfach zwischenfunken.


# Nun möchte man aber ggf. mit ioBroker oder sonstigem Smart-Home System zum einen die Informationen des Wechselrichters, aber auch die Informationen des Smart-Meters abfragen. Extra ein zweites Smart-Meter zu installieren macht keinen Sinn.


# Die aktuellen Growatt Wechselrichter haben alle eine Modbus Schnittstelle. Deren Register sind hinreichend bekannt, so dass man diese Werte super abfragen kann.

# Was aber nicht bekannt ist, dass man über diese Schnittstelle auch die Werte des angeschlossenen Smart-Meter abrufen kann.


# Dies erfolgt über den (meiner Meinung nach nicht offiziellen) Funktions-Code 0x20 auf der Modbus Schnittstelle.


# Das heißt, man senden dem Wechselrichter den folgenden Request:

# 01 20 00 00 00 64 81 E6


# und erhält einen Response mit 200 Byte Nutzdaten, welche den Werten des Smart-Meters entspricht.

# Dabei sind immer zwei Register (also 4 Byte) ein Wert, wodurch in Summe 50 Werte übermittelt werden. Diese konnte ich inzwischen fast vollständig zuordnen. Die Beispiele in der Tabelle entsprechen meinen ausgelesenen Werten.
# inzwischen fast vollständig zuordnen. Die Beispiele in der Tabelle entsprechen meinen ausgelesenen Werten.

# Zu den Punkten 96, 100 und 104 das müssten die Summen aus L1+L2 , L2+L3 und L3+L1 sein (V).


# Offset (in Byte)	Wert	Beispiel	Übersetzung
# 00	Unbekannt	134	?
# 04	Spannung L1	2347	234,7 V
# 08	Spannung L2	2342	234,2 V
# 12	Spannung L3	2331	233,1 V
# 16	Strom L1	22	2,2 A
# 20	Strom L2	9	0,9 A
# 24	Strom L3	26	2,6 A
# 28	Wirkleistung L1	4142	414,2 W
# 32	Wirkleistung L2	1570	157,0 W
# 36	Wirkleistung L3	5203	520,3 W
# 40	Scheinleistung L1	5385	538,5 VA
# 44	Scheinleistung L2	2289	228,9 VA
# 48	Scheinleistung L3	6000	600,0 VA
# 52	Blindleistung L1	62792	-271,2 VAr
# 56	Blindleistung L2	64104	-143,2 VAr
# 60	Blindleistung L3	62959	-410,7 VAr
# 64	Leistungsfaktor L1	771	0,771
# 68	Leistungsfaktor L2	684	0,684
# 72	Leistungsfaktor L3	910	0,910
# 76	Summe Wirkleistung	10915	1091,5 W
# 80	Summe Scheinleistung	13674	1367,4 VA
# 84	Summe Blindleistung	58760	5876,0 VAr
# 88	Summe Leistungsfaktor	773	0,773
# 92	Frequenz	499	49,9 Hz
# 96	L1+L2 	4061	406.1 V (aus L1+L2 , L2+L3 und L3+L1 sein (V).)
# 100	L2+L3	4047	407.1 V
# 104	L3+L1	4051	405.1 V
# 108	Wirkleistung importiert	1561	156,1 kWh
# 112	Wirkleistung exportiert	50	5,0 kWh
# 116	Blindleistung importiert	63	6,3 kVAr
# 120	Blindleistung exportiert	754	75,4 kVAr
# 124	Unbekannt	1806	?
# 128	Zählerstand Wirkleistung	1611	161,1 kWh
# 132	Zählerstand Blindleistung	81,7	kVAr
# 136..199	0	0	0

class SPH_TL3_BH_UP_Meter(SDM630):

    def __init__(self, *args, **kwargs):
        self.model = "SPH_TL3_BH_UP_Meter"
        self.baud = 9600
        self.client.register(CustomModbusResponse)

        super().__init__(*args, **kwargs)
        # self.registers = SDM630.registers

        self.registers = {
            "l1_voltage": (4, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L1 Voltage", "V", 1, 0.1),
            "l2_voltage": (8, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L2 Voltage", "V", 1, 0.1),
            "l3_voltage": (12, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L3 Voltage", "V", 1, 0.1),
            "l1_current": (16, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L1 Current", "A", 1, 0.1),
            "l2_current": (20, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L2 Current", "A", 1, 0.1),
            "l3_current": (24, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L3 Current", "A", 1, 0.1),
            "l1_power_active": (28, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L1 Power (Active)", "W", 1, 0.1),
            "l2_power_active": (32, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L2 Power (Active)", "W", 1, 0.1),
            "l3_power_active": (36, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L3 Power (Active)", "W", 1, 0.1),
            "l1_power_apparent": (40, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L1 Power (Apparent)", "VA", 1, 0.1),
            "l2_power_apparent": (44, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L2 Power (Apparent)", "VA", 1, 0.1),
            "l3_power_apparent": (48, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L3 Power (Apparent)", "VA", 1, 0.1),
            "l1_power_reactive": (52, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L1 Power (Reactive)", "VAr", 1, 0.1),
            "l2_power_reactive": (56, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L2 Power (Reactive)", "VAr", 1, 0.1),
            "l3_power_reactive": (60, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L3 Power (Reactive)", "VAr", 1, 0.1),
            "l1_power_factor": (64, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L1 Power Factor", "", 1, 0.1),
            "l2_power_factor": (68, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L2 Power Factor", "", 1, 0.1),
            "l3_power_factor": (72, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L3 Power Factor", "", 1, 0.1),
            # "l1_phase_angle": (0x0024, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L1 Phase Angle", "°", 1, 1),
            # "l2_phase_angle": (0x0026, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L2 Phase Angle", "°", 1, 1),
            # "l3_phase_angle": (0x0028, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L3 Phase Angle", "°", 1, 1),
            # "voltage_ln": (0x002a, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L-N Voltage", "V", 1, 1),
            # "current_ln": (0x002e, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L-N Current", "A", 1, 1),
            # "total_line_current": (0x0030, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Total Line Current", "A", 1, 1),
            "total_power_active": (76, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "Total Power (Active)", "W", 1, 0.1),
            "total_power_apparent": (80, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "Total Power (Apparent)", "VA", 1, 0.1),
            "total_power_reactive": (84, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "Total Power (Reactive)", "VAr", 1, 0.1),
            "total_power_factor": (88, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "Total Power Factor", "", 1, 0.1),
            # "total_phase_angle": (0x0042, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Total Phase Angle", "°", 1, 1),
            "frequency": (92, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "Frequency", "Hz", 1, 0.1),
            "l12_voltage": (96, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L1-L2 Voltage", "V", 3, 0.1),
            "l23_voltage": (100, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L2-L3 Voltage", "V", 3, 0.1),
            "l31_voltage": (104, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "L3-L1 Voltage", "V", 3, 0.1),

            "import_energy_active": (108, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "Imported Energy (Active)", "kWh", 1, 0.1),
            "export_energy_active": (112, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "Exported Energy (Active)", "kWh", 1, 0.1),
            "import_energy_reactive": (116, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "Imported Energy (Reactive)", "kVArh", 1, 0.1),
            "export_energy_reactive": (120, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "Exported Energy (Reactive)", "kVArh", 1, 0.1),
            "total_energy_apparent": (124, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "Total Energy (Apparent)", "kVAh", 2, 0.1),
            # "total_current": (0x0052, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Total Current", "A", 2, 1),
            # "total_import_demand_power_active": (0x0054, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Total Import Demand Power (Active)", "W", 2, 1),
            # "maximum_import_demand_power_apparent": (0x0056, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Maximum Import Demand Power (Apparent)", "VA", 2, 1),
            # "import_demand_power_active": (0x0058, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Import Demand Power (Active)", "W", 2, 1),
            # "maximum_import_demand_power_active": (0x005a, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Maximum Import Demand Power (Active)", "W", 2, 1),
            # "export_demand_power_active": (0x005c, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Export Demand Power (Active)", "W", 2, 1),
            # "maximum_export_demand_power_active": (0x005e, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Maximum Export Demand Power (Active)", "W", 2, 1),
            # "total_demand_power_apparent": (0x0064, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Total Demand Power (Apparent)", "VA", 2, 1),
            # "maximum_demand_power_apparent": (0x0066, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Maximum System Power (Apparent)", "VA", 2, 1),
            # "neutral_demand_current": (0x0068, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Neutral Demand Current", "A", 2, 1),
            # "maximum_neutral_demand_current": (0x006a, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Maximum Neutral Demand Current", "A", 2, 1),
            # "voltage_ll": (0x00ce, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L-L Voltage", "V", 3, 1),
            # "neutral_current": (0x00e0, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Neutral Current", "A", 3, 1),
            # "l1n_voltage_thd": (0x00ea, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L1-N Voltage THD", "%", 3, 1),
            # "l2n_voltage_thd": (0x00ec, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L2-N Voltage THD", "%", 3, 1),
            # "l3n_voltage_thd": (0x00ee, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L3-N Voltage THD", "%", 3, 1),
            # "l1_current_thd": (0x00f0, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L1 Current THD", "%", 3, 1),
            # "l2_current_thd": (0x00f2, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L2 Current THD", "%", 3, 1),
            # "l3_current_thd": (0x00f4, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L3 Current THD", "%", 3, 1),
            # "voltage_ln_thd": (0x00f8, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L-N Voltage THD", "%", 3, 1),
            # "current_thd": (0x00fa, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Current THD", "%", 3, 1),
            # "total_pf": (0x00fe, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Total Power Factor", "", 3, 1),
            # "l1_demand_current": (0x0102, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L1 Demand Current", "A", 3, 1),
            # "l2_demand_current": (0x0104, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L2 Demand Current", "A", 3, 1),
            # "l3_demand_current": (0x0106, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L3 Demand Current", "A", 3, 1),
            # "maximum_l1_demand_current": (0x0108, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Maximum L1 Demand Current", "A", 3, 1),
            # "maximum_l2_demand_current": (0x010a, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Maximum L2 Demand Current", "A", 3, 1),
            # "maximum_l3_demand_current": (0x010c, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "Maximum L3 Demand Current", "A", 3, 1),
            # "l12_voltage_thd": (0x014e, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L1-L2 Voltage THD", "%", 4, 1),
            # "l23_voltage_thd": (0x0150, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L2-L3 Voltage THD", "%", 4, 1),
            # "l31_voltage_thd": (0x0152, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L3-L1 Voltage THD", "%", 4, 1),
            # "voltage_ll_thd": (0x0154, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L-L Voltage THD", "%", 4, 1),
            "total_energy_active": (128, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "Total Energy (Active)", "kWh", 4, 0.1),
            "total_energy_reactive": (132, 4, meter.registerType.INPUT, meter.registerDataType.INT32, float, "Total Energy (Reactive)", "kVArh", 4, 0.1),
            # "l1_import_energy_active": (0x015a, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L1 Import Energy (Active)", "kWh", 4, 1),
            # "l2_import_energy_active": (0x015c, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L2 Import Energy (Active)", "kWh", 4, 1),
            # "l3_import_energy_active": (0x015e, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L3 Import Energy (Active)", "kWh", 4, 1),
            # "l1_export_energy_active": (0x0160, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L1 Export Energy (Active)", "kWh", 4, 1),
            # "l2_export_energy_active": (0x0162, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L2 Export Energy (Active)", "kWh", 4, 1),
            # "l3_export_energy_active": (0x0164, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L3 Export Energy (Active)", "kWh", 4, 1),
            # "l1_energy_active": (0x0166, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L1 Total Energy (Active)", "kWh", 4, 1),
            # "l2_energy_active": (0x0168, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L2 Total Energy (Active)", "kWh", 4, 1),
            # "l3_energy_active": (0x016a, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L3 Total Energy (Active)", "kWh", 4, 1),
            # "l1_import_energy_reactive": (0x016c, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L1 Import Energy (Reactive)", "kVArh", 4, 1),
            # "l2_import_energy_reactive": (0x016e, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L2 Import Energy (Reactive)", "kVArh", 4, 1),
            # "l3_import_energy_reactive": (0x0170, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L3 Import Energy (Reactive)", "kVArh", 4, 1),
            # "l1_export_energy_reactive": (0x0172, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L1 Export Energy (Reactive)", "kVArh", 4, 1),
            # "l2_export_energy_reactive": (0x0174, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L2 Export Energy (Reactive)", "kVArh", 4, 1),
            # "l3_export_energy_reactive": (0x0176, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L3 Export Energy (Reactive)", "kVArh", 4, 1),
            # "l1_energy_reactive": (0x0178, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L1 Total Energy (Reactive)", "kVArh", 4, 1),
            # "l2_energy_reactive": (0x017a, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L2 Total Energy (Reactive)", "kVArh", 4, 1),
            # "l3_energy_reactive": (0x017c, 2, meter.registerType.INPUT, meter.registerDataType.FLOAT32, float, "L3 Total Energy (Reactive)", "kVArh", 4, 1),

        }

    def read_all(self, rtype=meter.registerType.INPUT, scaling=False):

        # new modbus function code.


        results = {}
        addr_min = False
        addr_max = False
        for k, v in self.registers.items():
            v_addr = v[0]
            v_length = v[1]

            if addr_min is False:
                addr_min = v_addr
            if addr_max is False:
                addr_max = v_addr + v_length

            if v_addr < addr_min:
                addr_min = v_addr
            if (v_addr + v_length) > addr_max:
                addr_max = v_addr + v_length

        results = {}
        offset = addr_min
        length = addr_max - addr_min

        request = CustomModbusRequest(0, slave=self.unit)
        result = self.client.execute(request)
        
        if not isinstance(result, CustomModbusResponse):
            return {}
        if len(result.registers) != 200:
            return {}

        data = BinaryPayloadDecoder.fromRegisters(
            result.registers, byteorder=self.byteorder, wordorder=self.wordorder)

        for k, v in self.registers.items():
            address, length, rtype, dtype, vtype, label, fmt, batch, sf = v

            if address > offset:
                skip_bytes = address - offset
                offset += skip_bytes
                data.skip_bytes(skip_bytes * 2)

            results[k] = self._decode_value(data, length, dtype, vtype)
            offset += length

        # registers = {k: v for k, v in self.registers.items() if (v[2] == rtype)}

        if scaling:
            return {k: v * self.get_scaling(k) for k, v in results.items()}
        else:
            return {k: v for k, v in results.items()}

        # builder = BinaryPayloadBuilder(
