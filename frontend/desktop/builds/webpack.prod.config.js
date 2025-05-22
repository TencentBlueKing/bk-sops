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
const merge = require('webpack-merge')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const TerserPlugin = require('terser-webpack-plugin')
const CleanWebpackPlugin = require('clean-webpack-plugin')
const webpackBaseConfig = require('./webpack.base.js')
const CopyPlugin = require('copy-webpack-plugin')

// const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin

module.exports = merge(webpackBaseConfig, {
    mode: 'production',
    output: {
        publicPath: '{{BK_STATIC_URL}}',
        filename: 'js/[name].[contenthash:10].js'
    },
    module: {
        rules: [
            {
                test: /\.s?[ac]ss$/,
                exclude: /node_modules/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                        options: {
                            publicPath: '../'
                        }
                    },
                    'css-loader',
                    'postcss-loader',
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
                    {
                        loader: MiniCssExtractPlugin.loader,
                        options: {
                            publicPath: '../'
                        }
                    },
                    'css-loader'
                ]
            }

        ]
    },
    plugins: [
        new CleanWebpackPlugin([path.resolve('static')], {
            root: process.cwd(),
            verbose: true,
            dry: false
        }),
        new HtmlWebpackPlugin({
            template: './src/assets/html/index.html',
            filename: path.posix.join('index.html')
        }),
        // 只打 moment.js 中文包，减小体积
        new webpack.ContextReplacementPlugin(/moment[\/\\]locale$/, /zh-cn/),
        new MiniCssExtractPlugin({
            filename: 'css/[name].[contenthash:10].css'
        }),
        new CopyPlugin([
            {
                from: path.resolve(__dirname, '../src/assets/html/login_success.html'),
                to: path.resolve(__dirname, '../static/')
            }
        ])
        // new BundleAnalyzerPlugin()
    ],
    optimization: {
        minimizer: [
            new TerserPlugin({
                cache: true,
                parallel: true,
                sourceMap: false,
                extractComments: false
            })
        ]
    },
    stats: {
        performance: true,
        chunks: false,
        entrypoints: false,
        modules: false,
        children: false,
        publicPath: true,
        colors: true,
        errors: true,
        warnings: true
    },
    performance: {
        // maxEntrypointSize: 500000,
        // hints: "error"
    },
    devtool: false
})
