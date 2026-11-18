#!/bin/bash

RELEASE_VERSION=$1
C_OS="$(uname)"
MAC_OS="Darwin"

ver=$(grep '^version:' app.yml | cut -c 10- | tr -d '"')
echo "current version: ${ver}"

# version num replace
if [ "$C_OS" == "$MAC_OS" ];then
    sed -i.bak "s/^STATIC_VERSION = .*/STATIC_VERSION = \"${RELEASE_VERSION}\"/" config/default.py
    sed -i.bak "s/^version: .*/version: \"${RELEASE_VERSION}\"/" app.yml
    sed -i.bak "s/^appVersion: .*/appVersion: \"${RELEASE_VERSION}\"/" app_desc.yaml
    rm config/default.py.bak app.yml.bak app_desc.yaml.bak
else
    sed -i "s/^STATIC_VERSION = .*/STATIC_VERSION = \"${RELEASE_VERSION}\"/" config/default.py
    sed -i "s/^version: .*/version: \"${RELEASE_VERSION}\"/" app.yml
    sed -i "s/^appVersion: .*/appVersion: \"${RELEASE_VERSION}\"/" app_desc.yaml
fi

datetime=`date +%Y-%m-%d`
touch version_logs_md/V${RELEASE_VERSION}_${datetime}.md

# i18n process
# sh scripts/i18n/django_i18n.sh
