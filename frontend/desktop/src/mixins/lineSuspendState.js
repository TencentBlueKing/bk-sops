import tools from '@/utils/tools.js'

const lineSuspendState = {
    data () {
        return {
            suspendLines: []
        }
    },
    methods: {
        setLineSuspendState (info) {
            const { nodeId, lineId, isExecuted, location = 0.5, ref } = info
            const tplInstance = this.$refs[ref]
            const line = this.canvasData.lines.find(item => item.id === lineId)
            // 分支添加暂停icon
            if (isExecuted) {
                // 删除label
                const pauseDom = document.querySelector(`.suspend-${lineId}`)
                if (pauseDom) {
                    tplInstance.setPaintStyle(lineId, '#a9adb6')
                    tplInstance.$refs.jsFlow.removeLineOverlay(line, `suspend-${lineId}`)
                    const index = this.suspendLines.findIndex(item => item === lineId)
                    this.suspendLines.splice(index, 1)
                }
            } else if (!this.suspendLines.includes(lineId) && location > 0) {
                // 设置连线颜色
                tplInstance.setPaintStyle(lineId, '#ffb848')
                const labelData = {
                    type: 'Label',
                    location,
                    name: `<i class="common-icon-pause"></i>`,
                    cls: `suspend-line suspend-${lineId}`,
                    id: `suspend-${lineId}`
                }
                tplInstance.$refs.jsFlow.addLineOverlay(line, labelData)
                // 根据暂停icon所在线段的方向设置平移
                this.$nextTick(() => {
                    const direction = this.judgeIntersectSegmentDirection(tplInstance, line, nodeId)
                    if (direction) {
                        this.$nextTick(() => {
                            const pauseDom = document.querySelector(`.suspend-${lineId}`)
                            if (direction === 'vertical') { // 垂直
                                pauseDom.style.transform = 'rotate(90deg)'
                                const left = pauseDom.style.left.slice(0, -2)
                                pauseDom.style.left = `${Number(left) + 1}px`
                            } else { // 水平
                                const top = pauseDom.style.top.slice(0, -2)
                                pauseDom.style.top = `${Number(top) + 1}px`
                            }
                            this.suspendLines.push(lineId)
                        })
                    } else if (!direction) { // icon正在停在弯曲线段上
                        // 给曲线上的icon添加偏移计算量太大，改为删除旧的label生成一条偏移量location - 0.1的label
                        tplInstance.$refs.jsFlow.removeLineOverlay(line, `suspend-${lineId}`)
                        this.setLineSuspendState({
                            ...info,
                            location: location - 0.1
                        })
                    }
                })
            }
        },
        // 计算与暂停图标相交的线段方向
        judgeIntersectSegmentDirection (tplInstance, line, nodeId) {
            // 节点尺寸坐标
            const pauseDom = document.querySelector(`.suspend-${line.id}`)
            const iconPos = this.getDomPos(pauseDom)
            const { width: iWidth, height: iHeight } = pauseDom.getBoundingClientRect()
            // 存在偏移，所以真实坐标需要减去高/宽的一半
            iconPos.left = iconPos.left - iWidth / 2
            iconPos.top = iconPos.top - iHeight / 2

            // 暂停图标是在水平线还是垂直线还是曲线
            let direction = ''
            // 获取连线实例
            let connection = tplInstance.$refs.jsFlow.getConnectorsByNodeId(nodeId)
            if (Array.isArray(connection)) {
                connection = connection.find(item => item.sourceId === line.source.id && item.targetId === line.target.id)
            }
            // 连线各个线段
            const { left: lineLeft, top: lineTop } = this.getDomPos(connection.canvas)
            let segments = connection.connector.getSegments()
            // 第一段线段坐标
            const { x1, x2, y1, y2 } = segments[0].params
            const firstSegmentWidth = x2 - x1
            const firstSegmentHeight = y2 - y1
            // 切除插入到节点内部的两端线段
            segments = segments.slice(1, -1)
            // 克隆线段列表，直线时会对线段宽高重新计算，避免影响
            segments = tools.deepClone(segments)
            // 纯直线会重叠了1px，为线的折点预留的位置
            if (segments.length === 2 && segments.every(item => item.type === 'Straight')) {
                // 整合为一条线段
                let params = {}
                const { x1, x2, y1, y2 } = segments[0].params
                if (x1 === x2) {
                    if (y1 > y2) {
                        params = { x1: 0, x2: 0, y1, y2: 0 }
                    } else {
                        params = { x1: 0, x2: 0, y1: 0, y2: y2 * 2 }
                    }
                } else if (y1 === y2) {
                    if (x1 > x2) {
                        params = { x1, x2: 0, y1: 0, y2: 0 }
                    } else {
                        params = { x1: 0, x2: x2 * 2, y1: 0, y2: 0 }
                    }
                }
                segments[0].params = params
                segments = segments.slice(0, 1)
            }
            segments.some((item, index) => {
                // 过滤掉圆弧线段
                if (item.type === 'Arc') return false
                // 计算线段的高宽和坐标
                const { x1, x2, y1, y2 } = item.params
                // 线段的坐标的最大值/最小值
                const minX = Math.min(x1, x2)
                const minY = Math.min(y1, y2)
                let arcHeight = 0
                const prevSegment = segments[index - 1]
                const nextSegment = segments[index + 1]

                let left, top
                if (x1 === x2) { // 垂直
                    top = lineTop + minY + firstSegmentHeight
                    left = lineLeft + minX + firstSegmentWidth
                    if (left > iconPos.left && left < iconPos.left + iWidth) {
                        direction = 'vertical'
                    }
                } else if (y1 === y2) { // 水平
                    if (prevSegment?.type === 'Arc') {
                        const { y1: prevY1, y2: prevY2, r } = prevSegment.params
                        arcHeight = Math.min(prevY1, prevY2) < y1 ? r : 0
                    } else if (!arcHeight && nextSegment?.type === 'Arc') {
                        const { y1: nextY1, y2: nextY2, r } = nextSegment.params
                        arcHeight = Math.min(nextY1, nextY2) < y1 ? r : 0
                    }
                    top = lineTop + minY + firstSegmentHeight + arcHeight
                    left = lineLeft + minX + firstSegmentWidth
                    if (top > iconPos.top && top < iconPos.top + iHeight) {
                        direction = 'horizontal'
                    }
                }
                return !!direction
            })
            return direction
        },
        getDomPos (dom) {
            let { cssText } = dom.style
            cssText = cssText.split(';').filter(value => /:.(\-)?[0-9.]+px/.test(value))
            let left = cssText.find(item => item.indexOf('left') > -1)
            left = left ? /:.((\-)?[0-9.]+)px/.exec(left)[1] : 0
            left = Number(left)
            let top = cssText.find(item => item.indexOf('top') > -1)
            top = top ? /:.((\-)?[0-9.]+)px/.exec(top)[1] : 0
            top = Number(top)
            return { left, top }
        }
    }
}

export default lineSuspendState
