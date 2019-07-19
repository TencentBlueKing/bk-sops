# 正式环境上传部署

## Fork 源代码到自己的仓库  
通过 Fork 源代码到自己的仓库，可以进行二次开发和定制。建议公共特性开发和 bug 修复通过 Pull requests 及时提交到官方仓库。如果不需要进行二次开发，请直接在 releases 中获取打包好的版本，上传部署升级官方标准运维 SaaS。


## 修改版本号
如果有任何代码修改，请务必修改 app.yml 文件中 version 版本号。


## 打包并收集前端静态资源
1）安装依赖包  
进入 frontend/desktop/，执行以下命令安装
```bash
npm install
```

2）打包前端资源
在 frontend/desktop/ 目录下，继续执行以下命令打包前端静态资源
```bash
npm run build -- --SITE_URL="/o/bk_sops" --STATIC_ENV="open/prod"
```

3）收集静态资源
回到项目根目录，执行以下命令收集前端静态资源到 static 目录下
```bash
python manage.py collectstatic --noinput
rm -rf static/open static/images
mv frontend/desktop/static/open static/
mv frontend/desktop/static/images static/
```


## 准备环境
由于上传部署只支持从本地安装 python 依赖包，而 python 安装包是和部署的机器架构相关的，所以你需要在和蓝鲸社区版部署的机器一样的环境执行打包脚本。即准备 CentOS 7 以上操作系统的机器，可以使用 docker。


## 应用打包
在 CentOS 机器上，通过 git 拉取你的标准运维定制版仓库代码后，在项目根目录下运行以下命令执行打包操作。
```bash
bash scripts/publish/build.sh
```
注意，该脚本会把项目依赖的 python 包都下载到生成的版本包中，请务必保证把项目依赖的 python 包都加入到 requirements.txt 文件中。打包完成后会在当前目录下生成一个名为 "bk_sops-当前时间串.tar,gz" 格式的文件，即版本包。


## 上传版本并部署
前往你部署的蓝鲸PaaS平台，在"开发者中心"点击"S-mart应用"，找到官方标准运维应用并进入详情。在"上传版本"中，点击"上传文件"后选中上一步打包生成的版本包，等待上传完成。然后点击"发布部署"，你就可以在测试环境或者正式环境部署你最新的版本包了。
