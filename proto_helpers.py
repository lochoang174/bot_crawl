"""
Helper functions for protobuf serialization/deserialization
Preserves snake_case field names (bot_id stays bot_id, not botId)
"""
import json
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.message import Message

def to_json(proto_message: Message, **kwargs) -> str:
    """
    Convert protobuf message to JSON string
    Preserves snake_case field names (bot_id -> bot_id, not botId)
    """
    # preserving_proto_field_name=True keeps original field names
    dict_obj = MessageToDict(
        proto_message, 
        preserving_proto_field_name=True,
        including_default_value_fields=True,
        **kwargs
    )
    return json.dumps(dict_obj, ensure_ascii=False, indent=2)

def from_json(json_str: str, message_class, **kwargs):
    """
    Create protobuf message from JSON string
    Expects snake_case field names in JSON
    """
    dict_obj = json.loads(json_str)
    return ParseDict(dict_obj, message_class(), **kwargs)

def to_dict(proto_message: Message, **kwargs) -> dict:
    """
    Convert protobuf message to dictionary
    Preserves snake_case field names
    """
    return MessageToDict(
        proto_message, 
        preserving_proto_field_name=True,
        including_default_value_fields=True,
        **kwargs
    )

def from_dict(data: dict, message_class, **kwargs):
    """
    Create protobuf message from dictionary
    Expects snake_case field names in dictionary
    """
    return ParseDict(data, message_class(), **kwargs)

# Example usage:
# 
# from bot_pb2 import BotMessage
# from proto_helpers import to_json, from_json, to_dict, from_dict
#
# # Create message with snake_case fields
# msg = BotMessage()
# msg.bot_id = "my_bot_123"  # stays as bot_id
# msg.user_name = "john_doe"  # stays as user_name
#
# # Convert to JSON (preserves snake_case)
# json_str = to_json(msg)
# # Result: {"bot_id": "my_bot_123", "user_name": "john_doe"}
#
# # Convert from JSON (expects snake_case)
# new_msg = from_json(json_str, BotMessage)
# print(new_msg.bot_id)  # "my_bot_123"
