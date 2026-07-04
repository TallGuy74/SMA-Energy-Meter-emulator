#!/usr/bin/env python3
"""Build -> parse -> verify tests for the per-phase telegram builder.
Plain python3, no dependencies:  python3 tests/test_packet.py
The parser here is deliberately independent of the builder (reads the SMA
energy-meter protocol per EMETER-Protocol-TI): it doubles as a reference
decoder for validating datagrams on the wire."""
import struct, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sma', 'src'))
from emeter import emeterPacket, CHANNELS, payload_to_values, build_packet


def parse(pkt):
    """Return (susy, serial, {obis_id: value}) from a Speedwire emeter telegram."""
    assert pkt[:4] == b'SMA\x00', "missing SMA header"
    susy, serial = struct.unpack(">HI", pkt[18:24])
    pos, vals = 28, {}
    while pos + 4 <= len(pkt):
        (cid,) = struct.unpack(">I", pkt[pos:pos + 4]); pos += 4
        if cid == 0:
            break
        kind = (cid >> 8) & 0xFF
        if cid == 0x90000000:                       # software version pseudo-channel
            (v,) = struct.unpack(">I", pkt[pos:pos + 4]); pos += 4
        elif kind == 8:
            (v,) = struct.unpack(">Q", pkt[pos:pos + 8]); pos += 8
        else:
            (v,) = struct.unpack(">I", pkt[pos:pos + 4]); pos += 4
        assert cid not in vals, f"DUPLICATE OBIS id 0x{cid:08X}"
        vals[cid] = v
    return susy, serial, vals


def build(payload, derive=True, serial=902):
    p = build_packet(serial, 123456, payload_to_values(payload, derive=derive))
    return p.getData()[:p.getLength()]


def test_v1_payload():
    """v1 totals-only payload: full canonical channel set, phases zero, totals scaled."""
    pkt = build({"powerIn": 253.0, "powerOut": 0.0, "energyIn": 5000.603, "energyOut": 2000.707}, derive=False)
    susy, serial, vals = parse(pkt)
    assert (susy, serial) == (270, 902)
    assert len(vals) == len(CHANNELS) + 1               # + software version from end()
    assert vals[emeterPacket.SMA_POSITIVE_ACTIVE_POWER] == 2530          # 0.1 W units
    assert vals[emeterPacket.SMA_POSITIVE_ACTIVE_ENERGY] == round(5000.603 * 3600000)
    assert vals[emeterPacket.SMA_POSITIVE_ACTIVE_POWER_L2] == 0          # phases untouched
    assert emeterPacket.SMA_FREQUENCY not in vals                        # only when provided
    print("v1 payload: OK (%d channels, no duplicates)" % len(vals))


def test_v2_phases_and_scaling():
    pkt = build({
        "powerIn": 253.0, "powerOut": 259.0, "energyIn": 1.0, "energyOut": 2.0,
        "powerInL1": 0.0,   "powerOutL1": 205.0, "voltageL1": 234.0,
        "powerInL2": 253.0, "powerOutL2": 0.0,   "voltageL2": 233.5, "currentL2": 1.1,
        "powerInL3": 0.0,   "powerOutL3": 54.0,  "voltageL3": 234.8,
        "frequency": 49.98,
    })
    _, _, vals = parse(pkt)
    assert vals[emeterPacket.SMA_NEGATIVE_ACTIVE_POWER_L1] == 2050       # 205 W -> 0.1 W
    assert vals[emeterPacket.SMA_VOLTAGE_L1] == 234000                   # 234 V -> mV, on the FIXED id
    assert emeterPacket.SMA_VOLTAGE_L1 == 0x00200400
    assert vals[emeterPacket.SMA_NEGATIVE_APPARENT_POWER_L2] == 0        # 0x00320400 belongs to THIS channel only
    assert vals[emeterPacket.SMA_CURRENT_L2] == 1100                     # provided current wins over derivation
    assert vals[emeterPacket.SMA_CURRENT_L1] == round(205.0 / 234.0 * 1000)   # derived: S/V in mA
    assert vals[emeterPacket.SMA_POSITIVE_APPARENT_POWER_L2] == 2530     # derived apparent = active (cos-phi ~ 1)
    assert vals[emeterPacket.SMA_POWER_FACTOR_L1] == 1000                # derived cos-phi 1.000
    assert vals[emeterPacket.SMA_FREQUENCY] == 49980                     # Hz -> mHz, present because provided
    print("v2 phases + scaling + derivation: OK")


def test_derive_off():
    pkt = build({"powerIn": 100.0, "powerOut": 0, "energyIn": 0, "energyOut": 0,
                 "powerInL1": 100.0, "voltageL1": 230.0}, derive=False)
    _, _, vals = parse(pkt)
    assert vals[emeterPacket.SMA_CURRENT_L1] == 0                        # no derivation
    assert vals[emeterPacket.SMA_POSITIVE_APPARENT_POWER] == 0
    print("derive_missing=false: OK")


if __name__ == "__main__":
    test_v1_payload()
    test_v2_phases_and_scaling()
    test_derive_off()
    print("ALL TESTS PASS")
