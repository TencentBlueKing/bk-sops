/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
const path = require('path')
const webpack = require('webpack')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const VueLoaderPlugin = require('vue-loader/lib/plugin')

console.log(process.env.NODE_ENV)
console.log(process.env.SITE_URL)
const publicPath = (process.env.SITE_URL || '') + '/static/'
module.exports = {
    entry: {
        main: './src/main.js'
    },
    output: {
        path: path.join(__dirname, '../static'),
        publicPath: publicPath,
        pathinfo: true,
        filename: 'dist/js/[name].js'
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
                    path.resolve(__dirname, "../node_modules")
                ]
            },
            {
                test: /\.js$/,
                loader: 'babel-loader',
                exclude: [
                    path.resolve(__dirname, "../node_modules")
                ]
            },
            {
                test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
                loader: 'url-loader',
                options: {
                    limit: 10000,
                    name: 'dist/images/[name].[ext]'
                }
            },
            {
                test: /\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/,
                loader: 'url-loader',
                options: {
                    limit: 10000,
                    name: 'dist/videos/[name].[ext]'
                }
            },
            {
                test: /\.(woff2?|eot|ttf|otf|svg)(\?.*)?$/,
                loader: 'url-loader',
                exclude: path.join(__dirname, '../src/assets/images/'),
                options: {
                    limit: 10000,
                    name: 'dist/fonts/[name].[ext]'
                }
            }
        ]
    },
    plugins: [
        new VueLoaderPlugin(),
        new HtmlWebpackPlugin({
            template: './src/assets/html/template.html',
            filename: 'dist/index.html'
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
                commons: {
                    test: /[\\/]node_modules[\\/]/,
                    name: 'vendors',
                    chunks: 'all'
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
            // 'jquery': path.resolve(__dirname, 'src/assets/js/jquery-1.10.2.min.js'),
            // 'jsplumb': path.resolve(__dirname, 'src/assets/js/jsplumb.min.js'),
            // 'art-template': path.resolve(__dirname, 'src/assets/js/art-template.js'),
            // 'bkflow': path.resolve(__dirname, 'src/assets/js/bkflow.js')
        },
        extensions: ['*', '.js', '.vue', '.json']
    },
    node: {
        fs: 'empty'
    }
}
