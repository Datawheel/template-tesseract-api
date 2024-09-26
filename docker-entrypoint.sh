#!/usr/bin/env bash
set -ex

exec granian --interface asgi --host 0.0.0.0 --port 7777 --respawn-failed-workers app:layer
