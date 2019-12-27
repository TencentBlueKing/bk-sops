# 开发环境前端部署

## 安装 node.js  
标准运维前端是用 vue 框架开发的，在本地开发时需要先安装 node.js，直接去官网下载软件并安装即可，地址为：https://nodejs.org/en/。

## 安装依赖包  
进入 frontend/desktop/，执行以下命令安装。
```bash
npm install
```

## 修改配置文件  
把 frontend/desktop/ 中的所有文件中的 {BK_PAAS_HOST} 换成你部署的蓝鲸社区版地址，如果你的应用 ID 修改过，请把所有文件中的 bk_sops 改成你的新应用 ID。

## 启动前端工程  
进入 bk_sops/src/frontend/desktop/，执行以下命令运行前端工程。默认启动的是 9000 端口，然后通过 http://dev.{BK_PAAS_HOST}:9000/ 访问前端应用，此时后端请求会自动转发到你启动的 django 工程，即 8000 端口。

如果需要把接口请求代理到正式环境，请将 frontend/desktop/src/assets/html/template.html 和 frontend/desktop/builds/webpack.dev.config.js 文件里的 SITE_URL 变量设置为 /o/{APP_CODE}/（例如：/o/bk_sops/）， frontend/desktop/builds/webpack.dev.config.js 文件里 proxyPath 对应的 target 和 referer 替换为 BK_PAAS_HOST，若正式环境为 https，则需要将 https 配置项设置为 true。
```bash
npm run dev
```

## 开发后打包  
前端开发完成后，正式发布前需要先打包。还是在 frontend/desktop/ 目录下，执行如下命令打包，会自动在当前目录下生成 static/dist/ 目录，即打包好的前端资源。 

```bash
npm run build -- --SITE_URL="/o/bk_sops" --STATIC_ENV="open/prod" [--VERSION={STATIC_VERSION}]
```
其中 VERSION 是可选参数，建议正式打包加上该参数，{STATIC_VERSION} 是 config/default.py 中的 STATIC_VERSION 值。

## 收集静态资源  
前端打包后，需要在工程目录下运行如下命令收集静态资源到 static 下。
```bash
rm -rf static/open static/images
mv frontend/desktop/static/open static/
mv frontend/desktop/static/images static/
```