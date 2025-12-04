#!/bin/sh

cd "$(dirname $0)" || exit 1

if [ ! -d "venv" ]; then
    python -m venv venv
fi

pip install -r requirements.txt >/dev/null 2>&1
source ./venv/bin/activate
exec python ./main.py

