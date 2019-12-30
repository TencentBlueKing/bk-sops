#!/bin/bash
APP_CODE="bk_sops"
rm -rf $APP_CODE
mkdir -p $APP_CODE/src $APP_CODE/pkgs || exit 1
rsync -av --exclude="$APP_CODE" --exclude=".*" --exclude="*.tar.gz" --exclude="frontend/desktop/node_modules/ frontend/mobile/node_modules/" ./$APP_CODE/src/ || exit 1
cp app.yml $APP_CODE/ || exit 1
echo "libraries:" >> $APP_CODE/app.yml
grep -e "^[^#].*$" requirements.txt | awk '{split($1,b,"==");printf "- name: "b[1]"\n  version: "b[2]"\n"}' >> $APP_CODE/app.yml
pip download -d $APP_CODE/pkgs/ -r requirements.txt || exit 1
CURRENT=`date "+%Y%m%d%H%M%S"`
tar -zcvf "$APP_CODE-$CURRENT.tar.gz" $APP_CODE
rm -rf $APP_CODE
