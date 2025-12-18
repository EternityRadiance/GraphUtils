#!/bin/sh

cd "$(dirname $0)" || exit 1

if [ ! -d "venv" ]; then
    python -m venv venv
fi

source ./venv/bin/activate
pip install -r requirements.txt >/dev/null 2>&1
exec python ./main.py

