import merge from 'webpack-merge'
import prodEnv from './prod.env'

const NODE_ENV = JSON.stringify('development')

export default merge(prodEnv, {
    'process.env': {
        'NODE_ENV': NODE_ENV
    },
    staticUrl: '/static',
    NODE_ENV: NODE_ENV,
    LOGIN_SERVICE_URL: JSON.stringify(''),
    AJAX_URL_PREFIX: JSON.stringify('http://dev.paas.bk.com:9001/ajax'), // 本地开发路径
    SITE_URL: JSON.stringify('')
})
