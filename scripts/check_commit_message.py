# -*- coding: utf-8 -*-
"""
校验提交信息是否包含规范的前缀
"""
from __future__ import absolute_import, print_function, unicode_literals

import sys

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except NameError:
    # py3
    pass


ALLOWED_COMMIT_MSG_PREFIX = [
    ('feature', '新特性'),
    ('bugfix', '线上功能bug'),
    ('minor', '不重要的修改（换行，拼写错误等）'),
    ('optimization', '功能优化'),
    ('sprintfix', '未上线代码修改 （功能模块未上线部分bug）'),
    ('refactor', '功能重构'),
    ('test', '增加测试代码'),
    ('docs', '编写文档'),
    ('merge', '分支合并及冲突解决'),
]


def get_commit_message():
    args = sys.argv
    if len(args) <= 1:
        print("Warning: The path of file `COMMIT_EDITMSG` not given, skipped!")
        return 0
    commit_message_filepath = args[1]
    with open(commit_message_filepath, 'r') as fd:
        content = fd.read()
    return content.strip().lower()


def main():
    content = get_commit_message()
    for prefix in ALLOWED_COMMIT_MSG_PREFIX:
        if content.startswith(prefix[0]):
            return 0

    else:
        print("Commit Message 不符合规范！必须包含以下前缀之一：")
        [print("%-12s\t- %s" % prefix) for prefix in ALLOWED_COMMIT_MSG_PREFIX]

    return 1


if __name__ == '__main__':
    exit(main())
