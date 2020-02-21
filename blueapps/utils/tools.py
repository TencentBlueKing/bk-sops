

# 通过request对象拼接 app_host 访问地址
def get_app_host_by_request(request):
    return '%s://%s%s' % (request.META['wsgi.url_scheme'],
                          request.META['HTTP_HOST'],
                          request.META['SCRIPT_NAME'])
