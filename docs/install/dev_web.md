# 开发环境前端部署

## 安装 node.js  
标准运维前端是用 vue 框架开发的，在本地开发时需要先安装 node.js，直接去官网下载软件并安装即可，地址为：https://nodejs.org/en/。

## 安装依赖包  
进入 pipeline/blueflow/，执行以下命令安装。
```bash
npm install
```

## 修改配置文件  
把 pipeline/blueflow/ 中的所有文件中的 {BK_PAAS_HOST} 换成你部署的蓝鲸社区版地址，如果你的应用 ID 修改过，请把所有文件中的 bk_sops 改成你的新应用 ID。

## 启动前端工程  
进入 bk_sops/src/pipeline/blueflow/，执行以下命令运行前端工程。默认启动的是 9000 端口，然后通过 http://dev.{BK_PAAS_HOST}:9000/ 访问前端应用，此时后端请求会自动转发到你启动的 django 工程，即 8000 端口。
```bash
npm run dev
```

## 开发后打包  
前端开发完成后，正式发布前需要先打包。还是在 pipeline/blueflow/ 目录下，执行如下命令打包，会自动在当前目录下生成 static/dist/ 目录，即打包好的前端资源。 

```bash
npm run build -- --SITE_URL="/o/bk_sops" --STATIC_ENV="open/prod"
```

## 收集静态资源  
前端打包后，需要在工程目录下运行如下命令收集静态资源到 static 下。
```bash
rm -rf static/open static/images
mv pipeline/blueflow/static/open static/
mv pipeline/blueflow/static/images static/
```