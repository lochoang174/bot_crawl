from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BotCommand(_message.Message):
    __slots__ = ("type", "bot_id")
    class CommandType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        START: _ClassVar[BotCommand.CommandType]
        STOP: _ClassVar[BotCommand.CommandType]
    START: BotCommand.CommandType
    STOP: BotCommand.CommandType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    BOT_ID_FIELD_NUMBER: _ClassVar[int]
    type: BotCommand.CommandType
    bot_id: str
    def __init__(self, type: _Optional[_Union[BotCommand.CommandType, str]] = ..., bot_id: _Optional[str] = ...) -> None: ...

class BotLog(_message.Message):
    __slots__ = ("bot_id", "message")
    BOT_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    bot_id: str
    message: str
    def __init__(self, bot_id: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...
