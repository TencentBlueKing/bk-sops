# 快速配置Swagger UI

1. 安装依赖，请确保环境中已安装下列依赖包:Django、djangorestframework、drf-yasg

2. 在项目urls.py文件下配置对应的交互页面入口:
    ``` python
    from drf_yasg import openapi
    from drf_yasg.views import get_schema_view

    schema_view = get_schema_view(
        openapi.Info(
            title="{你的项目名}",
            default_version="v1",
        ),
        public=True,
    )

    urlpatterns += [
        re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
        re_path(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
        re_path(r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    ]
    ```

3. 启动项目，并在浏览器打开{django_project_host}/swagger路径，即可看到基于OPENAPI的Swagger UI交互页面。