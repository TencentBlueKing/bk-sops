#!/bin/bash

ts=$(date "+%Y%m%d%H%M")
user=$(git config user.name)
log_name="$user"_"$ts"

mkdir -p ./dev_log/dev
echo "add log: ./dev_log/dev/$log_name.yaml"
touch ./dev_log/dev/$log_name.yaml