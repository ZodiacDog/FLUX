"""Type tags and message kinds for the FLUX binary codec."""

from enum import IntEnum


class TypeTag(IntEnum):
    NULL = 0x00
    FALSE = 0x01
    TRUE = 0x02
    INT = 0x03
    FLOAT = 0x04
    STRING = 0x05
    BYTES = 0x06
    LIST = 0x07
    DICT = 0x08
    STRING_REF = 0x09


class MessageType(IntEnum):
    """Optional envelope type; the payload codec does not depend on this."""

    GENERIC = 0
    FUNCTION_CALL = 1
    FUNCTION_RESULT = 2
    EVENT = 3
