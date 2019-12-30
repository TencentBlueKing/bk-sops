/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
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
        <js-flow
            ref="jsFlow"
            selector="entry-item"
            :class="['canvas-wrapper', { 'tool-wrapper-telescopic': showNodeMenu }]"
            :data="flowData"
            :show-palette="showPalette"
            :show-tool="showTool"
            :editable="editable"
            :endpoint-options="endpointOptions"
            :connector-options="connectorOptions"
            @onCreateNodeBefore="onCreateNodeBefore"
            @onCreateNodeAfter="onCreateNodeAfter"
            @onConnectionDragStop="onConnectionDragStop"
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
                    :atom-type-list="atomTypeList"
                    :is-disable-start-point="isDisableStartPoint"
                    :is-disable-end-point="isDisableEndPoint"
                    @updateNodeMenuState="updateNodeMenuState">
                </palette-panel>
            </template>
            <template v-slot:toolPanel>
                <tool-panel
                    :is-selection-open="isSelectionOpen"
                    :is-show-select-all-tool="isShowSelectAllTool"
                    :is-select-all-tool-disabled="isSelectAllToolDisabled"
                    :is-all-selected="isAllSelected"
                    :editable="editable"
                    @onZoomIn="onZoomIn"
                    @onZoomOut="onZoomOut"
                    @onResetPosition="onResetPosition"
                    @onOpenFrameSelect="onOpenFrameSelect"
                    @onFormatPosition="onFormatPosition"
                    @onToggleAllNode="onToggleAllNode"
                    @onToggleHotKeyInfo="onToggleHotKeyInfo">
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
                    @onSubflowPauseResumeClick="onSubflowPauseResumeClick">
                </node-template>
            </template>
        </js-flow>
        <help-info
            :editable="editable"
            :is-show-hot-key="isShowHotKey"
            @onZoomIn="onZoomIn"
            @onZoomOut="onZoomOut"
            @onMovePosition="onMovePosition"
            @onResetPosition="onResetPosition"
            @onCloseHotkeyInfo="onCloseHotkeyInfo">
        </help-info>
        <div ref="dragReferenceLine" class="drag-reference-line"></div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import JsFlow from '@/assets/js/jsflow.esm.js'
    import { uuid } from '@/utils/uuid.js'
    import NodeTemplate from './NodeTemplate/index.vue'
    import PalettePanel from './PalettePanel/index.vue'
    import HelpInfo from './HelpInfo/index.vue'
    import ToolPanel from './ToolPanel/index.vue'
    import tools from '@/utils/tools.js'
    import dom from '@/utils/dom.js'
    import { endpointOptions, connectorOptions } from './options.js'
    import validatePipeline from '@/utils/validatePipeline.js'

    export default {
        name: 'TemplateCanvas',
        components: {
            JsFlow,
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
            singleAtomListLoading: {
                type: Boolean,
                default: false
            },
            subAtomListLoading: {
                type: Boolean,
                default: false
            },
            hasAdminPerm: {
                type: Boolean,
                default: false
            },
            canvasData: {
                type: Object,
                default () {
                    return {
                        'lines': [],
                        'locations': []
                    }
                }
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
                idOfNodeShortcutPanel: '',
                showNodeMenu: false,
                isDisableStartPoint: false,
                isDisableEndPoint: false,
                isSelectionOpen: false,
                isShowHotKey: false,
                isCanCreateline: false,
                selectedNodes: [],
                copyNodes: [],
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
                flowData,
                endpointOptions: combinedEndpointOptions,
                connectorOptions
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
        mounted () {
            this.isDisableStartPoint = !!this.canvasData.locations.find((location) => location.type === 'startpoint')
            this.isDisableEndPoint = !!this.canvasData.locations.find((location) => location.type === 'endpoint')
            document.body.addEventListener('click', this.handleShortcutPanelHide, false)
        },
        beforeDestroy () {
            this.$refs.jsFlow.$el.removeEventListener('mousemove', this.pasteMousePosHandler)
            document.removeEventListener('keydown', this.nodeSelectedhandler)
            document.removeEventListener('keydown', this.nodeLineDeletehandler)
            document.body.removeEventListener('click', this.handleShortcutPanelHide, false)
            document.body.removeEventListener('click', this.handleReferenceLineHide, false)
        },
        methods: {
            onZoomIn () {
                this.$refs.jsFlow.zoomIn()
            },
            onZoomOut () {
                this.$refs.jsFlow.zoomOut()
            },
            onResetPosition () {
                this.$refs.jsFlow.resetPosition()
            },
            onFormatPosition () {
                this.$emit('onFormatPosition')
            },
            onOpenFrameSelect () {
                this.isSelectionOpen = true
                this.$refs.jsFlow.frameSelect()
            },
            onFrameSelectEnd (nodes, x, y) {
                this.selectedNodes = nodes
                this.copyNodes = tools.deepClone(nodes)
                this.isSelectionOpen = false
                this.selectionOriginPos = { x, y }
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
                if (!this.editable) {
                    return false
                }
                const $branchEl = e.target
                const lineId = $branchEl.dataset.lineid
                const nodeId = $branchEl.dataset.nodeid
                const name = $branchEl.textContent
                const value = $branchEl.dataset.value
                // 先去除选中样式
                document.querySelectorAll('.branch-condition.editing').forEach(dom => {
                    dom.classList.remove('editing')
                })
                if ($branchEl.classList.contains('branch-condition')) {
                    e.stopPropagation()
                    $branchEl.classList.add('editing')
                    this.$emit('onConditionClick', {
                        id: lineId,
                        nodeId,
                        name,
                        value,
                        overlayId
                    })
                }
                this.$emit('variableDataChanged')
            },
            onToggleAllNode (val) {
                this.$emit('onToggleAllNode', val)
            },
            updateNodeMenuState (val) {
                this.showNodeMenu = val
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
                this.$emit('variableDataChanged')
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
                    this.$emit('variableDataChanged')
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
                    const lineInCanvasData = this.canvasData.lines.filter(item => {
                        return item.source.id === line.sourceId && item.target.id === line.targetId
                    })[0]
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
                                    title="${labelName}(${labelValue})"
                                    data-value="${labelValue}"
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
                this.$emit('variableDataChanged')
                this.$emit('onLineChange', 'delete', line)
            },
            onNodeMoveStop (loc) {
                this.$emit('variableDataChanged')
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
                    { type: 'close', rule: /^(close_)(\w*)/ },
                    { type: 'branchCondition', rule: /^(conditionline)(\w*)/ }
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
                }
                if (lineId && result.type === 'branchCondition') {
                    this.branchConditionEditHandler(e, overlay.id)
                }
            },
            onNodeRemove (node) {
                this.$refs.jsFlow.removeNode(node)
                this.$emit('variableDataChanged')
                this.$emit('onLocationChange', 'delete', node)

                if (node.type === 'startpoint') {
                    this.isDisableStartPoint = false
                } else if (node.type === 'endpoint') {
                    this.isDisableEndPoint = false
                }
            },
            onBeforeDrag (data) {
                if (this.referenceLine.id && this.referenceLine.id === data.sourceId) {
                    this.handleReferenceLineHide()
                }
            },
            // 节点拖动回调
            onNodeMoving (node) {
                // 在有参考线的情况下，拖动参考线来源节点，将移出参考线
                if (this.referenceLine.id && this.referenceLine.id === node.id) {
                    this.handleReferenceLineHide()
                }
                if (node.id !== this.idOfNodeShortcutPanel) {
                    this.handleShortcutPanelHide()
                }
            },
            // 锚点点击回调
            onEndpointClick (endpoint, event) {
                if (!this.editable) {
                    return false
                }
                const { pageX, pageY, offsetX, offsetY } = event
                const bX = pageX - offsetX + 5
                const bY = pageY - 50 - offsetY + 5
                const type = endpoint.anchor.type
                // 第二次点击
                if (this.referenceLine.id && endpoint.elementId !== this.referenceLine.id) {
                    this.createLine(
                        { id: this.referenceLine.id, arrow: this.referenceLine.arrow },
                        { id: endpoint.elementId, arrow: type }
                    )
                    this.handleReferenceLineHide()
                    return false
                }
                const line = this.$refs.dragReferenceLine
                line.style.left = bX + 'px'
                line.style.top = bY + 'px'
                this.referenceLine = { x: bX, y: bY, id: endpoint.elementId, arrow: type }
                document.getElementById('canvasContainer').addEventListener('mousemove', this.handleReferenceLine, false)
            },
            // 生成参考线
            handleReferenceLine (e) {
                const line = this.$refs.dragReferenceLine
                const { x: startX, y: startY } = this.referenceLine
                const { pageX, pageY } = e
                const pX = pageX - startX
                const pY = pageY - startY - 56
                let r = Math.atan2(Math.abs(pY), Math.abs(pX)) / (Math.PI / 180)
                if (pX < 0 && pY > 0) r = 180 - r
                if (pX < 0 && pY < 0) r = r + 180
                if (pX > 0 && pY < 0) r = 360 - r
                // set style
                const len = Math.pow(Math.pow(pX, 2) + Math.pow(pY, 2), 1 / 2)
                window.requestAnimationFrame(() => {
                    line.style.display = 'block'
                    line.style.width = len - 8 + 'px'
                    line.style.transformOrigin = `top left`
                    line.style.transform = 'rotate(' + r + 'deg)'
                    if (!this.referenceLine.id) {
                        this.handleReferenceLineHide()
                    }
                })
                document.body.addEventListener('mousedown', this.handleReferenceLineHide, false)
            },
            // 移出参考线
            handleReferenceLineHide (e) {
                const line = this.$refs.dragReferenceLine
                if (line) {
                    line.style.display = 'none'
                }
                this.referenceLine.id = ''
                document.getElementById('canvasContainer').removeEventListener('mousemove', this.handleReferenceLine, false)
                document.body.removeEventListener('mousedown', this.handleReferenceLineHide, false)
            },
            // 创建连线
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
                this.isShowHotKey = !this.isShowHotKey
            },
            onCloseHotkeyInfo () {
                this.isShowHotKey = false
            },
            /**
             * 单个添加选中节点
             */
            addNodeToSelectedList (selectedNode) {
                if (this.selectedNodes && this.selectedNodes.length === 0) {
                    document.addEventListener('keydown', this.nodeLineDeletehandler)
                }
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
                                title="${name}(${value})"
                                data-value="${value}"
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
                    this.handleReferenceLineHide()
                    return
                }
                if (type !== 'endpoint') {
                    this.showShortcutPane(id)
                }
            },
            onNodeDblclick (id) {
                this.onShowNodeConfig(id)
                this.handleShortcutPanelHide()
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
            onAppendNode ({ location, line }) {
                this.$refs.jsFlow.createNode(location)
                this.$emit('onLocationChange', 'add', location)
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
            onInsertNode ({ startNodeId, endNodeId, location }) {
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
                this.$emit('onLocationChange', 'add', location)
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
                this.$emit('variableDataChanged')
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
            }
        }
    }
</script>
<style lang="scss">
    .canvas-container {
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
            padding: 5px 0 7px 0;
            background: #c4c6cc;
            border-radius: 18px;
            opacity: 0.8;
            z-index: 5;
            transition: all 0.5s ease;
            user-select: none;
        }
        .jtk-endpoint {
            z-index: 3;
            cursor: pointer;
        }
        .jsflow-node {
            z-index: 3;
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
            z-index: 2;
            &:not(.branch-condition) {
                display: none;
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
                max-width: 86px;
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
                &.editing {
                    background: #b1ac84;
                    color: #ffffff;
                }
                &.failed {
                    color: #ffffff;
                    background: #ea3636;
                }
            }
        }
        &.editable {
            .jtk-overlay.jtk-hover {
                display: inline-block;
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
                    top: 124px;
                    left: 380px;
                    z-index: 5;
                }
            }
        }
        .jsflow-node.actived {
            z-index: 4;
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
</style>
