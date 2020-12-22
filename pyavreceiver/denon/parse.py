"""Define helpers for parsing integer values returned by receiver."""
import math


class Parse:
    """Define parsers for string integer to db and back."""

    def __getitem__(self, key):
        return getattr(self, key)

    @staticmethod
    def num_to_db(num: str = None, zero: int = None):
        """Convert the string num to a decibel float."""
        if num is None:
            return None
        if zero is None:
            zero = 80

        if len(num) == 3:
            vol = int(num) / 10
        elif int(num) < 100 and int(num) > -100:
            vol = int(num)
        else:
            return None

        return vol - zero

    @staticmethod
    def db_to_num(decibel: int = None, zero: int = 80, str_len: int = 0):
        """Convert the float decibel to a string num."""
        if decibel is None:
            return None

        decibel = round(decibel * 2) / 2

        vol = decibel + zero
        if vol - math.ceil(vol) != 0:
            vol *= 10

        out = str(int(vol))
        if padding := str_len - len(out) > 0:
            pad = ""
            while padding > -1:
                pad += "0"
                padding -= 1
            return pad + out
        return out


parse = Parse()
