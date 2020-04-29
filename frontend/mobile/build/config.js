/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import path from 'path'
import prodEnv from './prod.env'
import devEnv from './dev.env'

/**
 * 生产环境分版本打包命令
 * npm run build -- --SITE_URL="/o/bk_sops" --STATIC_ENV="open/prod"
 */
let SITE_URL = ''
let STATIC_ENV = ''

process.argv.forEach(val => {
    if (/--SITE_URL=/.test(val)) {
        SITE_URL = val.replace(/--SITE_URL=/, '')
    }
    if (/--STATIC_ENV=/.test(val)) {
        STATIC_ENV = val.replace(/--STATIC_ENV=/, '')
    }
})

process.env.STATIC_ENV = STATIC_ENV

// const publicPath = path.posix.join(SITE_URL, '/static/')

console.log('build mode:', process.env.NODE_ENV)
console.log('SITE_URL:', SITE_URL)
console.log('publicPath:', STATIC_ENV)

const prodPubPath = SITE_URL + '/static/weixin/' + (STATIC_ENV ? STATIC_ENV + '/' : '')

export default {
    build: {
        env: prodEnv,
        assetsRoot: path.resolve(__dirname, '../dist', STATIC_ENV),
        assetsSubDirectory: 'dist',
        assetsPublicPath: prodPubPath,
        productionSourceMap: true,
        productionGzip: false,
        productionGzipExtensions: ['js', 'css'],
        bundleAnalyzerReport: process.env.npm_config_report
    },
    dev: {
        env: devEnv,
        host: '{BK_PAAS_URL}',
        port: 9001,
        assetsSubDirectory: 'static',
        assetsPublicPath: '/',
        proxyTable: {
            '/ajax': { // 需要代理的路径
                target: 'http://{BK_PAAS_URL}', // 目标服务器host
                secure: false,
                pathRewrite: {
                    '^/ajax': ''
                },
                headers: {
                    referer: '{BK_PAAS_URL}' // 目标服务器host
                }
            }
        },
        cssSourceMap: false,
        autoOpenBrowser: false
    }
}
