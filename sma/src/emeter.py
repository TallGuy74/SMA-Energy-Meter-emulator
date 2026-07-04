class emeterPacket:
    SMA_POSITIVE_ACTIVE_POWER = 0x00010400
    SMA_POSITIVE_ACTIVE_POWER_L1 = 0x00150400
    SMA_POSITIVE_ACTIVE_POWER_L2 = 0x00290400
    SMA_POSITIVE_ACTIVE_POWER_L3 = 0x003D0400
    SMA_POSITIVE_ACTIVE_ENERGY = 0x00010800
    SMA_POSITIVE_ACTIVE_ENERGY_L1 = 0x00150800
    SMA_POSITIVE_ACTIVE_ENERGY_L2 = 0x00290800
    SMA_POSITIVE_ACTIVE_ENERGY_L3 = 0x003D0800
    SMA_NEGATIVE_ACTIVE_POWER = 0x00020400
    SMA_NEGATIVE_ACTIVE_POWER_L1 = 0x00160400
    SMA_NEGATIVE_ACTIVE_POWER_L2 = 0x002A0400
    SMA_NEGATIVE_ACTIVE_POWER_L3 = 0x003E0400
    SMA_NEGATIVE_ACTIVE_ENERGY = 0x00020800
    SMA_NEGATIVE_ACTIVE_ENERGY_L1 = 0x00160800
    SMA_NEGATIVE_ACTIVE_ENERGY_L2 = 0x002A0800
    SMA_NEGATIVE_ACTIVE_ENERGY_L3 = 0x003E0800
    SMA_POSITIVE_REACTIVE_POWER = 0x00030400
    SMA_POSITIVE_REACTIVE_POWER_L1 = 0x00170400
    SMA_POSITIVE_REACTIVE_POWER_L2 = 0x002B0400
    SMA_POSITIVE_REACTIVE_POWER_L3 = 0x003F0400
    SMA_POSITIVE_REACTIVE_ENERGY = 0x00030800
    SMA_POSITIVE_REACTIVE_ENERGY_L1 = 0x00170800
    SMA_POSITIVE_REACTIVE_ENERGY_L2 = 0x002B0800
    SMA_POSITIVE_REACTIVE_ENERGY_L3 = 0x003F0800
    SMA_NEGATIVE_REACTIVE_POWER = 0x00040400
    SMA_NEGATIVE_REACTIVE_POWER_L1 = 0x00180400
    SMA_NEGATIVE_REACTIVE_POWER_L2 = 0x002C0400
    SMA_NEGATIVE_REACTIVE_POWER_L3 = 0x00400400
    SMA_NEGATIVE_REACTIVE_ENERGY = 0x00040800
    SMA_NEGATIVE_REACTIVE_ENERGY_L1 = 0x00180800
    SMA_NEGATIVE_REACTIVE_ENERGY_L2 = 0x002C0800
    SMA_NEGATIVE_REACTIVE_ENERGY_L3 = 0x00400800
    SMA_POSITIVE_APPARENT_POWER = 0x00090400
    SMA_POSITIVE_APPARENT_POWER_L1 = 0x001D0400
    SMA_POSITIVE_APPARENT_POWER_L2 = 0x00310400
    SMA_POSITIVE_APPARENT_POWER_L3 = 0x00450400
    SMA_POSITIVE_APPARENT_ENERGY = 0x00090800
    SMA_POSITIVE_APPARENT_ENERGY_L1 = 0x001D0800
    SMA_POSITIVE_APPARENT_ENERGY_L2 = 0x00310800
    SMA_POSITIVE_APPARENT_ENERGY_L3 = 0x00450800
    SMA_NEGATIVE_APPARENT_POWER = 0x000A0400
    SMA_NEGATIVE_APPARENT_POWER_L1 = 0x001E0400
    SMA_NEGATIVE_APPARENT_POWER_L2 = 0x00320400
    SMA_NEGATIVE_APPARENT_POWER_L3 = 0x00460400
    SMA_NEGATIVE_APPARENT_ENERGY = 0x000A0800
    SMA_NEGATIVE_APPARENT_ENERGY_L1 = 0x001E0800
    SMA_NEGATIVE_APPARENT_ENERGY_L2 = 0x00320800
    SMA_NEGATIVE_APPARENT_ENERGY_L3 = 0x00460800
    SMA_POWER_FACTOR = 0x000D0400
    SMA_POWER_FACTOR_L1 = 0x00210400
    SMA_POWER_FACTOR_L2 = 0x00350400
    SMA_POWER_FACTOR_L3 = 0x00490400
    SMA_CURRENT_L1 = 0x001F0400
    SMA_CURRENT_L2 = 0x00330400
    SMA_CURRENT_L3 = 0x00470400
    SMA_VOLTAGE_L1 = 0x00200400  # index 32 (1:32.4.0); upstream had 0x0032.. = index 50, colliding with SMA_NEGATIVE_APPARENT_POWER_L2
    SMA_VOLTAGE_L2 = 0x00340400
    SMA_VOLTAGE_L3 = 0x00480400
    SMA_VERSION = 0x90000000

    INITIAL_PAYLOAD_LENGTH = 12
    METER_PACKET_SIZE = 1000

    def __init__(self, serNo=0):
        self.meterPacket = bytearray(self.METER_PACKET_SIZE)
        self.initEmeterPacket(serNo)
        self.begin(0)
        self.end()

    def init(self, serNo):
        self.initEmeterPacket(serNo)

    def beginEmpty(self, timeStampMs):
        """Header + timestamp only; the caller emits the complete channel set (see build_packet)."""
        self._pPacketPos = self._headerLength
        self.storeU32BE(self._pMeterTime, timeStampMs)
        self._length = self.INITIAL_PAYLOAD_LENGTH

    def begin(self, timeStampMs):
        self.beginEmpty(timeStampMs)

        # Add dummy values for measurements to make sure the package always contains these. Solves tripower inverters not recognizing the data as valid.
        # Totals
        self.addMeasurementValue(emeterPacket.SMA_POSITIVE_REACTIVE_POWER, 0)
        self.addCounterValue(emeterPacket.SMA_POSITIVE_REACTIVE_ENERGY, 0)
        self.addMeasurementValue(emeterPacket.SMA_NEGATIVE_REACTIVE_POWER, 0)
        self.addCounterValue(emeterPacket.SMA_NEGATIVE_REACTIVE_ENERGY, 0)
        self.addMeasurementValue(emeterPacket.SMA_POSITIVE_APPARENT_POWER, 0)
        self.addCounterValue(emeterPacket.SMA_POSITIVE_APPARENT_ENERGY, 0)
        self.addMeasurementValue(emeterPacket.SMA_NEGATIVE_APPARENT_POWER, 0)
        self.addCounterValue(emeterPacket.SMA_NEGATIVE_APPARENT_ENERGY, 0)
        self.addMeasurementValue(emeterPacket.SMA_POWER_FACTOR, 0)

        #L1
        self.addMeasurementValue(emeterPacket.SMA_POSITIVE_ACTIVE_POWER_L1, 0)
        self.addCounterValue(emeterPacket.SMA_POSITIVE_ACTIVE_ENERGY_L1, 0)
        self.addMeasurementValue(emeterPacket.SMA_NEGATIVE_ACTIVE_POWER_L1, 0)
        self.addCounterValue(emeterPacket.SMA_NEGATIVE_ACTIVE_ENERGY_L1, 0)
        self.addMeasurementValue(emeterPacket.SMA_POSITIVE_REACTIVE_POWER_L1, 0)
        self.addCounterValue(emeterPacket.SMA_POSITIVE_REACTIVE_ENERGY_L1, 0)
        self.addMeasurementValue(emeterPacket.SMA_NEGATIVE_REACTIVE_POWER_L1, 0)
        self.addCounterValue(emeterPacket.SMA_NEGATIVE_REACTIVE_ENERGY_L1, 0)
        self.addMeasurementValue(emeterPacket.SMA_POSITIVE_APPARENT_POWER_L1, 0)
        self.addCounterValue(emeterPacket.SMA_POSITIVE_APPARENT_ENERGY_L1, 0)
        self.addMeasurementValue(emeterPacket.SMA_NEGATIVE_APPARENT_POWER_L1, 0)
        self.addCounterValue(emeterPacket.SMA_NEGATIVE_APPARENT_ENERGY_L1, 0)
        self.addMeasurementValue(emeterPacket.SMA_CURRENT_L1, 0)
        self.addMeasurementValue(emeterPacket.SMA_VOLTAGE_L1, 0)
        self.addMeasurementValue(emeterPacket.SMA_POWER_FACTOR_L1, 0) 

        #L2
        self.addMeasurementValue(emeterPacket.SMA_POSITIVE_ACTIVE_POWER_L2, 0)
        self.addCounterValue(emeterPacket.SMA_POSITIVE_ACTIVE_ENERGY_L2, 0)
        self.addMeasurementValue(emeterPacket.SMA_NEGATIVE_ACTIVE_POWER_L2, 0)
        self.addCounterValue(emeterPacket.SMA_NEGATIVE_ACTIVE_ENERGY_L2, 0)
        self.addMeasurementValue(emeterPacket.SMA_POSITIVE_REACTIVE_POWER_L2, 0)
        self.addCounterValue(emeterPacket.SMA_POSITIVE_REACTIVE_ENERGY_L2, 0)
        self.addMeasurementValue(emeterPacket.SMA_NEGATIVE_REACTIVE_POWER_L2, 0)
        self.addCounterValue(emeterPacket.SMA_NEGATIVE_REACTIVE_ENERGY_L2, 0)
        self.addMeasurementValue(emeterPacket.SMA_POSITIVE_APPARENT_POWER_L2, 0)
        self.addCounterValue(emeterPacket.SMA_POSITIVE_APPARENT_ENERGY_L2, 0)
        self.addMeasurementValue(emeterPacket.SMA_NEGATIVE_APPARENT_POWER_L2, 0)
        self.addCounterValue(emeterPacket.SMA_NEGATIVE_APPARENT_ENERGY_L2, 0)
        self.addMeasurementValue(emeterPacket.SMA_CURRENT_L2, 0)
        self.addMeasurementValue(emeterPacket.SMA_VOLTAGE_L2, 0)
        self.addMeasurementValue(emeterPacket.SMA_POWER_FACTOR_L2, 0)

        #L3
        self.addMeasurementValue(emeterPacket.SMA_POSITIVE_ACTIVE_POWER_L3, 0)
        self.addCounterValue(emeterPacket.SMA_POSITIVE_ACTIVE_ENERGY_L3, 0)
        self.addMeasurementValue(emeterPacket.SMA_NEGATIVE_ACTIVE_POWER_L3, 0)
        self.addCounterValue(emeterPacket.SMA_NEGATIVE_ACTIVE_ENERGY_L3, 0)
        self.addMeasurementValue(emeterPacket.SMA_POSITIVE_REACTIVE_POWER_L3, 0)
        self.addCounterValue(emeterPacket.SMA_POSITIVE_REACTIVE_ENERGY_L3, 0)
        self.addMeasurementValue(emeterPacket.SMA_NEGATIVE_REACTIVE_POWER_L3, 0)
        self.addCounterValue(emeterPacket.SMA_NEGATIVE_REACTIVE_ENERGY_L3, 0)
        self.addMeasurementValue(emeterPacket.SMA_POSITIVE_APPARENT_POWER_L3, 0)
        self.addCounterValue(emeterPacket.SMA_POSITIVE_APPARENT_ENERGY_L3, 0)
        self.addMeasurementValue(emeterPacket.SMA_NEGATIVE_APPARENT_POWER_L3, 0)
        self.addCounterValue(emeterPacket.SMA_NEGATIVE_APPARENT_ENERGY_L3, 0)
        self.addMeasurementValue(emeterPacket.SMA_CURRENT_L3, 0)
        self.addMeasurementValue(emeterPacket.SMA_VOLTAGE_L3, 0)
        self.addMeasurementValue(emeterPacket.SMA_POWER_FACTOR_L3, 0)

    def addMeasurementValue(self, id, value):
        self._pPacketPos = self.storeU32BE(self._pPacketPos, id)
        self._pPacketPos = self.storeU32BE(self._pPacketPos, value)
        self._length += 8

    def addCounterValue(self, id, value):
        self._pPacketPos = self.storeU32BE(self._pPacketPos, id)
        self._pPacketPos = self.storeU64BE(self._pPacketPos, value)
        self._length += 12

    def end(self):
        self._pPacketPos = self.storeU32BE(self._pPacketPos, self.SMA_VERSION)
        self._pPacketPos = self.storeU32BE(self._pPacketPos, 0x01020452)
        self._length += 8

        self.storeU16BE(self._pDataSize, self._length)
        self.storeU32BE(self._pPacketPos, 0)
        self._length += 4

        self._length = self._headerLength + self._length - self.INITIAL_PAYLOAD_LENGTH
        return self._length

    def getData(self):
        return self.meterPacket

    def getLength(self):
        return self._length

    def storeU16BE(self, pPos, value):
        self.meterPacket[pPos] = (value >> 8) & 0xFF
        self.meterPacket[pPos + 1] = value & 0xFF
        return pPos + 2

    def storeU32BE(self, pPos, value):
        pPos = self.storeU16BE(pPos, (value >> 16) & 0xFFFF)
        return self.storeU16BE(pPos, value & 0xFFFF)

    def storeU64BE(self, pPos, value):
        pPos = self.storeU32BE(pPos, (value >> 32) & 0xFFFFFFFF)
        return self.storeU32BE(pPos, value & 0xFFFFFFFF)

    def offsetOf(self, pData, identifier, size):
        for i in range(size):
            if pData[i] == identifier:
                return i
        return None

    def initEmeterPacket(self, serNo):
        WLEN = 0xfa
        DSRC = 0xfb
        DTIM = 0xfc

        SMA_METER_HEADER = bytearray([
            ord('S'), ord('M'), ord('A'), 0,
            0x00, 0x04, 0x02, 0xa0, 0x00, 0x00, 0x00, 0x01,
            WLEN, WLEN, 0x00, 0x10, 0x60, 0x69,
            0x01, 0x0e, DSRC, DSRC, DSRC, DSRC,
            DTIM, DTIM, DTIM, DTIM
        ])

        self._headerLength = len(SMA_METER_HEADER)
        self.meterPacket[:self._headerLength] = SMA_METER_HEADER

        self._pDataSize = self.offsetOf(self.meterPacket, WLEN, self._headerLength)
        self._pMeterTime = self.offsetOf(self.meterPacket, DTIM, self._headerLength)

        pSerNo = self.offsetOf(self.meterPacket, DSRC, self._headerLength)
        self.storeU32BE(pSerNo, serNo)



    # ------------------------------------------------------------------------------------------------
    # Canonical channel table: the complete channel set of a real SMA Energy Meter, in a fixed order
    # (the dummy-block order of begin(), with the active totals at the end, matching the historical
    # wire layout). buildFrom() emits every channel exactly once - absent values become 0. This kills
    # the duplicate-OBIS hazard of the old begin()-dummies-then-append pattern for good.
    # kind: m = 4-byte measurement, c = 8-byte counter. key: payload field that fills the channel.
    # scale: payload unit -> wire unit (power W -> 0.1 W, energy kWh -> Ws, current A -> mA,
    # voltage V -> mV, cos-phi -> 1/1000, frequency Hz -> mHz).
    # ------------------------------------------------------------------------------------------------
    SMA_FREQUENCY = 0x000E0400          # index 14 (net frequency, EM 2.0+); emitted only when provided

CHANNELS = [
    ('m', emeterPacket.SMA_POSITIVE_REACTIVE_POWER,  'reactivePowerIn',   10),
    ('c', emeterPacket.SMA_POSITIVE_REACTIVE_ENERGY, 'reactiveEnergyIn',  3600000),
    ('m', emeterPacket.SMA_NEGATIVE_REACTIVE_POWER,  'reactivePowerOut',  10),
    ('c', emeterPacket.SMA_NEGATIVE_REACTIVE_ENERGY, 'reactiveEnergyOut', 3600000),
    ('m', emeterPacket.SMA_POSITIVE_APPARENT_POWER,  'apparentPowerIn',   10),
    ('c', emeterPacket.SMA_POSITIVE_APPARENT_ENERGY, 'apparentEnergyIn',  3600000),
    ('m', emeterPacket.SMA_NEGATIVE_APPARENT_POWER,  'apparentPowerOut',  10),
    ('c', emeterPacket.SMA_NEGATIVE_APPARENT_ENERGY, 'apparentEnergyOut', 3600000),
    ('m', emeterPacket.SMA_POWER_FACTOR,             'powerFactor',       1000),
]
for _x, _pap, _pae, _nap, _nae, _prp, _pre, _nrp, _nre, _papp, _pape, _napp, _nape, _cur, _volt, _pf in [
    (1, emeterPacket.SMA_POSITIVE_ACTIVE_POWER_L1, emeterPacket.SMA_POSITIVE_ACTIVE_ENERGY_L1,
        emeterPacket.SMA_NEGATIVE_ACTIVE_POWER_L1, emeterPacket.SMA_NEGATIVE_ACTIVE_ENERGY_L1,
        emeterPacket.SMA_POSITIVE_REACTIVE_POWER_L1, emeterPacket.SMA_POSITIVE_REACTIVE_ENERGY_L1,
        emeterPacket.SMA_NEGATIVE_REACTIVE_POWER_L1, emeterPacket.SMA_NEGATIVE_REACTIVE_ENERGY_L1,
        emeterPacket.SMA_POSITIVE_APPARENT_POWER_L1, emeterPacket.SMA_POSITIVE_APPARENT_ENERGY_L1,
        emeterPacket.SMA_NEGATIVE_APPARENT_POWER_L1, emeterPacket.SMA_NEGATIVE_APPARENT_ENERGY_L1,
        emeterPacket.SMA_CURRENT_L1, emeterPacket.SMA_VOLTAGE_L1, emeterPacket.SMA_POWER_FACTOR_L1),
    (2, emeterPacket.SMA_POSITIVE_ACTIVE_POWER_L2, emeterPacket.SMA_POSITIVE_ACTIVE_ENERGY_L2,
        emeterPacket.SMA_NEGATIVE_ACTIVE_POWER_L2, emeterPacket.SMA_NEGATIVE_ACTIVE_ENERGY_L2,
        emeterPacket.SMA_POSITIVE_REACTIVE_POWER_L2, emeterPacket.SMA_POSITIVE_REACTIVE_ENERGY_L2,
        emeterPacket.SMA_NEGATIVE_REACTIVE_POWER_L2, emeterPacket.SMA_NEGATIVE_REACTIVE_ENERGY_L2,
        emeterPacket.SMA_POSITIVE_APPARENT_POWER_L2, emeterPacket.SMA_POSITIVE_APPARENT_ENERGY_L2,
        emeterPacket.SMA_NEGATIVE_APPARENT_POWER_L2, emeterPacket.SMA_NEGATIVE_APPARENT_ENERGY_L2,
        emeterPacket.SMA_CURRENT_L2, emeterPacket.SMA_VOLTAGE_L2, emeterPacket.SMA_POWER_FACTOR_L2),
    (3, emeterPacket.SMA_POSITIVE_ACTIVE_POWER_L3, emeterPacket.SMA_POSITIVE_ACTIVE_ENERGY_L3,
        emeterPacket.SMA_NEGATIVE_ACTIVE_POWER_L3, emeterPacket.SMA_NEGATIVE_ACTIVE_ENERGY_L3,
        emeterPacket.SMA_POSITIVE_REACTIVE_POWER_L3, emeterPacket.SMA_POSITIVE_REACTIVE_ENERGY_L3,
        emeterPacket.SMA_NEGATIVE_REACTIVE_POWER_L3, emeterPacket.SMA_NEGATIVE_REACTIVE_ENERGY_L3,
        emeterPacket.SMA_POSITIVE_APPARENT_POWER_L3, emeterPacket.SMA_POSITIVE_APPARENT_ENERGY_L3,
        emeterPacket.SMA_NEGATIVE_APPARENT_POWER_L3, emeterPacket.SMA_NEGATIVE_APPARENT_ENERGY_L3,
        emeterPacket.SMA_CURRENT_L3, emeterPacket.SMA_VOLTAGE_L3, emeterPacket.SMA_POWER_FACTOR_L3),
]:
    CHANNELS += [
        ('m', _pap,  f'powerInL{_x}',           10),
        ('c', _pae,  f'energyInL{_x}',          3600000),
        ('m', _nap,  f'powerOutL{_x}',          10),
        ('c', _nae,  f'energyOutL{_x}',         3600000),
        ('m', _prp,  f'reactivePowerInL{_x}',   10),
        ('c', _pre,  f'reactiveEnergyInL{_x}',  3600000),
        ('m', _nrp,  f'reactivePowerOutL{_x}',  10),
        ('c', _nre,  f'reactiveEnergyOutL{_x}', 3600000),
        ('m', _papp, f'apparentPowerInL{_x}',   10),
        ('c', _pape, f'apparentEnergyInL{_x}',  3600000),
        ('m', _napp, f'apparentPowerOutL{_x}',  10),
        ('c', _nape, f'apparentEnergyOutL{_x}', 3600000),
        ('m', _cur,  f'currentL{_x}',           1000),
        ('m', _volt, f'voltageL{_x}',           1000),
        ('m', _pf,   f'powerFactorL{_x}',       1000),
    ]
CHANNELS += [                                              # active totals last, matching the historical wire layout
    ('m', emeterPacket.SMA_POSITIVE_ACTIVE_POWER,  'powerIn',   10),
    ('c', emeterPacket.SMA_POSITIVE_ACTIVE_ENERGY, 'energyIn',  3600000),
    ('m', emeterPacket.SMA_NEGATIVE_ACTIVE_POWER,  'powerOut',  10),
    ('c', emeterPacket.SMA_NEGATIVE_ACTIVE_ENERGY, 'energyOut', 3600000),
]


def payload_to_values(data, derive=True):
    """Map an MQTT payload (v1 or v2 keys) to {payload_key: float}, optionally deriving missing
    values that follow from the provided ones: apparent power from active power (cos-phi ~ 1),
    current from apparent power / voltage (beats DSMR's whole-ampere rounding), power factor 1.0
    when active power is known but reactive is not. Only ever derives from keys the sender
    actually provided - absent stays absent (emitted as 0 by buildFrom)."""
    v = {k: float(data[k]) for k, _ in [(key, None) for _, _, key, _ in CHANNELS] if k in data}
    if 'frequency' in data:
        v['frequency'] = float(data['frequency'])

    if not derive:
        return v

    def d(key, val):                                       # derive only when the sender did not provide it
        if key not in v:
            v[key] = val

    scopes = [''] + [f'L{x}' for x in (1, 2, 3)]
    for sc in scopes:
        pin, pout = v.get(f'powerIn{sc}'), v.get(f'powerOut{sc}')
        if pin is not None:  d(f'apparentPowerIn{sc}',  pin)     # cos-phi ~ 1 assumption, documented
        if pout is not None: d(f'apparentPowerOut{sc}', pout)
        if pin is not None or pout is not None:
            d(f'powerFactor{sc}', 1.0)
        if sc:                                                    # per-phase current from S / V
            volt = v.get(f'voltage{sc}')
            if volt and f'current{sc}' not in v:
                s_tot = v.get(f'apparentPowerIn{sc}', 0.0) + v.get(f'apparentPowerOut{sc}', 0.0)
                if s_tot > 0:
                    v[f'current{sc}'] = s_tot / volt
    return v


def build_packet(serial_number, time_stamp_ms, values):
    """One canonical telegram: every CHANNELS entry exactly once (0 when absent), frequency
    appended only when provided (EM 2.0-only channel; a hardcoded 0 Hz would be nonsense)."""
    packet = emeterPacket(int(serial_number))
    packet.beginEmpty(time_stamp_ms)
    for kind, cid, key, scale in CHANNELS:
        raw = round(values.get(key, 0.0) * scale)
        if kind == 'm':
            packet.addMeasurementValue(cid, max(0, raw))
        else:
            packet.addCounterValue(cid, max(0, raw))
    if 'frequency' in values:
        packet.addMeasurementValue(emeterPacket.SMA_FREQUENCY, max(0, round(values['frequency'] * 1000)))
    packet.end()
    return packet
