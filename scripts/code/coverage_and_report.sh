#!/bin/bash

usage() { echo "Usage: [-m test module] [-e exclude tag]" 1>&2; exit 1; }

if [[ -d .cover ]]; then
    rm -rf .cover
fi

INCLUDE_PATH="django_signal_valve/*,gcloud/*,pipeline/*,pipeline_plugins/*"
OMIT_PATH="*/migrations/*,*/tests/*"

exclude_tag=''
module=''

while getopts ":e:m:" opt; do
    case ${opt} in
      e )
        exclude_tag=$OPTARG
        ;;
      m )
        module=$OPTARG
        ;;
      * )
        usage
        ;;
    esac
done

# random test database name
DB_NAME="test_$RANDOM"
sed -i.bak "s/test_sops/$DB_NAME/g" config/dev.py && rm config/dev.py.bak

revert_db() { sed -i.bak "s/$DB_NAME/test_sops/g" config/dev.py && rm config/dev.py.bak; exit 1; }

coverage erase
coverage run --include=$INCLUDE_PATH --omit=$OMIT_PATH ./manage.py test $module --exclude-tag=$exclude_tag || revert_db
coverage html -d .cover
coverage report --include=$INCLUDE_PATH --omit=$OMIT_PATH || revert_db

sed -i.bak "s/$DB_NAME/test_sops/g" config/dev.py && rm config/dev.py.bak
