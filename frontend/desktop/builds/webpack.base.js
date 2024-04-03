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
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin')
const CaseSensitivePathsPlugin = require('case-sensitive-paths-webpack-plugin')

module.exports = {
    entry: {
        main: './src/main.js'
    },
    output: {
        path: path.join(__dirname, '../static')
    },
    module: {
        rules: [
            {
                test: require.resolve('jquery'),
                loader: 'expose-loader',
                options: {
                    exposes: ['$', 'jQuery']
                }
            },
            {
                enforce: 'pre',
                test: /\.(js|vue)$/,
                loader: 'eslint-loader',
                exclude: /node_modules/,
                options: {
                    formatter: require('eslint-friendly-formatter')
                }
            },
            {
                test: /\.vue$/,
                use: [
                    {
                        loader: 'vue-loader',
                        options: {
                            extractCSS: true

                        }
                    }
                ],
                exclude: [
                    path.join(__dirname, '../node_modules')
                ]
            },
            {
                test: /\.js$/,
                loader: 'babel-loader',
                exclude: [
                    path.join(__dirname, '../node_modules')
                ]
            },
            {
                test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
                type: 'asset/resource',
                generator: {
                    filename: path.posix.join('images/[name].[contenthash:10].[ext]')
                }
            },
            {
                test: /\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/,
                type: 'asset/resource',
                generator: {
                    filename: path.posix.join('videos/[name].[contenthash:10].[ext]')
                }
            },
            {
                test: /\.(woff2?|eot|ttf|otf|svg)(\?.*)?$/,
                type: 'asset/resource',
                exclude: [
                    path.join(__dirname, '../src/assets/images/'),
                    path.join(__dirname, '../src/assets/bk-magic/images/')
                ],
                generator: {
                    filename: path.posix.join('fonts/[name].[contenthash:10].[ext]')
                }
            }
        ]
    },
    plugins: [
        new CaseSensitivePathsPlugin(),
        new VueLoaderPlugin(),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
            'window.jQuery': 'jquery'
        }),
        new MonacoWebpackPlugin({
            output: path.posix.join('js/'),
            languages: ['javascript', 'typescript', 'json', 'python', 'shell']
        })
    ],
    optimization: {
        moduleIds: 'named',
        splitChunks: {
            cacheGroups: {
                defaultVendors: { // 框架相关
                    test: /(vue|vue-router|vuex|axios|vee-validate|axios|vuedraggable)/,
                    name: 'vendors',
                    chunks: 'initial',
                    priority: 100
                },
                'moment-timezone': {
                    test: /moment-timezone/,
                    name: 'moment-timezone',
                    chunks: 'all',
                    priority: 100
                },
                'monaco-editor': {
                    test: /monaco-editor/,
                    name: 'monaco-editor',
                    chunks: 'all',
                    priority: 100
                },
                'bk-magic-vue': {
                    test: /bk-magic-vue\/dist\/bk-magic-vue\.min\.js/,
                    name: 'bk-magic-vue',
                    chunks: 'initial',
                    priority: 100
                },
                bkcharts: {
                    test: /@blueking\/bkcharts\/dist\/bkcharts\.min\.js/,
                    name: 'bkcharts',
                    chunks: 'all',
                    priority: 100
                },
                jquery: {
                    test: /jquery/,
                    name: 'jquery',
                    chunks: 'all',
                    priority: 100
                }
            }
        },
        runtimeChunk: {}
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, '../src/'),
            'vue': 'vue/dist/vue.esm.js'
        },
        extensions: ['*', '.js', '.vue', '.json'],
        fallback: {
            path: false,
            buffer: false
        }
    },
    node: false
}
