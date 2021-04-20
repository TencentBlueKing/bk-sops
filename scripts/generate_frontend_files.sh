#!/bin/bash
# sh scripts/generate_frontend_files.sh [build]

# build frontend files
if [ -n "$1" ]; then
  cd frontend/desktop
  npm install
  npm run build -- --STATIC_ENV=dev
  cd ../..
  if [ -d "staticfiles/bk_sops" ]; then
    cp -rf staticfiles/bk_sops staticfiles/bk_sops_bak
  fi
  rm -rf staticfiles/bk_sops
  cp -r frontend/desktop/static staticfiles/bk_sops
fi

if [ -d "staticfiles/bk_sops" ]; then
  mkdir -p gcloud/core/templates/core
  cp staticfiles/bk_sops/index.html gcloud/core/templates/core/base_vue.html
fi