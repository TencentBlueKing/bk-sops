// 接口异常通知提示，出现在页面右上角，10s后自动关闭，鼠标hover时暂停计时
import i18n from '@/config/i18n/index.js'
import bus from '@/utils/bus.js'
export default class ErrorNotify {
    constructor (errorInfo, vueInstance) {
        const { msg, type, traceId, errorSource, content } = errorInfo
        const h = vueInstance.$createElement
        this.showMore = false
        this.isPlugin = !errorSource
        this.notify = vueInstance.$bkNotify({
            theme: type,
            offsetY: 80,
            limit: 5,
            limitLine: 0,
            delay: 0,
            title: this.setNotifyTitleAndContent(msg, true, errorSource),
            message: h('div',
                [
                    traceId || msg ? h('p', {
                        class: 'toggle-btn',
                        style: { position: 'absolute', top: '24px', right: '36px', color: '#3a84ff', cursor: 'pointer' },
                        on: {
                            click: () => {
                                this.toggleShowMore()
                            }
                        }
                    }, [i18n.t('展开详情')]) : '',
                    h('div', {
                        class: 'bk-notify-content-text',
                        style: this.showMore ? {} : {
                            'display': '-webkit-box',
                            'overflow': 'hidden',
                            'text-overflow': 'ellipsis',
                            'word-break': 'break-all',
                            '-webkit-line-clamp': '2',
                            '-webkit-box-orient': 'vertical'
                        }
                    }, [
                        msg ? this.setNotifyTitleAndContent(msg, false, errorSource, 0, content) : ''
                    ]),
                    h('div', {
                        class: 'bk-notify-trace-content',
                        style: { display: 'none', maxHeight: '300px', overflow: 'auto', margin: '10px 0 0 0' }
                    }, [
                        traceId ? h('p', [`trace_id：${traceId}`]) : '',
                        msg && errorSource === 'result' ? h('p', ['error_function: ', this.setNotifyTitleAndContent(msg, false, errorSource, 1) || '--']) : ''
                    ]),
                    h('bk-button', {
                        class: 'copy-btn',
                        style: { display: 'none', position: 'relative', margin: '10px 10px 0 auto' },
                        on: {
                            click: () => {
                                this.handleCopy(vueInstance, errorInfo)
                            }
                        }
                    }, [i18n.t('复制')])
                ]
            ),
            onClose: this.handleClose
        })
        
        // 内容区域及进度条样式处理
        this.notify.$el.style.width = '450px'
        this.notify.$el.style.zIndex = '2500'
        // 插件提示展示在top-center
        if (this.isPlugin) this.notify.$el.style.left = 'calc(50% - 225px)'
        const progressWrap = document.createElement('div')
        const bar = document.createElement('div')
        progressWrap.style.cssText = 'position: absolute; left: 0; bottom: 0; width: 100%; height: 4px; background: #f0f1f5;'
        bar.style.cssText = 'height: 100%; width: 100%; background: #cbcedb;'
        bar.className = 'progress-bar'
        progressWrap.appendChild(bar)
        this.notify.$el.appendChild(progressWrap)

        // title 样式处理
        const notifyContentDom = document.querySelector('.bk-notify-content')
        const titleDom = document.querySelector('.bk-notify-content-title')
        notifyContentDom.style.cssText = 'width: 90%'
        titleDom.style.cssText = 'width: 80%; white-space: nowrap;overflow: hidden; text-overflow: ellipsis;'
        titleDom.title = this.setNotifyTitleAndContent(msg, true, errorSource) || ''

        this.remainingTime = 10000 // 倒数10s
        this.timer = null // 定时器示例
        this.errorMsg = msg // 来自window.msg_list的错误信息
        this.startTimeCountDown(this.remainingTime)
        this.handleMouseEvent()
    }
    setNotifyTitleAndContent (info, isTitle, errorSource, msgIndex, pluginContent) {
        let content = ''
        if (errorSource !== 'result') {
            if (!errorSource) { // 插件报错信息
                content = isTitle ? info : pluginContent
            } else {
                const infoArr = info.split(': ')
                content = isTitle ? infoArr[0].split('{')[1].replace(/\'|\"/g, '') : (infoArr[1] || infoArr[0]).split('}')[0]
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
        if (isTitle && (!content || content.length > 21)) { // 21为标题能容纳的最大数量
            content = errorSource === 'result' ? i18n.t('请求异常（外部系统错误或非法操作）') : i18n.t('请求异常（内部系统发生未知错误）')
        }
        return content
    }
    // 开始倒计时
    startTimeCountDown () {
        if (!this.notify) {
            return
        }
        this.timer = setTimeout(() => {
            if (this.remainingTime > 0) {
                this.remainingTime -= 100
                this.notify.$el.querySelector('.progress-bar').style.width = `${(this.remainingTime / 10000) * 100}%`
                this.startTimeCountDown()
            } else {
                const index = window.msg_list.findIndex(item => item.msg === this.errorMsg)
                if (index > -1) {
                    window.msg_list.splice(index, 1)
                }
                this.notify.$el.removeEventListener('mouseenter', this.stopTimeCountDown, false)
                this.notify.$el.removeEventListener('mouseleave', this.startTimeCountDown, false)
                this.notify && this.notify.close()
                this.notify = null
            }
        }, 100)
    }
    stopTimeCountDown () {
        this.timer && clearTimeout(this.timer)
    }
    handleMouseEvent () {
        this.notify.$el.addEventListener('mouseenter', this.stopTimeCountDown.bind(this), false)
        this.notify.$el.addEventListener('mouseleave', this.startTimeCountDown.bind(this), false)
    }
    toggleShowMore () {
        this.showMore = !this.showMore
        // 设置切换按钮文案
        const btnDom = this.notify.$el.querySelector('.toggle-btn')
        if (btnDom) {
            btnDom.innerHTML = this.showMore ? i18n.t('隐藏详情') : i18n.t('展开详情')
        }
        // 计算当前展开的notify最大层级
        const notifyErrorDoms = document.querySelectorAll('.bk-notify')
        const zIndexList = [2500] // 默认层级2500
        if (notifyErrorDoms) {
            notifyErrorDoms.forEach(dom => {
                zIndexList.push(Number(dom.style.zIndex))
            })
        }
        this.notify.$el.style.zIndex = this.showMore ? Math.max(...zIndexList) + 1 : 2500
        const contentTextDom = this.notify.$el.querySelector('.bk-notify-content-text')
        if (this.showMore) {
            contentTextDom.classList.add('is-expand')
        } else {
            contentTextDom.scrollTop = 0
            contentTextDom.classList.remove('is-expand')
        }
        this.notify.$el.querySelector('.bk-notify-trace-content').style.display = this.showMore ? 'block' : 'none'
        this.notify.$el.querySelector('.copy-btn').style.display = this.showMore ? 'block' : 'none'
    }
    handleClose (instance) {
        instance.$el.querySelector('.bk-notify-trace-content').style.display = 'none'
        const errorMsg = instance.$el.textContent
        bus.$emit('onCloseErrorNotify', errorMsg)
    }
    handleCopy (vueInstance, errorInfo) {
        const { msg, traceId, errorSource } = errorInfo
        let copyMsg = ''
        if (msg) {
            copyMsg = this.setNotifyTitleAndContent(msg, true, errorSource) + '\n'
            copyMsg = copyMsg + this.setNotifyTitleAndContent(msg, false, errorSource, 0) + '\n'
        }
        if (traceId) {
            copyMsg = copyMsg + `trace_id：${traceId}` + '\n'
        }
        if (msg && errorSource === 'result') {
            copyMsg = copyMsg + 'error_function: ' + this.setNotifyTitleAndContent(msg, false, errorSource, 1) || '--'
        }
        const textarea = document.createElement('textarea')
        document.body.appendChild(textarea)
        textarea.style.position = 'fixed'
        textarea.style.clip = 'rect(0 0 0 0)'
        textarea.style.top = '10px'
        textarea.value = copyMsg
        textarea.select()
        document.execCommand('copy', true)
        document.body.removeChild(textarea)
        vueInstance.$bkMessage({
            theme: 'success',
            message: i18n.t('复制成功')
        })
    }
}
