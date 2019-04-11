/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
const path = require('path')
const webpack = require('webpack')
const merge = require('webpack-merge')
const webpackBaseConfig = require('./webpack.base.js')

const proxyPath = [
    '/o/bk_sops/api/*',
    '/o/bk_sops/core/api/*',
    '/o/bk_sops/taskflow/api/*',
    '/o/bk_sops/static/',
    '/o/bk_sops/blueflow/atom/',
    '/o/bk_sops/pipeline/*',
    '/o/bk_sops/template/api',
    '/o/bk_sops/template/get_business_basic_info/',
    '/o/bk_sops/appmaker/*',
    '/o/bk_sops/get_biz_person_list/*',
    '/o/bk_sops/config/api/*',
    '/o/bk_sops/jsi18n/gcloud/',
    '/o/bk_sops/core/api/change_default_business/',
    '/o/bk_sops/common_template/*',
    '/o/bk_sops/analysis/*',
    '/o/bk_sops/periodictask/*'
]
const proxyRule = {}
proxyPath.forEach(item => {
    proxyRule[item] = {
        target: 'http://dev.{BK_PAAS_HOST}:8000',
        secure: false,
        changeOrigin: true,
        headers: {
            referer: 'http://dev.{BK_PAAS_HOST}:8000'
        }
    }
})

module.exports = merge( webpackBaseConfig, {
    plugins: [
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: '"development"'
            }
        }),
        new webpack.NamedModulesPlugin(),
        new webpack.HotModuleReplacementPlugin()
    ],
    mode: 'development',
    performance: {
        hints: false
    },
    devtool: 'cheap-module-eval-source-map',
    devServer: {
        port: 9000,
        public: 'dev.{BK_PAAS_HOST}',
        hot: true,
        https: true,
        historyApiFallback: {
            rewrites: [
                { from: /^.*$/, to: '/static/dist/index.html' }
            ]
        },
        proxy: proxyRule,
        overlay: true,
        stats: {
            children: false,
            chunks: false,
            entrypoints: false,
            modules: false
        }
    }
})
