#!/bin/bash

ts=$(date "+%Y%m%d%H%M")
user=$(git config user.name)
log_name="$user"_"$ts"

mkdir -p ./dev_log/dev
echo "add log: ./dev_log/dev/$log_name.yaml"

if [ $# -eq 2 ]; then
text=$1":
  - "$2
elif [ ! -n "$1" ]; then
text="feature:
  - 新增 xxx 功能
improvement:
  - 优化 xxx 功能
bugfix:
  - 修复 xxx 问题
（请根据上述格式填写，并删除无关项）"
elif [ "feature" == "$1" ]; then
text="feature:
  - 新增 xxx 功能"
elif [ "improvement" == "$1" ]; then
text="improvement:
  - 优化 xxx 功能"
elif [ "bugfix" == "$1" ]; then
text="bugfix:
  - 修复 xxx 问题"
fi

echo "$text" > ./dev_log/dev/$log_name.yaml