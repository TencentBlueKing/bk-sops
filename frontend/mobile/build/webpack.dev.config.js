/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
const webpack = require('webpack')
const merge = require('webpack-merge')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const webpackBaseConfig = require('./webpack.base.js')
const SITE_URL = '/'
const proxyPath = [
    'static/*',
    'jsi18n/*',
    'api/*',
    'core/api/*',
    'config/api/*',
    'apigw/*',
    'common_template/api/*',
    'template/api/*',
    'taskflow/api/*',
    'appmaker/save/',
    'appmaker/get_appmaker_count/',
    'pipeline/*',
    'analysis/*',
    'periodictask/api/*',
    'admin/search/',
    'admin/api/*',
    'admin/taskflow/*',
    'admin/template/*',
    'develop/api/*',
    'version_log/*',
    'iam/*'
]
const proxyRule = {}
proxyPath.forEach(item => {
    proxyRule[SITE_URL + item] = {
        target: 'http://dev.{BK_PAAS_HOST}:8000',
        secure: false,
        changeOrigin: true,
        headers: {
            referer: 'http://dev.{BK_PAAS_HOST}:8000'
        }
    }
})

module.exports = merge(webpackBaseConfig, {
    mode: 'development',
    output: {
        publicPath: '/',
        filename: 'js/[name].[hash:10].js'
    },
    module: {
        rules: [
            {
                test: /\.s?[ac]ss$/,
                use: [
                    'style-loader',
                    'css-loader',
                    {
                        loader: 'px2rem-loader',
                        // options here
                        options: {
                            remUnit: 37.5,
                            remPrecision: 8//换算的rem保留几位小数点
                        }
                    },
                    'sass-loader'
                ]
        
            }
        ]
    },
    plugins: [
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: '"development"'
            }
        }),
        new webpack.NamedModulesPlugin(),
        new webpack.HotModuleReplacementPlugin(),
        new HtmlWebpackPlugin({
            template: './index-dev.html',
            filename: 'index.html'
        })
    ],
    performance: {
        hints: false
    },
    devtool: 'cheap-module-eval-source-map',
    devServer: {
        port: 9001,
        public: 'dev.{BK_PAAS_HOST}',
        hot: true,
        https: false,
        historyApiFallback: {
            rewrites: [
                { from: /^.*$/, to: '/index.html' }
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
