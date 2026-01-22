/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
const path = require('path')
const webpack = require('webpack')
const { merge } = require('webpack-merge')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const webpackBaseConfig = require('./webpack.base.js')
const mocker = require('./mock/index.js')
const SITE_URL = '/'
const proxyPath = [
    'static',
    'jsi18n',
    'api',
    'core/api',
    'core/footer',
    'config/api',
    'apigw',
    'common_template/api',
    'template/api',
    'taskflow/api',
    'appmaker/save/',
    'appmaker/get_appmaker_count/',
    'pipeline',
    'analysis',
    'periodictask/api',
    'admin/search/',
    'admin/api',
    'admin/taskflow',
    'admin/template',
    'develop/api',
    'version_log',
    'iam',
    'plugin_service',
    'mako_operations',
    'collection',
    'template_market'
]

const context = proxyPath.map(item => SITE_URL + item)

module.exports = merge(webpackBaseConfig, {
    mode: 'development',
    output: {
        publicPath: '/',
        filename: 'js/[name].[contenthash:10].js'
    },
    module: {
        rules: [
            {
                test: /\.s?[ac]ss$/,
                exclude: /node_modules/,
                use: [
                    'style-loader',
                    'css-loader',
                    {
                        loader: 'sass-loader',
                        options: {
                            implementation: require('sass'), // 强制使用 Dart Sass
                            sassOptions: {
                                includePaths: [path.resolve(__dirname, '../src/')],
                                indentedSyntax: false, // 如果使用 SCSS 语法需设为 false
                                silenceDeprecations: ['import', 'legacy-js-api']
                            }
                        }
                    }
                ]
            },
            {
                test: /\.css$/,
                include: /node_modules/,
                use: [
                'style-loader',
                {
                    loader: 'css-loader',
                    options: {
                    importLoaders: 1 // 避免重复处理 @import
                    }
                }
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
        new webpack.HotModuleReplacementPlugin(),
        new HtmlWebpackPlugin({
            template: './src/assets/html/index-dev.html',
            filename: 'index.html'
        })
    ],
    performance: {
        hints: false
    },
    devtool: 'inline-cheap-module-source-map',
    devServer: {
        port: 9000,
        host: 'dev.{BK_PAAS_HOST}',
        server: 'https',
        historyApiFallback: {
            rewrites: [
                { from: /^.*$/, to: '/index.html' }
            ]
        },
        proxy: [
            {
                context,
                target: 'https://{BK_PAAS_HOST}:8000',
                secure: false,
                changeOrigin: true,
                headers: {
                    referer: 'https://{BK_PAAS_HOST}:8000'
                }
            }
        ],
        client: {
            overlay: true,
            progress: true
        }
    }
})
