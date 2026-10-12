#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
mkdir -p runtime
for name in minimal multiple deep; do
    cp "examples/$name.xml" "runtime/$name.xml"
    python3 -m src.main --headless --vfs "runtime/$name.xml" \
        --startup examples/stage3.txt
done
python3 -m src.main --headless --vfs examples/invalid.xml \
    --startup examples/stage3.txt
