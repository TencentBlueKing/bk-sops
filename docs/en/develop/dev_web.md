# Development environment frontend deployment

## Instal node.js  
SOPS frontend is developed under vue framework. node.js should be installed before local development. Simply visit the official website and install: https://nodejs.org/en/.

## Install dependencies  
Go to frontend/desktop/ and execute the following command to install
```bash
npm install
```

## Modify Configuration File  
Replace {BK_PAAS_HOST} in all files in frontend/desktop/ with the address of your deployed Blueking Community Edition, and change bk_sops in all files to your new app ID if you have a modified app ID.

Add the following into environment variables in command line: 
 BK_STATIC_URL = Your BK_PAAS_HOST
 SITE_URL = The root address of frontend (Usually `/`)
## Launch frontend project  
Go to bk_sops/src/frontend/desktop/ and execute the following command to launch the frontend project. The default port is 9000. Then, access the frontend app via http://dev.{BK_PAAS_HOST}:9000/. Backend requests will be automatically forwarded to the django project you launched, which is port 8000.

If you need a proxy for the interface requests in production environment, set the SITE_URL variable in the frontend/desktop/src/assets/html/template.html and frontend/desktop/builds/webpack.dev.config.js files to /o/{APP_CODE}/ (e.g. /o/bk_sops/), replace the target and referer that corresponds to proxyPath in frontend/desktop/builds/webpack.dev.config.js with BK_PAAS_HOST. If you are using HTTPS for production environment, then you need to set the https configuration item to true. 
```bash
npm run dev
```

## Post-development packaging  
After frontend development is completed, you need to package it before release. Execute the following command in frontend/desktop/ to automatically generate static/dist/ directory in the current directory, which is the packaged frontend resource 

```bash
npm run build
```

## Collect static resources  
After frontend packaging is completed, execute the following commands in project directory to collect static resources in static directory.
```bash
cd frontend/desktop
npm run build
cd ../..
rm -rf ./static/bk_sops
cp -r ./frontend/desktop/static ./static/bk_sops
rm ./gcloud/core/templates/core/base_vue.html
mv ./static/bk_sops/index.html ./gcloud/core/templates/core/base_vue.html
```