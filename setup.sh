#!/bin/bash

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

deactivate
source venv/bin/activate

find . -name 'requirements.txt' -print0 | while IFS= read -r -d '' filename; do
    echo "Installing requirements from: $filename"
    pip install -r "$filename"
done

rootdir=$(pwd)

echo "Root directory: $rootdir"
export PYTHONPATH="$PYTHONPATH:$rootdir"

uvicorn app:app --host=0.0.0.0 --port=8000 --reload