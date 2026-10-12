#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
mkdir -p runtime
cp examples/deep.xml runtime/commands.xml
python3 -m src.main --headless --vfs runtime/commands.xml \
    --startup examples/stage4.txt
python3 -m src.main --headless --vfs runtime/commands.xml \
    --startup examples/stage5.txt
cp examples/deep.xml runtime/all.xml
python3 -m src.main --headless --vfs runtime/all.xml \
    --startup examples/all_commands.txt
