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
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const VueLoaderPlugin = require('vue-loader/lib/plugin')

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

const publicPath = path.posix.join(SITE_URL, '/static/')

console.log('build mode:', process.env.NODE_ENV)
console.log('SITE_URL:', SITE_URL)
console.log('publicPath:', publicPath)

module.exports = {
    entry: {
        main: './src/main.js'
    },
    output: {
        path: path.join(__dirname, '../static'),
        publicPath: publicPath,
        pathinfo: true,
        filename: path.posix.join(process.env.STATIC_ENV, 'dist/js/[name].js')
    },
    module: {
        rules: [
            {
                test: require.resolve('jquery'),
                use: [
                    {
                        loader: 'expose-loader',
                        options: 'jQuery'
                    },
                    {
                        loader: 'expose-loader',
                        options: '$'
                    }
                ]
            },
            {
                enforce: 'pre',
                test: /\.(js|vue)$/,
                loader: 'eslint-loader',
                exclude: /node_modules/
            },
            {
                test: /\.s?[ac]ss$/,
                use: [
                    process.env.NODE_ENV === 'development' ?
                        'style-loader' :
                        MiniCssExtractPlugin.loader,
                    'css-loader',
                    'postcss-loader',
                    'sass-loader'
                ]

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
                    path.join(__dirname, "../node_modules")
                ]
            },
            {
                test: /\.js$/,
                loader: 'babel-loader',
                exclude: [
                    path.join(__dirname, "../node_modules")
                ]
            },
            {
                test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
                loader: 'url-loader',
                options: {
                    limit: 10000,
                    name: path.posix.join('/images/[name].[ext]')
                }
            },
            {
                test: /\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/,
                loader: 'url-loader',
                options: {
                    limit: 10000,
                    name: path.posix.join(process.env.STATIC_ENV, 'dist/videos/[name].[ext]')
                }
            },
            {
                test: /\.(woff2?|eot|ttf|otf|svg)(\?.*)?$/,
                loader: 'url-loader',
                exclude: [
                    path.join(__dirname, '../src/assets/images/'),
                    path.join(__dirname, '../src/assets/bk-magic/images/')
                ],
                options: {
                    limit: 10000,
                    name: path.posix.join(process.env.STATIC_ENV, 'dist/fonts/[name].[ext]')
                }
            }
        ]
    },
    plugins: [
        new VueLoaderPlugin(),
        new HtmlWebpackPlugin({
            template: './src/assets/html/template.html',
            filename: path.posix.join(process.env.STATIC_ENV, 'dist/index.html')
        }),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
            'window.jQuery': 'jquery'
        })
    ],
    optimization: {
        splitChunks: {
            cacheGroups: {
                vendors: { // 框架相关
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
                plotly: {
                    test: /plotly.js\/dist\/plotly-basic\.min\.js/,
                    name: 'plotly',
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
        runtimeChunk: {

        }
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, '../src/'),
            'vue': 'vue/dist/vue.esm.js'
        },
        extensions: ['*', '.js', '.vue', '.json']
    },
    node: {
        fs: 'empty'
    }
}
