import struct

class S16_BE:
    def __init__(self, value):
        if isinstance(value, str):
            self.value: bytes = bytes.fromhex(value)
        elif isinstance(value, bytes):
            self.value: bytes = value
        elif isinstance(value, int):
            self.value: bytes = struct.pack('>h', value)
        else:
            assert False, "Not Supported"

    @classmethod
    def from_bytes(cls, data:bytes) -> 'S16_BE':
        return cls(data)

    def to_int(self) -> int:
        return struct.unpack('>h', self.value)[0]

    def __or__(self, other: 'S16_BE') -> 'S16_BE':
        assert len(self.value) == len(other.value)
        return S16_BE.from_bytes(bytes(map(lambda a,b: a|b, self.value, other.value)))

    def __and__(self, other: 'S16_BE') -> 'S16_BE':
        assert len(self.value) == len(other.value)
        return S16_BE.from_bytes(bytes(map(lambda a,b: a&b, self.value, other.value)))

    def __eq__(self, other: 'S16_BE') -> bool:
        if not isinstance(other, S16_BE):
            return False
        assert len(self.value) == len(other.value)
        return self.value == other.value

    def __repr__(self):
        return f'S16_BigEndian("{self.value.hex(" ")}")'
