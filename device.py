FIELD = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
GENERATOR = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)


def point_add(p, q):
    if p is None:
        return q
    if q is None:
        return p
    x, y = p
    u, v = q
    if x == u:
        if (y + v) % FIELD == 0:
            return None
        slope = 3*x*x*pow(2*y, -1, FIELD) % FIELD
    else:
        slope = (v-y)*pow(u-x, -1, FIELD) % FIELD
    rx = (slope*slope-x-u) % FIELD
    return rx, (slope*(x-rx)-y) % FIELD


class Accelerator:
    def __init__(self):
        self.clock_ms = 0

    def wait_until(self, deadline_ms):
        if deadline_ms < self.clock_ms:
            raise ValueError('command exceeded slot')
        self.clock_ms = deadline_ms

    def command(self, name, length_ms):
        self.clock_ms += length_ms

    def synchronize(self):
        """Wait until the controller permits the next command group."""
        pass

    def load_generator(self):
        self.wait_until(1150)
        self.command('LOAD', 150)
        return GENERATOR

    def double(self, p):
        self.command('DOUBLE', 110)
        return point_add(p, p)

    def add(self, p, q):
        self.command('ADD', 160)
        return point_add(p, q)

    def balance(self):
        self.command('BALANCE', 160)
