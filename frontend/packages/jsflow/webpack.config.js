const path = require('path')
const webpack = require('webpack')
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const FriendlyErrorsPlugin = require('friendly-errors-webpack-plugin')

module.exports = {
    entry: {
        'main': './site/main.js'
    },
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, 'dist')
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                loader: 'eslint-loader',
                options: {
                    formatter: require('eslint-friendly-formatter'),
                    emitWarning: false
                },
                enforce: 'pre',
                exclude: /node_modules/
            },
            {
                test: /\.js$/,
                use: [
                    'babel-loader'
                ],
                exclude: /node_modules/
            },
            {
                test: /\.s?[ac]ss$/,
                use: [
                    'style-loader',
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
                exclude: /node_modules/
            },
            {
                test: /\.md$/,
                loader: 'raw-loader',
                exclude: /node_modules/
            },
            {
                test: /\.art$/,
                use: ['art-template-loader'],
                exclude: /node_modules/
            },
            {
                test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
                loader: 'url-loader',
                options: {
                    limit: 10000
                }
            }
        ]
    },
    resolve: {
        extensions: ['.js', '.json', '.vue', '.css'],
        alias: {
            // 'vue$': 'vue/dist/vue.esm.js'
        }
    },
    plugins: [
        new VueLoaderPlugin(),
        new HtmlWebpackPlugin({
            title: 'jsflow',
            template: '!!html-loader!site/index.html'
        }),
        new FriendlyErrorsPlugin(),
        new webpack.HotModuleReplacementPlugin()
    ],
    externals: {
    },
    optimization: {
        splitChunks: {
            cacheGroups: {
                test: 'node_modules/',
                name: 'vendors',
                chunks: 'all'
            }
        }
    },
    devtool: 'inline-source-map',
    mode: 'development',
    devServer: {
        port: 8001,
        hot: true,
        open: false,
        overlay: {
            warnings: false,
            errors: true
        },
        historyApiFallback: true,
        stats: {
            colors: true,
            children: false,
            chunks: false,
            modules: false
        }
    }
}
