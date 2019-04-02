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
        port: 9001,
        assetsSubDirectory: 'static',
        assetsPublicPath: '/',
        proxyTable: {
            'xx_repalce': { // 需要代理的路径
                target: 'xx_repalce', // 目标服务器host
                secure: false,
                changeOrigin: true,
                headers: {
                    referer: 'xx_repalce' // 目标服务器host
                }
            }
        },
        cssSourceMap: false,
        autoOpenBrowser: false
    }
}
