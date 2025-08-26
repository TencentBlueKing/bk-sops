<template>
    <div
        class="sub-process"
        :style="{ height: `${subprocessHeight}px` }"
        v-bkloading="{ isLoading: loading, opacity: 1, zIndex: 100 }">
        <TemplateCanvas
            ref="subProcessCanvas"
            class="sub-flow"
            :show-palette="false"
            :show-tool="false"
            :editable="false"
            :canvas-data="canvasData"
            @onConditionClick="onOpenConditionEdit"
            @onNodeClick="onNodeClick">
        </TemplateCanvas>
        <div class="flow-option">
            <i
                class="bk-icon icon-narrow-line"
                :class="{ 'disabled': zoom === 0.25 }"
                v-bk-tooltips.top="$t('缩小')"
                @click="onZoomOut">
            </i>
            <i
                class="bk-icon icon-enlarge-line"
                :class="{ 'disabled': zoom === 1.5 }"
                v-bk-tooltips.top="$t('放大')"
                @click="onZoomIn">
            </i>
        </div>
        <!--可拖拽-->
        <template v-if="!loading">
            <div class="resize-trigger" @mousedown.left="handleMousedown($event)"></div>
            <i :class="['resize-proxy', 'top']" :style="{ top: `${subprocessHeight}px` }" ref="resizeProxy"></i>
            <div class="resize-mask" ref="resizeMask"></div>
        </template>
    </div>
</template>

<script>
    import tools from '@/utils/tools.js'
    import TemplateCanvas from '@/components/common/TemplateCanvas/index.vue'
    import lineSuspendState from '@/mixins/lineSuspendState.js'
    export default {
        name: 'subProcessCanvas',
        components: {
            TemplateCanvas
        },
        mixins: [lineSuspendState],
        props: {
            subprocessPipeline: {
                type: Object,
                value: () => ({})
            },
            loading: {
                type: Boolean,
                default: false
            },
            nodeStateMapping: {
                type: Object,
                value: () => ({})
            },
            subprocessState: {
                type: String,
                value: ''
            },
            subprocessHeight: {
                type: [Number, String],
                default: 0
            }
        },
        data () {
            return {
                subprocessLoading: false,
                zoom: 0.75
            }
        },
        computed: {
            canvasData () {
                if (!this.subprocessPipeline) return {}
                const { line, location, gateways, activities } = this.subprocessPipeline
                const branchConditions = {}
                for (const gKey in gateways) {
                    const item = gateways[gKey]
                    if (item.conditions) {
                        branchConditions[item.id] = Object.assign({}, item.conditions)
                    }
                    if (item.default_condition) {
                        const nodeId = item.default_condition.flow_id
                        branchConditions[item.id][nodeId] = item.default_condition
                    }
                }
                return {
                    lines: line,
                    locations: location.map(item => {
                        const code = item.type === 'tasknode' ? activities[item.id].component.code : ''
                        return { ...item, mode: 'execute', checked: true, code, ready: true }
                    }),
                    gateways,
                    branchConditions
                }
            }
        },
        watch: {
            nodeStateMapping: {
                handler (val) {
                    this.updateNodeInfo(val)
                },
                deep: true,
                immediate: true
            },
            subprocessState: {
                handler (val, oldVal) {
                    if ([val, oldVal].includes('SUSPENDED')) {
                        this.handleLinesSuspendState(val)
                    }
                },
                immediate: true
            }
        },
        mounted () {
            this.setCanvasZoomPosition()
        },
        methods: {
            // 更新子流程画布
            updateNodeInfo (nodeStatus) {
                if (!this.subprocessPipeline) return

                this.subprocessPipeline.location.forEach(item => {
                    let code, skippable, retryable, errorIgnorable, autoRetry
                    const currentNode = nodeStatus[item.id]
                    if (!currentNode) return
                    const nodeActivity = this.subprocessPipeline.activities[item.id]

                    if (nodeActivity) {
                        code = nodeActivity.component ? nodeActivity.component.code : ''
                        skippable = nodeActivity.isSkipped || nodeActivity.skippable
                        retryable = nodeActivity.can_retry || nodeActivity.retryable
                        errorIgnorable = nodeActivity.error_ignorable
                        autoRetry = nodeActivity.auto_retry
                    }
                    const data = {
                        code,
                        skippable,
                        retryable,
                        loop: currentNode.loop,
                        status: currentNode.state,
                        skip: currentNode.skip,
                        auto_retry_info: currentNode.retryInfo,
                        retry: currentNode.retry,
                        error_ignored: currentNode.error_ignored,
                        error_ignorable: errorIgnorable,
                        auto_retry: autoRetry,
                        ready: false,
                        task_state: this.state // 任务状态
                    }

                    this.$nextTick(() => {
                        this.onUpdateNodeInfo(item.id, data)
                    })
                })
            },
            onUpdateNodeInfo (id, info) {
                this.$refs.subProcessCanvas && this.$refs.subProcessCanvas.onUpdateNodeInfo(id, info)
            },
            // 移动画布，将节点放到画布中央
            moveNodeToView (id) {
                // 判断dom是否存在当前视图中
                const nodeEl = document.querySelector(`#${id} .canvas-node-item`)
                if (!nodeEl) return
                const isInViewPort = this.judgeInViewPort(nodeEl)
                // 如果不存在需要将节点挪到画布中间
                if (!isInViewPort) {
                    const { width, height } = this.$el.querySelector('#canvasContainer').getBoundingClientRect()
                    const { x, y } = this.canvasData.locations.find(item => item.id === id)
                    const { width: nodeWidth, height: nodeHeight } = nodeEl.getBoundingClientRect()
                    let jsFlowInstance = this.$refs.subProcessCanvas
                    jsFlowInstance = jsFlowInstance.$refs.jsFlow
                    let offsetX = (width - nodeWidth) / 2 - x
                    offsetX = offsetX * jsFlowInstance.zoom
                    let offsetY = (height - nodeHeight) / 2 - y
                    offsetY = offsetY * jsFlowInstance.zoom
                    jsFlowInstance.setCanvasPosition(offsetX, offsetY, true)
                }
            },
            // 画布初始化时缩放比偏移
            setCanvasZoomPosition () {
                if (!this.canvasData.locations) return
                // 设置默认高度
                if (!this.subprocessHeight) {
                    const subprocessDom = document.querySelector('.sub-process')
                    const { top } = subprocessDom.getBoundingClientRect()
                    this.$emit('updateSubprocessHeight', window.innerHeight - top - 320)
                }
                // 设置缩放比例
                let jsFlowInstance = this.$refs.subProcessCanvas
                jsFlowInstance = jsFlowInstance && jsFlowInstance.$refs.jsFlow
                jsFlowInstance && jsFlowInstance.setZoom(this.zoom, 0, 0)
                // 设置偏移量
                const startNode = this.canvasData.locations.find(item => item.type === 'startpoint')
                // 判断dom是否存在当前视图中
                const nodeEl = document.querySelector(`#${startNode.id} .canvas-node-item`)
                if (!nodeEl) return
                const isInViewPort = this.judgeInViewPort(nodeEl)
                if (!isInViewPort) {
                    let jsFlowInstance = this.$refs.subProcessCanvas
                    jsFlowInstance = jsFlowInstance.$refs.jsFlow
                    const offsetX = (20 - startNode.x) * this.zoom
                    const offsetY = (160 - startNode.y) * this.zoom
                    jsFlowInstance && jsFlowInstance.setCanvasPosition(offsetX, offsetY, true)
                }
            },
            // dom是否存在当前视图中
            judgeInViewPort (element) {
                if (!element) return false
                const { width, height, top: canvasTop, left: canvasLeft } = this.$el.querySelector('.sub-flow').getBoundingClientRect()
                const { top, left } = element.getBoundingClientRect()
                return top > canvasTop && top < canvasTop + height && left > canvasLeft && left < canvasLeft + width
            },
            onOpenConditionEdit (data) {
                this.$emit('onNodeClick', `${data.nodeId}-${data.id}`)
            },
            onNodeClick (node) {
                this.$emit('onNodeClick', node)
            },
            onZoomOut () {
                const jsFlowInstance = this.$refs.subProcessCanvas
                jsFlowInstance.onZoomOut()
                this.zoom = jsFlowInstance.zoomRatio / 100
            },
            onZoomIn () {
                const jsFlowInstance = this.$refs.subProcessCanvas
                jsFlowInstance.onZoomIn()
                this.zoom = jsFlowInstance.zoomRatio / 100
            },
            handleMousedown (event) {
                this.updateResizeMaskStyle()
                this.updateResizeProxyStyle()
                document.addEventListener('mousemove', this.handleMouseMove)
                document.addEventListener('mouseup', this.handleMouseUp)
            },
            handleMouseMove (event) {
                const flowDom = this.$el.querySelector('.sub-flow')
                const { top: flowTop } = flowDom.getBoundingClientRect()
                let top = event.clientY - flowTop
                let maxHeight = window.innerHeight - 180
                maxHeight = maxHeight - (this.isShowActionWrap ? 48 : 0)
                top = top > maxHeight ? maxHeight : top
                top = top < 160 ? 160 : top
                const resizeProxy = this.$refs.resizeProxy
                resizeProxy.style.top = `${top}px`
            },
            updateResizeMaskStyle () {
                const resizeMask = this.$refs.resizeMask
                resizeMask.style.display = 'block'
                resizeMask.style.cursor = 'row-resize'
            },
            updateResizeProxyStyle () {
                const resizeProxy = this.$refs.resizeProxy
                resizeProxy.style.visibility = 'visible'
            },
            handleMouseUp () {
                const resizeMask = this.$refs.resizeMask
                const resizeProxy = this.$refs.resizeProxy
                resizeProxy.style.visibility = 'hidden'
                resizeMask.style.display = 'none'
                this.$emit('updateSubprocessHeight', resizeProxy.style.top.slice(0, -2))
                document.removeEventListener('mousemove', this.handleMouseMove)
                document.removeEventListener('mouseup', this.handleMouseUp)
            },
            // 根据子任务的状态，设置边的暂停样式
            handleLinesSuspendState (state) {
                const { activities, gateways, flows } = tools.deepClone(this.subprocessPipeline)
                const children = {
                    ...activities,
                    ...gateways
                }
                Object.values(children).forEach(node => {
                    // 查看输出节点状态
                    let { outgoing } = activities[node.id] || gateways[node.id] || {}
                    if (!Array.isArray(outgoing)) {
                        outgoing = [outgoing]
                    }
                    outgoing.forEach(outLine => {
                        const targetNode = flows[outLine].target
                        const isExecuted = state === 'SUSPENDED' ? (this.nodeStateMapping[node.id].state === 'PENDING_TASK_CONTINUE' || targetNode in children) : true
                        // 输出节点未被执行则表明任务暂停后该分支在当前节点停止往下继续执行
                        this.$nextTick(() => {
                            this.setLineSuspendState({
                                nodeId: node.id,
                                lineId: outLine,
                                isExecuted,
                                location: 0.5,
                                ref: 'subProcessCanvas'
                            })
                        })
                    })
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
.sub-process {
    flex-shrink: 0;
    height: 320px;
    margin: 0 25px 8px 15px;
    position: relative;
    background: #f5f7fa;
    .sub-flow {
        height: 100%;
        border: 0;
       ::v-deep .canvas-wrapper {
            background: #f5f7fa;
        }
        ::v-deep .canvas-flow {
            .active {
                box-shadow: none;
                &::before {
                    content: '';
                    display: block;
                    height: calc(100% + 16px);
                    width: calc(100% + 16px);
                    position: absolute;
                    top: -9px;
                    left: -9px;
                    z-index: -1;
                    background: #e1ecff;
                    border: 1px solid #1768ef;
                    border-radius: 2px;
                }
            }
            .state-icon {
                display: none !important;
            }
            .task-node {
                &.actived {
                    .node-name {
                        border-color: #b4becd !important;
                        background-color: #fff !important;
                    }
                }
            }
            .jtk-connector {
                cursor: default;
            }
        }
        ::v-deep .node-tips-content {
            display: none;
        }
    }
    .flow-option {
        width: 68px;
        height: 32px;
        position: absolute;
        bottom: 16px;
        right: 16px;
        z-index: 5;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        color: #979ba5;
        background: #fff;
        box-shadow: 0 2px 4px 0 #0000001a;
        border-radius: 2px;
        i {
            cursor: pointer;
            &:last-child {
                margin-left: 14px;
            }
            &:hover {
                color: #3a84ff;
            }
            &.disabled {
                color: #ccc;
                cursor: not-allowed;
            }
        }
    }
    .resize-trigger {
        height: 5px;
        width: calc(100% + 40px);
        position: absolute;
        left: -15px;
        bottom: -5px;
        cursor: row-resize;
        z-index: 3;
        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            height: 1px;
            width: 100%;
        }
        &::after {
            content: "";
            position: absolute;
            top: 5px;
            right: 50%;
            width: 2px;
            height: 2px;
            color: #979ba5;
            transform: translate3d(0,-50%,0);
            background: currentColor;
            box-shadow: 4px 0 0 0 currentColor,8px 0 0 0 currentColor,-4px 0 0 0 currentColor,-8px 0 0 0 currentColor;
        }
        &:hover::before {
            background-color: #3a84ff;
        }
    }
    .resize-proxy {
        visibility: hidden;
        position: absolute;
        pointer-events: none;
        z-index: 9999;
        &.top {
            top: 320px;
            left: -15px;
            width: calc(100% + 40px);
            border-top: 1px dashed #3a84ff;
        }
    }
    .resize-mask {
        display: none;
        position: fixed;
        left: 0;
        right: 0;
        top: 0;
        bottom: 0;
        z-index: 9999;
    }
}
</style>
