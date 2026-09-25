import hashlib
import re

from device import FIELD, GENERATOR, point_add
from firmware import ORDER

DOMAIN = b'phase-signer/schnorr/v1\x00'


def encode(point):
    if point is None:
        raise ValueError('identity has no permitted encoding')
    x, y = point
    return bytes([2 + (y & 1)]) + x.to_bytes(32, 'big')


def decode(data):
    if not isinstance(data, bytes) or len(data) != 33 or data[0] not in (2, 3):
        raise ValueError('invalid compressed point')
    x = int.from_bytes(data[1:], 'big')
    if x >= FIELD:
        raise ValueError('noncanonical coordinate')
    square = (pow(x, 3, FIELD) + 7) % FIELD
    y = pow(square, (FIELD + 1) // 4, FIELD)
    if y * y % FIELD != square:
        raise ValueError('point is not on curve')
    if (y & 1) != (data[0] & 1):
        y = FIELD - y
    return x, y


def multiply(scalar, point=GENERATOR):
    if type(scalar) is not int or not 0 <= scalar < ORDER:
        raise ValueError('scalar outside group order')
    acc = None
    while scalar:
        if scalar & 1:
            acc = point_add(acc, point)
        point = point_add(point, point)
        scalar >>= 1
    return acc


def challenge(r_bytes, key_bytes, message):
    if not isinstance(message, bytes) or len(message) >= 2**32:
        raise ValueError('message must be bytes shorter than 2^32')
    preimage = DOMAIN + r_bytes + key_bytes + len(message).to_bytes(4, 'big') + message
    return int.from_bytes(hashlib.sha256(preimage).digest(), 'big') % ORDER


def verify(key_bytes, message, r_bytes, s):
    try:
        if type(s) is not int or not 0 <= s < ORDER:
            return False
        key, r = decode(key_bytes), decode(r_bytes)
        e = challenge(r_bytes, key_bytes, message)
        return multiply(s) == point_add(r, multiply(e, key))
    except (ValueError, TypeError, OverflowError):
        return False


def parse_signature(value):
    if not isinstance(value, dict) or set(value) != {'R', 's'}:
        raise ValueError('signature must contain exactly R and s')
    r_hex, s_hex = value['R'], value['s']
    if not isinstance(r_hex, str) or re.fullmatch(r'(02|03)[0-9a-f]{64}', r_hex) is None:
        raise ValueError('R must be a lowercase compressed point hex string')
    if not isinstance(s_hex, str) or re.fullmatch(r'[0-9a-f]{64}', s_hex) is None:
        raise ValueError('s must be a lowercase 32-byte hex string without 0x')
    r, s = bytes.fromhex(r_hex), int(s_hex, 16)
    decode(r)
    if s >= ORDER:
        raise ValueError('s outside group order')
    return r, s


def check_submission(manifest, submission):
    try:
        r, s = parse_signature(submission)
        return verify(bytes.fromhex(manifest['public_key']),
                      manifest['target_message'].encode('utf-8'), r, s)
    except (ValueError, TypeError, KeyError):
        return False
