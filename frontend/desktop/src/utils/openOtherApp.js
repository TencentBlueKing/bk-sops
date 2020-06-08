import isCrossOriginIFrame from './isCrossOriginIFrame.js'

/**
 * 打开其他应用，分为页面打开和 PaaS 平台 iframe打开，iframe 可能会出现跨域的情况
 * @param {String} code app 的 code
 * @param {String} url app 跳转链接
 */
export default function (code, url) {
    if (self !== top) { // iframe 打开
        if (isCrossOriginIFrame()) {
            window.open(url, '__blank')
        } else {
            window.PAAS_API.open_other_app(code, url)
        }
    } else {
        window.open(url, '__blank')
    }
}
