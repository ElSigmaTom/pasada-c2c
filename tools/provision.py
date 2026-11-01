#!/usr/bin/env python3
"""Provision a PASADA serial-only draft, or test persistence in an explicit simulator."""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
import uuid

def validate_config(config):
    if config.get('schema') != 'pasada.device/0.1.0':
        raise ValueError('Unsupported device schema.')
    if config.get('role') not in ('sensor', 'controller', 'beacon') or not config.get('device_id'):
        raise ValueError('Device ID and supported role required.')
    if config.get('output_mode') != 'serial-only' or config.get('security_mode') != 'simulation':
        raise ValueError('This draft accepts only serial-only / simulation configuration.')
    if not isinstance(config.get('esp_now_channel'), int) or not 1 <= config['esp_now_channel'] <= 11:
        raise ValueError('ESP-NOW channel must be 1–11.')
    if config.get('installation_ready') is False:
        raise ValueError('Cabinet position is unlocated; assign its coordinates before provisioning.')
    if len(json.dumps(config).encode()) > 16384:
        raise ValueError('Configuration exceeds draft firmware limit.')

def simulate(config, store):
    validate_config(config)
    db = json.loads(store.read_text()) if store.exists() else {}
    db[config['device_id']] = config
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps(db, indent=2), encoding='utf-8')
    actual = json.loads(store.read_text(encoding='utf-8'))[config['device_id']]
    if actual != config:
        raise ValueError('Simulator readback mismatch.')
    return {'ok': True, 'transport': 'simulated', 'device_id': actual['device_id'],
            'configuration_persisted': True, 'readback_verified': True,
            'radio_verified': False, 'physical_outputs_enabled': False}

def serial_request(port, command, **payload):
    request_id = uuid.uuid4().hex
    packet = {'request_id': request_id, 'command': command, **payload}
    port.write((json.dumps(packet, separators=(',', ':'))+'\n').encode())
    port.flush()
    deadline = time.monotonic()+8
    while time.monotonic() < deadline:
        line = port.readline()
        if not line:
            continue
        try:
            response = json.loads(line)
        except (ValueError, UnicodeDecodeError):
            continue
        if response.get('request_id') == request_id:
            if not response.get('ok'):
                raise ValueError(response.get('error', 'Device rejected command.'))
            return response
    raise RuntimeError(f'Timeout waiting for {command}. Check serial firmware and boot mode.')

def provision_serial(config, port_name):
    validate_config(config)
    try:
        import serial
    except ImportError as exc:
        raise RuntimeError('Real serial mode needs pyserial in your local environment. Simulator mode uses only the Python standard library.') from exc
    with serial.Serial(port_name, 115200, timeout=.3) as port:
        # Opening USB serial may reset a board. Readiness is tested with a handshake.
        time.sleep(1.5)
        port.reset_input_buffer()
        info = serial_request(port, 'get_info')
        if info.get('protocol') != 'pasada.serial/0.1.0':
            raise ValueError('Connected firmware does not implement this draft protocol.')
        serial_request(port, 'set_config', config=config)
        readback = serial_request(port, 'get_config').get('config')
        if readback != config:
            raise ValueError('Device readback differs from intended configuration.')
        return {'ok': True, 'transport': 'serial', 'device_id': config['device_id'],
                'readback_verified': True, 'reboot_retention_verified': False,
                'radio_verified': False, 'physical_outputs_enabled': False}

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, required=True)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--simulate', action='store_true')
    mode.add_argument('--port')
    p.add_argument('--store', type=Path, default=Path('output/virtual-devices.json'))
    p.add_argument('--flash', type=Path, help='Optional merged ESP32-C3 firmware image. Real serial mode only.')
    p.add_argument('--address', default='0x0', help='Address for an explicitly supplied merged image')
    args = p.parse_args(argv)
    try:
        config = json.loads(args.config.read_text(encoding='utf-8'))
        validate_config(config)
        if args.flash:
            if args.simulate:
                raise ValueError('Simulator mode never flashes firmware.')
            if not args.flash.is_file():
                raise ValueError('Firmware image not found.')
            subprocess.run([sys.executable, '-m', 'esptool', '--chip', 'esp32c3', '--port', args.port, 'write-flash', args.address, str(args.flash)], check=True)
        result = simulate(config, args.store) if args.simulate else provision_serial(config, args.port)
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        p.exit(2, f'Error: {exc}\n')

if __name__ == '__main__':
    main()
