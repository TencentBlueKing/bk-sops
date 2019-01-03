#!/bin/bash
PROJECT_DIR=$1

function echo_step() {
    echo -e '\033[0;32m'"$1"'\033[0m'
}

function log_info() {
    NOW=$(date +"%Y-%m-%d %H:%M:%S")
    echo "${NOW} [INFO] $1"
}

function log_error() {
    NOW=$(date +"%Y-%m-%d %H:%M:%S")
    echo "${NOW} [ERROR] $1"
}


function if_error_then_exit() {
    if [ "$1" -ne 0 ]
    then
        log_error "$2"
        exit 1
    fi
}

echo_step "add vue header"
VUE_FILES=$(find ${PROJECT_DIR} -name "*.vue" | grep -v asset | grep -v node_modules | grep -v admin)
for VUE_FILE in ${VUE_FILES}
do
    LINE_C=$(head -5 "${VUE_FILE}")
    LINE_H=$(head -5 ${PROJECT_DIR}/scripts/add_license/tmp/LICENSE_JS_CSS_CUE_HEADER.txt)

    if [ "${LINE_C}" != "${LINE_H}" ]
    then
        echo "${VUE_FILE} without license header, add"
        cat ${PROJECT_DIR}/scripts/add_license/tmp/LICENSE_JS_CSS_CUE_HEADER.txt "${VUE_FILE}" > t.vue && mv t.vue "${VUE_FILE}" && echo "add header to ${VUE_FILE}"
        if_error_then_exit $? "add header to vue fail"
    fi
done

echo_step "add js header"
JS_FILES=$(find ${PROJECT_DIR} -name "*.js" -not -name "*.min.js" | grep -v asset | grep -v node_modules | grep -v admin)
for JS_FILE in ${JS_FILES}
do
    LINE_C=$(head -5 "${JS_FILE}")
    LINE_H=$(head -5 ${PROJECT_DIR}/scripts/add_license/tmp/LICENSE_JS_CSS_CUE_HEADER.txt)

    if [ "${LINE_C}" != "${LINE_H}" ]
    then
        echo "${JS_FILE} without license header, add"
        cat ${PROJECT_DIR}/scripts/add_license/tmp/LICENSE_JS_CSS_CUE_HEADER.txt "${JS_FILE}" > t.js && mv t.js "${JS_FILE}" && echo "add header to ${JS_FILE}"
        if_error_then_exit $? "add header to js fail"
    fi
done

echo_step "add css header"
# CSS_FILES=$(find $CSS_DIR -name "*.css" -not -name "*.min.css")
CSS_FILES=$(find ${PROJECT_DIR} -name "*.css" -not -name "*.min.css" | grep -v asset | grep -v node_modules | grep -v admin)
for CSS_FILE in ${CSS_FILES}
do
    LINE_C=$(head -5 "${CSS_FILE}")
    LINE_H=$(head -5 ${PROJECT_DIR}/scripts/add_license/tmp/LICENSE_JS_CSS_CUE_HEADER.txt)

    if [ "${LINE_C}" != "${LINE_H}" ]
    then
        echo "${CSS_FILE} without license header, add"
        cat ${PROJECT_DIR}/scripts/add_license/tmp/LICENSE_JS_CSS_CUE_HEADER.txt "${CSS_FILE}" > t.js && mv t.js "${CSS_FILE}" && echo "add header to ${CSS_FILE}"
        if_error_then_exit $? "add header to css fail"
    fi
done
