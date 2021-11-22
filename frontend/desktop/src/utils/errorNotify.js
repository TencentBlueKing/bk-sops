// 接口异常通知提示，出现在页面右上角，10s后自动关闭，鼠标hover时暂停计时
export default class ErrorNotify {
    constructor (msg, type = 'error', traceId, vueInstance) {
        this.notify = vueInstance.$bkNotify({
            theme: type,
            offsetY: 80,
            limit: 5,
            limitLine: 0,
            delay: 0,
            title: traceId ? `trace_id: ${traceId}` : '',
            message: msg
        })

        // 内容区域及进度条样式处理
        this.notify.$el.style.width = '580px'
        this.notify.$el.querySelector('.bk-notify-content-text').style.cssText = 'max-height: 140px; overflow: auto;'
        const progressWrap = document.createElement('div')
        const bar = document.createElement('div')
        progressWrap.style.cssText = 'position: absolute; left: 0; bottom: 0; width: 100%; height: 4px; background: #f0f1f5;'
        bar.style.cssText = 'height: 100%; width: 100%; background: #cbcedb;'
        bar.className = 'progress-bar'
        progressWrap.appendChild(bar)
        this.notify.$el.appendChild(progressWrap)

        this.remainingTime = 10000 // 倒数10s
        this.timer = null // 定时器示例
        this.startTimeCountDown(this.remainingTime)
        this.handleMouseEvent()
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
}
