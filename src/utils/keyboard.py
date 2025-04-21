import json
from .ino import sendCommandArduino

def getAsciiFromKey(key):
    """
    Retorna o código ASCII ou HID da tecla, para validação.
    Se não for reconhecida, retorna 0.
    """
    if not key:
        return 0

    sanitized = key.lower()

    if sanitized == '?':
        return 63

    if sanitized.isalpha() and len(sanitized) == 1:
        return ord(sanitized)
    
    special = {
        'space': 32,
        'esc': 177,
        'ctrl': 128,
        'alt': 130,
        'shift': 129,
        'enter': 176,
        'up': 218,
        'down': 217,
        'left': 216,
        'right': 215,
        'backspace': 178,
        'f1': 194,  'f2': 195,  'f3': 196,  'f4': 197,
        'f5': 198,  'f6': 199,  'f7': 200,  'f8': 201,
        'f9': 202,  'f10': 203, 'f11': 204, 'f12': 205
    }
    return special.get(sanitized, 0)

def _sendKeyToArduino(key_label: str):
    """
    Monta e envia o payload JSON para o Arduino.
    action=6 dispara o case 6 no sketch, que exibe 'k' na matriz.
    """
    payload = {
        "a": 6,
        "k": key_label
    }
    sendCommandArduino(json.dumps(payload))

def hotkey(*args):
    """
    Segura todas as teclas e solta em sequência.
    Aqui só exibimos cada tecla na matriz; se precisar
    enviar HID real, implemente no sketch.
    """
    for key in args:
        if getAsciiFromKey(key):
            _sendKeyToArduino(key)
    # opcional: delay breve entre pressões
    # time.sleep(0.05)
    for key in args:
        if getAsciiFromKey(key):
            _sendKeyToArduino(key)

def keyDown(key: str):
    """
    Envia tecla como 'pressionada'.
    """
    if getAsciiFromKey(key):
        _sendKeyToArduino(key)

def keyUp(key: str):
    """
    Envia tecla como 'solta'.
    """
    if getAsciiFromKey(key):
        _sendKeyToArduino(key)

def press(*args):
    """
    Pressiona e imediatamente solta cada tecla,
    útil para caracteres únicos.
    """
    for key in args:
        if getAsciiFromKey(key):
            _sendKeyToArduino(key)

def write(phrase: str):
    """
    Percorre cada caractere da frase e envia
    para exibir na matriz.
    """
    for ch in phrase:
        if getAsciiFromKey(ch) or ch.isprintable():
            _sendKeyToArduino(ch)
