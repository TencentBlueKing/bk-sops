<template>
    <div :class="['jsflow', { editable }]">
        <div class="canvas-area">
            <div v-if="showTool" class="tool-panel-wrap">
                <slot name="toolPanel">
                    <tool-panel
                        :tools="tools"
                        :is-frame-selecting="isFrameSelecting"
                        @onToolClick="onToolClick">
                    </tool-panel>
                </slot>
            </div>
            <div v-if="showPalette" ref="palettePanel" class="palette-panel-wrap">
                <slot name="palettePanel">
                    <palette-panel :selector="selector"></palette-panel>
                </slot>
            </div>
            <div
                ref="canvasFlowWrap"
                class="canvas-flow-wrap"
                :style="canvasWrapStyle"
                @[mousedown]="onCanvasMouseDown"
                @[mouseup]="onCanvasMouseUp">
                <div
                    ref="canvasFlow"
                    id="canvas-flow"
                    class="canvas-flow"
                    :style="canvasStyle">
                    <div v-for="node in nodes" :key="node.id">
                        <!-- 加一层 div 元素是为了解决调用节点删除DOM后，数据更新时虚拟DOM计算错误 -->
                        <div
                            class="jsflow-node canvas-node"
                            :id="node.id"
                            @mouseover="toggleHighLight(node, true)"
                            @mouseout="toggleHighLight(node, false)">
                            <slot name="nodeTemplate" :node="node">
                                <node-template :node="node"></node-template>
                            </slot>
                        </div>
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
                    <node-template :node="addingNodeConfig"></node-template>
                </slot>
            </div>
        </div>
    </div>
</template>
<script>
    import { jsPlumb } from 'jsplumb'
    import PalettePanel from './PalettePanel.vue'
    import ToolPanel from './ToolPanel.vue'
    import NodeTemplate from './NodeTemplate.vue'

    import { matchSelector, getPolyfillEvent } from '../lib/dom.js'
    import { paletteOptions, endpointOptions, nodeOptions, connectorOptions } from '../lib/defaultOptions.js'
    import { uuid } from '../lib/uuid.js'

    const props = {
        showPalette: {
            type: Boolean,
            default: true
        },
        showTool: {
            type: Boolean,
            default: true
        },
        tools: { // 工具栏选项，通过传入值来选择工具项及其顺序
            type: Array,
            default () {
                return [
                    {
                        type: 'zoomIn',
                        name: '放大',
                        cls: 'tool-item'
                    },
                    {
                        type: 'zoomOut',
                        name: '缩小',
                        cls: 'tool-item'
                    },
                    {
                        type: 'resetPosition',
                        name: '重置',
                        cls: 'tool-item'
                    }
                ]
            }
        },
        editable: {
            type: Boolean,
            default: true
        },
        selector: {
            type: String,
            default: paletteOptions.selector
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
        nodeOptions: { // 节点配置项
            type: Object,
            default () {
                return { ...nodeOptions }
            }
        },
        connectorOptions: { // 连接线配置项
            type: Object,
            default () {
                return { ...connectorOptions }
            }
        },
        endpointOptions: { // 端点配置项
            type: Object,
            default () {
                return { ...endpointOptions }
            }
        }
    }

    // 兼容移动端的点击、拖拽事件
    const eventDict = {
        'mousedown': 'ontouchstart' in document.documentElement ? 'touchstart' : 'mousedown',
        'mousemove': 'ontouchmove' in document.documentElement ? 'touchmove' : 'mousemove',
        'mouseup': 'ontouchend' in document.documentElement ? 'touchend' : 'mouseup'
    }

    export default {
        name: 'JsFlow',
        components: {
            PalettePanel,
            ToolPanel,
            NodeTemplate
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
            'data.nodes': {
                handler (val) {
                    this.nodes = val
                },
                deep: true
            },
            editable (val) {
                const nodes = this.$el.querySelectorAll('.canvas-node')
                this.toggleNodeDraggable(nodes, val)
            }
        },
        mounted () {
            this.initCanvas()
            this.registerEvent()
            this.renderData()
            if (this.$refs.palettePanel) {
                this.paletteRect = this.$refs.palettePanel.getBoundingClientRect()
                this.registerPaletteEvent()
            }
        },
        beforeDestroy () {
            if (this.$refs.palettePanel) {
                this.$refs.palettePanel.removeEventListener(this.mousedown, this.nodeCreateHandler)
            }
            this.$el.removeEventListener(this.mousemove, this.nodeMovingHandler)
            document.removeEventListener(this.mouseup, this.nodeMoveEndHandler)
        },
        methods: {
            initCanvas () {
                const defaultOptions = {}
                const options = {
                    ...this.endpointOptions,
                    ...this.connectorOptions
                }
                // jsplumb 默认属性首字母要大写
                for (const key in options) {
                    const firstChar = key[0].toUpperCase()
                    const upperKey = `${firstChar}${key.slice(1)}`
                    
                    defaultOptions[upperKey] = options[key]
                }

                this.instance = jsPlumb.getInstance({
                    Container: 'canvas-flow',
                    ...defaultOptions
                })
            },
            // 注册事件
            registerEvent () {
                // 连线拖动之前，需要返回值
                this.instance.bind('beforeDrag', (connection) => {
                    if (!this.editable) {
                        return false
                    }
                    if (typeof this.$listeners.onBeforeDrag === 'function') {
                        return this.$listeners.onBeforeDrag(connection)
                    } else {
                        return true
                    }
                })
                // 连线放下之前，需要返回值
                this.instance.bind('beforeDrop', (connection) => {
                    if (!this.editable) {
                        return false
                    }
                    if (typeof this.$listeners.onBeforeDrop === 'function') {
                        return this.$listeners.onBeforeDrop(connection)
                    } else {
                        return true
                    }
                })
                // 连线开始拖动
                this.instance.bind('connectionDrag', (connection) => {
                    if (typeof this.$listeners.connectionDrag === 'function') {
                        this.$emit('connectionDrag', connection)
                    }
                })
                // 连线吸附之后
                this.instance.bind('connection', (connection) => {
                    if (typeof this.$listeners.onConnection === 'function') {
                        this.$emit('onConnection', connection)
                    }
                })
                this.instance.bind('connectionDragStop', (connection, event) => {
                    if (connection.target && connection.target.classList.contains('jsflow-node')) {
                        return
                    }
                    const nodeEl = this.getNodeWithEndpoint(event.target)
                    if (nodeEl) {
                        const node = this.nodes.find(item => nodeEl.id === item.id)
                        if (typeof this.$listeners.onConnectionDragStop === 'function') {
                            const source = {
                                id: connection.source.id,
                                arrow: connection.endpoints[0].anchor.type
                            }
                            this.$emit('onConnectionDragStop', source, node.id, event)
                        }
                    }
                })
                // 连线删除之前
                this.instance.bind('beforeDetach', (connection) => {
                    if (typeof this.$listeners.onBeforeDetach === 'function') {
                        return this.$listeners.onBeforeDetach(connection)
                    } else {
                        return true
                    }
                })
                // 连线已删除
                this.instance.bind('connectionDetached', (connection, originalEvent) => {
                    const lines = this.lines.filter(line => {
                        return line.source.id !== connection.sourceId && line.target.id !== connection.targetId
                    })
                    this.lines = lines
                    if (typeof this.$listeners.onConnectionDetached === 'function') {
                        this.$emit('onConnectionDetached', connection)
                    }
                })
                // 连线端点移动到另外端点
                this.instance.bind('connectionMoved', (connection, originalEvent) => {
                    if (typeof this.$listeners.onConnectionMoved === 'function') {
                        this.$emit('onConnectionMoved', lines)
                    }
                })
                // 连线单击
                this.instance.bind('click', (connection, originalEvent) => {
                    if (typeof this.$listeners.onConnectionClick === 'function') {
                        this.$emit('onConnectionClick', connection, originalEvent)
                    }
                })
                // 连线双击
                this.instance.bind('dblclick', (connection, originalEvent) => {
                    if (typeof this.$listeners.onConnectionDbClick === 'function') {
                        this.$emit('onConnectionDbClick', connection, originalEvent)
                    }
                })
                // 端点单击
                this.instance.bind('endpointClick', (endpoint, originalEvent) => {
                    if (typeof this.$listeners.onEndpointClick === 'function') {
                        this.$emit('onEndpointClick', endpoint, originalEvent)
                    }
                })
                // 端点双击击
                this.instance.bind('endpointDblClick', (endpoint, originalEvent) => {
                    if (typeof this.$listeners.onEndpointDbClick === 'function') {
                        this.$emit('onEndpointDbClick', endpoint, originalEvent)
                    }
                })
            },
            renderData () {
                this.instance.batch(() => {
                    this.nodes.forEach(node => {
                        this.initNode(node)
                    })
                    this.lines.forEach(line => {
                        this.createConnector(line, this.connectorOptions)
                    })
                })
            },
            /**
             * @todo 画布更新方式优化
             */
            updateCanvas (data) {
                this.removeAllConnector()
                this.lines = data.lines
                this.nodes = data.nodes
                this.renderData()
            },
            // 创建节点并初始化拖拽
            createNode (node) {
                if (typeof this.$listeners.onCreateNodeBefore === 'function') {
                    if (!this.$listeners.onCreateNodeBefore(node)) {
                        return
                    }
                }
                this.nodes.push(node)
                this.$nextTick(() => {
                    this.initNode(node)
                })
            },
            // 初始化节点
            initNode (node) {
                const nodeEl = document.getElementById(node.id)
                nodeEl.style.left = `${node.x}px`
                nodeEl.style.top = `${node.y}px`
                this.setNodeDraggable(node, this.nodeOptions)
                this.setNodeEndPoint(node, this.endpointOptions)
                if (typeof this.$listeners.onCreateNodeAfter === 'function') {
                    this.$emit('onCreateNodeAfter', node)
                }
            },
            // 删除节点
            removeNode (node) {
                const index = this.nodes.findIndex(item => item.id === node.id)
                this.nodes.splice(index, 1)
                this.instance.remove(node.id)
            },
            // 设置节点端点
            setNodeEndPoint (node, options) {
                const endpoints = node.endpoints || ['Top', 'Right', 'Bottom', 'Left']
                endpoints.forEach(item => {
                    this.instance.addEndpoint(node.id, {
                        anchor: item,
                        uuid: item + node.id,
                        ...options
                    })
                })
            },
            /**
             * 设置节点可拖拽
             * @param node 支持节点元素、节点id或者类数组的节点元素、节点id
             */
            setNodeDraggable (node, options) {
                if (!this.editable) {
                    return
                }
                
                const vm = this
                this.instance.draggable(node.id, {
                    grid: [20, 20],
                    drag (event) {
                        const curNode = vm.nodes.find(item => node.id === item.id)
                        const nodeConfig = Object.assign({}, curNode)
                        vm.$emit('onNodeMoving', nodeConfig, event)
                    },
                    stop (event) {
                        let index = -1
                        const [nodeX, nodeY] = event.pos
                        const curNode = vm.nodes.find((el, i) => {
                            if (el.id === node.id) {
                                index = i
                                return true
                            }
                        })
                        const nodeConfig = Object.assign({}, curNode, {
                            x: nodeX,
                            y: nodeY
                        })
          
                        vm.nodes.splice(index, 1, nodeConfig)
                        vm.$emit('onNodeMoveStop', nodeConfig, event)
                    },
                    ...options
                })
            },
            /**
             * 更新节点位置
             * @params {Object} node 节点对象，eg: {id: 'test', x: 23, y: 500}
             */
            setNodePosition (node) {
                const curNode = document.getElementById(node.id)
                curNode.style.left = `${node.x}px`
                curNode.style.top = `${node.y}px`
                this.instance.revalidate(curNode)
            },
            /**
             * 节点和端点开启或关闭拖拽
             * @param {String、Number} node 支持节点元素、节点id或者类数组的节点元素、节点id
             * @param draggable
             */
            toggleNodeDraggable(node, draggable) {
                this.instance.setDraggable(node, draggable)
            },
            // 设置节点位置
            setNodeInitialPos (node) {
                return {
                    left: `${node.x}px`,
                    top: `${node.y}px`,
                    visibility: node.visible ? 'initial' : 'hidden'
                }
            },
            // 创建连接线
            createConnector (line, options) {
                const lineOptions = line.options || {}
                const connection = this.instance.connect(
                    {
                        source: line.source.id,
                        target: line.target.id,
                        uuids: [line.source.arrow + line.source.id, line.target.arrow + line.target.id]
                    },
                    {
                        ...options,
                        ...lineOptions
                    }
                )
                return connection
            },
            /**
             * 修改指定连线的配置
             * @param {String} source 连线起点 DOM-ID
             * @param {String} target 连线终点 DOM-ID
             * @param {Array} config 连线配置 对应底层 api 不是增量修改 需要传全量配置：
             * eg: [
             *     'Flowchart', // 流程图种类
             *     {
             *          stub: [5, 20], // 起始端点连接线的最小长度
             *          gap: 8, // 线与端点点最小间隔
             *          cornerRadius: 2, // 折线弧度
             *          alwaysRespectStubs: true, // 允许 stub 配置生效
             *          midpoint: 0.9 // 折线比例
             *      }
             *  ]
             */
            setConnector (source, target, config) {
                var connections = this.instance.getAllConnections().filter(item => {
                    return item.sourceId === source && item.targetId === target
                })
                connections.forEach(connection => {
                    connection.setConnector(config)
                    if (this.endpointOptions && this.endpointOptions.connectorOverlays) {
                        this.endpointOptions.connectorOverlays.forEach(overlay => {
                            connection.addOverlay(overlay)
                        })
                    }
                })
            },
            // 删除连接线
            removeConnector (line) {
                const connections = this.instance.getConnections({ source: line.source.id, target: line.target.id })
                connections.forEach(connection => {
                    this.instance.deleteConnection(connection)
                })
            },
            // 删除所有连接线
            removeAllConnector () {
                this.instance.deleteEveryConnection()
                this.lines = []
            },
            // 通过节点id获取所有该节点上所有连接线
            getConnectorsByNodeId (id) {
                const allConnectors = this.instance.getAllConnections()
                const connectors = allConnectors.filter(item => {
                    return item.sourceId === id || item.targetId === id
                })
                return connectors
            },
            /**
             * 获取包含连线目标端点的节点，匹配返回节点 DOM，不匹配返回 false
             * @param {Object} 端点 DOM 对象
             * 
             * @return 节点 DOM 或 false
             */
            getNodeWithEndpoint (endpoint) {
                const parentEl = endpoint.parentNode

                if (!parentEl || parentEl.nodeName === 'HTML') {
                    return false
                }

                if (parentEl.classList.contains('jsflow-node')) {
                    return parentEl
                } else {
                    return this.getNodeWithEndpoint(parentEl)
                }
            },
            /**
             * 添加连线overlay
             *
             * @param {Object} line 连线数据对象
             * @param {Object} overlay 连线overlay对象
             * eg: overlay = {
             *    type: 'Label',
             *    name: 'xxx',
             *    location: '-60',
             *    cls: 'branch-conditions',
             *    editable: true
             * }
             *
             */
            addLineOverlay (line, overlay) {
                const vm = this
                const connections = this.instance.getConnections({ source: line.source.id, target: line.target.id })
                connections.forEach(connection => {
                    connection.addOverlay([overlay.type, {
                        label: overlay.name,
                        location: overlay.location,
                        cssClass: overlay.cls,
                        id: overlay.id,
                        events: {
                            click (labelOverlay, originalEvent) {
                                vm.$emit('onOverlayClick', labelOverlay, originalEvent)
                            }
                        }},
                    ])
                })
            },
            // 删除连线ovelay
            removeLineOverlay (line, id) {
                const connections = this.instance.getConnections({ source: line.source.id, target: line.target.id })
                connections.forEach(connection => {
                    connection.removeOverlay(id)
                })
            },
            onCanvasMouseDown (e) {
                e = getPolyfillEvent(e)
                if (this.isFrameSelecting) {
                    this.frameSelectHandler(e)
                } else {
                    this.canvasGrabbing = true
                    this.mouseDownPos = {
                        x: e.pageX,
                        y: e.pageY
                    }
                    this.$refs.canvasFlowWrap.addEventListener(this.mousemove, this.canvasFlowMoveHandler, false)
                }
            },
            canvasFlowMoveHandler (e) {
                e = getPolyfillEvent(e)

                this.canvasOffset = {
                    x: this.canvasPos.x + e.pageX - this.mouseDownPos.x,
                    y: this.canvasPos.y + e.pageY - this.mouseDownPos.y
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
            // 注册节点拖拽源事件
            registerPaletteEvent () {
                this.$refs.palettePanel.addEventListener(this.mousedown, this.nodeCreateHandler, false)
            },
            nodeCreateHandler (e) {
                const paletteNode = matchSelector(e.target, this.selector)
                if (!paletteNode) {
                    return
                }
                const nodeType = paletteNode.dataset.type ? paletteNode.dataset.type : ''
                const nodeConfig = {}
                for (const item in paletteNode.dataset) {
                    const result = item.match(/(config)(\w*)/)
                    if (result && result[2] !== ''){
                        const dataKey = result[2]
                        const attr = dataKey[0].toLowerCase() + dataKey.slice(1)
                        nodeConfig[attr] = paletteNode.dataset[item]
                    }
                }

                this.showAddingNode = true
                this.addingNodeConfig.id = uuid('node')
                this.addingNodeConfig.type = nodeType
                this.$nextTick(() => {
                    const node = this.$el.querySelector('.adding-node')
                    this.addingNodeRect = node.getBoundingClientRect()
                    const nodePos = this.getAddingNodePos(e)
                    this.addingNodeConfig = {
                        id: uuid('node'),
                        type: nodeType,
                        x: nodePos.x,
                        y: nodePos.y,
                        adding: true,
                        visible: false,
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
                this.$set(this.addingNodeConfig, 'visible', true)
            },
            nodeMoveEndHandler (e) {
                this.$el.removeEventListener(this.mousemove, this.nodeMovingHandler)
                document.removeEventListener(this.mouseup, this.nodeMoveEndHandler)

                this.showAddingNode = false

                if (e.pageX > (this.paletteRect.left + this.paletteRect.width)) {
                    const nodeX = this.addingNodeConfig.x - this.paletteRect.width - this.canvasOffset.x
                    const nodeY = this.addingNodeConfig.y - this.canvasOffset.y
                    this.$set(this.addingNodeConfig, 'x', nodeX)
                    this.$set(this.addingNodeConfig, 'y', nodeY)
                    delete this.addingNodeConfig.adding
                    delete this.addingNodeConfig.visible
                    this.createNode(this.addingNodeConfig)
                }

                this.addingNodeConfig = {}
                this.addingNodeRect = {}
            },
            getAddingNodePos (e) {
                return {
                    x: e.pageX - this.paletteRect.left - (this.addingNodeRect.width / 2),
                    y: e.pageY - this.paletteRect.top - (this.addingNodeRect.height / 2)
                }
            },
            toggleHighLight (node, isHighLight = true) {
                if (!this.editable) { return } // 不可编辑状态不高亮端点

                const endpoints = this.instance.getEndpoints(node.id)
                const nodeEl = document.getElementById(node.id)
                const endpoint = this.instance.selectEndpoints({ source: nodeEl })
                endpoint.each(item => {
                    const paintStyle = isHighLight ? this.endpointOptions.hoverPaintStyle : this.endpointOptions.paintStyle
                    paintStyle && item.setStyle(paintStyle)
                })
            },
            onToolClick (tool) {
                typeof this[tool.type] === 'function' && this[tool.type]()
                this.$emit('onToolClick', tool)
            },
            setZoom (zoom, offsetX, offsetY) {
                this.instance.setContainer('canvas-flow')
                this.$refs.canvasFlow.style['transform'] = 'matrix(' + zoom + ',0,0,' + zoom + ',' + offsetX + ',' + offsetY + ')'
                this.$refs.canvasFlow.style['transformOrigin'] = '0 0'
                this.$refs.canvasFlow.zoom = zoom
                this.zoom = zoom
                this.instance.setZoom(zoom)
            },
            zoomIn (radio = 1.1, x = 0, y = 0) {
                const zoom = this.zoom * radio
                const offsetX = x - x * zoom
                const offsetY = y - y * zoom
                if (zoom > 2) {
                    return
                }
                this.setZoom(zoom, offsetX, offsetY)
            },
            zoomOut (radio = 0.9, x = 0, y = 0) {
                const zoom = this.zoom * radio
                const offsetX = x - x * zoom
                const offsetY = y - y * zoom
                if (zoom < 0.1) {
                    return
                }
                this.setZoom(zoom, offsetX, offsetY)
            },
            resetPosition () {
                this.setZoom(1, 0, 0)
                this.setCanvasPosition(0, 0)
            },
            setCanvasPosition (x, y) {
                this.canvasOffset = { x, y }
                this.canvasPos = { x, y }
            },
            // 节点框选点击
            frameSelect (val = true) {
                this.isFrameSelecting = val
            },
            onOpenFrameSelect () {
                this.frameSelect()
            },
            onCloseFrameSelect () {
                this.frameSelect(false)
            },
            frameSelectHandler (e) {
                this.canvasRect = this.$refs.canvasFlowWrap.getBoundingClientRect()

                this.mouseDownPos = {
                    x: e.clientX - this.canvasRect.left,
                    y: e.clientY - this.canvasRect.top
                }
                this.$refs.canvasFlowWrap.addEventListener(this.mousemove, this.frameSelectMovingHandler, false)
            },
            // 节点框选选框大小、位置设置
            frameSelectMovingHandler (e) {
                const widthGap = e.clientX - this.mouseDownPos.x - this.canvasRect.left
                const heightGap = e.clientY - this.mouseDownPos.y - this.canvasRect.top
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
        
                document.addEventListener(this.mousedown, this.cancelFrameSelectorHandler, { capture: false, once: true })
                const selectedNodes = this.getSelectedNodes()
                const ids = selectedNodes.map(node => node.id)
                const { x, y } = this.mouseDownPos
                this.isFrameSelecting = false
                this.frameSelectorPos = { x: 0, y: 0 }
                this.frameSelectorRect = { width: 0, height: 0 }
                this.selectedNodes = selectedNodes
                this.clearNodesDragSelection()
                this.addNodesToDragSelection(ids)
                this.$emit('onFrameSelectEnd', selectedNodes.slice(0), x, y)
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
                        return true
                    }
                })
                return selectedNodes
            },
            cancelFrameSelectorHandler (e) {
                this.selectedNodes = []
                this.clearNodesDragSelection()
                this.$emit('onCloseFrameSelect')
            },
            /**
             * 添加节点到拖拽分组，实现多个节点一起拖拽的效果
             * @param {Array} ids 节点id数组
             */
            addNodesToDragSelection (ids) {
                ids.forEach(id => {
                    const nodeEl = document.querySelector(`#${id}`)
                    nodeEl && nodeEl.classList.add('selected')
                })
                this.instance.addToDragSelection(ids)
            },
            clearNodesDragSelection () {
                const nodes = document.querySelectorAll(`.jsflow-node.selected`)
                nodes.forEach(node => {
                    node.classList.remove('selected')
                })
                this.instance.clearDragSelection()
            }
        }
    }
</script>
<style lang="scss">
    .jsflow {
        height: 100%;
        border: 1px solid #cccccc;
        .canvas-area {
            position: relative;
            height: 100%;
        }
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
            position: relative;
            height: 100%;
            overflow: hidden;
        }
        .canvas-flow {
            position: relative;
            min-width: 100%;
            min-height: 100%;
        }
        .canvas-frame-selector {
            position: absolute;
            border: 1px solid #3a84ff;
            background: rgba(58, 132, 255, 0.15);
        }
        .jsflow-node {
            position: absolute;
            user-select: none;
        }
        .jtk-endpoint {
            z-index: 1;
            cursor: pointer;
        }
        .adding-node {
            opacity: 0.8;
        }
        .jtk-endpoint.jtk-dragging {
            z-index: 0;
        }
        .jtk-connector {
            cursor: pointer;
        }
    }
</style>
