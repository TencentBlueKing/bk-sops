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
        @onBeforeDrop="onBeforeDrop"
        @onConnection="onConnection"
        @onConnectionDetached="onConnectionDetached"
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
                @onToggleAllNode="onToggleAllNode">
            </tool-panel>
        </template>
        <template v-slot:nodeTemplate="{ node }">
            <node-template
                :node="node"
                :is-node-check-open="isNodeCheckOpen"
                :editable="editable"
                @onNodeClick="onNodeClick"
                @onNodeCheckClick="onNodeCheckClick"
                @onNodeRemove="onNodeRemove"
                @onRetryClick="onRetryClick"
                @onSkipClick="onSkipClick"
                @onModifyTimeClick="onModifyTimeClick"
                @onGatewaySelectionClick="onGatewaySelectionClick"
                @onTaskNodeResumeClick="onTaskNodeResumeClick"
                @onSubflowPauseResumeClick="onSubflowPauseResumeClick">
            </node-template>
        </template>
    </js-flow>
</template>
<script>
    import '@/utils/i18n.js'
    import JsFlow from '@/assets/js/jsflow.esm.js'
    import { uuid } from '@/utils/uuid.js'
    import NodeTemplate from './NodeTemplate/index.vue'
    import PalettePanel from './PalettePanel/index.vue'
    import ToolPanel from './ToolPanel/index.vue'
    import tools from '@/utils/tools.js'
    import { endpointOptions, connectorOptions } from './options.js'
    import validatePipeline from '@/utils/validatePipeline.js'

    export default {
        name: 'TemplateCanvas',
        components: {
            JsFlow,
            NodeTemplate,
            PalettePanel,
            ToolPanel
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
            return {
                showNodeMenu: false,
                isDisableStartPoint: false,
                isDisableEndPoint: false,
                isSelectionOpen: false,
                selectedNodes: [],
                selectionOriginPos: {
                    x: 0,
                    y: 0
                },
                pasteMousePos: {
                    x: 0,
                    y: 0
                },
                flowData,
                endpointOptions,
                connectorOptions
            }
        },
        mounted () {
            this.isDisableStartPoint = !!this.canvasData.locations.find((location) => location.type === 'startpoint')
            this.isDisableEndPoint = !!this.canvasData.locations.find((location) => location.type === 'endpoint')
            if (this.editable) {
                this.$el.addEventListener('click', this.branchConditionEditHandler)
            }
        },
        beforeDestroy () {
            this.$refs.jsFlow.$el.removeEventListener('mousemove', this.pasteMousePosHandler)
            document.removeEventListener('keydown', this.nodeLinePastehandler)
            document.removeEventListener('keydown', this.nodeLineDeletehandler)
            this.$el.removeEventListener('click', this.branchConditionEditHandler)
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
                this.isSelectionOpen = false
                this.selectionOriginPos = { x, y }
                this.$refs.jsFlow.$el.addEventListener('mousemove', this.pasteMousePosHandler)
                document.addEventListener('keydown', this.nodeLinePastehandler)
                document.addEventListener('keydown', this.nodeLineDeletehandler, { once: true })
            },
            onCloseFrameSelect () {
                this.selectedNodes = []
                this.$refs.jsFlow.$el.removeEventListener('mousemove', this.pasteMousePosHandler)
                document.removeEventListener('keydown', this.pasteMousePosHandler)
                document.removeEventListener('keydown', this.nodeLinePastehandler)
            },
            pasteMousePosHandler (e) {
                this.pasteMousePos = {
                    x: e.offsetX,
                    y: e.offsetY
                }
            },
            nodeLinePastehandler (e) {
                if ((e.ctrlKey || e.metaKey) && e.keyCode === 86) {
                    const { locations, lines } = this.createCopyOfSelectedNodes(this.selectedNodes)
                    const selectedIds = []
                    const { x: originX, y: originY } = this.selectionOriginPos
                    const { x, y } = this.pasteMousePos

                    locations.forEach(location => {
                        location.x += (x - originX)
                        location.y += (y - originY)
                        selectedIds.push(location.id)
                        this.$refs.jsFlow.createNode(location)
                        this.$emit('onLocationChange', 'add', location)
                    })
                    this.$refs.jsFlow.addNodesToDragSelection(selectedIds)
                    // 需要先生成节点 DOM，才能连线
                    lines.forEach(line => {
                        this.$emit('onLineChange', 'add', line)
                        this.$nextTick(() => {
                            this.$refs.jsFlow.createConnector(line)
                        })
                    })
                    this.$refs.jsFlow.clearNodesDragSelection()
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
                    }
                })
                // 复制 line 数据
                this.canvasData.lines.forEach(line => {
                    if (locationIdReplaceHash[line.source.id] && locationIdReplaceHash[line.target.id]) {
                        const lineCopy = tools.deepClone(line)
                        lineIdReplaceHash[line.id] = lineCopy.id = 'line' + uuid()
                        lineCopy.source.id = locationIdReplaceHash[line.source.id]
                        lineCopy.target.id = locationIdReplaceHash[line.target.id]
                        lines.push(lineCopy)
                    }
                })
                return { locations, lines }
            },
            branchConditionEditHandler (e) {
                const $branchEl = e.target
                if ($branchEl.classList.contains('branch-condition')) {
                    $branchEl.classList.add('editing')
                    $branchEl.addEventListener('blur', this.branchConditionBlurHandler, { once: true })
                }
            },
            branchConditionBlurHandler (e) {
                const $branchEl = e.target
                const lineId = $branchEl.dataset.lineid
                const nodeId = $branchEl.dataset.nodeid
                const value = $branchEl.textContent
                const labelData = {
                    id: lineId,
                    nodeId,
                    name: value
                }
                $branchEl.classList.remove('editing')
                this.$emit('onLabelBlur', labelData)
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
            onNodeClick (id, type) {
                this.$emit('onNodeClick', id, type)
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
                const validateMessage = validatePipeline.isLocationValid(node, this.canvasData.locations)

                if (!validateMessage.result) {
                    this.$bkMessage({
                        message: validateMessage.message,
                        theme: 'warning'
                    })
                    return false
                }
                return true
            },
            onCreateNodeAfter (node) {
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
                    return false // 节点不可以连接自身
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
                        const labelName = branchInfo[lineId].evaluate
                        const labelData = {
                            type: 'Label',
                            name: `<div class="branch-condition"
                                    contentEditable=${this.editable ? 'plaintext-only' : 'false'}
                                    title="${labelName}"
                                    data-lineid="${lineId}"
                                    data-nodeid="${line.sourceId}">${labelName}</div>`,
                            location: -70,
                            cls: 'branch-condition',
                            id: `condition${lineId}`
                        }
                        this.$refs.jsFlow.addLineOverlay(line, labelData)
                    }
                    // 调整连线配置
                    if (lineInCanvasData.hasOwnProperty('midpoint')) {
                        const config = [
                            'Flowchart',
                            {
                                stub: [6, 6],
                                alwaysRespectStub: true,
                                gap: 8,
                                cornerRadius: 2,
                                midpoint: lineInCanvasData.midpoint
                            }
                        ]
                        this.$refs.jsFlow.setConnector(lineInCanvasData.source.id, lineInCanvasData.target.id, config)
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
                this.$emit('onLineChange', 'delete', line)
            },
            onNodeMoveStop (loc) {
                this.$emit('onLocationMoveDone', loc)
            },
            onOverlayClick (overlay, e) {
                const result = overlay.id.match(/^(close_)(\w*)/)
                if (result && result[2] !== '') {
                    const lineId = result[2]
                    const line = this.canvasData.lines.find(item => item.id === lineId)
                    this.$refs.jsFlow.removeConnector(line)
                }
            },
            onNodeRemove (node) {
                this.$refs.jsFlow.removeNode(node)
                this.$emit('onLocationChange', 'delete', node)

                if (node.type === 'startpoint') {
                    this.isDisableStartPoint = false
                } else if (node.type === 'endpoint') {
                    this.isDisableEndPoint = false
                }
            },
            onRetryClick (id) {
                this.$emit('onRetryClick', id)
            },
            onSkipClick (id) {
                this.$emit('onSkipClick', id)
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
            }
        }
    }
</script>
<style lang="scss">
    .canvas-wrapper.jsflow {
        border: none;
        background: #e1e4e8;
        .palette-panel-wrap {
            border-right: 1px solid #cacedb;
        }
        .tool-panel-wrap {
            top: 20px;
            left: 80px;
            padding: 7px 0;
            background: #c4c6cc;
            border-radius: 18px;
            opacity: 0.8;
            z-index: 4;
            transition: all 0.5s ease;
            user-select: none;
        }
        .jtk-endpoint {
            z-index: 1;
            cursor: pointer;
        }
        .jsflow-node {
            z-index: 3;
            &.adding-node {
                z-index: 6;
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
                color: #ff5757;
                background: #ffffff;
                border-radius: 50%;
            }
            .branch-condition {
                padding: 4px 10px;
                min-width: 60px;
                max-width: 200px;
                font-size: 12px;
                text-align: center;
                background: #e1f3ff;
                border: 1px solid #c3cdd7;
                border-radius: 2px;
                outline: none;
                cursor: pointer;
                &:focus,
                &:hover {
                    border-color: #3a84ff;
                }
                &:not(.editing) {
                    white-space: nowrap;
                    text-overflow: ellipsis;
                    overflow: hidden;
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
        }
    }
</style>
