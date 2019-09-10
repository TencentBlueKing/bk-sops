#!bin/bash
WORK_PATH=`pwd`

# check_vue_i18n_utils
# 所有的 vue 文件都需要添加 import '@/utils/i18n.js'，排除不能和项目代码耦合的独立组件 IpSelector
# $1 参数表示当前目录
for item in `find $WORK_PATH/frontend/desktop/src -name "*.vue" ! -path "*IpSelector*"`;do
    echo $item
    grep "i18n.js" $item || exit 1
done

mkdir -p  ~/Temp/gcloud_open/ || exit 1
mv -f $WORK_PATH/static/ ~/Temp/gcloud_open/ || exit 1
rm -rf $WORK_PATH/frontend/desktop/static/ || exit 1

pybabel extract -F babel.cfg --copyright-holder=blueking . -o django.pot || exit 1
# first time
# pybabel init -i django.pot -D django -d locale -l en --no-wrap
# pybabel init -i django.pot -D django -d locale -l zh_hans --no-wrap
pybabel update -i django.pot -d locale -D django --no-wrap || exit 1
django-admin makemessages -d djangojs -e vue,js -i '*node_modules*' -i '*dist*' --no-wrap || exit 1

# 避免手动翻译被注释
#sed -i -e 's/#~ //g' $WORK_PATH/locale/en/LC_MESSAGES/djangojs.po
#sed -i -e 's/#~ //g' $WORK_PATH/locale/en/LC_MESSAGES/django.po
#sed -i -e 's/#~ //g' $WORK_PATH/locale/zh_hans/LC_MESSAGES/djangojs.po
#sed -i -e 's/#~ //g' $WORK_PATH/locale/zh_hans/LC_MESSAGES/django.po

# 中文自动翻译
pip install xlrd || exit 1
which python
pyenv versions
python $WORK_PATH/scripts/i18n/fill_po_with_po.py -p $WORK_PATH/locale/zh_hans/LC_MESSAGES/djangojs.po
python $WORK_PATH/scripts/i18n/fill_po_with_po.py -p $WORK_PATH/locale/zh_hans/LC_MESSAGES/django.po

# 输出需要翻译的位置
echo "可能需要翻译的内容，请检查"
echo -e "\nen.django.po"
grep -n -e 'msgstr ""' $WORK_PATH/locale/en/LC_MESSAGES/django.po
grep -n -e 'fuzzy' $WORK_PATH/locale/en/LC_MESSAGES/django.po
echo -e "\nen.djangojs.po"
grep -n -e 'msgstr ""' $WORK_PATH/locale/en/LC_MESSAGES/djangojs.po
grep -n -e 'fuzzy' $WORK_PATH/locale/en/LC_MESSAGES/djangojs.po
echo -e "\nzh_hans.django.po"
grep -n -e 'msgstr ""' $WORK_PATH/locale/zh_hans/LC_MESSAGES/django.po
grep -n -e 'fuzzy' $WORK_PATH/locale/zh_hans/LC_MESSAGES/django.po
echo -e "\nzh_hans.djangojs.po"
grep -n -e 'msgstr ""' $WORK_PATH/locale/zh_hans/LC_MESSAGES/djangojs.po
grep -n -e 'fuzzy' $WORK_PATH/locale/zh_hans/LC_MESSAGES/djangojs.po


read -rsp $'Press translate django.po and djangojs.po, then press any key to continue...\n' -n1 key
django-admin compilemessages

mv -f ~/Temp/gcloud_open/static/ $WORK_PATH/
