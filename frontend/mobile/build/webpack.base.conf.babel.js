/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import webpack from 'webpack'
import {VueLoaderPlugin} from 'vue-loader'
import friendlyFormatter from 'eslint-friendly-formatter'

import {resolve, assetsPath} from './util'
import config from './config'

const isProd = process.env.NODE_ENV === 'production'

export default {
    output: {
        path: isProd ? config.build.assetsRoot : config.dev.assetsRoot,
        filename: '[name].js',
        publicPath: isProd ? config.build.assetsPublicPath : config.dev.assetsPublicPath
    },

    resolve: {
        // 指定以下目录寻找第三方模块，避免 webpack 往父级目录递归搜索，
        // 默认值为 ['node_modules']，会依次查找./node_modules、../node_modules、../../node_modules
        modules: [resolve('src'), resolve('node_modules')],
        extensions: ['.js', '.vue', '.json'],
        alias: {
            'vue$': 'vue/dist/vue.esm.js',
            'jquery': 'jquery',
            '@': resolve('src')
        }
    },

    module: {
        noParse: [
            /\/node_modules\/jquery\/dist\/jquery\.min\.js$/,
            /\/node_modules\/echarts\/dist\/echarts\.min\.js$/
        ],
        rules: [
            {
                test: /\.(js|vue)$/,
                loader: 'eslint-loader',
                enforce: 'pre',
                include: [resolve('src'), resolve('test'), resolve('static')],
                exclude: /node_modules/,
                options: {
                    formatter: friendlyFormatter
                }
            },
            {
                test: /\.vue$/,
                use: {
                    loader: 'vue-loader',
                    options: {
                        extractCSS: true
                    }
                }
            },
            {
                test: /\.js$/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        // include: [resolve('src')],
                        include: [resolve('src'), resolve('node_modules/@tencent/bk-magic-vue')],
                        cacheDirectory: './webpack_cache/',
                        // 确保 JS 的转译应用到 node_modules 的 Vue 单文件组件
                        exclude: file => (
                            /node_modules/.test(file) && !/\.vue\.js/.test(file)
                        )
                    }
                }
            },
            {
                test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
                loader: 'url-loader',
                options: {
                    limit: 10000,
                    name: assetsPath('images/[name].[ext]')
                }
            },
            {
                test: /\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/,
                use: {
                    loader: 'url-loader',
                    options: {
                        limit: 10000,
                        name: assetsPath('media/[name].[ext]')
                    }
                }
            },
            {
                test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/,
                use: {
                    loader: 'url-loader',
                    options: {
                        limit: 1,
                        name: assetsPath('fonts/[name].[ext]')
                    }
                }
            }
        ]
    },
    plugins: [
        new VueLoaderPlugin(),
        // moment 优化，只提取本地包
        new webpack.ContextReplacementPlugin(/moment\/locale$/, /zh-cn/),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
            'window.jQuery': 'jquery'
        })
    ]
}
