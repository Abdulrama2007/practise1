#!/bin/sh
cd "$(dirname "$0")" || exit 1
mkdir -p runtime
cp examples/deep.xml runtime/demo.xml
exec python3 -m src.main --vfs runtime/demo.xml --startup examples/demo.txt
