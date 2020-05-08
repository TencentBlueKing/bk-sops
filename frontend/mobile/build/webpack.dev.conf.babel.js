/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import path from 'path'

import webpack from 'webpack'
import merge from 'webpack-merge'
import CopyWebpackPlugin from 'copy-webpack-plugin'
import HtmlWebpackPlugin from 'html-webpack-plugin'
import FriendlyErrorsPlugin from 'friendly-errors-webpack-plugin'

import config from './config'
import baseConf from './webpack.base.conf.babel'
import manifest from '../static/lib-manifest.json'

import { resolve } from './util'


// const HOST = 'localhost'
// const PORT = 8080

const webpackConfig = merge(baseConf, {
    mode: 'development',
    entry: {
        main: './src/main.js'
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
        new webpack.DefinePlugin(config.dev.env),

        new webpack.DllReferencePlugin({
            context: __dirname,
            manifest: manifest
        }),

        new webpack.HotModuleReplacementPlugin(),

        new webpack.NoEmitOnErrorsPlugin(),

        new HtmlWebpackPlugin({
            filename: 'index.html',
            template: 'index.html',
            inject: true,
            staticUrl: config.dev.env.staticUrl
        }),

        new FriendlyErrorsPlugin(),
        new CopyWebpackPlugin([
            {
                from: resolve('static/images'),
                to: resolve('dist/static/images'),
                toType: 'dir'
            }
        ]),
    ]
})

Object.keys(webpackConfig.entry).forEach(name => {
    webpackConfig.entry[name] = ['./build/dev-client'].concat(webpackConfig.entry[name])
})

export default webpackConfig
