# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import re

from six.moves.html_parser import HTMLParser


"""
Python 富文本XSS过滤类
@package XssHtml
@version 0.1
@link http://phith0n.github.io/python-xss-filter
@since 20150407
@copyright (c) Phithon All Rights Reserved
Based on native Python module HTMLParser purifier of HTML, To Clear all javascript in html
You can use it in all python web framework
Written by Phithon <root@leavesongs.com> in 2015 and placed in the public domain.
phithon <root@leavesongs.com> 编写于20150407
From: XDSEC <www.xdsec.org> & 离别歌 <www.leavesongs.com>
GitHub Pages: https://github.com/phith0n/python-xss-filter
Usage:
    parser = XssHtml()
    parser.feed('<html code>')
    parser.close()
    html = parser.get_html()
    print html
Requirements
Python 2.6+ or 3.2+
Cannot defense xss in browser which is belowed IE7
浏览器版本：IE7+ 或其他浏览器，无法防御IE6及以下版本浏览器中的XSS
"""


class XssHtml(HTMLParser):
    allow_tags = [
        "a",
        "img",
        "br",
        "strong",
        "b",
        "code",
        "pre",
        "p",
        "div",
        "em",
        "span",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "blockquote",
        "ul",
        "ol",
        "tr",
        "th",
        "td",
        "hr",
        "li",
        "u",
        "embed",
        "s",
        "table",
        "thead",
        "tbody",
        "caption",
        "small",
        "q",
        "sup",
        "sub",
    ]
    common_attrs = ["id", "style", "class", "name"]
    nonend_tags = ["img", "hr", "br", "embed"]
    tags_own_attrs = {
        "img": ["src", "width", "height", "alt", "align"],
        "a": ["href", "target", "rel", "title"],
        "embed": [
            "src",
            "width",
            "height",
            "type",
            "allowfullscreen",
            "loop",
            "play",
            "wmode",
            "menu",
        ],
        "table": ["border", "cellpadding", "cellspacing"],
    }

    def __init__(self, allows=None):
        HTMLParser.__init__(self)
        if allows is None:
            allows = []
        self.allow_tags = allows if allows else self.allow_tags
        self.result = []
        self.start = []
        self.data = []

    def get_html(self):
        """
        Get the safe html code
        """
        for i in range(0, len(self.result)):
            tmp = self.result[i].rstrip("\n")
            tmp = tmp.lstrip("\n")
            if tmp:
                self.data.append(tmp)
        return "".join(self.data)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_starttag(self, tag, attrs):
        if tag not in self.allow_tags:
            return
        end_diagonal = " /" if tag in self.nonend_tags else ""
        if not end_diagonal:
            self.start.append(tag)
        attdict = {}
        for attr in attrs:
            attdict[attr[0]] = attr[1]

        attdict = self.__wash_attr(attdict, tag)
        if hasattr(self, "node_%s" % tag):
            attdict = getattr(self, "node_%s" % tag)(attdict)
        else:
            attdict = self.node_default(attdict)

        attrs = []
        for (key, value) in attdict.items():
            attrs.append('{}="{}"'.format(key, self.__htmlspecialchars(value)))
        attrs = (" " + " ".join(attrs)) if attrs else ""
        self.result.append("<" + tag + attrs + end_diagonal + ">")

    def handle_endtag(self, tag):
        if self.start and tag == self.start[len(self.start) - 1]:
            self.result.append("</" + tag + ">")
            self.start.pop()

    def handle_data(self, data):
        self.result.append(self.__htmlspecialchars(data))

    def handle_entityref(self, name):
        if name.isalpha():
            self.result.append("&%s;" % name)

    def handle_charref(self, name):
        if name.isdigit():
            self.result.append("&#%s;" % name)

    def node_default(self, attrs):
        attrs = self.__common_attr(attrs)
        return attrs

    def node_a(self, attrs):
        attrs = self.__common_attr(attrs)
        attrs = self.__get_link(attrs, "href")
        attrs = self.__set_attr_default(attrs, "target", "_blank")
        attrs = self.__limit_attr(attrs, {"target": ["_blank", "_self"]})
        return attrs

    def node_embed(self, attrs):
        attrs = self.__common_attr(attrs)
        attrs = self.__get_link(attrs, "src")
        attrs = self.__limit_attr(
            attrs,
            {
                "type": ["application/x-shockwave-flash"],
                "wmode": ["transparent", "window", "opaque"],
                "play": ["true", "false"],
                "loop": ["true", "false"],
                "menu": ["true", "false"],
                "allowfullscreen": ["true", "false"],
            },
        )
        attrs["allowscriptaccess"] = "never"
        attrs["allownetworking"] = "none"
        return attrs

    def __true_url(self, url):
        prog = re.compile(r"^(http|https|ftp)://.+", re.I | re.S)
        if prog.match(url):
            return url
        else:
            return "http://%s" % url

    def __true_style(self, style):
        if style:
            style = re.sub(r"(\\|&#|/\*|\*/)", "_", style)
            style = re.sub(r"e.*x.*p.*r.*e.*s.*s.*i.*o.*n", "_", style)
        return style

    def __get_style(self, attrs):
        if "style" in attrs:
            attrs["style"] = self.__true_style(attrs.get("style"))
        return attrs

    def __get_link(self, attrs, name):
        if name in attrs:
            attrs[name] = self.__true_url(attrs[name])
        return attrs

    def __wash_attr(self, attrs, tag):
        if tag in self.tags_own_attrs:
            other = self.tags_own_attrs.get(tag)
        else:
            other = []
        if attrs:
            for (key, _) in list(attrs.items()):
                if key not in self.common_attrs + other:
                    del attrs[key]
        return attrs

    def __common_attr(self, attrs):
        attrs = self.__get_style(attrs)
        return attrs

    def __set_attr_default(self, attrs, name, default=""):
        if name not in attrs:
            attrs[name] = default
        return attrs

    def __limit_attr(self, attrs, limit=None):
        if limit is None:
            limit = {}
        for (key, value) in limit.items():
            if key in attrs and attrs[key] not in value:
                del attrs[key]
        return attrs

    def __htmlspecialchars(self, html):
        return (
            html.replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#039;")
        )


if "__main__" == __name__:
    parser = XssHtml()
    parser.feed(
        """<p><img src=1 onerror=alert(/xss/)></p><div class="left">
        <a href='javascript:prompt(1)'><br />hehe</a></div>
        <p id="test" onmouseover="alert(1)">&gt;M<svg>
        <a href="https://www.baidu.com" target="self">MM</a></p>
        <embed src='javascript:alert(/hehe/)' allowscriptaccess=always />"""
    )
    parser.close()
    print(parser.get_html())
