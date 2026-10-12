#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
python3 -m src.main --headless --startup examples/stage2.txt
python3 -m src.main --headless --vfs examples/minimal.xml \
    --startup examples/stage2.txt
python3 -m src.main --headless --startup examples/missing.txt
