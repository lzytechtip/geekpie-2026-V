import secrets
from device import Accelerator
from firmware import ORDER, multiply_generator
from protocol import encode, multiply, challenge


def sign_message(private_key, message, *, nonce=None, hardware=None):
    if type(private_key) is not int or not 0 < private_key < ORDER:
        raise ValueError('invalid private key')
    if nonce is None:
        nonce = secrets.randbelow(ORDER-1)+1
    hw = Accelerator() if hardware is None else hardware
    key = encode(multiply(private_key))
    r = encode(multiply_generator(nonce, hw))
    s = (nonce+challenge(r, key, message)*private_key) % ORDER
    return dict(R=r.hex(), s=f'{s:064x}')
