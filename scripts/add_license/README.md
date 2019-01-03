1. move LICENSE into the root


2. add to js/css

   do gulp first
   # use the tmp/LICENSE_JSCSS_HEADER.txt
   bash add_jscss_license_header.sh

   if you add new js/css, do it again

3. add to py

```
$ python add_py_license_header.py
Usage: add_py_license_header.py headerfile directory [filenameregex [dirregex [skip regex]]]
```

```
# use the tmp/LICENSE_HEADER.txt
# NOTE: only change the paas-ce/paas to your python project dir
python addheader.py tmp/LICENSE_HEADER.txt paas-ce/paas ".*\.py" ".*" 'Tencent is pleased to support'
```
