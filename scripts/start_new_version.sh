#!/bin/bash

RELEASE_VERSION=$1
C_OS="$(uname)"
MAC_OS="Darwin"

ver=$(grep 'version:' app.yml | cut -c 10-)
echo "current version: ${ver}"

if [ "$C_OS" == "$MAC_OS" ];then
    sed -i "" "s/release-${ver}-brightgreen.svg/release-${RELEASE_VERSION}-brightgreen.svg/" readme_en.md
    sed -i "" "s/release-${ver}-brightgreen.svg/release-${RELEASE_VERSION}-brightgreen.svg/" readme.md
    sed -i "" "s/STATIC_VERSION = \"${ver}\"/STATIC_VERSION = \"${RELEASE_VERSION}\"/" config/default.py
    sed -i "" "s/version: ${ver}/version: ${RELEASE_VERSION}/" app.yml
else
    sed -i "s/release-${ver}-brightgreen.svg/release-${RELEASE_VERSION}-brightgreen.svg/" readme_en.md
    sed -i "s/release-${ver}-brightgreen.svg/release-${RELEASE_VERSION}-brightgreen.svg/" readme.md
    sed -i "s/STATIC_VERSION = \"${ver}\"/STATIC_VERSION = \"${RELEASE_VERSION}\"/" config/default.py
    sed -i "s/version: ${ver}/version: ${RELEASE_VERSION}/" app.yml
fi

# extract version logs
python3 scripts/extract_version_log.py ${RELEASE_VERSION}

# rename dev_log
mv dev_log/dev ${RELEASE_VERSION}

# i18n process
sh scripts/i18n/django_i18n.sh
