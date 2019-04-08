#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import xlrd


class Translate(object):
    def __init__(self, excel_file):
        self.trans_resource = {}
        self.read_excel(excel_file)
        pass

    def read_excel(self, excel_file):
        data = xlrd.open_workbook(excel_file)
        table = data.sheet_by_index(0)
        nrows = table.nrows
        for r in range(nrows):
            key = table.cell(r, 0).value
            val = table.cell(r, 1).value
            self.trans_resource[key] = val

    def __contains__(self, item):
        return item in self.trans_resource.keys()

    def __getitem__(self, item):
        return self.trans_resource.get(item)


def safe_encode(s):
    try:
        return s.decode('utf-8')
    except Exception:
        return s


class ScanPoFile(object):
    def __init__(self):
        pass

    def scan(self, po_file):
        write_list = []
        with open(po_file, 'rb') as f:
            ori_content = []
            for line in f.readlines():
                line = safe_encode(line)
                if line.startswith('msgid "'):
                    ori_content = ["msgstr" + line[5:], ]
                    write_list.append(line)
                elif line.startswith('msgstr ""') and ori_content:
                    write_list.extend(ori_content)
                    ori_content = []
                elif line.startswith('"') and ori_content:
                    ori_content.append(line)
                    write_list.append(line)
                else:
                    write_list.append(line)

        # print ''.join(write_list)
        content = ''.join(write_list)
        with open(po_file, 'w') as f:
            f.write(content.encode('utf-8'))
        pass


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="fill .po file with excel resource")
    parser.add_argument("-p", "--pofile", help=".po file to handle")
    # parser.add_argument("-s", "--source", help="translate resource")
    args = parser.parse_args()

    # trans = Translate(args.source)
    scanner = ScanPoFile()
    scanner.scan(args.pofile)


if __name__ == '__main__':
    main()
