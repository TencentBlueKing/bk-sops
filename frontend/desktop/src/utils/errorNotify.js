// 接口异常通知提示
import i18n from '@/config/i18n/index.js'
import bus from '@/utils/bus.js'
export default class ErrorNotify {
    constructor (errorInfo, vueInstance) {
        const { msg, type, traceId, errorSource, title } = errorInfo
        this.type = type
        // 标题
        const msgTitle = title || this.getTitleAndContent(msg, true, errorSource)
        
        // 详情
        let details = {}
        const msgLabel = type === 'success' ? 'success_msg' : 'error_msg'
        details[msgLabel] = this.getTitleAndContent(msg, false, errorSource, 0)
        if (traceId) {
            details.trace_id = traceId
        }
        if (errorSource === 'result') {
            details.error_func = this.getTitleAndContent(msg, false, errorSource, 1) || '--'
        }
        details = JSON.stringify(details)

        // 助手
        const helperUrl = type === 'success' ? '' : window.MESSAGE_HELPER_URL || ''

        // 工具列表
        const actions = [
            { id: 'assistant', disabled: !helperUrl },
            { id: 'details' },
            { id: 'fix' },
            { id: 'close' }
        ]
        vueInstance.$bkMessage({
            message: {
                title: msgTitle,
                details,
                assistant: helperUrl,
                type: 'key-value'
            },
            actions,
            theme: type,
            ellipsisLine: 2,
            ellipsisCopy: true,
            extCls: 'interface-exception-notify-message',
            onClose: () => {
                const index = window.msg_list.findIndex(item => item.msg === msg)
                if (index > -1) {
                    window.msg_list.splice(index, 1)
                }
                bus.$emit('onCloseErrorNotify', details)
            }
        })
    }
    getTitleAndContent (info, isTitle, errorSource, msgIndex) {
        let content = ''
        if (errorSource !== 'result') {
            if (info.match(': ')) {
                const infoArr = info.split(': ')
                if (isTitle) {
                    content = infoArr[0].indexOf('{') !== -1 ? infoArr[0].split('{')[1].replace(/\'|\"/g, '') : infoArr[0]
                } else {
                    content = infoArr[1].indexOf('}') !== -1 ? infoArr[1].split('}')[0] : infoArr[1]
                }
            } else {
                content = isTitle ? '' : info
            }
        } else {
            const { message } = JSON.parse(info)
            const regex = /([^:]*)?: (.*)?/ // 标准数据结构
            if (regex.test(message)) {
                const arr = message.match(regex)
                content = isTitle ? arr[1] : arr[2]?.split(' | ')[msgIndex]
            } else {
                content = isTitle ? message : message?.split(' | ')[msgIndex]
            }
        }
        if (isTitle && !content) {
            content = this.type === 'success'
                ? i18n.t('请求成功')
                : errorSource === 'result'
                    ? i18n.t('请求异常（外部系统错误或非法操作）')
                    : i18n.t('请求异常（内部系统发生未知错误）')
        }
        return content
    }
}
