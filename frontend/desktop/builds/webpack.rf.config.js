const path = require('path')
const webpack = require('webpack')
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')


module.exports = {
    entry: {
        renderform: './src/renderForm/entry.js'
    },
    output: {
        path: path.join(__dirname, '../static/renderform'),
    },
    module: {
        rules: [
            {
                test: /\.s?[ac]ss$/,
                use: [
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
                loader: 'url-loader',
                options: {
                    limit: 10000,
                    name: path.posix.join('images/[name].[ext]')
                }
            },
            {
                test: /\.(woff2?|eot|ttf|otf|svg)(\?.*)?$/,
                loader: 'url-loader',
                options: {
                    limit: 10000,
                    name: path.posix.join('dist/fonts/[name].[ext]')
                }
            }
        ]
    },
    plugins: [
        new VueLoaderPlugin(),
        new MiniCssExtractPlugin({
            filename: path.posix.join('dist/css/[name].css')
        })
    ],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, '../src/'),
            'vue': 'vue/dist/vue.esm.js'
        }
    },
    externals: {
        vue: 'vue',
        vuex: 'vuex'
    },
    mode: 'production'
}