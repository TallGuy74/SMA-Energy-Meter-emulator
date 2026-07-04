# 1.0.0-pp3

* Default MQTT topic base is now `sma/emeter2.0` (full message topic
  `sma/emeter2.0/<id>/state`), staying inside the `sma/` namespace while
  remaining distinct from the original add-on's `sma/emeter`.
* Serial extraction is now depth-independent (second-to-last topic segment);
  it was a hardcoded segment index that silently misparsed serials for topic
  bases with more or fewer than two segments.

# 1.0.0-pp2

* Default MQTT topic changed to `sma2/emeter` and exposed as the `sma_mqtt_topic` add-on
  option. With the upstream default (`sma/emeter`) the fork also picked up the original
  add-on's serial-1 messages and both add-ons emulated the same meter simultaneously —
  double datagrams to the inverter.

# 1.0.0-pp1 (per-phase fork)

* Renamed add-on (`sma_perphase`) so it installs alongside the original.
* Complete per-phase support: optional v2 MQTT payload fields for per-phase active/reactive/
  apparent power & energy, current, voltage and power factor, plus totals companions and
  frequency. Absent fields transmit as 0 (bit-compatible with v1 payloads).
* Telegrams are built from one canonical channel table — every channel exactly once. This
  also fixes two latent upstream bugs: duplicate reactive-power OBIS entries in HomeWizard
  telegrams, and `SMA_VOLTAGE_L1` using OBIS index 50 (colliding with negative apparent
  power L2) instead of 32.
* `derive_missing` option (default on): derive apparent power (cos φ ≈ 1), per-phase current
  (S/V) and power factor when not provided.
* HomeWizard: per-phase power/voltage/current and frequency are now forwarded when the meter
  provides them.
* `host_network: true` so empty `destinationAddresses` multicasts to 239.12.255.254:9522 on
  the real LAN, exactly like a genuine Energy Meter (upstream's multicast never left the
  docker bridge).
* Dockerfile builds from the local `requirements.txt` instead of downloading upstream `main`.
* Added `tests/test_packet.py` — build → parse → verify, doubles as a reference decoder.

<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->

## 0.1.4

- patch for tripower inverters

## 0.1.3

- Extend package to support tripower inverters

## 0.1.0

- Add homewizard support
- Catch invalid json messages

## 0.0.10

- Updated docs.
- Confirmed functionality with Sunny Boy Smart Energy 5.0

## 0.0.9

- Change measurment units

## 0.0.8

- fix configuration

## 0.0.7

- Add configuration options

## 0.0.6

- bugfix setup mqtt

## 0.0.5

- Cleanup

## 0.0.4

- Changes docs

## 0.0.3

- fix dependencies

## 0.0.2

- version bump build test

## 0.0.1

- Initial release
