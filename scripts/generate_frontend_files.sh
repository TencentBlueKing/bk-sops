#!/bin/bash
# sh scripts/generate_frontend_files.sh [build]

DJANGO_VERSION=$(cat requirements.txt | grep Django= | awk -F '==' '{print $NF}')
if [[ $DJANGO_VERSION == 1* ]]; then
  STATIC_DIR="static"
else
  STATIC_DIR="staticfiles"
fi
echo $STATIC_DIR

# build frontend files
if [ -n "$1" ]; then
  cd frontend/desktop
  # 必须按 lockfile 安装：npm install 会在 package.json 的版本范围内重新解析依赖，
  # 曾导致同一份源码在不同时间构建出行为不同的产物。
  npm ci
  npm run build -- --STATIC_ENV=dev
  cd ../..
  if [ -d "$STATIC_DIR/bk_sops" ]; then
    cp -rf $STATIC_DIR/bk_sops $STATIC_DIR/bk_sops_bak
  fi
  rm -rf $STATIC_DIR/bk_sops
  cp -r frontend/desktop/static $STATIC_DIR/bk_sops
fi

if [ -d "staticfiles/bk_sops" ]; then
  mkdir -p gcloud/core/templates/core
  cp $STATIC_DIR/bk_sops/index.html gcloud/core/templates/core/base_vue.html
fi