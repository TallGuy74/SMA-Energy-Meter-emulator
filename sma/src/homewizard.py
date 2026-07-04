import hashlib
import json
import logging
import time

import requests
from config import settings, workingdata
from emeter import emeterPacket, payload_to_values, build_packet
from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf


def setup_homewizard():
    if settings.get("enable_homewizard", False) is False:
        return None
    
    zeroconf = Zeroconf()
    browser = ServiceBrowser(zeroconf, "_hwenergy._tcp.local.", handlers=[lambda zeroconf, service_type, name, state_change: on_service_state_change(zeroconf, service_type, name, state_change)])
    for ip in settings.get("homewizard_manual_addresses", []):
        ip = ip.lower()
        serial_number = string_to_int(ip)
        logging.info(f"HomeWizard manual entry ip/hostname: {ip}, assigned serial number: {serial_number}")
        workingdata['homewizard_meters'][ip] = serial_number

def on_service_state_change(zeroconf, service_type, name, state_change):
    if state_change is not ServiceStateChange.Added:
        return
    
    logging.debug(f"Found device with name: {name}, state_change: {state_change}, trying to get info")
    info = zeroconf.get_service_info(service_type, name)
    if not info:
        return
    hostname = info.server
    logging.debug(f"Found device with hostname from ServiceInfo: {hostname}")

    if not hostname.startswith("p1meter") and not hostname.startswith("kwhmeter"):
        return
    
    hostname = hostname.lower()
    if hostname in workingdata['homewizard_meters'].keys():
        return
    
    serial_number = string_to_int(hostname)
    
    logging.info(f"Found HomeWizard meter with hostname: {hostname}, assigned serial number: {serial_number}")
    with workingdata['lock']:
        workingdata['homewizard_meters'][hostname] = serial_number

def update_homewizard():
    if len(workingdata['homewizard_meters']) == 0:
        return None
    
    try:
        with workingdata['lock']:
            hostnames = workingdata['homewizard_meters']

        for (hostname, serial_number) in hostnames.items():
            # Perform the GET request
            response = requests.get(f'http://{hostname}/api/v1/data')
            
            # Raise an exception for HTTP errors
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()
            logging.debug(f"Message data: {data}")

            # Map the HomeWizard reading to payload keys and build one canonical telegram.
            # (The old path appended reactive-power zeros that begin() had already written as
            # dummies -> duplicate OBIS entries in every HomeWizard telegram. build_packet
            # structurally prevents that.)
            hw = {}
            active_power = data['active_power_w']
            hw['powerIn'] = active_power if active_power > 0 else 0.0
            hw['powerOut'] = -active_power if active_power < 0 else 0.0
            hw['energyIn'] = data['total_power_import_t1_kwh'] + data['total_power_import_t2_kwh']
            hw['energyOut'] = data['total_power_export_t1_kwh'] + data['total_power_export_t2_kwh']
            for x in (1, 2, 3):                                     # per-phase fields exist on 3-phase HomeWizard meters
                pw = data.get(f'active_power_l{x}_w')
                if pw is not None:
                    hw[f'powerInL{x}'] = pw if pw > 0 else 0.0
                    hw[f'powerOutL{x}'] = -pw if pw < 0 else 0.0
                if data.get(f'active_voltage_l{x}_v') is not None:
                    hw[f'voltageL{x}'] = data[f'active_voltage_l{x}_v']
                if data.get(f'active_current_l{x}_a') is not None:
                    hw[f'currentL{x}'] = abs(data[f'active_current_l{x}_a'])
            if data.get('active_frequency_hz') is not None:
                hw['frequency'] = data['active_frequency_hz']

            values = payload_to_values(hw, derive=settings.get("derive_missing", True))
            packet = build_packet(serial_number, int(time.time() * 1000), values)

            # Get packet data
            packet_data = packet.getData()[:packet.getLength()]
            destination_addresses = settings.get("homewizard_destination_addresses", [])

            with workingdata['lock']:
                workingdata['packets'][serial_number] = (packet_data, destination_addresses)
                logging.debug(f"Updated homewizard packet for serial number {serial_number}")

    except requests.RequestException as e:
        logging.error(f"HTTP Request failed: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON payload: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    
def string_to_int(string_value):
    # Create a SHA-256 hash of the string
    hash_object = hashlib.sha256(string_value.encode())
    # Convert the hash to an integer
    hash_int = int(hash_object.hexdigest(), 16) % (10 ** 8)
    return hash_int