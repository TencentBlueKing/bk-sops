# Production environment upload deployment

## Fork source code to your own repository  
By forking source code to your own repository, you can carry out extended development and customizations. It is suggested that public feature development and bug fixes be submitted to the official repository via pull requests in time.
If there is no need for extended development, please retrieve a packaged version from releases, then upload, deploy and update official SOPS SaaS.


## Modify version number
If there are any code changes, please change the version in app.yml accordingly.


## Package and collect frontend static resources

#### 1. Install dependencies  
Go to frontend/desktop/ and execute the following command to install NPM package
```bash
npm install
```

### 2. Package frontend resource
Go to frontend/desktop/ and execute the following command to package the frontend static resources
```bash
npm run build -- --SITE_URL="/o/bk_sops" --STATIC_ENV="open/prod"
```

### 3. Collect static resources
Go back to the project root directory and execute the following command to collect the frontend static resources and put them into the static directory
```bash
python manage.py collectstatic --noinput
rm -rf static/open static/images
mv frontend/desktop/static/open static/
mv frontend/desktop/static/images static/
```


## Prepare environment
Because upload deployment only supports local python dependencies installation, and python installation packages are architecture-dependent on the deployed machine, you need to execute the packaging script in the same environment as the machine where the Blueking Community Edition is deployed on.
That is to use a machine with a CentOS 7 or above. You can also use docker.


## App packaging
On a CentOS machine, after pulling your SOPS custom repository code via git, execute the following command in the project root directory to start packaging.
```bash
bash scripts/publish/build.sh
```
Note that this script will download all dependent python packages into the final version package. Please be sure to add all the dependent python packages to the requirements.txt file.
When the packaging is completed, a file named "bk_sops-CurrentTimeString.tar.gz" will be generated in the current directory, which is the version package.


## Upload the version and deploy
Go to your deployed Blueking PaaS platform, click "S-mart App" in "Developer Center", locate official SOPS app and click details.
Click "upload files" in "upload version", then select the version package generated in the previous step and wait until the upload is complete. Then, click "Release and Deploy". You should now be able to deploy your latest version package in testing environment or production environment.
