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
  npm install
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