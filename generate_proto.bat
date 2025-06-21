@echo off
echo 🚀 Generating Python files from proto/bot.proto...

REM Check if proto folder exists
if not exist "proto" (
    echo ❌ proto folder not found!
    echo Please create a 'proto' folder with bot.proto inside.
    pause
    exit /b 1
)

REM Check if bot.proto exists in proto folder
if not exist "proto\bot.proto" (
    echo ❌ bot.proto file not found in proto folder!
    echo Please make sure proto/bot.proto exists.
    pause
    exit /b 1
)

REM Change to proto directory and generate Python files
cd proto
python -m grpc_tools.protoc --python_out=. --grpc_python_out=. --proto_path=. bot.proto

if %errorlevel% equ 0 (
    echo ✅ Successfully generated Python files in proto folder!
    
    REM List generated files
    for %%f in (*_pb2*.py) do (
        echo 📁 Generated: %%f
    )
) else (
    echo ❌ Failed to generate Python files!
)

cd ..
pause 