class BitArrayNumber:
    WIDTH = 32

    def __init__(self, bits: list[int]):
        if len(bits) != self.WIDTH:
            raise ValueError(f"bits length must be {self.WIDTH}")
        for b in bits:
            if b not in (0, 1):
                raise ValueError("bits must be 0 or 1")
        self.bits = bits

    def to_bits(self) -> list[int]:
        return self.bits[:]

    def to_bin_str(self) -> str:
        return "".join("1" if b else "0" for b in self.bits)

    @staticmethod
    def _unsigned_to_bits(value: int, width: int) -> list[int]:
        if value < 0:
            raise ValueError("value must be non-negative")
        bits = [0] * width
        v = value
        for i in range(width - 1, -1, -1):
            v, rem = divmod(v, 2)
            bits[i] = rem
        if v != 0:
            raise OverflowError("value does not fit in width")
        return bits

    @staticmethod
    def _bits_to_unsigned(bits: list[int]) -> int:
        value = 0
        for b in bits:
            value = value * 2 + b
        return value

