#!/usr/bin/env python3
"""
Script to generate Python files from bot.proto
"""

import subprocess
import sys
import os
from pathlib import Path


def generate_proto_files():
    """Generate Python files from bot.proto"""
    
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
        
        # Command to generate Python files from proto
        cmd = [
            sys.executable, "-m", "grpc_tools.protoc",
            f"--python_out={proto_dir}",
            f"--grpc_python_out={proto_dir}",
            f"--proto_path={proto_dir}",
            "bot.proto"
        ]
        
        print("🔧 Generating Python files from proto/bot.proto...")
        print(f"Command: {' '.join(cmd)}")
        
        # Run the protoc command in proto directory
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(proto_dir))
        
        if result.returncode == 0:
            print("✅ Successfully generated Python files in proto folder!")
            
            # List generated files
            generated_files = []
            for file in proto_folder.glob("*_pb2*.py"):
                generated_files.append(file.name)
            
            if generated_files:
                print(f"📁 Generated files in proto/: {', '.join(generated_files)}")
            else:
                print("⚠️ No Python files were generated (check your proto file)")
                
            return True
        else:
            print("❌ Failed to generate Python files!")
            print(f"Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ grpcio-tools not found!")
        print("Please install it first:")
        print("  uv add grpcio-tools")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def install_grpcio_tools():
    """Install grpcio-tools if not available"""
    try:
        import grpc_tools
        print("✅ grpcio-tools is already installed")
        return True
    except ImportError:
        print("📦 Installing grpcio-tools...")
        try:
            subprocess.run([sys.executable, "-m", "uv", "add", "grpcio-tools"], check=True)
            print("✅ grpcio-tools installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install grpcio-tools")
            return False


if __name__ == "__main__":
    print("🚀 Proto File Generator")
    print("=" * 30)
    
    # Check and install dependencies if needed
    if not install_grpcio_tools():
        sys.exit(1)
    
    # Generate proto files
    if generate_proto_files():
        print("\n🎉 Proto generation completed!")
    else:
        print("\n❌ Proto generation failed!")
        sys.exit(1) 