# !/bin/bash
# set -e
# echo $PWD
# base_dir=/Users/wklken/workspace/tx/open_source/bk-PaaS
base_dir=$(PWD)
cd ${base_dir}
change_files=$(git diff --cached --name-only)
fileNo=${change_files[@]}
if [ -z "$fileNo" ];then
    echo "not change file"
    exit 0
fi
echo "scan the source:"${change_files[*]}
echo "checking the rtx name"
check_name=$(grep -aEinor -f  "${base_dir}/.git/hooks/rtx"  ${change_files[*]}  | grep -v ':tencent.com')
if [ -z "${check_name}" ];then
    echo "  OK"
else
    for tmp in ${check_name};do
        echo "  invalid:"${tmp}
    done
    exit 1
fi
echo "checking the ip"
check_ip=$(grep "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)" -REnoa  ${change_files[*]} | grep -v -f "${base_dir}/.git/hooks/ips" )
if [ -z "${check_ip}" ];then
    echo "  OK"
else
    for tmp in ${check_ip};do
        echo "  invalid:"${tmp}
    done
    exit 1
fi