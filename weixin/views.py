# -*- coding: utf-8 -*-
from common.mymako import render_mako_context


def index(request):
    """
    首页
    """
    return render_mako_context(request, '/weixin/index.html')
