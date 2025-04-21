# src/utils/ino.py

import json
import serial
from serial.tools import list_ports
import time

HANDSHAKE_CMD = {"a": 99}
BAUDRATE = 115200
HANDSHAKE_TIMEOUT = 3  # s
LINE_TIMEOUT = 0.5     # s

def _find_and_open_arduino():
    for port in list_ports.comports():
        try:
            ser = serial.Serial(port.device, BAUDRATE, timeout=LINE_TIMEOUT)
        except (serial.SerialException, PermissionError):
            continue

        # dá tempo do sketch resetar e imprimir “Ready”
        time.sleep(2)
        ser.reset_input_buffer()

        # tenta o handshake
        ser.write((json.dumps(HANDSHAKE_CMD) + "\n").encode())
        deadline = time.time() + HANDSHAKE_TIMEOUT
        while time.time() < deadline:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line == '{"ack":"arduino"}':
                return ser
        ser.close()

    raise RuntimeError("Arduino não respondeu ao handshake em nenhuma porta.")

# instância única de Serial para todo o bot
_ser = _find_and_open_arduino()

def sendCommandArduino(payload: str):
    """
    payload já deve ser o JSON stringificado.
    """
    if not _ser.is_open:
        _ser.open()
    _ser.write(payload.encode('utf-8') + b"\n")
