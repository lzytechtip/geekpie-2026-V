ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
BOOT_DONE_MS = 1800
ROUND_MS = 450


def multiply_generator(scalar, hw):
    if type(scalar) is not int or not 0 < scalar < ORDER:
        raise ValueError('scalar outside group order')
    acc = None
    base = hw.load_generator()
    hw.wait_until(BOOT_DONE_MS)
    for j in range(256):
        deadline = hw.clock_ms + ROUND_MS
        next_base = hw.double(base)
        if (scalar >> j) & 1:
            acc = hw.add(acc, base)
        else:
            hw.balance()
        base = next_base
        hw.wait_until(deadline)
        hw.synchronize()
    return acc
