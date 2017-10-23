#!/bin/sh
set -e

set -- python3 /opt/redismoke/redismoke.py $@

exec "$@"
