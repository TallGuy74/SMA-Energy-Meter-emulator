# SMA Energy Meter emulator

This home assistant add-on can emulate the existence of one or more SMA Energy Meters on the local network. This makes it possible to use the data from other meter types and integrate them with your SMA inverter.

# features

* Emulate meter based on mqtt messages
* Auto discover HomeWizard meters and emulate meters based on there measurements.

# Configuration

## How to use MQTT

If you have a mqtt broker configured in home assistant you do not need to configure anything. Otherwise fill in the mqtt configuration in the configuration tab.

The add-on will subscribe to the following mqtt topic: `sma/emeter/<NUMERIC_METER_ID>/state`. When receiving the first message the emulator wil start the emulation of the energy meter with the provided <NUMERIC_METER_ID>. The emulator wil send a udp packet every 1000ms. The content of the packet wil stay the same until it gets updated by the next mqtt message.

```json
{
  "powerIn": 125.5, // power consumption in W
  "powerOut": 80.3, // power production in W
  "energyIn": 5000.603, // consumed energy in kWh
  "energyOut": 2000.707, // produced energy in Kwh
  "destinationAddresses": [
    "192.168.1.34" // ip-address(es) to send the packets to. Leave empty to multicast to 239.12.255.254:9522 like a real Energy Meter (this fork runs with host_network, so multicast reaches the LAN).
  ]
}
```

## Per-phase values (v2 payload, this fork)

Every field below is optional and backward compatible: telegrams always contain the complete
channel set of a real SMA Energy Meter, and any field you do not send is transmitted as 0 —
exactly what the original add-on sent for the phase channels. Fields per phase `x` in 1..3:

| field | unit | SMA channel |
|---|---|---|
| `powerInLx` / `powerOutLx` | W | active power + / − (1:21/22, 41/42, 61/62) |
| `energyInLx` / `energyOutLx` | kWh | active energy counters |
| `reactivePowerInLx` / `reactivePowerOutLx` | var | reactive power |
| `reactiveEnergyInLx` / `reactiveEnergyOutLx` | kvarh | reactive energy |
| `apparentPowerInLx` / `apparentPowerOutLx` | VA | apparent power |
| `apparentEnergyInLx` / `apparentEnergyOutLx` | kVAh | apparent energy |
| `currentLx` | A | phase current (1:31/51/71) |
| `voltageLx` | V | phase voltage (1:32/52/72) |
| `powerFactorLx` | cos φ | phase power factor |

Totals gain the same optional companions: `reactivePowerIn/Out`, `reactiveEnergyIn/Out`,
`apparentPowerIn/Out`, `apparentEnergyIn/Out`, `powerFactor`, and `frequency` (Hz — emitted
only when provided; it is an Energy Meter 2.0 channel).

### Derived values (`derive_missing`, default on)

To fill the telegram as completely as a real meter, missing values that follow from the
provided ones are derived automatically (turn off with the `derive_missing` option):

* `apparentPower*` ← `|activePower*|` (assumes cos φ ≈ 1)
* `currentLx` ← apparent power ÷ `voltageLx` (much finer than DSMR's whole-ampere current fields)
* `powerFactor*` ← 1.0 when active power is provided and reactive power is not

### Example: DSMR 5.x per-phase payload from Home Assistant

```yaml
service: mqtt.publish
data:
  topic: sma/emeter/2/state
  payload_template: |-
    {
      "powerIn": {{ states('sensor.electricity_meter_power_consumption') | float(0) * 1000 }},
      "powerOut": {{ states('sensor.electricity_meter_power_production') | float(0) * 1000 }},
      "energyIn": {{ states('sensor.energy_grid_consumed_helper') }},
      "energyOut": {{ states('sensor.energy_grid_returned_helper') }},
      "powerInL1": {{ states('sensor.electricity_meter_power_consumption_phase_l1') | float(0) }},
      "powerOutL1": {{ states('sensor.electricity_meter_power_production_phase_l1') | float(0) }},
      "voltageL1": {{ states('sensor.electricity_meter_voltage_phase_l1') | float(0) }},
      "powerInL2": {{ states('sensor.electricity_meter_power_consumption_phase_l2') | float(0) }},
      "powerOutL2": {{ states('sensor.electricity_meter_power_production_phase_l2') | float(0) }},
      "voltageL2": {{ states('sensor.electricity_meter_voltage_phase_l2') | float(0) }},
      "powerInL3": {{ states('sensor.electricity_meter_power_consumption_phase_l3') | float(0) }},
      "powerOutL3": {{ states('sensor.electricity_meter_power_production_phase_l3') | float(0) }},
      "voltageL3": {{ states('sensor.electricity_meter_voltage_phase_l3') | float(0) }}
    }
```

(Adjust units to your sensors: the example assumes the total power sensors report kW and the
phase sensors report W, as the HA DSMR integration does by default.)

## How to use with HomeWizard meters

Enable the HomeWizard functionality in the configuration. On startup the addon will try to find the homewizard meters on the local network. When a meter is found(it can take a few minutes) a serial number will be assigned and printed to the log output. To speed up the process for the next startup you can add the hostname in the configuration in the field "HomeWizard manual addresses". 

If your homewizard meter is not automatically detected you can manually add it by entering the ip address of the meter(s) in the field "HomeWizard manual addresses". 

If the meter is not detected by the inverter you can add the ip address of your inverter in the field "HomeWizard destination ip addresses". 

# Home Assistant

example of a service call to publish the mqtt message:

```yaml
service: mqtt.publish
data:
  payload_template: |-
    {
      "powerIn": {{states('sensor.power_consumed_from_grid')}},
      "powerOut": {{states('sensor.power_returned_to_grid')}},
      "energyIn": {{states('sensor.energy_grid_consumed_helper')}},
      "energyOut": {{states('sensor.energy_grid_returned_helper')}},
      "destinationAddresses": [
          "192.168.1.34"
        ]
    }
  topic: sma/emeter/1/state
```