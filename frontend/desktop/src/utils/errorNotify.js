// 接口异常通知提示，出现在页面右上角，10s后自动关闭，鼠标hover时暂停计时
import i18n from '@/config/i18n/index.js'
export default class ErrorNotify {
    constructor (errorInfo, vueInstance) {
        const { msg, type, traceId, errorSource } = errorInfo
        const h = vueInstance.$createElement
        this.showMore = false
        this.notify = vueInstance.$bkNotify({
            theme: type,
            offsetY: 80,
            limit: 5,
            limitLine: 0,
            delay: 0,
            title: errorSource === 'result' ? this.setNotifyTitleAndContent(msg, 'title') : i18n.t('请求异常（内部系统发生未知错误）'),
            message: h('div',
                [
                    traceId || msg ? h('p', {
                        style: { position: 'absolute', top: '24px', right: '36px', color: '#3a84ff', cursor: 'pointer' },
                        on: {
                            click: () => {
                                this.toggleShowMore()
                            }
                        }
                    }, [i18n.t('查看更多')]) : '',
                    h('div', {
                        class: 'bk-notify-content-text',
                        style: { display: 'none', maxHeight: '300px', overflow: 'auto' }
                    }, [
                        traceId ? h('p', [`trace_id：${traceId}`]) : '',
                        msg ? h('p', [this.setNotifyTitleAndContent(msg, 'content')]) : ''
                    ]),
                    h('bk-button', {
                        class: 'copy-btn',
                        style: { display: 'none', position: 'relative', margin: '10px 10px 0 auto' },
                        on: {
                            click: () => {
                                this.handleCopy(vueInstance, traceId ? `trace_id：${traceId}\n${msg}` : msg)
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
        const progressWrap = document.createElement('div')
        const bar = document.createElement('div')
        progressWrap.style.cssText = 'position: absolute; left: 0; bottom: 0; width: 100%; height: 4px; background: #f0f1f5;'
        bar.style.cssText = 'height: 100%; width: 100%; background: #cbcedb;'
        bar.className = 'progress-bar'
        progressWrap.appendChild(bar)
        this.notify.$el.appendChild(progressWrap)

        // title 样式处理
        const titleDom = document.querySelector('.bk-notify-content-title')
        titleDom.style.cssText = 'width: 80%; white-space: nowrap;overflow: hidden; text-overflow: ellipsis;'
        titleDom.title = this.setNotifyTitleAndContent(msg, 'title') || ''

        this.remainingTime = 10000 // 倒数10s
        this.timer = null // 定时器示例
        this.errorMsg = msg // 来自window.msg_list的错误信息
        this.startTimeCountDown(this.remainingTime)
        this.handleMouseEvent()
    }
    setNotifyTitleAndContent (info, type) {
        return type === 'title' ? JSON.parse(info).message.split(':')[0] : JSON.parse(info).message.split(':').slice(1).join(':')
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
        // 计算当前展开的notify最大层级
        const notifyErrorDoms = document.querySelectorAll('.bk-notify')
        const zIndexList = [2500] // 默认层级2500
        if (notifyErrorDoms) {
            notifyErrorDoms.forEach(dom => {
                zIndexList.push(Number(dom.style.zIndex))
            })
        }
        this.notify.$el.style.zIndex = this.showMore ? Math.max(...zIndexList) + 1 : 2500
        this.notify.$el.querySelector('.bk-notify-content-text').style.display = this.showMore ? 'block' : 'none'
        this.notify.$el.querySelector('.copy-btn').style.display = this.showMore ? 'block' : 'none'
    }
    handleClose (instance) {
        instance.$el.querySelector('.bk-notify-content-text').style.display = 'none'
    }
    handleCopy (vueInstance, msg) {
        const textarea = document.createElement('textarea')
        document.body.appendChild(textarea)
        textarea.style.position = 'fixed'
        textarea.style.clip = 'rect(0 0 0 0)'
        textarea.style.top = '10px'
        textarea.value = msg
        textarea.select()
        document.execCommand('copy', true)
        document.body.removeChild(textarea)
        vueInstance.$bkMessage({
            theme: 'success',
            message: i18n.t('复制成功')
        })
    }
}
