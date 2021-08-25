/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div
        id="canvasContainer"
        class="canvas-container">
        <bk-flow
            ref="jsFlow"
            selector="entry-item"
            :class="['canvas-wrapper', { 'tool-wrapper-telescopic': showNodeMenu }]"
            :data="flowData"
            :show-palette="showPalette"
            :show-tool="showTool"
            :editable="editable"
            :endpoint-options="endpointOptions"
            :connector-options="connectorOptions"
            :node-options="nodeOptions"
            @onCreateNodeBefore="onCreateNodeBefore"
            @onCreateNodeAfter="onCreateNodeAfter"
            @onConnectionDragStop="onConnectionDragStop"
            @onConnectionClick="onConnectionClick"
            @onBeforeDrag="onBeforeDrag"
            @onBeforeDrop="onBeforeDrop"
            @onConnection="onConnection"
            @onConnectionDetached="onConnectionDetached"
            @onEndpointClick="onEndpointClick"
            @onNodeMoving="onNodeMoving"
            @onNodeMoveStop="onNodeMoveStop"
            @onOverlayClick="onOverlayClick"
            @onFrameSelectEnd="onFrameSelectEnd"
            @onCloseFrameSelect="onCloseFrameSelect">
            <template v-slot:palettePanel>
                <palette-panel
                    :common="common"
                    :atom-type-list="atomTypeList"
                    :template-labels="templateLabels"
                    :is-disable-start-point="isDisableStartPoint"
                    :is-disable-end-point="isDisableEndPoint"
                    :subflow-list-loading="subAtomListLoading"
                    @updateNodeMenuState="updateNodeMenuState"
                    @getAtomList="getAtomList">
                </palette-panel>
            </template>
            <template v-slot:toolPanel>
                <tool-panel
                    :is-selection-open="isSelectionOpen"
                    :is-show-select-all-tool="isShowSelectAllTool"
                    :is-select-all-tool-disabled="isSelectAllToolDisabled"
                    :is-all-selected="isAllSelected"
                    :show-small-map="showSmallMap"
                    :editable="editable"
                    :zoom-ratio="zoomRatio"
                    :is-show-hot-key="isShowHotKey"
                    @onShowMap="onToggleMapShow"
                    @onZoomIn="onZoomIn"
                    @onZoomOut="onZoomOut"
                    @onResetPosition="onResetPosition"
                    @onOpenFrameSelect="onOpenFrameSelect"
                    @onFormatPosition="onFormatPosition"
                    @onToggleAllNode="onToggleAllNode"
                    @onToggleHotKeyInfo="onToggleHotKeyInfo"
                    @onDownloadCanvas="onDownloadCanvas">
                </tool-panel>
            </template>
            <template v-slot:nodeTemplate="{ node }">
                <node-template
                    :node="node"
                    :canvas-data="canvasData"
                    :is-node-check-open="isNodeCheckOpen"
                    :editable="editable"
                    :id-of-node-shortcut-panel="idOfNodeShortcutPanel"
                    :has-admin-perm="hasAdminPerm"
                    @onConfigBtnClick="onShowNodeConfig"
                    @onInsertNode="onInsertNode"
                    @onAppendNode="onAppendNode"
                    @onNodeDblclick="onNodeDblclick"
                    @onNodeClick="onNodeClick"
                    @onNodeMousedown="onNodeMousedown"
                    @onNodeCheckClick="onNodeCheckClick"
                    @onNodeRemove="onNodeRemove"
                    @onRetryClick="onRetryClick"
                    @onForceFail="onForceFail"
                    @onSkipClick="onSkipClick"
                    @onModifyTimeClick="onModifyTimeClick"
                    @onGatewaySelectionClick="onGatewaySelectionClick"
                    @onTaskNodeResumeClick="onTaskNodeResumeClick"
                    @addNodesToDragSelection="addNodeToSelectedList"
                    @onSubflowPauseResumeClick="onSubflowPauseResumeClick"
                    @getAtomList="getAtomList">
                </node-template>
            </template>
        </bk-flow>
        <help-info
            :editable="editable"
            :is-show-hot-key="isShowHotKey"
            @onZoomIn="onZoomIn"
            @onZoomOut="onZoomOut"
            @onMovePosition="onMovePosition"
            @onResetPosition="onResetPosition"
            @onCloseHotkeyInfo="onCloseHotkeyInfo">
        </help-info>
        <div class="small-map" ref="smallMap" v-if="showSmallMap">
            <img :src="smallMapImg" alt="">
            <div
                ref="selectBox"
                class="select-box"
                @mousedown.prevent="onMouseDownSelect">
            </div>
        </div>
    </div>
</template>
<script>
    // import html2canvas from 'html2canvas'
    // import domtoimage from 'dom-to-image'
    import domtoimage from '@/utils/domToImage.js'
    // import htmltoimage from 'html-to-image'
    import BkFlow from '@/assets/js/flow.js'
    import { uuid } from '@/utils/uuid.js'
    import NodeTemplate from './NodeTemplate/index.vue'
    import PalettePanel from './PalettePanel/index.vue'
    import HelpInfo from './HelpInfo/index.vue'
    import ToolPanel from './ToolPanel/index.vue'
    import tools from '@/utils/tools.js'
    import dom from '@/utils/dom.js'
    import { endpointOptions, connectorOptions, nodeOptions } from './options.js'
    import validatePipeline from '@/utils/validatePipeline.js'

    export default {
        name: 'TemplateCanvas',
        components: {
            BkFlow,
            NodeTemplate,
            PalettePanel,
            ToolPanel,
            HelpInfo
        },
        props: {
            showPalette: {
                type: Boolean,
                default: true
            },
            showTool: {
                type: Boolean,
                default: true
            },
            editable: {
                type: Boolean,
                default: true
            },
            atomTypeList: {
                type: Object,
                default () {
                    return {}
                }
            },
            isNodeCheckOpen: {
                type: Boolean,
                default: false
            },
            isShowSelectAllTool: {
                type: Boolean,
                default: false
            },
            isSelectAllToolDisabled: {
                type: Boolean,
                default: false
            },
            isAllSelected: {
                type: Boolean,
                default: false
            },
            hasAdminPerm: {
                type: Boolean,
                default: false
            },
            common: {
                type: [String, Number],
                default: ''
            },
            subflowListLoading: {
                type: Boolean,
                default: true
            },
            templateLabels: {
                type: Array,
                default: () => ([])
            },
            canvasData: {
                type: Object,
                default () {
                    return {
                        'lines': [],
                        'locations': []
                    }
                }
            },
            isCanvasImg: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const { lines, locations: nodes } = this.canvasData
            const flowData = {
                lines,
                nodes
            }
            let combinedEndpointOptions = endpointOptions
            if (!this.editable) {
                combinedEndpointOptions = Object.assign({}, endpointOptions, {
                    isTarget: false,
                    isSource: false,
                    connectionsDetachable: false
                })
            }
            return {
                isSmallMap: false, // 小地图激活态
                smallMapWidth: 344, // 344 小地图宽度
                smallMapHeight: 216, // 216 小地图高度
                smallMapImg: '',
                showSmallMap: false,
                isMouseEnterX: '', // 鼠标在选择框中按下的offsetX值
                isMouseEnterY: '', // 鼠标在选择框中按下的offsetY值
                windowWidth: document.documentElement.offsetWidth - 60, // 60 header的宽度
                windowHeight: document.documentElement.offsetHeight - 60 - 50, // 50 tab栏的宽度
                canvasWidth: 0, // 生成画布的宽
                canvasHeight: 0, // 生成画布的高
                canvasImgDownloading: false,
                idOfNodeShortcutPanel: '',
                showNodeMenu: false,
                isDisableStartPoint: false,
                isDisableEndPoint: false,
                isSelectionOpen: false,
                isShowHotKey: false,
                isCanCreateline: false,
                selectedNodes: [],
                copyNodes: [],
                activeCon: null,
                selectionOriginPos: {
                    x: 0,
                    y: 0
                },
                pasteMousePos: {
                    x: 0,
                    y: 0
                },
                referenceLine: {
                    x: 0,
                    y: 0,
                    id: '',
                    arrow: ''
                },
                zoomOriginPosition: {
                    x: 0,
                    y: 0
                },
                endpointOptions: combinedEndpointOptions,
                flowData,
                connectorOptions,
                nodeOptions,
                zoomRatio: 100
            }
        },
        watch: {
            canvasData (val) {
                const { lines, locations: nodes } = val
                this.flowData = {
                    lines,
                    nodes
                }
            }
        },
        created () {
            this.onWindowResize = tools.throttle(this.handlerWindowResize, 300)
        },
        mounted () {
            this.isDisableStartPoint = !!this.canvasData.locations.find((location) => location.type === 'startpoint')
            this.isDisableEndPoint = !!this.canvasData.locations.find((location) => location.type === 'endpoint')
            document.body.addEventListener('click', this.handleShortcutPanelHide, false)
            document.body.addEventListener('mousedown', this.handleDeleteLineIconHide, false)
            // 画布快捷键缩放
            const canvasPaintArea = document.querySelector('.canvas-flow-wrap')
            canvasPaintArea.addEventListener('mousewheel', this.onMouseWheel, false)
            canvasPaintArea.addEventListener('DOMMouseScroll', this.onMouseWheel, false)
            canvasPaintArea.addEventListener('mousemove', this.onCanvasMouseMove, false)
            // 监听页面视图变化
            window.addEventListener('resize', this.onWindowResize, false)
        },
        beforeDestroy () {
            this.$refs.jsFlow.$el.removeEventListener('mousemove', this.pasteMousePosHandler)
            document.removeEventListener('keydown', this.nodeSelectedhandler)
            document.removeEventListener('keydown', this.nodeLineDeletehandler)
            document.body.removeEventListener('click', this.handleShortcutPanelHide, false)
            document.body.removeEventListener('mousedown', this.handleDeleteLineIconHide, false)
            // 画布快捷键缩放
            const canvasPaintArea = document.querySelector('.canvas-flow-wrap')
            if (canvasPaintArea) {
                canvasPaintArea.removeEventListener('mousewheel', this.onMouseWheel, false)
                canvasPaintArea.removeEventListener('DOMMouseScroll', this.onMouseWheel, false)
                canvasPaintArea.removeEventListener('mousemove', this.onCanvasMouseMove, false)
            }
            window.removeEventListener('resize', this.onWindowResize, false)
        },
        methods: {
            getAtomList (val) {
                this.$emit('getAtomList', val)
            },
            handlerWindowResize () {
                this.windowWidth = document.documentElement.offsetWidth - 60
                this.windowHeight = document.documentElement.offsetHeight - 60 - 50
                if (this.showSmallMap) {
                    this.onGenerateCanvas().then(res => {
                        this.smallMapImg = res
                    })
                    this.getInitialValue()
                }
            },
            onToggleMapShow () {
                this.showSmallMap = !this.showSmallMap
                if (this.showSmallMap) {
                    this.onGenerateCanvas().then(res => {
                        this.smallMapImg = res
                    })
                    this.$nextTick(() => {
                        this.getInitialValue()
                    })
                }
            },
            onZoomIn (pos) {
                if (pos) {
                    const { x, y } = pos
                    this.$refs.jsFlow.zoomIn(1.1, x, y)
                } else {
                    this.$refs.jsFlow.zoomIn(1.1, 0, 0)
                }
                this.clearReferenceLine()
                this.zoomRatio = Math.round(this.$refs.jsFlow.zoom * 100)
                this.showSmallMap = false
            },
            onZoomOut (pos) {
                if (pos) {
                    const { x, y } = pos
                    this.$refs.jsFlow.zoomOut(0.9, x, y)
                } else {
                    this.$refs.jsFlow.zoomOut(0.9, 0, 0)
                }
                this.clearReferenceLine()
                this.zoomRatio = Math.round(this.$refs.jsFlow.zoom * 100)
                this.showSmallMap = false
            },
            onResetPosition () {
                this.$refs.jsFlow.resetPosition()
                this.zoomRatio = Math.round(this.$refs.jsFlow.zoom * 100)
            },
            onFormatPosition () {
                this.$emit('onFormatPosition')
                this.showSmallMap = false
            },
            onOpenFrameSelect () {
                this.isSelectionOpen = true
                this.$refs.jsFlow.frameSelect()
                this.showSmallMap = false
            },
            onFrameSelectEnd (nodes) {
                this.selectedNodes = nodes
                this.copyNodes = tools.deepClone(nodes)
                this.isSelectionOpen = false
                this.selectionOriginPos = this.getNodesLocationOnLeftTop(nodes)
                this.$refs.jsFlow.$el.addEventListener('mousemove', this.pasteMousePosHandler)
                document.addEventListener('keydown', this.nodeSelectedhandler)
                document.addEventListener('keydown', this.nodeLineDeletehandler, { once: true })
            },
            onCloseFrameSelect () {
                this.selectedNodes = []
                this.copyNodes = []
                this.$refs.jsFlow.$el.removeEventListener('mousemove', this.pasteMousePosHandler)
                document.removeEventListener('keydown', this.pasteMousePosHandler)
                document.removeEventListener('keydown', this.nodeSelectedhandler)
            },
            pasteMousePosHandler (e) {
                this.pasteMousePos = {
                    x: e.offsetX,
                    y: e.offsetY
                }
            },
            nodeSelectedhandler (e) {
                if ((e.ctrlKey || e.metaKey) && e.keyCode === 86) { // ctrl + v
                    this.onCopyNodes()
                } else if ([37, 38, 39, 40].includes(e.keyCode)) { // 选中后支持上下左右移动节点
                    const typeMap = {
                        '37': 'left',
                        '38': 'top',
                        '39': 'right',
                        '40': 'bottom'
                    }
                    this.onMovePosition(typeMap[e.keyCode])
                }
            },
            nodeLineDeletehandler (e) {
                if (e.keyCode === 46 || e.keyCode === 8) {
                    this.selectedNodes.forEach(node => {
                        this.onNodeRemove(node)
                    })
                    this.onCloseFrameSelect()
                }
            },
            /**
             * 复制节点
             * @description
             * 生成新节点
             * 生成新连线
             * 选中新节点
             * 复制基础信息
             * 输入参数信息（勾选复用变量）
             * 输出参数（勾选新建变量）
             * 分支数据
             */
            onCopyNodes () {
                const { locations, lines } = this.createCopyOfSelectedNodes(this.copyNodes)
                const selectedIds = []
                const { x: originX, y: originY } = this.selectionOriginPos
                const { x, y } = this.pasteMousePos
                locations.forEach(location => {
                    location.x += (x - originX)
                    location.y += (y - originY)
                    selectedIds.push(location.id)
                    this.$refs.jsFlow.createNode(location)
                    this.$emit('onLocationChange', 'copy', location)
                })
                // 需要先生成节点 DOM，才能连线
                lines.forEach(line => {
                    this.$emit('onLineChange', 'add', line)
                    this.$nextTick(() => {
                        this.$refs.jsFlow.createConnector(line)
                    })
                })
                this.$nextTick(() => {
                    this.$refs.jsFlow.clearNodesDragSelection()
                    this.$refs.jsFlow.addNodesToDragSelection(selectedIds)
                    this.selectedNodes = locations
                })
            },
            // 获取复制节点、连线数据
            createCopyOfSelectedNodes (nodes) {
                const lines = []
                const locations = []
                const locationIdReplaceHash = {} // 节点 id 替换映射表
                const lineIdReplaceHash = {} // 连线 id 替换映射表
                nodes.forEach((node, index) => {
                    const location = tools.deepClone(node)
                    const activity = tools.deepClone(this.canvasData.activities[node.id])
                    // 复制 location 数据
                    if (activity) {
                        location.atomId = activity.type === 'ServiceActivity' ? activity.component.code : activity.template_id
                    }
                    if (location.type !== 'startpoint' && location.type !== 'endpoint') {
                        locations.push(location)
                        locationIdReplaceHash[node.id] = location.id = 'node' + uuid()
                        location.oldSouceId = node.id
                    }
                })
                // 复制 line 数据
                this.canvasData.lines.forEach(line => {
                    if (locationIdReplaceHash[line.source.id] && locationIdReplaceHash[line.target.id]) {
                        const lineCopy = tools.deepClone(line)
                        lineIdReplaceHash[line.id] = lineCopy.id = 'line' + uuid()
                        lineCopy.source.id = locationIdReplaceHash[line.source.id]
                        lineCopy.target.id = locationIdReplaceHash[line.target.id]
                        lineCopy.oldSouceId = line.id
                        lines.push(lineCopy)
                    }
                })
                return { locations, lines }
            },
            // 分支条件点击回调
            branchConditionEditHandler (e, overlayId) {
                const $branchEl = e.target
                const lineId = $branchEl.dataset.lineid
                const nodeId = $branchEl.dataset.nodeid
                const { name, evaluate: value } = this.canvasData.branchConditions[nodeId][lineId]
                if ($branchEl.classList.contains('branch-condition')) {
                    e.stopPropagation()
                    this.$emit('onConditionClick', {
                        id: lineId,
                        nodeId,
                        name,
                        value,
                        overlayId
                    })
                }
                if (this.editable) {
                    this.$emit('templateDataChanged')
                }
            },
            onToggleAllNode (val) {
                this.$emit('onToggleAllNode', val)
                this.showSmallMap = false
            },
            updateNodeMenuState (val) {
                this.showNodeMenu = val
                this.$emit('update:nodeMemuOpen', val)
            },
            updateCanvas () {
                const { locations: nodes, lines } = this.canvasData
                this.$refs.jsFlow.updateCanvas({ nodes, lines })
            },
            removeAllConnector () {
                this.$refs.jsFlow.removeAllConnector()
            },
            onShowNodeConfig (id) {
                this.$emit('onShowNodeConfig', id)
            },
            onNodeCheckClick (id, val) {
                this.$emit('onNodeCheckClick', id, val)
            },
            onUpdateNodeInfo (id, info) {
                const index = this.flowData.nodes.findIndex(item => item.id === id)
                const node = Object.assign({}, this.flowData.nodes[index], info)
                this.$set(this.flowData.nodes, index, node)
            },
            /**
             * 获取包含连线目标端点的节点
             * @param {Object} 端点 DOM 对象
             */
            getNodeWithEndpoint (endpoint) {
                const parentEl = endpoint.parentNode

                if (!parentEl || parentEl.nodeName === 'HTML') {
                    return false
                }

                if (parentEl.classList.contains('bk-flow-location')) {
                    return parentEl
                } else {
                    return this.getNodeWithEndpoint(parentEl)
                }
            },
            onCreateNodeBefore (node) {
                const nodeMenuEl = document.querySelector(`.node-menu`)
                if (node.atomId && nodeMenuEl) {
                    const nodeEl = document.querySelector('.adding-node')
                    const nodeWidth = nodeEl.offsetWidth
                    const nodeMenuWidth = nodeMenuEl.offsetWidth
                    if (nodeMenuWidth - node.x > (nodeWidth / 2)) {
                        return false
                    }
                }
                const validateMessage = validatePipeline.isLocationValid(node, this.canvasData.locations)

                if (!validateMessage.result) {
                    this.$bkMessage({
                        message: validateMessage.message,
                        theme: 'warning'
                    })
                    return false
                }
                this.$emit('templateDataChanged')
                return true
            },
            onCreateNodeAfter (node) {
                // copy 的节点不需要回调 add 方法
                if (node.oldSouceId) return
                this.$emit('onLocationChange', 'add', Object.assign({}, node))
                if (node.type === 'startpoint') {
                    this.isDisableStartPoint = true
                } else if (node.type === 'endpoint') {
                    this.isDisableEndPoint = true
                }
            },
            // 拖拽到节点上自动连接
            onConnectionDragStop (source, targetId, event) {
                if (source.id === targetId) {
                    return false // 非分支节点不可以连接自身
                }
                let arrow
                const nodeEl = document.getElementById(targetId)
                const nodeRects = nodeEl.getBoundingClientRect()
                const offsetX = event.clientX - nodeRects.left
                const offsetY = event.clientY - nodeRects.top
                if (offsetX < nodeRects.width / 2) {
                    if (offsetY < nodeRects.height / 2) {
                        arrow = offsetX > offsetY ? 'Top' : 'Left'
                    } else {
                        arrow = offsetX > (nodeRects.height - offsetY) ? 'Bottom' : 'Left'
                    }
                } else {
                    if (offsetY < nodeRects.height / 2) {
                        arrow = (nodeRects.width - offsetX) > offsetY ? 'Top' : 'Right'
                    } else {
                        arrow = (nodeRects.width - offsetX) > (nodeRects.height - offsetY) ? 'Bottom' : 'Right'
                    }
                }

                const line = {
                    source,
                    target: {
                        id: targetId,
                        arrow
                    }
                }
                const validateMessage = validatePipeline.isLineValid(line, this.canvasData)
                if (validateMessage.result) {
                    this.$emit('onLineChange', 'add', line)
                    this.$refs.jsFlow.createConnector(line)
                } else {
                    this.$bkMessage({
                        message: validateMessage.message,
                        theme: 'warning'
                    })
                }
            },
            onConnectionClick (connection, e) {
                if (e.target.tagName !== 'path') {
                    return
                }
                const lineInCanvasData = this.canvasData.lines.find(item => {
                    return item.source.id === connection.sourceId && item.target.id === connection.targetId
                })
                const lineId = lineInCanvasData.id
                const deleteOverlay = connection.getOverlay(`delete_icon_${lineId}`)
                if (!deleteOverlay) {
                    this.$refs.jsFlow.addLineOverlay(connection, {
                        type: 'Label',
                        name: '<i class="common-icon-bkflow-delete"></i>',
                        location: -45,
                        cls: 'delete-line-icon',
                        id: `delete_icon_${lineId}`
                    })
                    this.activeCon = connection
                }
            },
            // 拖拽到端点上连接
            onBeforeDrop (line) {
                const { sourceId, targetId, connection, dropEndpoint } = line
                if (sourceId === targetId) {
                    return false
                }

                const data = {
                    source: {
                        id: sourceId,
                        arrow: connection.endpoints[0].anchor.type
                    },
                    target: {
                        id: targetId,
                        arrow: dropEndpoint.anchor.type
                    }
                }
                const validateMessage = validatePipeline.isLineValid(data, this.canvasData)
                if (validateMessage.result) {
                    this.$emit('onLineChange', 'add', data)
                    this.$emit('templateDataChanged')
                    return true
                } else {
                    this.$bkMessage({
                        message: validateMessage.message,
                        theme: 'warning'
                    })
                }
            },
            onConnection (line) {
                this.$nextTick(() => {
                    const lineInCanvasData = this.canvasData.lines.find(item => {
                        return item.source.id === line.sourceId && item.target.id === line.targetId
                    })
                    const lineId = lineInCanvasData.id
                    // 调整连线配置
                    if (lineInCanvasData.hasOwnProperty('midpoint')) {
                        const config = [
                            'Flowchart',
                            {
                                stub: [10, 10],
                                alwaysRespectStub: true,
                                gap: 0,
                                cornerRadius: 10,
                                midpoint: lineInCanvasData.midpoint
                            }
                        ]
                        
                        this.$refs.jsFlow.setConnector(lineInCanvasData.source.id, lineInCanvasData.target.id, config)
                    }
                    // 增加连线删除 icon
                    this.$refs.jsFlow.addLineOverlay(line, {
                        type: 'Label',
                        name: '<i class="common-icon-dark-circle-close"></i>',
                        location: 0.5,
                        cls: 'delete-line-circle-icon',
                        id: `close_${lineId}`
                    })
                    const branchInfo = this.canvasData.branchConditions[line.source.id]
                    // 增加分支网关 label
                    if (branchInfo && Object.keys(branchInfo).length > 0) {
                        const labelValue = branchInfo[lineId].evaluate
                        // 兼容旧数据，分支条件里没有 name 属性的情况
                        const labelName = branchInfo[lineId].name || labelValue
                        const labelData = {
                            type: 'Label',
                            name: `<div class="branch-condition"
                                    title="${tools.escapeStr(labelName)}(${tools.escapeStr(labelValue)})"
                                    data-lineid="${lineId}"
                                    data-nodeid="${line.sourceId}">${labelName}</div>`,
                            location: -70,
                            cls: 'branch-condition',
                            id: `condition${lineId}`
                        }
                        this.$refs.jsFlow.addLineOverlay(line, labelData)
                    }
                })
            },
            onConnectionDetached (connection) {
                const line = {
                    source: {
                        id: connection.sourceId
                    },
                    target: {
                        id: connection.targetId
                    }
                }
                this.$emit('templateDataChanged')
                this.$emit('onLineChange', 'delete', line)
            },
            onNodeMoveStop (loc) {
                this.$emit('templateDataChanged')
                if (this.selectedNodes.length) {
                    const item = this.selectedNodes.find(m => m.id === loc.id)
                    if (!item) {
                        return false
                    }
                    const { x, y } = item
                    const bX = loc.x - x
                    const bY = loc.y - y
                    this.selectedNodes.forEach(node => {
                        node.x += bX
                        node.y += bY
                        this.$emit('onLocationMoveDone', node)
                    })
                } else {
                    this.$emit('onLocationMoveDone', loc)
                }
            },
            onOverlayClick (overlay, e) {
                // 点击 overlay 类型
                const TypeMap = [
                    { type: 'close', rule: /^(close|delete_icon)_(\w*)/ },
                    { type: 'branchCondition', rule: /^(condition)(\w*)/ }
                ]
                let lineId = ''
                const result = TypeMap.find(m => {
                    const val = overlay.id.match(m.rule)
                    if (val && val[2] !== '') {
                        lineId = val[2]
                        return true
                    }
                })
                if (lineId && result.type === 'close') {
                    const line = this.canvasData.lines.find(item => item.id === lineId)
                    this.$refs.jsFlow.removeConnector(line)
                    this.activeCon = null
                }
                if (lineId && result.type === 'branchCondition') {
                    this.branchConditionEditHandler(e, overlay.id)
                }
            },
            onNodeRemove (node) {
                this.$refs.jsFlow.removeNode(node)
                this.$emit('templateDataChanged')
                this.$emit('onLocationChange', 'delete', node)

                if (node.type === 'startpoint') {
                    this.isDisableStartPoint = false
                } else if (node.type === 'endpoint') {
                    this.isDisableEndPoint = false
                }
            },
            onBeforeDrag (data) {
                if (this.referenceLine.id && this.referenceLine.id === data.sourceId) {
                    this.clearReferenceLine()
                }
                this.handleDeleteLineIconHide()
            },
            // 节点拖动回调
            onNodeMoving (node) {
                // 在有参考线的情况下，拖动参考线来源节点，将移出参考线
                if (this.referenceLine.id && this.referenceLine.id === node.id) {
                    this.clearReferenceLine()
                }
                if (node.id !== this.idOfNodeShortcutPanel) {
                    this.handleShortcutPanelHide()
                }
                this.handleDeleteLineIconHide()
            },
            // 初始化生成参考线
            createReferenceLine () {
                const canvas = document.querySelector('.canvas-flow-wrap')
                const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
                svg.setAttribute('id', 'referenceLine')
                svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
                svg.setAttribute('version', '1.1')
                svg.setAttribute('style', 'position:absolute;left:0;top:0;width:100%;height:100%;pointer-events: none;')

                const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs')
                const marker = `
                    <marker id="arrow" markerWidth="10" markerHeight="10" refx="0" refy="2" orient="auto" markerUnits="strokeWidth">
                        <path d="M0,0 L0,4 L6,2 z" fill="#979ba5" />
                    </marker>
                `
                defs.innerHTML = marker

                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line')
                line.setAttribute('id', 'referencePath')
                line.setAttribute('marker-end', 'url(#arrow)')
                line.setAttribute('x1', '0')
                line.setAttribute('y1', '0')
                line.setAttribute('x2', '0')
                line.setAttribute('y2', '0')
                line.setAttribute('style', 'stroke:#979ba5;stroke-width:2')
                line.setAttribute('id', 'referencePath')

                svg.appendChild(defs)
                svg.appendChild(line)
                canvas.appendChild(svg)
                document.body.addEventListener('mousedown', this.clearReferenceLine, { once: true })
            },
            // 更新参考线位置
            updataReferenceLinePositon (startPos, endPos) {
                const referencePath = document.getElementById('referencePath')
                if (referencePath) {
                    referencePath.setAttribute('x1', startPos.x)
                    referencePath.setAttribute('y1', startPos.y)
                    referencePath.setAttribute('x2', endPos.x)
                    referencePath.setAttribute('y2', endPos.y)
                }
            },
            // 清除参考线
            clearReferenceLine () {
                const canvas = document.querySelector('.canvas-flow-wrap')
                const line = document.getElementById('referenceLine')
                if (canvas && line) {
                    canvas.removeChild(line)
                }
                document.getElementById('canvasContainer').removeEventListener('mousemove', this.handleReferenceLine, false)
                this.referenceLine = {}
            },
            // 锚点点击回调
            onEndpointClick (edp, event) {
                if (!this.editable) {
                    return false
                }
                const { x: offsetX, y: offsetY } = document.querySelector('.canvas-flow-wrap').getBoundingClientRect()
                const { left, top, width, height } = edp.canvas.getBoundingClientRect()
                const type = edp.anchor.type
                const bX = left + width / 2 - offsetX
                const bY = top + height / 2 - offsetY
                // 第二次点击
                if (this.referenceLine.id && edp.elementId !== this.referenceLine.id) {
                    this.createLine(
                        { id: this.referenceLine.id, arrow: this.referenceLine.arrow },
                        { id: edp.elementId, arrow: type }
                    )
                    this.clearReferenceLine()
                    return false
                }
                this.createReferenceLine()
                this.handleDeleteLineIconHide()
                this.referenceLine = { x: bX, y: bY, id: edp.elementId, arrow: type }
                document.getElementById('canvasContainer').addEventListener('mousemove', this.handleReferenceLine, false)
            },
            // 鼠标移动更新参考线
            handleReferenceLine (e) {
                const { pageX, pageY } = e
                const { x: offsetX, y: offsetY } = document.querySelector('.canvas-flow-wrap').getBoundingClientRect()
                const bX = pageX - offsetX
                const bY = pageY - offsetY
                const endPos = { x: bX, y: bY }
                const animationFrame = () => {
                    return window.requestAnimationFrame || function (fn) {
                        setTimeout(fn, 1000 / 60)
                    }
                }
                animationFrame(this.updataReferenceLinePositon(this.referenceLine, endPos))
            },
            // 创建节点间连线
            createLine (source, target) {
                if (source.id === target.id) {
                    return false
                }
                
                const line = {
                    source,
                    target
                }
                const validateMessage = validatePipeline.isLineValid(line, this.canvasData)
                if (validateMessage.result) {
                    this.$emit('onLineChange', 'add', line)
                    this.$refs.jsFlow.createConnector(line)
                    this.referenceLine.id = ''
                } else {
                    this.$bkMessage({
                        message: validateMessage.message,
                        theme: 'warning'
                    })
                }
            },
            onRetryClick (id) {
                this.$emit('onRetryClick', id)
            },
            onSkipClick (id) {
                this.$emit('onSkipClick', id)
            },
            onForceFail (id) {
                this.$emit('onForceFail', id)
            },
            onModifyTimeClick (id) {
                this.$emit('onModifyTimeClick', id)
            },
            onGatewaySelectionClick (id) {
                this.$emit('onGatewaySelectionClick', id)
            },
            onTaskNodeResumeClick (id) {
                this.$emit('onTaskNodeResumeClick', id)
            },
            onSubflowPauseResumeClick (id, value) {
                this.$emit('onSubflowPauseResumeClick', id, value)
            },
            onToggleHotKeyInfo (val) {
                this.showSmallMap = false
                this.isShowHotKey = !this.isShowHotKey
            },
            onCloseHotkeyInfo () {
                this.isShowHotKey = false
            },
            /**
             * 单个添加选中节点
             */
            addNodeToSelectedList (selectedNode) {
                document.removeEventListener('keydown', this.nodeLineDeletehandler)
                document.addEventListener('keydown', this.nodeLineDeletehandler)
                const index = this.selectedNodes.findIndex(m => m.id === selectedNode.id)
                if (index > -1) { // 已存在
                    this.$refs.jsFlow.clearNodesDragSelection()
                    this.$delete(this.selectedNodes, index)
                    this.$delete(this.copyNodes, index)
                    const ids = this.selectedNodes.map(m => m.id)
                    this.$refs.jsFlow.addNodesToDragSelection(ids)
                } else {
                    this.selectedNodes.push(selectedNode)
                    this.copyNodes.push(selectedNode)
                    const ids = this.selectedNodes.map(m => m.id)
                    this.$refs.jsFlow.addNodesToDragSelection(ids)
                }
                // 重新计算粘贴相对位置
                this.selectionOriginPos = this.getNodesLocationOnLeftTop(this.selectedNodes)
                document.addEventListener('keydown', this.nodeSelectedhandler)
                document.addEventListener('mousedown', this.handleClearDragSelection, { once: true })
                this.$refs.jsFlow.$el.addEventListener('mousemove', this.pasteMousePosHandler)
            },
            /**
             * 失焦时移除选中节点
             */
            handleClearDragSelection () {
                this.selectedNodes = []
                this.copyNodes = []
                this.$refs.jsFlow.clearNodesDragSelection()
                document.removeEventListener('mousedown', this.handleClearDragSelection, { once: true })
                document.removeEventListener('keydown', this.nodeSelectedhandler)
                document.removeEventListener('keydown', this.nodeLineDeletehandler)

                this.$refs.jsFlow.$el.removeEventListener('mousemove', this.pasteMousePosHandler)
            },
            /**
             * 获取节点组里，相对画布靠左上角的点位置
             */
            getNodesLocationOnLeftTop (nodes) {
                let x = 0
                let y = 0
                nodes.forEach((node, index) => {
                    x = index === 0 ? node.x : Math.min(x, node.x)
                    y = index === 0 ? node.y : Math.min(y, node.y)
                })
                return { x, y }
            },
            // 更新分支条件数据
            updataConditionCanvasData (data) {
                const { name, overlayId, id: lineId, value } = data
                const line = this.canvasData.lines.find(item => item.id === lineId)
                this.$refs.jsFlow.removeLineOverlay(line, overlayId)
                this.$nextTick(() => {
                    const labelData = {
                        type: 'Label',
                        name: `<div class="branch-condition"
                                title="${tools.escapeStr(name)}(${tools.escapeStr(value)})"
                                data-lineid="${lineId}"
                                data-nodeid="${line.source.id}">${name}</div>`,
                        location: -70,
                        cls: 'branch-condition',
                        id: `condition${lineId}`
                    }
                    this.$refs.jsFlow.addLineOverlay(line, labelData)
                })
            },
            // node mousedown
            onNodeMousedown (id) {
                this.$emit('onNodeMousedown', id)
            },
            // 点击节点
            onNodeClick (id, type, event) {
                this.$emit('onNodeClick', id, type)
                // 如果不是模版编辑页面，点击节点相当于打开配置面板（任务执行是打开执行信息面板）
                if (!this.editable) {
                    this.onShowNodeConfig(id)
                    return
                }
                if (this.referenceLine.id) {
                    // 自动连线
                    this.onConnectionDragStop({ id: this.referenceLine.id, arrow: this.referenceLine.arrow }, id, event)
                    // 移出参考线
                    this.clearReferenceLine()
                    return
                }
                if (type !== 'endpoint') {
                    this.showShortcutPane(id)
                }
                this.handleDeleteLineIconHide()
            },
            onNodeDblclick (id) {
                this.onShowNodeConfig(id)
                this.handleShortcutPanelHide()
                this.handleDeleteLineIconHide()
            },
            // 显示快捷节点面板
            showShortcutPane (id) {
                if (this.idOfNodeShortcutPanel) {
                    this.onUpdateNodeInfo(this.idOfNodeShortcutPanel, { isActived: false })
                }
                this.onUpdateNodeInfo(id, { isActived: true })
                this.updataSelctedNodeData(id)
            },
            // 隐藏快捷节点面板
            handleShortcutPanelHide (e) {
                if (e && dom.parentClsContains('canvas-node', e.target)) {
                    return false
                }
                this.onUpdateNodeInfo(this.idOfNodeShortcutPanel, { isActived: false })
                this.toggleNodeLevel(this.idOfNodeShortcutPanel, false)
                this.idOfNodeShortcutPanel = ''
            },
            handleDeleteLineIconHide (e) {
                if (this.activeCon && (e && !dom.parentClsContains('delete-line-icon', e.target))) {
                    const lineInCanvasData = this.canvasData.lines.find(item => {
                        return item.source.id === this.activeCon.sourceId && item.target.id === this.activeCon.targetId
                    })
                    if (lineInCanvasData) {
                        const lineId = lineInCanvasData.id
                        this.activeCon.removeOverlay(`delete_icon_${lineId}`)
                        this.activeCon = null
                    }
                }
            },
            // 切换节点层级状态
            toggleNodeLevel (id, isActived) {
                const node = document.getElementById(id)
                if (!id || !node) return
                if (!isActived) {
                    node.classList.remove('actived')
                } else {
                    node.classList.add('actived')
                }
            },
            // 更新选中节点数据
            updataSelctedNodeData (id) {
                // 切换节点层级状态
                this.toggleNodeLevel(this.idOfNodeShortcutPanel, false)
                this.toggleNodeLevel(id, true)
                this.idOfNodeShortcutPanel = id
            },
            // 节点后面追加
            onAppendNode ({ location, line, isFillParam }) {
                const type = isFillParam ? 'copy' : 'add'
                this.$refs.jsFlow.createNode(location)
                this.$emit('onLocationChange', type, location)
                this.$emit('onLineChange', 'add', line)
                this.$nextTick(() => {
                    this.$refs.jsFlow.createConnector(line)
                    this.showShortcutPane(location.id)
                })
            },
            /**
             * 两个节点间插入一个节点
             * @param {String} startNode -前节点 id
             * @param {String} endNode -后节点 id
             * @param {Object} location -新建节点的 location
             */
            onInsertNode ({ startNodeId, endNodeId, location, isFillParam }) {
                const type = isFillParam ? 'copy' : 'add'
                const deleteLine = this.canvasData.lines.find(line => line.source.id === startNodeId && line.target.id === endNodeId)
                if (!deleteLine) {
                    return false
                }
                this.$refs.jsFlow.removeConnector(deleteLine)
                const startLine = {
                    source: {
                        arrow: 'Right',
                        id: startNodeId
                    },
                    target: {
                        id: location.id,
                        arrow: 'Left'
                    }
                }
                const endLine = {
                    source: {
                        arrow: 'Right',
                        id: location.id
                    },
                    target: {
                        id: endNodeId,
                        arrow: 'Left'
                    }
                }
                this.$refs.jsFlow.createNode(location)
                this.$emit('onLocationChange', type, location)
                this.$emit('onLineChange', 'add', startLine)
                this.$emit('onLineChange', 'add', endLine)
                this.$nextTick(() => {
                    this.$refs.jsFlow.createConnector(startLine)
                    this.$refs.jsFlow.createConnector(endLine)
                    this.showShortcutPane(location.id)
                })
            },
            /**
             * 切换选中节点
             * @description
             * 临时添加该方法，后面还和 jsflow 配合实现
             */
            toggleSelectedNode (nodeId, isSelected) {
                this.selecAtomtNodeId = nodeId
                const node = document.getElementById(nodeId)
                if (isSelected) {
                    node && node.classList.add('selected')
                } else {
                    node && node.classList.remove('selected')
                }
            },
            // 移动微调节点位置
            onMovePosition (type) {
                if (!this.selectedNodes.length) {
                    return false
                }
                this.onMoveNodesByHand(this.selectedNodes, type)
            },
            /**
             * 手动移动节点
             * @param {Array} selectedIds 移动节点信息，数组
             * @param {String} direction 移动方向
             * @param {Number} length 移动距离，默认 5px
             */
            onMoveNodesByHand (selectedIds, direction, length = 5) {
                const ins = this.$refs.jsFlow.instance
                let bx = 0
                let by = 0
                switch (direction) {
                    case 'left':
                        bx = -length
                        break
                    case 'right':
                        bx = length
                        break
                    case 'top':
                        by = -length
                        break
                    case 'bottom':
                        by = length
                        break
                }
                this.$emit('templateDataChanged')
                selectedIds.forEach((node, index) => {
                    const el = document.getElementById(node.id)
                    const newX = node.x + bx
                    const newY = node.y + by
                    const newLoc = { id: node.id, x: newX, y: newY }
                    node.x = newX
                    node.y = newY
                    this.$emit('onLocationMoveDone', newLoc)
                    window.requestAnimationFrame(() => {
                        el.style.top = newY + 'px'
                        el.style.left = newX + 'px'
                        ins.revalidate(el)
                    })
                })
            },
            // 画布滚轮缩放
            onMouseWheel (e) {
                if (!e.ctrlKey) {
                    return false
                }
                e.preventDefault()
                const ev = e || window.event
                let down = true
                down = ev.wheelDelta ? ev.wheelDelta < 0 : ev.detail > 0
                if (down) {
                    this.onZoomOut(this.zoomOriginPosition)
                } else {
                    this.onZoomIn(this.zoomOriginPosition)
                }
                return false
            },
            // 记录缩放点
            onCanvasMouseMove (e) {
                const { x: offsetX, y: offsetY } = document.querySelector('.canvas-flow-wrap').getBoundingClientRect()
                this.zoomOriginPosition.x = e.pageX - offsetX
                this.zoomOriginPosition.y = e.pageY - offsetY
            },
            /**
             * 设置画布偏移量
             * @param {Number} x 画布向右偏移量
             * @param {Number} y 画布向下偏移量
             * @param {Boolean} animation 是否设置缓动动画
             */
            setCanvasPosition (x, y, animation = false) {
                if (animation) {
                    const canvas = this.$refs.jsFlow.$el.querySelector('#canvas-flow')
                    canvas.style.transition = 'left 0.4s, top 0.4s'
                    this.$refs.jsFlow.setCanvasPosition(x, y)
                    setTimeout(() => {
                        canvas.style.transition = 'unset'
                    }, 600)
                } else {
                    this.$refs.jsFlow.setCanvasPosition(x, y)
                }
            },
            // 下载画布图片
            onDownloadCanvas () {
                this.onGenerateCanvas().then(res => {
                    if (this.canvasImgDownloading) {
                        return
                    }
                    this.canvasImgDownloading = true
                    const imgEl = document.createElement('a')
                    imgEl.download = `bk_sops_template_${+new Date()}.png`
                    imgEl.href = res
                    imgEl.click()
                    this.canvasImgDownloading = false
                })
            },
            // 生成画布图片
            onGenerateCanvas  () {
                const canvasFlWp = document.querySelector('.canvas-flow-wrap')
                const baseOffset = 200 // 节点宽度
                const xList = this.canvasData.locations.map(node => node.x)
                const yList = this.canvasData.locations.map(node => node.y)
                const minX = Math.min(...xList)
                const maxX = Math.max(...xList)
                const minY = Math.min(...yList)
                const maxY = Math.max(...yList)
                const offsetX = minX < 0 ? -minX : 0
                const offsetY = minY < 0 ? -minY : 0
                let width = null
                if (minX < 0) {
                    width = maxX > this.windowWidth ? maxX - minX : this.windowWidth - minX
                } else {
                    width = maxX > this.windowWidth ? maxX : this.windowWidth
                }
                let height = null
                if (minY < 0) {
                    height = maxY > this.windowHeight ? maxY - minY : this.windowHeight - minY
                } else {
                    height = maxY > this.windowHeight ? maxY : this.windowHeight
                }
                this.canvasHeight = height + baseOffset + 30
                this.canvasWidth = width + baseOffset + 80
                return domtoimage.toJpeg(canvasFlWp, {
                    bgcolor: '#ffffff',
                    height: this.canvasHeight,
                    width: this.canvasWidth,
                    cloneBack: clone => {
                        clone.style.width = this.canvasWidth + 'px'
                        clone.style.height = this.canvasHeight + 'px'
                        const canvasDom = clone.querySelector('#canvas-flow')
                        canvasDom.style.left = offsetX + 30 + 'px'
                        canvasDom.style.top = offsetY + 30 + 'px'
                        canvasDom.style.right = 0 + 'px'
                        canvasDom.style.bottom = 0 + 'px'
                        canvasDom.style.transform = 'inherit'
                        canvasDom.style.border = 0
                    }
                })
            },
            getInitialValue () {
                // 计算选择框的初始left top
                const canvasFlow = document.querySelector('#canvas-flow')
                const selectBox = document.querySelector('.select-box')
                const miniMapWidth = this.windowWidth / this.canvasWidth * this.smallMapWidth
                const miniMapHeight = this.windowHeight / this.canvasHeight * this.smallMapHeight
                // 画布的Top和Left
                const xList = this.canvasData.locations.map(node => node.x)
                const yList = this.canvasData.locations.map(node => node.y)
                const minX = Math.min(...xList)
                const minY = Math.min(...yList)
                let initialLeft = null
                const leftMostNodeLeft = minX < 0 ? -minX : 0
                const topMostNodeTop = minY < 0 ? -minY : 0
                const offsetGapLeft = (canvasFlow.offsetLeft > 0 ? -leftMostNodeLeft : leftMostNodeLeft) - canvasFlow.offsetLeft
                const scaleOffsetLeft = this.smallMapWidth / this.canvasWidth * offsetGapLeft
                if (scaleOffsetLeft + miniMapWidth >= this.smallMapWidth) {
                    initialLeft = miniMapWidth < this.smallMapWidth ? this.smallMapWidth - miniMapWidth : scaleOffsetLeft
                } else {
                    initialLeft = scaleOffsetLeft > 0 ? scaleOffsetLeft : 0
                }
                let initialTop = null
                const offsetGapTop = (canvasFlow.offsetTop > 0 ? -topMostNodeTop : topMostNodeTop) - canvasFlow.offsetTop
                const scaleOffsetTop = this.smallMapHeight / this.canvasHeight * offsetGapTop
                if (scaleOffsetTop + miniMapHeight >= this.smallMapHeight) {
                    initialTop = miniMapHeight < this.smallMapHeight ? this.smallMapHeight - miniMapHeight : scaleOffsetTop
                } else {
                    initialTop = scaleOffsetTop > 0 ? scaleOffsetTop : 0
                }
                this.initialLeft = leftMostNodeLeft
                this.initialTop = topMostNodeTop
                selectBox.style.width = miniMapWidth + 'px'
                selectBox.style.height = miniMapHeight + 'px'
                selectBox.style.left = initialLeft + 'px'
                selectBox.style.top = initialTop + 'px'
            },
            onMouseDownSelect (e) {
                this.isMouseEnterX = e.offsetX
                this.isMouseEnterY = e.offsetY
                this.$refs.selectBox.addEventListener('mousemove', this.selectBoxMoveHandler, false)
                window.addEventListener('mouseup', this.onMouseUpListener, false)
            },
            onMouseUpListener () {
                this.$refs.selectBox.removeEventListener('mousemove', this.selectBoxMoveHandler, false)
                window.removeEventListener('mouseup', this.onMouseUpListener, false)
            },
            selectBoxMoveHandler (e) {
                const moreOffsetTop = 30 // 画布多向上偏移30px  露出点空白
                const moreOffsetLeft = 30 // 画布多向左偏移30px  露出点空白
                const selectBox = document.querySelector('.select-box')
                const smallMapDistanceTop = this.$refs.smallMap.getBoundingClientRect().top // 小地图到顶部的距离
                const samllmapDistanceLeft = this.$refs.smallMap.getBoundingClientRect().left // 小地图到左侧的距离
                const targetX = e.clientX - this.isMouseEnterX - samllmapDistanceLeft
                const targetY = e.clientY - this.isMouseEnterY - smallMapDistanceTop
                // // 计算选择框宽高
                const selectWidth = this.windowWidth / this.canvasWidth * this.smallMapWidth
                const selectHeight = this.windowHeight / this.canvasHeight * this.smallMapHeight
                // 边界检查
                let left = null
                let top = null
                const maxLeft = this.smallMapWidth - selectWidth
                if (targetX < 0) {
                    left = 0
                } else if (targetX > maxLeft) {
                    left = maxLeft
                } else {
                    left = targetX
                }
                const maxTop = this.smallMapHeight - selectHeight
                if (targetY < 0) {
                    top = 0
                } else if (targetY > maxTop) {
                    top = maxTop
                } else {
                    top = targetY
                }
                selectBox.style.left = left + 'px'
                selectBox.style.top = top + 'px'
                // 计算画布的Top和Left
                const canvasPositionX = -left * (this.canvasWidth / this.smallMapWidth) + this.initialLeft + moreOffsetLeft
                const canvasPositionY = -top * (this.canvasHeight / this.smallMapHeight) + this.initialTop + moreOffsetTop
                this.setCanvasPosition(canvasPositionX, canvasPositionY)
            }
        }
    }
</script>
<style lang="scss">
    .canvas-container {
        position: relative;
        width: 100%;
        height: 100%;
    }
    .canvas-wrapper.jsflow {
        border: none;
        background: #e1e4e8;
        .palette-panel-wrap {
            border-right: 1px solid #cacedb;
        }
        .tool-panel-wrap {
            top: 20px;
            left: 80px;
            z-index: 5;
            transition: all 0.5s ease;
            user-select: none;
            background: #ffffff;
            opacity: 1;
            padding: 0;
            border-radius: 2px;
            box-shadow: 0px 2px 4px 0px rgba(0,0,0,0.10);
        }
        .jtk-endpoint {
            z-index: 3;
        }
        .jsflow-node {
            z-index: 4;
            &.adding-node {
                z-index: 6;
            }
            &.jtk-drag,
            &.adding-node
             {
                .process-node,
                .subflow-node,
                .gateway-node,
                .circle-node {
                    cursor: move;
                }
            }
        }
        .jtk-connector {
            z-index: 2;
        }
        .jtk-overlay {
            cursor: pointer;
            z-index: 3;
            &.delete-line-circle-icon {
                display: none;
            }
            &.delete-line-icon {
                margin-left: 10px;
                margin-top: -14px;
                color: #52699d;
                font-size: 14px;
                line-height: 1;
                background: #e1e4e8;
                z-index: 10;
            }
            .common-icon-dark-circle-close{
                font-size: 16px;
                color: #63656e;
                background: #ffffff;
                border-radius: 50%;
            }
            .branch-condition {
                padding: 4px 6px;
                min-width: 60px;
                max-width: 112px;
                min-height: 20px;
                font-size: 12px;
                text-align: center;
                color: #978e4d;
                background: #fcf9e2;
                border: 1px solid #ccc79f;
                border-radius: 2px;
                outline: none;
                cursor: pointer;
                &:focus,
                &:hover {
                    border-color: #3a84ff;
                }
                white-space: nowrap;
                text-overflow: ellipsis;
                overflow: hidden;
            }
        }
        &.editable {
            .jtk-overlay.jtk-hover {
                display: inline-block;
            }
            .jtk-endpoint {
                cursor: pointer;
                &.template-canvas-endpoint:not(.jtk-dragging) {
                    &:after {
                        display: none;
                        position: absolute;
                        content: '';
                        height: 32px;
                        width: 32px;
                        background: url('~@/assets/images/endpoint.png') center/32px no-repeat;
                        border-radius: 50%;
                        box-shadow: 0px 2px 4px 0px rgba(0,0,0,0.10);
                    }
                    &:hover:after {
                        background: url('~@/assets/images/endpoint-hover.png') center/32px no-repeat;
                    }
                    &:hover,
                    &.jtk-endpoint-highlight {
                        &:after {
                            display: block;
                        }
                        &[data-pos="Top"]:after {
                            bottom: 22px;
                            left: 0px;
                            transform: rotate(-90deg);
                        }
                        &[data-pos="Bottom"]:after {
                            top: 22px;
                            left: 0;
                            transform: rotate(90deg);
                        }
                        &[data-pos="Left"]:after {
                            top: 0;
                            right: 22px;
                            transform: rotate(-180deg);
                        }
                        &[data-pos="Right"]:after {
                            top: 0;
                            left: 22px;
                        }
                    }
                }
            }
        }
        &:not(.editable) {
            .jtk-endpoint circle{
                fill: transparent;
                stroke: transparent;
            }
        }
        &.tool-wrapper-telescopic {
            .tool-panel-wrap {
                top: 20px;
                left: 380px;
                z-index: 5;
            }
            & + .help-info-wrap {
                .hot-key-panel {
                    left: 380px;
                    z-index: 5;
                }
            }
        }
        .jsflow-node.actived,
        .jsflow-node.jtk-drag {
            z-index: 5;
        }
        .reference-line-vertical,
        .reference-line-horizontal {
            z-index: 6;
        }
    }
    .drag-reference-line {
        display: none;
        position: absolute;
        width: 0px;
        height: 2px;
        background: #979ba5;
        left: 120px;
        top: 126px;
        z-index: 1;
        cursor: grab;
        &::before {
            position: absolute;
            right: 0;
            top: -3px;
            content: '';
            width: 0;
            height: 0;
            border-top: 4px solid transparent;
            border-left: 8px solid #979ba5;
            border-bottom: 4px solid transparent;
        }
    }
    .small-map {
        position: absolute;
        z-index: 5;
        left: 80px;
        top: 80px;
        width: 344px;
        height: 216px;
        border-radius: 4px;
        background-color: #fafbfd;
        transition: all 0.5s ease;
        box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.15);
        img {
            height: 100%;
            width: 100%;
        }
        .select-box {
            position: absolute;
            z-index: 6;
            top: 0;
            left: 0;
            width: 205px;
            height: 112px;
            border: 1px solid #738abe;
            border-radius: 2px;
            cursor: pointer;
        }
    }
</style>
