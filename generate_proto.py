#!/usr/bin/env python3
"""
Script to generate Python files from bot.proto
Keeps snake_case field names (no camelCase conversion)
"""
import subprocess
import sys
import os
from pathlib import Path

def generate_proto_files():
    """Generate Python files from bot.proto while preserving snake_case"""
    # Check if proto folder and bot.proto exists
    proto_folder = Path("proto")
    proto_file = proto_folder / "bot.proto"
    
    if not proto_folder.exists():
        print("❌ proto folder not found!")
        print("Please create a 'proto' folder with bot.proto inside.")
        return False
    
    if not proto_file.exists():
        print("❌ bot.proto file not found in proto folder!")
        print("Please make sure proto/bot.proto exists.")
        return False

    try:
        # Get absolute paths
        current_dir = Path.cwd()
        proto_dir = current_dir / "proto"
        output_dir = current_dir  # Output to root
        
        # Command to generate Python files from proto
        cmd = [
            sys.executable, "-m", "grpc_tools.protoc",
            f"--python_out={output_dir}",
            f"--pyi_out={output_dir}",  # Generate type hints
            f"--grpc_python_out={output_dir}",
            f"--proto_path={proto_dir}",
            "bot.proto"
        ]
        
        print("🔧 Generating Python files from proto/bot.proto...")
        print(f"Command: {' '.join(cmd)}")
        
        # Run the protoc command
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(current_dir))
        
        if result.returncode == 0:
            print("✅ Successfully generated Python files!")
            
            # List generated files
            generated_files = []
            patterns = ["*_pb2.py", "*_pb2.pyi", "*_pb2_grpc.py"]
            
            for pattern in patterns:
                for file in current_dir.glob(pattern):
                    generated_files.append(file.name)
            
            if generated_files:
                print(f"📁 Generated files: {', '.join(generated_files)}")
            else:
                print("⚠️ No Python files were generated (check your proto file)")
            
            return True
        else:
            print("❌ Failed to generate Python files!")
            print(f"Error: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return False
            
    except FileNotFoundError:
        print("❌ grpcio-tools not found!")
        print("Please install required dependencies:")
        print("  pip install grpcio grpcio-tools protobuf")
        print("  # or")
        print("  uv add grpcio grpcio-tools protobuf")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_helper_functions():
    """Create helper functions that preserve snake_case field names"""
    helper_content = '''"""
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
'''
    
    helper_file = Path("proto_helpers.py")
    with open(helper_file, 'w', encoding='utf-8') as f:
        f.write(helper_content)
    
    print(f"✅ Created {helper_file.name} with snake_case preserving helpers")

def check_dependencies():
    """Check if required dependencies are installed"""
    dependencies = [
    ("grpcio", "grpc"),
    ("grpcio-tools", "grpc_tools"), 
    ("protobuf", "google.protobuf")
    ]
    
    missing_deps = []
    
    for dep_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {dep_name} is installed")
        except ImportError:
            print(f"❌ {dep_name} is missing")
            missing_deps.append(dep_name)
    
    if missing_deps:
        print(f"\n📦 Please install missing dependencies first:")
        print(f"  pip install {' '.join(missing_deps)}")
        print(f"  # or")
        print(f"  uv add {' '.join(missing_deps)}")
        return False
    
    return True

def main():
    print("🚀 Proto File Generator (Python)")
    print("🐍 Preserves snake_case field names")
    print("=" * 45)
    
    # Check dependencies
    print("📋 Checking dependencies...")
    if not check_dependencies():
        print("❌ Please install required dependencies first!")
        sys.exit(1)
    
    # Generate proto files
    if generate_proto_files():
        # Create helper functions
        create_helper_functions()
        
        print("\n🎉 Proto generation completed successfully!")
        print("\n📝 Key features:")
        print("  ✅ Field names stay snake_case (bot_id → bot_id)")
        print("  ✅ No camelCase conversion (bot_id ≠ botId)")
        print("  ✅ Helper functions preserve original naming")
        
        print("\n📝 Usage example:")
        print("  from bot_pb2 import YourMessage")
        print("  from proto_helpers import to_json, from_json")
        print("  ")
        print("  # Create message with snake_case")
        print("  msg = YourMessage()")
        print("  msg.bot_id = 'example_123'  # stays bot_id")
        print("  msg.user_name = 'john_doe'   # stays user_name")
        print("  ")
        print("  # JSON output preserves snake_case")
        print("  json_str = to_json(msg)")
        print("  # → {\"bot_id\": \"example_123\", \"user_name\": \"john_doe\"}")
        print("  ")
        print("  # Parse from snake_case JSON")
        print("  new_msg = from_json(json_str, YourMessage)")
        
    else:
        print("\n❌ Proto generation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()