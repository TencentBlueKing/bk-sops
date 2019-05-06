<template xmlns:v-slot="http://www.w3.org/1999/XSL/Transform">
    <div class="jsflow">
        <div v-if="showTool" class="tool-panel-wrap">
            <ToolPanel
                :tools="tools"
                :is-frame-selecting="isFrameSelecting"
                @onToolClick="onToolClick">
            </ToolPanel>
        </div>
        <div v-if="showPalette" class="palette-panel-wrap">
            <palette-panel
                ref="palettePanel"
                :selector="selector"
                @registerPaletteEvent="registerPaletteEvent">
                <template v-slot:palette>
                    <slot name="palette"></slot>
                </template>
            </palette-panel>
        </div>
        <div
            ref="canvasFlowWrap"
            class="canvas-flow-wrap"
            :style="canvasWrapStyle"
            @click="hideToolTips"
            @[mousedown]="onCanvasMouseDown"
            @[mouseup]="onCanvasMouseUp">
            <div
                ref="canvasFlow"
                id="canvas-flow"
                class="canvas-flow"
                :style="canvasStyle">
                <div v-for="node in nodes" :key="node.id">
                    <div
                        class="jsflow-node"
                        :id="node.id"
                        :style="setNodeInitialPos(node)">
                        <slot name="nodeTemplate" :node="node">
                            <div class="node-default"></div>
                        </slot>
                    </div>
                    <Tooltips :id="['tool' + node.id]" :node="node"></Tooltips>
                </div>

            </div>
            <div
                v-if="isFrameSelecting"
                class="canvas-frame-selector"
                :style="frameSelectorStyle">
            </div>
        </div>
        <div
            v-if="showAddingNode"
            class="jsflow-node adding-node"
            :style="setNodeInitialPos(addingNodeConfig)">
            <slot name="nodeTemplate" :node="addingNodeConfig">
                <div class="node-default"></div>
            </slot>
        </div>
    </div>
</template>
<script>
    import { jsPlumb } from 'jsplumb'
    import PalettePanel from './PalettePanel.vue'
    import ToolPanel from './ToolPanel.vue'
    import Tooltips from './Tooltips.vue'
    import { matchSelector } from '../../../static/jsflow/dom.js'
    import { uuid } from '../../../static/jsflow/uuid.js'

    const props = {
        showPalette: {
            type: Boolean,
            default: false
        },
        showTool: {
            type: Boolean,
            default: false
        },
        tools: { // 工具栏选项，通过传入值来选择工具项及其顺序
            type: Array,
            default () {
                return [
                    {
                        type: 'zoomIn',
                        cls: ''
                    },
                    {
                        type: 'zoomOut',
                        cls: ''
                    },
                    {
                        type: 'resetPostions',
                        cls: ''
                    },
                    {
                        type: 'frameSelect',
                        cls: ''
                    }
                ]
            }
        },
        editable: {
            type: Boolean,
            default: false
        },
        isPreview: {
            type: Boolean,
            default: false
        },
        selector: {
            type: String,
            default: 'palette-item'
        },
        data: {
            type: Object,
            default () {
                return {
                    nodes: [],
                    lines: []
                }
            }
        },
        options: {
            type: Object,
            default: function _default () {
                return {
                    PaintStyle: {
                        strokeWidth: 1,
                        stroke: '#666',
                        outlineWidth: 1
                    },
                    Connector: ['Straight'],
                    Overlays: [['Arrow', { width: 6, length: 6, location: 1 }]],
                    Anchors: ['Left', 'Right']
                }
            }
        },
        nodeOptions: { // 节点配置项

        },
        connectorOptions: {
            // 连接线配置项
            type: Object,
            default: function _default () {
                return {
                    paintStyle: {
                        strokeWidth: 1,
                        stroke: '#aaa',
                        outlineWidth: 1
                    },
                    Overlays: [['Arrow', { width: 6, length: 6, location: 1 }]],
                    connector: ['Flowchart']
                }
            }
        },
        endpointOptions: {
            // 端点配置项
            type: Object,
            default: function _default () {
                return {
                    endpoint: 'Rectangle',
                    anchor: ['Top', 'Right', 'Bottom', 'Left'],
                    isSource: false,
                    isTarget: true,
                    paintStyle: {},
                    hoverPaintStyle: {}
                }
            }
        }
    }

    const eventDict = {
        'mousedown': 'ontouchstart' in document.documentElement ? 'touchstart' : 'mousedown',
        'mousemove': 'ontouchmove' in document.documentElement ? 'touchmove' : 'mousemove',
        'mouseup': 'ontouchend' in document.documentElement ? 'touchend' : 'mouseup',
        'click': 'ontouchstart' in document.documentElement ? 'touchstart' : 'click'
    }

    export default {
        name: 'MobileNodeCanvas',
        components: {
            PalettePanel,
            ToolPanel,
            Tooltips
        },
        model: {
            prop: 'data',
            event: 'change'
        },
        props,
        data () {
            const { nodes, lines } = this.data
            return {
                nodes,
                lines,
                canvasGrabbing: false,
                isFrameSelecting: false,
                mouseDownPos: {},
                canvasPos: { x: 0, y: 0 },
                canvasOffset: { x: 0, y: 0 },
                frameSelectorPos: { x: 0, y: 0 },
                frameSelectorRect: { width: 0, height: 0 },
                selectedNodes: [],
                showAddingNode: false,
                addingNodeConfig: {},
                addingNodeRect: {},
                canvasRect: {},
                paletteRect: {},
                zoom: 1,
                ...eventDict
            }
        },
        computed: {
            canvasWrapStyle () {
                let cursor = ''
                if (this.isFrameSelecting) {
                    cursor = 'crosshair'
                } else {
                    cursor = this.canvasGrabbing ? '-webkit-grabbing' : '-webkit-grab'
                }
                return { cursor }
            },
            canvasStyle () {
                return {
                    left: `${this.canvasOffset.x}px`,
                    top: `${this.canvasOffset.y}px`
                }
            },
            frameSelectorStyle () {
                return {
                    left: `${this.frameSelectorPos.x}px`,
                    top: `${this.frameSelectorPos.y}px`,
                    width: `${this.frameSelectorRect.width}px`,
                    height: `${this.frameSelectorRect.height}px`
                }
            }
        },
        watch: {
            data: {
                handler (val) {
                    const { nodes, lines } = val
                    this.nodes = nodes
                    this.lines = lines
                },
                deep: true
            }
        },
        mounted () {
            this.initCanvas()
            // this.registerEvent()
            this.renderData()
            this.canvasRect = this.$refs.canvasFlow.getBoundingClientRect()
            if (this.$refs.palettePanel) {
                this.paletteRect = this.$refs.palettePanel ? this.$refs.palettePanel.$el.getBoundingClientRect() : {}
            }
        },
        beforeDestroy () {
            if (this.$refs.palettePanel) {
                this.$refs.palettePanel.$el.removeEventListener(this.mousedown, this.nodeCreateHandler)
            }
            // this.$el.removeEventListener(this.mousemove, this.nodeMovingHandler)
            // document.removeEventListener(this.mouseup, this.nodeMoveEndHandler)
        },
        methods: {
            initCanvas () {
                this.instance = jsPlumb.getInstance({
                    container: 'canvas-flow',
                    ...this.options
                })
            },
            // 注册事件
            registerEvent () {
                // 连线拖动之前，需要返回值
                this.instance.bind('beforeDrag', (params) => {
                    console.log('beforeDrag:', params)
                    return true
                })
                // 连线放下之前，需要返回值
                this.instance.bind('beforeDrop', (params) => {
                    return true
                })
                // 连线吸附之后
                this.instance.bind('connection', (connection) => {
                    console.log('connection')
                })
                // 连线删除之前
                this.instance.bind('beforeDetach', (connection) => {
                    console.log('beforeDetach')
                    return true
                })

                // 连线已删除
                this.instance.bind('connectionDetached', (info, originalEvent) => {
                    const lines = this.lines.filter(line => {
                        return line.source.id !== info.sourceId && line.target.id !== info.targetId
                    })
                    this.lines = lines
                    console.log('connectionDetached')
                })
                // 连线端点移动到另外端点
                this.instance.bind('connectionMoved', (info, originalEvent) => {
                    console.log('connectionMoved')
                })
                // 连线单击
                this.instance.bind('click', (connection, originalEvent) => {
                    console.log(connection, originalEvent)
                })
                // 连线双击
                this.instance.bind('dblclick', (connection, originalEvent) => {
                    console.log(connection, originalEvent)
                })
            },
            renderData () {
                this.instance.batch(() => {
                    this.nodes.forEach(node => {
                        // 节点拖拽// this.setNodeDraggable(node)
                        this.setNodeEndPoint(node, this.endpointOptions)
                    })
                    this.lines.forEach(line => {
                        this.createConnector(line, this.connectorOptions)
                    })
                })
            },
            // 创建节点并初始化拖拽
            createNode (node) {
                this.nodes.push(node)
                this.$nextTick(() => {
                    this.setNodeDraggable(node)
                    this.setNodeEndPoint(node, this.endpointOptions)
                })
            },
            // 删除节点
            removeNode (node) {
                const index = this.nodes.findIndex(item => item.id === node.id)
                this.nodes.splice(index, 1)
                this.instance.remove(node.id)
            },
            // 设置节点端点
            setNodeEndPoint (node, options) {
                const endpoints = options.anchor
                endpoints.forEach(item => {
                    this.instance.addEndpoint(node.id, {
                        ...options,
                        anchor: item,
                        uuid: item + node.id
                    })
                })
            },
            /**
             * 设置节点可拖拽
             * @param node 支持节点元素、节点id或者类数组的节点元素、节点id
             */
            setNodeDraggable (node) {
                const vm = this
                this.instance.draggable(node.id, {
                    grid: [20, 20],
                    stop (event) {
                        const index = vm.nodes.findIndex(el => el.id === node.id)
                        const nodeConfig = Object.assign({}, node)
                        const [nodeX, nodeY] = event.pos
                        nodeConfig.x = nodeX
                        nodeConfig.y = nodeY

                        vm.nodes.splice(index, 1, nodeConfig)
                        vm.$emit('onNodeMove', nodeConfig, event)
                    }
                })
            },
            // 设置节点位置
            setNodeInitialPos (node) {
                return {
                    left: `${node.x}px`,
                    top: `${node.y}px`
                }
            },
            // 创建连接线
            createConnector (line, options) {
                const connection = this.instance.connect(
                    {
                        source: line.source.id,
                        target: line.target.id,
                        detachable: false, // 取消端点断开
                        uuids: [line.source.arrow + line.source.id, line.target.arrow + line.target.id]
                    },
                    {
                        label: '',
                        ...options
                    }
                )
                return connection
            },
            // 删除连接线
            removeConnector (line) {
                const connections = this.instance.getConnections({ source: line.source.id, target: line.target.id })
                connections.forEach(connection => {
                    this.instance.detach(connection)
                })
            },
            /**
             * 添加连线overlay
             *
             * @param {Object} line 连线数据对象
             * @param {Object} overlay 连线overlay对象
             * eg: overlay = {
             *    type: 'label',
             *    name: 'xxx',
             *    location: '-60',
             *    cls: 'branch-conditions',
             *    editable: true
             * }
             *
             */
            addLineOverlay (line, overlay) {
                const connections = this.instance.getConnections({ source: line.source.id, target: line.target.id })
                console.log(connections)
                connections.forEach(connection => {
                    connection.addOverlay([overlay.type, {
                        label: overlay.name,
                        location: overlay.location,
                        cssClass: overlay.cls
                    }])
                })
            },
            // 删除连线ovelay
            removeLineOverlay () {},
            onCanvasMouseDown (e) {
                if (this.isFrameSelecting) {
                    this.frameSelectHandler(e)
                } else {
                    this.canvasGrabbing = true
                    if (e.touches && e.touches.length > 0) {
                        const pageX = e.touches[0].pageX
                        const pageY = e.touches[0].pageY
                        this.mouseDownPos = {
                            x: pageX,
                            y: pageY
                        }
                    } else {
                        this.mouseDownPos = {
                            x: e.pageX,
                            y: e.pageY
                        }
                    }
                    this.$refs.canvasFlowWrap.addEventListener(this.mousemove, this.canvasFlowMoveHandler, false)
                }
            },
            canvasFlowMoveHandler (e) {
                if (e.touches && e.touches.length > 0) {
                    const pageX = e.touches[0].pageX
                    const pageY = e.touches[0].pageY
                    this.canvasOffset = {
                        x: this.canvasPos.x + pageX - this.mouseDownPos.x,
                        y: this.canvasPos.y + pageY - this.mouseDownPos.y
                    }
                } else {
                    this.canvasOffset = {
                        x: this.canvasPos.x + e.pageX - this.mouseDownPos.x,
                        y: this.canvasPos.y + e.pageY - this.mouseDownPos.y
                    }
                }
            },
            onCanvasMouseUp (e) {
                if (this.isFrameSelecting) {
                    this.frameSelectEndHandler(e)
                } else {
                    this.canvasGrabbing = false
                    this.$refs.canvasFlowWrap.removeEventListener(this.mousemove, this.canvasFlowMoveHandler)
                    this.canvasPos = {
                        x: this.canvasOffset.x,
                        y: this.canvasOffset.y
                    }
                }
            },
            registerPaletteEvent () {
                if (this.$refs.palettePanel) {
                    this.$refs.palettePanel.$el.addEventListener(this.mousedown, this.nodeCreateHandler, false)
                }
            },
            nodeCreateHandler (e) {
                console.info('mousedown:', e.target)
                const paletteNode = matchSelector(e.target, this.selector)
                if (!paletteNode) {
                    return false
                }
                const nodeType = paletteNode.dataset.type ? paletteNode.dataset.type : ''
                const nodeConfig = paletteNode.dataset ? paletteNode.dataset.config : {}

                this.showAddingNode = true
                this.$nextTick(() => {
                    const node = this.$el.querySelector('.adding-node')
                    this.addingNodeRect = node.getBoundingClientRect()
                    const nodePos = this.getAddingNodePos(e)
                    this.addingNodeConfig = {
                        id: uuid('node'),
                        type: nodeType,
                        x: nodePos.x,
                        y: nodePos.y,
                        ...nodeConfig
                    }

                    this.$el.addEventListener(this.mousemove, this.nodeMovingHandler, false)
                    document.addEventListener(this.mouseup, this.nodeMoveEndHandler, false)
                })
            },
            nodeMovingHandler (e) {
                const nodePos = this.getAddingNodePos(e)
                this.$set(this.addingNodeConfig, 'x', nodePos.x)
                this.$set(this.addingNodeConfig, 'y', nodePos.y)
            },
            nodeMoveEndHandler (e) {
                this.$el.removeEventListener(this.mousemove, this.nodeMovingHandler)
                document.removeEventListener(this.mouseup, this.nodeMoveEndHandler)

                this.showAddingNode = false
                let pageX
                if (e.touches && e.touches.length > 0) {
                    pageX = e.touches[0].pageX
                } else {
                    pageX = e.pageX
                }
                if (pageX > (this.paletteRect.left + this.paletteRect.width)) {
                    const nodeX = this.addingNodeConfig.x - this.paletteRect.width - this.canvasOffset.x
                    const nodeY = this.addingNodeConfig.y - this.canvasOffset.y
                    this.$set(this.addingNodeConfig, 'x', nodeX)
                    this.$set(this.addingNodeConfig, 'y', nodeY)
                    // this.createNode(this.addingNodeConfig)
                }

                this.addingNodeConfig = {}
                this.addingNodeRect = {}
            },
            getAddingNodePos (e) {
                let pageX, pageY
                if (e.touches && e.touches.length > 0) {
                    pageX = e.touches[0].pageX
                    pageY = e.touches[0].pageY
                } else {
                    pageX = e.pageX
                    pageY = e.pageY
                }
                return {
                    x: pageX - this.paletteRect.left - (this.addingNodeRect.width / 2),
                    y: pageY - this.paletteRect.top - (this.addingNodeRect.height / 2)
                }
            },
            onToolClick (tool) {
                typeof this[tool.type] === 'function' && this[tool.type]()
                this.$emit('onToolClick', tool)
            },
            setZoom (zoom) {
                this.instance.setContainer('canvas-flow')
                const transformOrigin = '0 0'
                this.$refs.canvasFlow.style['transform'] = 'matrix(' + zoom + ',0,0,' + zoom + ',0,0)'
                this.$refs.canvasFlow.style['transformOrigin'] = transformOrigin
                this.$refs.canvasFlow.zoom = zoom
                this.zoom = zoom
                this.instance.setZoom(zoom)
            },
            zoomIn (radio = 1.1) {
                this.setZoom(this.zoom * radio)
            },
            zoomOut (radio = 0.9) {
                this.setZoom(this.zoom * radio)
            },
            resetPostions () {
                this.setZoom(1)
                this.setCanvasPosition(0, 0)
            },
            setCanvasPosition (x, y) {
                this.canvasOffset = { x, y }
                this.canvasPos = { x, y }
            },
            // 节点框选点击
            frameSelect () {
                this.isFrameSelecting = true
            },
            frameSelectHandler (e) {
                if (e.touches && e.touches.length > 0) {
                    const pageX = e.touches[0].pageX
                    const pageY = e.touches[0].pageY
                    this.mouseDownPos = {
                        x: pageX - this.canvasRect.left,
                        y: pageY - this.canvasRect.top
                    }
                } else {
                    this.mouseDownPos = {
                        x: e.pageX - this.canvasRect.left,
                        y: e.pageY - this.canvasRect.top
                    }
                }

                this.$refs.canvasFlowWrap.addEventListener(this.mousemove, this.frameSelectMovingHandler, false)
            },
            // 节点框选选框大小、位置设置
            frameSelectMovingHandler (e) {
                let widthGap
                let heightGap
                if (e.touches && e.touches.length > 0) {
                    const pageX = e.touches[0].pageX
                    const pageY = e.touches[0].pageY
                    widthGap = pageX - this.mouseDownPos.x - this.canvasRect.left
                    heightGap = pageY - this.mouseDownPos.y - this.canvasRect.top
                } else {
                    widthGap = e.pageX - this.mouseDownPos.x - this.canvasRect.left
                    heightGap = e.pageY - this.mouseDownPos.y - this.canvasRect.top
                }

                this.frameSelectorRect = {
                    width: Math.abs(widthGap),
                    height: Math.abs(heightGap)
                }
                this.frameSelectorPos = {
                    x: widthGap > 0 ? this.mouseDownPos.x : this.mouseDownPos.x + widthGap,
                    y: heightGap > 0 ? this.mouseDownPos.y : this.mouseDownPos.y + heightGap
                }
            },
            frameSelectEndHandler (e) {
                this.$refs.canvasFlowWrap.removeEventListener(this.mousemove, this.frameSelectMovingHandler)
                this.$refs.canvasFlowWrap.removeEventListener(this.mouseup, this.frameSelectEndHandler)
                document.addEventListener('keydown', this.nodeLineCopyhandler, false)
                document.addEventListener('keydown', this.nodeLinePastehandler, false)
                document.addEventListener('keydown', this.nodeLineDeletehandler, false)
                document.addEventListener(this.mousedown, this.cancelFrameSelectorHandler, { capture: false, once: true })

                const selectedNodes = this.getSelectedNodes()
                this.isFrameSelecting = false
                this.frameSelectorPos = { x: 0, y: 0 }
                this.frameSelectorRect = { width: 0, height: 0 }
                console.log(selectedNodes)
                this.selectedNodes = selectedNodes
                this.$emit('frameSelectNodes', selectedNodes.slice(0))
            },
            getSelectedNodes () {
                const { x: selectorX, y: selectorY } = this.frameSelectorPos
                const { width: selectorWidth, height: selectorHeight } = this.frameSelectorRect
                const selectedNodes = this.nodes.filter(node => {
                    const nodeEl = document.querySelector(`#${node.id}`)
                    const nodeRect = nodeEl.getBoundingClientRect()
                    const nodePos = {
                        left: nodeRect.left - this.canvasRect.left,
                        top: nodeRect.top - this.canvasRect.top
                    }
                    if (selectorX < nodePos.left
                        && selectorX + selectorWidth > nodePos.left
                        && selectorY < nodePos.top
                        && selectorY + selectorHeight > nodePos.top
                    ) {
                        nodeEl.classList.add('selected')
                        return true
                    }
                })
                return selectedNodes
            },
            cancelFrameSelectorHandler (e) {
                this.selectedNodes.forEach(node => {
                    const nodeEl = document.querySelector(`#${node.id}`)
                    nodeEl && nodeEl.classList.remove('selected')
                })
                this.selectedNodes = []
            },
            nodeLineCopyhandler (e) {
                if ((e.ctrlKey || e.metaKey) && e.keyCode === 67) {
                    this.$emit('onNodeCopy', this.selectedNodes)
                }
            },
            nodeLinePastehandler (e) {
                if ((e.ctrlKey || e.metaKey) && e.keyCode === 86) {
                    this.$emit('onNodePaste')
                }
            },
            nodeLineDeletehandler (e) {
                if (e.keyCode === 46 || e.keyCode === 8) {
                    this.selectedNodes.forEach(node => {
                        this.removeNode(node)
                    })
                    this.cancelFrameSelectorHandler()
                }
            },
            hideToolTips () {
                this.nodes.forEach(function (node) {
                    const $tool = document.getElementById('tool' + node.id)
                    $tool.style.display = 'none'
                })
            }
        }
    }
</script>
<style lang="scss">
    @import '../../../static/style/app.scss';
    .jsflow {
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        z-index: auto;
        .tool-panel-wrap {
            position: absolute;
            top: 20px;
            left: 70px;
            padding: 10px 20px;
            background: #c4c6cc;
            opacity: 0.65;
            border-radius: 4px;
            z-index: 4;
        }
        .palette-panel-wrap {
            float: left;
            width: 60px;
            height: 100%;
            border-right: 1px solid #cccccc;
        }
        .canvas-flow-wrap {
            position: fixed;
            /*height: 100%;*/
            width: 100%;
            top: 50%;
            transform: translateY(-50%);
            bottom: 0;
            /*overflow: hidden;*/
        }
        .canvas-flow {
            position: relative;
        }
        .canvas-frame-selector {
            position: absolute;
            border: 1px solid #3a84ff;
            background: rgba(58, 132, 255, 0.15);
        }
        .jsflow-node {
            position: absolute;
            height: 90px;
            display: flex;
            align-items: center;
            .node-default {
                width: 120px;
                height: 80px;
                line-height: 80px;
                border: 1px solid #cccccc;
                border-radius: 2px;
                text-align: center;
            }
            &.selected {
                border: 1px solid #3a84ff;
            }
        }
        .adding-node {
            opacity: 0.8;
        }
    }
</style>
