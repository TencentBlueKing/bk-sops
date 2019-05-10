import path from 'path'
import prodEnv from './prod.env'
import devEnv from './dev.env'

export default {
    build: {
        env: prodEnv,
        assetsRoot: path.resolve(__dirname, '../dist'),
        assetsSubDirectory: 'static',
        assetsPublicPath: '/',
        productionSourceMap: true,
        productionGzip: false,
        productionGzipExtensions: ['js', 'css'],
        bundleAnalyzerReport: process.env.npm_config_report
    },
    dev: {
        env: devEnv,
        host: 'dev.paas.bk.com',
        port: 9001,
        assetsSubDirectory: 'static',
        assetsPublicPath: '/',
        proxyTable: {
            '/ajax': { // 需要代理的路径
                target: 'http://dev.paas.bk.com:8000/', // 目标服务器host
                secure: false,
                pathRewrite: {
                    '^/ajax': ''
                },
                headers: {
                    referer: 'dev.paas.bk.com' // 目标服务器host
                }
            }
        },
        cssSourceMap: false,
        autoOpenBrowser: false
    }
}
