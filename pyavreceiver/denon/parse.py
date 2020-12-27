"""Define helpers for parsing integer values returned by receiver."""
import math

from pyavreceiver.denon.error import DenonCannotParse


class Parse:
    """Define parsers for string integer to db and back."""

    def __getitem__(self, key):
        return getattr(self, key)

    @staticmethod
    def num_to_db(num: str = None, zero: int = 80, valid_strings=None):
        """Convert the string num to a decibel float."""
        zero = 0 if zero is None else zero
        if valid_strings and num in valid_strings:
            return valid_strings[num]
        try:
            if len(num) == 3 and num[0] != "-":
                vol = int(num) / 10
            elif int(num) < 100 and int(num) > -100:
                vol = int(num)
            else:
                raise DenonCannotParse

            return vol - zero
        except TypeError:
            return num
        except ValueError:
            return None

    @staticmethod
    def db_to_num(
        decibel: int = None, zero: int = 80, str_len: int = 0, valid_strings=None
    ):
        """Convert the float decibel to a string num."""
        try:
            zero = 0 if zero is None else zero

            decibel = round(decibel * 2)
            if decibel != 0:
                decibel /= 2

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
        except TypeError:
            return decibel


parse = Parse()
