#!/bin/sh

cd "$(dirname $0)" || exit 1
printf "Currdir: $(pwd)\n"

if [ ! -d "venv" ]; then
    printf "Creating venv...\n"
    python -m venv venv
fi

printf "Activate venv...\n"
source ./venv/bin/activate
printf "Installing requirements...\n"
pip install -r requirements.txt >/dev/null 2>&1
exec python ./main.py

