/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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
            class="canvas-wrapper"
            :data="flowData"
            :show-palette="showPalette"
            :show-tool="showTool"
            :editable="editable"
            :endpoint-options="endpointOptions"
            :connector-options="connectorOptions"
            :node-options="nodeOptions"
            @onCreateNodeBefore="onCreateNodeBefore"
            @onCreateNodeAfter="onCreateNodeAfter"
            @onAddNodeMoving="onCreateNodeMoving"
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
                    :is-disable-end-point="isDisableEndPoint">
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
                    :is-perspective="isPerspective"
                    @onShowMap="onToggleMapShow"
                    @onZoomIn="onZoomIn"
                    @onZoomOut="onZoomOut"
                    @onResetPosition="onResetPosition"
                    @onOpenFrameSelect="onOpenFrameSelect"
                    @onFormatPosition="onFormatPosition"
                    @onToggleAllNode="onToggleAllNode"
                    @onToggleHotKeyInfo="onToggleHotKeyInfo"
                    @onTogglePerspective="onTogglePerspective"
                    @onDownloadCanvas="onDownloadCanvas">
                </tool-panel>
            </template>
            <template v-slot:nodeTemplate="{ node }">
                <node-template
                    :node="node"
                    :is-node-check-open="isNodeCheckOpen"
                    :editable="editable"
                    :has-admin-perm="hasAdminPerm"
                    :node-variable-info="nodeVariableInfo"
                    :activities="canvasData.activities"
                    :is-perspective="isPerspective"
                    @onNodeDblclick="onNodeDblclick"
                    @onNodeClick="onNodeClick"
                    @onNodeMousedown="onNodeMousedown"
                    @onNodeMouseEnter="onNodeMouseEnter"
                    @onNodeCheckClick="onNodeCheckClick"
                    @onRetryClick="$emit('onRetryClick', $event)"
                    @onForceFail="$emit('onForceFail', $event)"
                    @onSkipClick="$emit('onSkipClick', $event)"
                    @onModifyTimeClick="$emit('onModifyTimeClick', $event)"
                    @onGatewaySelectionClick="$emit('onGatewaySelectionClick', $event)"
                    @onTaskNodeResumeClick="$emit('onTaskNodeResumeClick', $event)"
                    @onApprovalClick="$emit('onApprovalClick', $event)"
                    @addNodesToDragSelection="addNodeToSelectedList"
                    @onSubflowPauseResumeClick="onSubflowPauseResumeClick">
                </node-template>
            </template>
        </bk-flow>
        <ShortcutPanel
            v-if="showShortcutPanel"
            :node="activeNode"
            :line="activeCon"
            :position="shortcutPanelPosition"
            :node-operate="shortcutPanelNodeOperate"
            :delete-line="shortcutPanelDeleteLine"
            :canvas-data="canvasData"
            @onAppendNode="onAppendNode"
            @onInsertNode="onInsertNode"
            @onNodeRemove="onNodeRemove"
            @onConfigBtnClick="onShowNodeConfig"
            @onDeleteLineClick="onShortcutDeleteLine">
        </ShortcutPanel>
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
            <div class="small-map-body" v-bkloading="{ isLoading: smallMapLoading }">
                <img :src="smallMapImg" alt="">
                <div
                    ref="selectBox"
                    class="select-box"
                    v-show="!smallMapLoading"
                    @mousedown.prevent="onMouseDownSelect">
                </div>
            </div>
        </div>
        <!-- 节点历史执行时间/透视面板 -->
        <div v-if="isExecRecordPanelShow || isPerspectivePanelShow" class="node-tips-content" :style="nodeTipsPanelPosition">
            <!-- 节点历史执行时间展示 -->
            <div class="execute-record-tips-content" v-if="isExecRecordPanelShow">
                <div class="content-wrap" v-bkloading="{ isLoading: execRecordLoading }">
                    <ul>
                        <li class="content-item">
                            <span>{{ $t('当前已执行') }}</span>
                            <span class="time">{{ nodeExecRecordInfo.curTime || '--' }}</span>
                        </li>
                        <li class="content-item">
                            <span>{{ $t('最近1次成功执行耗时') }}</span>
                            <span class="time">{{ nodeExecRecordInfo.latestTime || '--' }}</span>
                        </li>
                        <li class="content-item">
                            <span>{{ $t('近 n 次成功执行平均耗时', { n: nodeExecRecordInfo.count }) }}</span>
                            <span class="time">{{ nodeExecRecordInfo.meanTime || '--' }}</span>
                        </li>
                    </ul>
                    <p class="deadline">{{ $t('*数据统计截至') + ' ' + nodeExecRecordInfo.deadline }}</p>
                </div>
            </div>
            <!-- 节点输入输出变量(node.name用来判断节点是否选择过插件) -->
            <div class="perspective-tips-context" v-if="isPerspectivePanelShow">
                <div class="tips-content">
                    <p class="tip-label">{{ $t('引用变量') }}</p>
                    <template v-if="nodeVariable.input.length">
                        <p v-for="item in nodeVariable.input" :key="item">{{ item }}</p>
                    </template>
                    <template v-else>{{ '--' }}</template>
                    <div class="dividLine"></div>
                    <p class="tip-label">{{ $t('输出变量') }}</p>
                    <template v-if="nodeVariable.output.length">
                        <p v-for="item in nodeVariable.output" :key="item">{{ item }}</p>
                    </template>
                    <template v-else>{{ '--' }}</template>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
    import domtoimage from '@/utils/domToImage.js'
    import BkFlow from '@/assets/js/flow.js'
    import { uuid } from '@/utils/uuid.js'
    import NodeTemplate from './NodeTemplate/index.vue'
    import ShortcutPanel from './NodeTemplate/ShortcutPanel.vue'
    import PalettePanel from './PalettePanel/index.vue'
    import HelpInfo from './HelpInfo/index.vue'
    import ToolPanel from './ToolPanel/index.vue'
    import tools from '@/utils/tools.js'
    import dom from '@/utils/dom.js'
    import { NODES_SIZE_POSITION } from '@/constants/nodes.js'
    import { endpointOptions, connectorOptions, nodeOptions } from './options.js'
    import validatePipeline from '@/utils/validatePipeline.js'

    export default {
        name: 'TemplateCanvas',
        components: {
            BkFlow,
            NodeTemplate,
            ShortcutPanel,
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
            },
            nodeVariableInfo: {
                type: Object,
                default: () => ({})
            },
            nodeExecRecordInfo: {
                type: Object,
                default: () => ({})
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
                smallMapLoading: true, // 小地图loading
                isMouseEnterX: '', // 鼠标在选择框中按下的offsetX值
                isMouseEnterY: '', // 鼠标在选择框中按下的offsetY值
                windowWidth: document.documentElement.offsetWidth - 60, // 60 header的宽度
                windowHeight: document.documentElement.offsetHeight - 60 - 50, // 50 tab栏的宽度
                canvasWidth: 0, // 生成画布的宽
                canvasHeight: 0, // 生成画布的高
                canvasImgDownloading: false,
                isDisableStartPoint: false,
                isDisableEndPoint: false,
                isSelectionOpen: false,
                isShowHotKey: false,
                isPerspective: false,
                isCanCreateline: false,
                selectedNodes: [],
                copyNodes: [],
                activeNode: null,
                activeCon: null,
                showShortcutPanel: false,
                shortcutPanelPosition: { left: 0, right: 0 },
                shortcutPanelNodeOperate: false,
                shortcutPanelDeleteLine: false,
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
                zoomRatio: 100,
                labelDrag: false, // 标识分支条件是否为拖动触发
                connectorPosition: {}, // 鼠标hover的连线的坐标
                conditionInfo: null,
                nodeTipsPanelPosition: {},
                nodeVariable: {},
                isPerspectivePanelShow: false,
                isExecRecordPanelShow: false,
                connectionHoverList: [],
                execRecordLoading: false
            }
        },
        watch: {
            canvasData (val) {
                const { lines, locations: nodes } = val
                this.flowData = {
                    lines,
                    nodes
                }
            },
            nodeExecRecordInfo: {
                handler (val) {
                    this.execRecordLoading = false
                },
                deep: true
            }
        },
        created () {
            this.onWindowResize = tools.throttle(this.handlerWindowResize, 300)
        },
        mounted () {
            this.isDisableStartPoint = !!this.canvasData.locations.find((location) => location.type === 'startpoint')
            this.isDisableEndPoint = !!this.canvasData.locations.find((location) => location.type === 'endpoint')
            document.body.addEventListener('click', this.closeShortcutPanel, false)
            // 画布快捷键缩放
            const canvasPaintArea = document.querySelector('.canvas-flow-wrap')
            canvasPaintArea.addEventListener('mousewheel', this.onMouseWheel, false)
            canvasPaintArea.addEventListener('DOMMouseScroll', this.onMouseWheel, false) // 单独处理firefox
            canvasPaintArea.addEventListener('mousemove', tools.debounce(this.onCanvasMouseMove, 300), false)
            // 监听页面视图变化
            window.addEventListener('resize', this.onWindowResize, false)
            // 监听画布移入
            const canvasContainer = document.querySelector('#canvasContainer')
            canvasContainer.addEventListener('mousemove', tools.debounce(this.onCanvasContainerMouseMove, 300), false)
        },
        beforeDestroy () {
            this.$refs.jsFlow.$el.removeEventListener('mousemove', this.pasteMousePosHandler)
            document.removeEventListener('keydown', this.nodeSelectedhandler)
            document.removeEventListener('keydown', this.nodeLineDeletehandler)
            document.body.removeEventListener('click', this.closeShortcutPanel, false)
            // 画布快捷键缩放
            const canvasPaintArea = document.querySelector('.canvas-flow-wrap')
            if (canvasPaintArea) {
                canvasPaintArea.removeEventListener('mousewheel', this.onMouseWheel, false)
                canvasPaintArea.removeEventListener('DOMMouseScroll', this.onMouseWheel, false)
                canvasPaintArea.removeEventListener('mousemove', this.onCanvasMouseMove, false)
            }
            window.removeEventListener('resize', this.onWindowResize, false)
            const canvasContainer = document.querySelector('#canvasContainer')
            if (canvasContainer) {
                canvasContainer.removeEventListener('mousemove', this.onCanvasContainerMouseMove, false)
            }
        },
        methods: {
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
                this.isShowHotKey = false
                this.showSmallMap = !this.showSmallMap
                this.smallMapLoading = true
                this.smallMapImg = ''
                setTimeout(() => {
                    if (this.showSmallMap) {
                        this.onGenerateCanvas().then(res => {
                            this.smallMapImg = res
                            this.smallMapLoading = false
                        })
                        this.$nextTick(() => {
                            this.getInitialValue()
                        })
                    }
                }, 0)
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
                if (this.labelDrag) {
                    this.labelDrag = false
                    return
                }
                const $branchEl = e.target
                const lineId = $branchEl.dataset.lineid
                const nodeId = $branchEl.dataset.nodeid
                const { name, evaluate: value, tag } = this.canvasData.branchConditions[nodeId][lineId]
                if ($branchEl.classList.contains('branch-condition')) {
                    e.stopPropagation()
                    this.$emit('onConditionClick', {
                        id: lineId,
                        nodeId,
                        name,
                        value,
                        tag,
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
                this.$nextTick(() => {
                    // 拖拽节点到线上, 自动生成连线
                    this.handleDraggerNodeToLine(node)
                })
            },
            onCreateNodeMoving (node) {
                // 计算节点基于画布的坐标
                const canvasDom = document.querySelector('.canvas-flow')
                let nodeLeft = 0
                let nodeTop = 0
                let { style } = canvasDom.attributes
                if (style) {
                    style = style.value.split(';').filter(value => value)
                    nodeLeft = style.find(item => item.indexOf('left') > -1)
                    nodeLeft = nodeLeft ? /:.([0-9.]+)px/.exec(nodeLeft)[1] : 0
                    nodeLeft = Number(nodeLeft)
                    nodeTop = style.find(item => item.indexOf('top') > -1)
                    nodeTop = nodeTop ? /:.([0-9.]+)px/.exec(nodeTop)[1] : 0
                    nodeTop = Number(nodeTop)
                }
                const location = {
                    ...node,
                    x: node.x - 60 - nodeLeft, // 60为画布左边栏的宽度
                    y: node.y - nodeTop
                }
                // 拖拽节点到线上, 自动生成连线
                const matchLines = this.getNodeMatchLines(location)
                if (Object.keys(matchLines).length === 1) {
                    const lineConfig = Object.values(matchLines)[0]
                    this.setPaintStyle(lineConfig.id, '#3a84ff')
                    this.connectionHoverList.push(lineConfig.id)
                } else if (this.connectionHoverList.length) {
                    this.connectionHoverList.forEach(lineId => {
                        this.setPaintStyle(lineId, '#a9adb6')
                    })
                    this.connectionHoverList = []
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
            onConnectionClick (conn, e) {
                this.activeCon = conn
                // const [sEdp, tEdp] = conn.endpoints
                // const { sourceId, targetId } = conn
                // this.replaceEndpoint(sEdp, sourceId, true)
                // this.replaceEndpoint(tEdp, targetId, true)
                // setTimeout(() => {
                //     const connections = this.$refs.jsFlow.instance.getConnections({ source: sourceId, targetId: targetId })
                //     this.activeCon = tools.deepClone(connections[0])
                // }, 0)
            },
            replaceEndpoint (oEdp, nodeId, draggable = false) {
                const oldConnections = tools.deepClone(oEdp.connections)
                const anchor = this.endpointOptions.anchors[oEdp.anchor.cssClass]
                const conditions = []
                oldConnections.forEach(conn => {
                    const { sourceId, targetId } = conn
                    const line = this.canvasData.lines.find(item => {
                        return item.source.id === sourceId && item.target.id === targetId
                    })
                    const node = this.$store.state.template.gateways[sourceId]
                    if (node && node.conditions && node.conditions[line.id]) {
                        conditions.push({
                            source: sourceId,
                            target: targetId,
                            data: Object.assign({}, node.conditions[line.id])
                        })
                    } else if (node && node.default_condition && node.default_condition.flow_id === line.id) {
                        conditions.push({
                            source: sourceId,
                            target: targetId,
                            data: Object.assign({}, node.default_condition)
                        })
                    }
                })
                const endpointOptions = Object.assign({
                    anchor: anchor,
                    uuid: anchor + nodeId
                }, this.endpointOptions)
                delete endpointOptions.anchors
                this.$refs.jsFlow.instance.deleteEndpoint(oEdp)
                if (draggable) {
                    delete endpointOptions.isSource
                }
                const edp = this.$refs.jsFlow.instance.addEndpoint(nodeId, endpointOptions)
                if (edp && edp.endpoint.canvas) {
                    edp.endpoint.canvas.dataset.pos = anchor
                }
                setTimeout(() => {
                    oldConnections.forEach(conn => {
                        const { sourceId, targetId, endpoints } = conn
                        const line = this.canvasData.lines.find(item => item.source.id === sourceId && item.target.id === targetId)
                        if (line) {
                            return
                        }

                        const lineCondition = conditions.find(item => item.source === sourceId && item.target === targetId)
                        const condition = lineCondition ? lineCondition.data : undefined
                        const source = {
                            id: sourceId,
                            arrow: endpoints[0].anchor.cssClass
                        }
                        const target = {
                            id: targetId,
                            arrow: endpoints[1].anchor.cssClass
                        }
                        this.createLine(source, target, condition)
                    })
                }, 0)
            },
            // 拖拽到端点上连接
            onBeforeDrop (line) {
                const { sourceId, targetId, connection, dropEndpoint } = line
                if (sourceId === targetId) {
                    return false
                }

                const [sourceEndpoint, targetEndpoint] = connection.endpoints
                const sourceType = sourceEndpoint.anchor.cssClass || dropEndpoint.anchor.cssClass
                const targetType = targetEndpoint.anchor.cssClass || dropEndpoint.anchor.cssClass

                const data = {
                    source: {
                        id: sourceId,
                        arrow: sourceType
                    },
                    target: {
                        id: targetId,
                        arrow: targetType
                    }
                }
                if (this.activeCon) {
                    const sEdp = tools.deepClone(this.activeCon.endpoints[0])
                    const tEdp = tools.deepClone(this.activeCon.endpoints[1])
                    this.replaceEndpoint(sEdp, this.activeCon.sourceId)
                    this.replaceEndpoint(tEdp, this.activeCon.targetId)
                    this.$nextTick(() => {
                        this.activeCon = null
                        this.createLine(data.source, data.target)
                    })
                } else {
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
                                alwaysRespectStubs: true,
                                gap: -12,
                                cornerRadius: 10,
                                midpoint: lineInCanvasData.midpoint
                            }
                        ]

                        this.$refs.jsFlow.setConnector(lineInCanvasData.source.id, lineInCanvasData.target.id, config)
                    }
                    // 增加连线删除 icon
                    this.$refs.jsFlow.addLineOverlay(line, {
                        type: 'Label'
                    })
                    const branchInfo = this.canvasData.branchConditions[line.source.id]
                    // 增加分支网关 label
                    if (branchInfo && Object.keys(branchInfo).length > 0) {
                        const conditionInfo = this.conditionInfo || branchInfo[lineId]
                        const labelValue = conditionInfo.evaluate
                        // 兼容旧数据，分支条件里没有 name 属性的情况
                        const labelName = conditionInfo.name || labelValue
                        const loc = ('loc' in conditionInfo) ? conditionInfo.loc : -70
                        const gatewayInfo = this.$store.state.template.gateways[line.source.id]
                        let defaultCls = conditionInfo.default_condition ? 'default-branch' : ''
                        if (gatewayInfo && gatewayInfo.default_condition && gatewayInfo.default_condition.flow_id === lineId) {
                            defaultCls = 'default-branch'
                        }
                        const labelData = {
                            type: 'Label',
                            name: `<div class="branch-condition ${defaultCls}"
                                    title="${tools.escapeStr(labelName)}(${tools.escapeStr(labelValue)})"
                                    data-lineid="${lineId}"
                                    data-nodeid="${line.sourceId}">${labelName}</div>`,
                            location: loc,
                            cls: 'branch-condition',
                            id: `condition${lineId}`
                        }
                        this.$refs.jsFlow.addLineOverlay(line, labelData)
                        const condition = {
                            id: lineId,
                            nodeId: line.source.id,
                            name: conditionInfo.name,
                            tag: conditionInfo.tag,
                            value: conditionInfo.evaluate
                        }
                        if (conditionInfo.default_condition) {
                            condition.default_condition = {
                                name: conditionInfo.name,
                                tag: conditionInfo.tag,
                                flow_id: lineId
                            }
                        }
                        // 更新本地condition配置
                        if (this.conditionInfo) {
                            this.$emit('updateCondition', condition)
                        }
                        this.conditionInfo = null
                        this.setLabelDraggable({ ...line, id: lineId }, condition)
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
                    // 拖拽节点到线上, 自动生成连线
                    this.handleDraggerNodeToLine(loc)
                }
            },
            // 拖拽节点到线上, 自动生成连线
            handleDraggerNodeToLine (location) {
                // 获取节点对应匹配连线
                const matchLines = this.getNodeMatchLines(location)
                // 只对符合单条线的情况进行处理
                if (Object.keys(matchLines).length === 1) {
                    const values = Object.values(matchLines)[0]
                    // 计算新建节点的坐标和两端节点的左边是否在一条线上
                    if (!location.mode) {
                        const canvasData = tools.deepClone(this.canvasData)
                        const isTaskNode = ['tasknode', 'subflow'].includes(location.type)
                        const { source, target, segmentPosition } = values
                        const bothNodes = canvasData.locations.filter(item => {
                            return [source.id, target.id].includes(item.id)
                        })
                        bothNodes.some(item => {
                            let nodeWidth, nodeHeight
                            if (['tasknode', 'subflow'].includes(item.type)) {
                                nodeWidth = 154
                                nodeHeight = 54
                            } else {
                                nodeWidth = 34
                                nodeHeight = 34
                            }
                            const { left, top, height, width } = segmentPosition
                            if (height === 8 && item.y < top && top < (item.y + nodeHeight)) {
                                location.y = item.y + nodeHeight / 2 - (isTaskNode ? 54 : 34) / 2
                                return true
                            } else if (width === 8 && item.x < left && left < (item.x + nodeWidth)) {
                                location.x = item.x + nodeWidth / 2 - (isTaskNode ? 154 : 34) / 2
                                return true
                            }
                        })
                    }
                    // 删除当前的，在原有位置插入一个新的
                    this.onNodeRemove(location)
                    this.$nextTick(() => {
                        // 按照连线本身的方向，插入新的节点
                        this.onInsertNode({
                            startNodeId: values.source.id,
                            endNodeId: values.target.id,
                            location,
                            startLineArrow: {
                                source: values.source.arrow,
                                target: values.inputArrow
                            },
                            endLineArrow: {
                                source: values.outputArrow,
                                target: values.target.arrow
                            }
                        })
                    })
                }
            },
            // 拖拽节点到线上, 获取对应匹配连线
            getNodeMatchLines (loc) {
                /**
                 * 54 节点默认高度 154 节点默认宽度
                 */
                // 左侧添加节点时没有生成节点id
                if (loc.id) {
                    // 已有连线的节点不做处理
                    const { flows } = this.$store.state.template
                    const isExistLine = Object.values(flows).some(item => [item.source, item.target].includes(loc.id))
                    if (isExistLine) {
                        return {}
                    }
                }
                // 横向区间
                let horizontalInterval = [loc.x + 40, loc.x + 154 - 40]
                // 纵向区间
                let verticalInterval = [loc.y + 15, loc.y + 54 - 15 + 2]
                if (loc.type.indexOf('gateway') > -1) { // 网关区间
                    horizontalInterval = [loc.x + 7, loc.x + 34 - 7]
                    verticalInterval = [loc.y + 7, loc.y + 34 - 7 + 2]
                }
                // 符合匹配连线
                const matchLines = {}
                // 符合匹配的线段
                let segmentPosition = {}
                // 获取所有连线实例
                const connections = this.$refs.jsFlow.instance.getConnections()
                connections.forEach(connection => {
                    // 计算连线的top, left
                    let { cssText } = connection.canvas.style
                    cssText = cssText.split(';').filter(value => /:.[0-9.]+px/.test(value))
                    let lineLeft = cssText.find(item => item.indexOf('left') > -1)
                    lineLeft = lineLeft ? /:.([0-9.]+)px/.exec(lineLeft)[1] : 0
                    lineLeft = Number(lineLeft)
                    let lineTop = cssText.find(item => item.indexOf('top') > -1)
                    lineTop = lineTop ? /:.([0-9.]+)px/.exec(lineTop)[1] : 0
                    lineTop = Number(lineTop)

                    // 根据下标找到对应的line的配置
                    const lineConfig = this.canvasData.lines.find(item => {
                        return item.source.id === connection.sourceId && item.target.id === connection.targetId
                    })
                    let inputArrow = 'Left'
                    let outputArrow = 'Right'
                    // 获取所有连线线段
                    let segments = connection.connector.getSegments() || []
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
                    // 过滤掉圆弧线段
                    segments = segments.filter(item => item.type === 'Straight')
                    const isMatch = segments.some(item => {
                        // 计算线段的高宽和坐标
                        const { x1, x2, y1, y2 } = item.params
                        // 线段的坐标的最大值/最小值
                        const maxX = Math.max(x1, x2)
                        const minX = Math.min(x1, x2)
                        const maxY = Math.max(y1, y2)
                        const minY = Math.min(y1, y2)

                        let left, top, width, height
                        if (x1 === x2) { // 垂直
                            width = 8
                            height = maxY - minY
                            top = lineTop + minY + firstSegmentHeight
                            left = lineLeft + minX + firstSegmentWidth
                            inputArrow = y1 > y2 ? 'Bottom' : 'Top'
                            outputArrow = y1 > y2 ? 'Top' : 'Bottom'
                        } else if (y1 === y2) { // 水平
                            height = 8
                            width = maxX - minX
                            top = lineTop + minY + firstSegmentHeight + 5
                            left = lineLeft + minX + firstSegmentWidth
                            inputArrow = x1 > x2 ? 'Right' : 'Left'
                            outputArrow = x1 > x2 ? 'Left' : 'Right'
                        }
                        segmentPosition = { left, top, height, width }

                        let nodeWidth = 154
                        let nodeHeight = 54
                        if (loc.type.indexOf('gateway') > -1) { // 网关区间
                            nodeWidth = 34
                            nodeHeight = 34
                        }
                        
                        if (width > nodeWidth || height > nodeHeight) { // 线段长需大于节点宽度或高度
                            if (height > 8) { // 垂直线
                                return (left > horizontalInterval[0] && horizontalInterval[1] > left)
                                    && (top < verticalInterval[0] && top + height > verticalInterval[1])
                            } else {
                                return (top > verticalInterval[0] && verticalInterval[1] > top)
                                    && (left < horizontalInterval[0] && left + width > horizontalInterval[1])
                            }
                        }
                        return false
                    })
                    if (isMatch) {
                        matchLines[lineConfig.id] = {
                            ...lineConfig,
                            segmentPosition,
                            inputArrow,
                            outputArrow
                        }
                    }
                })
                return matchLines || {}
            },
            // 设置连线颜色
            setPaintStyle (lineId, color = '#a9adb6') {
                const lineConfig = this.canvasData.lines.find(item => item.id === lineId)
                if (!lineConfig) return
                const connection = this.$refs.jsFlow.instance.getConnections({
                    source: lineConfig.source.id,
                    target: lineConfig.target.id
                })[0]
                connection.setPaintStyle({
                    ...this.connectorOptions.paintStyle,
                    stroke: color
                })
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
                // 拷贝数据更新前的数据
                const canvasData = tools.deepClone(this.canvasData)
                const { activities, lines } = canvasData
                let nodeConfig = activities[node.id] || {}
                const isGatewayNode = node.type.indexOf('gateway') > -1
                let gateways = this.$store.state.template.gateways
                gateways = tools.deepClone(gateways)
                if (isGatewayNode) {
                    nodeConfig = gateways[node.id]
                }
                this.showShortcutPanel = false
                
                this.$refs.jsFlow.removeNode(node)
                this.$emit('templateDataChanged')
                this.$emit('onLocationChange', 'delete', node)

                if (node.type === 'startpoint') {
                    this.isDisableStartPoint = false
                } else if (node.type === 'endpoint') {
                    this.isDisableEndPoint = false
                }
                // 被删除的节点只存在一条输入连线和输出连线时才允许自动连线
                const { incoming, outgoing } = nodeConfig
                if (
                    (!['startpoint', 'endpoint'].includes(node.type))
                    && incoming.length === 1
                    && (Array.isArray(outgoing) ? outgoing.length === 1 : outgoing)) {
                    let { source } = lines.find(item => item.id === incoming[0])
                    const outlinesId = Array.isArray(outgoing) ? outgoing[0] : outgoing
                    let { target } = lines.find(item => item.id === outlinesId)
                    // 当分支上只剩开始/结束节点时，不自动连线
                    const { start_event, end_event } = this.$store.state.template
                    if (source.id === start_event.id && target.id === end_event.id) return
                    // 当分支上只剩网关节点时，不自动连线
                    if (gateways[source.id] && gateways[target.id]) return
                    // 当两端为汇聚节点和结束节点时，自动连线
                    if (gateways[source.id] && gateways[source.id].type !== 'ConvergeGateway' && target.id === end_event.id) return
                    // 当需要生成的连线已存在，不自动连线
                    const isExist = lines.find(item => item.source.id === source.id && item.target.id === target.id)
                    if (isExist) return
                    // 先更新数据再进行连线
                    this.$nextTick(() => {
                        const sourcePosition = this.getNodeEndpointPosition(source.id, 'source')
                        const targetPosition = this.getNodeEndpointPosition(target.id, 'target')
                        const instance = this.$refs.jsFlow.instance
                        const eps = instance.selectEndpoints({ source: source.id })
                        const oEps = instance.selectEndpoints({ target: target.id })
                        let sourceArrow, targetArrow
                        let minDis = Infinity
                        // 排除源头节点输入连线的端点和目标短线输出连线的端点
                        eps.each(e => {
                            if (sourcePosition.includes(e.anchor.cssClass)) return
                            oEps.each(oe => {
                                if (targetPosition.includes(oe.anchor.cssClass)) return
                                const [eX, eY] = e.anchor.lastReturnValue
                                const [tEpX, tEpY] = oe.anchor.lastReturnValue
                                const distance = Math.sqrt(Math.pow((tEpX - eX), 2) + Math.pow((tEpY - eY), 2))
                                if (distance < minDis) {
                                    minDis = distance
                                    sourceArrow = e.anchor.cssClass
                                    targetArrow = oe.anchor.cssClass
                                }
                            })
                        })
                        if (!sourceArrow || !sourceArrow) return
                        source = { ...source, arrow: sourceArrow }
                        target = { ...target, arrow: targetArrow }
                        // 创建连线状态
                        const createResult = this.createLine(source, target)
                        // 删除节点时，若起始节点为网关节点则保留分支表达式
                        if (createResult && source.id in gateways) {
                            const branchInfo = gateways[source.id]
                            const { conditions, default_condition } = branchInfo
                            if (!conditions) return
                            const tagCode = `branch_${source.id}_${target.id}`
                            conditions.tag = tagCode
                            this.conditionInfo = conditions[incoming[0]]
                            if (default_condition && default_condition.flow_id === incoming[0]) {
                                default_condition.tag = tagCode
                                this.conditionInfo = { ...default_condition, default_condition }
                            }
                        }
                    })
                }
            },
            // 获取节点端点被占用情况
            getNodeEndpointPosition (nodeId, type) {
                const { activities, lines } = this.canvasData
                const { start_event, gateways, end_event } = this.$store.state.template
                let nodeConfig = {}
                // 获取节点配置
                if (start_event.id === nodeId) {
                    nodeConfig = start_event
                } else if (end_event.id === nodeId) {
                    nodeConfig = end_event
                } else if (nodeId in activities) {
                    nodeConfig = activities[nodeId]
                } else if (nodeId in gateways) {
                    nodeConfig = gateways[nodeId]
                }
                let { incoming, outgoing } = nodeConfig
                // 统一incoming, outgoing数据格式为数组
                if (!Array.isArray(incoming)) {
                    incoming = incoming ? [incoming] : []
                }
                if (!Array.isArray(outgoing)) {
                    outgoing = outgoing ? [outgoing] : []
                }
                const position = []
                // 计算源头节点输入连线的端点和目标短线输出连线的端点
                lines.forEach(item => {
                    if (type === 'source' && incoming.includes(item.id)) {
                        position.push(item.target.arrow)
                    }
                    if (type === 'target' && outgoing.includes(item.id)) {
                        position.push(item.source.arrow)
                    }
                })
                return position
            },
            onBeforeDrag (data) {
                if (this.referenceLine.id && this.referenceLine.id === data.sourceId) {
                    this.clearReferenceLine()
                }
            },
            // 节点拖动回调
            onNodeMoving (node) {
                // 在有参考线的情况下，拖动参考线来源节点，将移出参考线
                if (this.referenceLine.id && this.referenceLine.id === node.id) {
                    this.clearReferenceLine()
                }
                if (this.activeNode) {
                    this.closeShortcutPanel()
                }
                this.adjustLineEndpoint(node.id)
                // 获取节点的动态坐标
                const nodeDom = document.querySelector(`#${node.id}`)
                let { style } = nodeDom.attributes
                style = style.value.split(';').filter(value => value)
                let nodeLeft = style.find(item => item.indexOf('left') > -1)
                nodeLeft = nodeLeft ? /:.-?([0-9.]+)px/.exec(nodeLeft)[1] : 0
                nodeLeft = Number(nodeLeft)
                let nodeTop = style.find(item => item.indexOf('top') > -1)
                nodeTop = nodeTop ? /:.-?([0-9.]+)px/.exec(nodeTop)[1] : 0
                nodeTop = Number(nodeTop)
                const location = {
                    ...node,
                    x: nodeLeft,
                    y: nodeTop
                }
                // 拖拽节点到线上, 自动生成连线
                const matchLines = this.getNodeMatchLines(location)
                if (Object.keys(matchLines).length === 1) {
                    const lineConfig = Object.values(matchLines)[0]
                    this.setPaintStyle(lineConfig.id, '#3a84ff')
                    this.connectionHoverList.push(lineConfig.id)
                } else if (this.connectionHoverList.length) {
                    this.connectionHoverList.forEach(lineId => {
                        this.setPaintStyle(lineId, '#a9adb6')
                    })
                    this.connectionHoverList = []
                }
            },
            /**
             * 节点移动时，计算当前节点的四个端点到目标端点的最短距离，取出对应端点，重新连线
             */
            adjustLineEndpoint (id) {
                const instance = this.$refs.jsFlow.instance
                // const sourceLines = instance.getConnections({ source: id })
                const targetLines = instance.getConnections({ target: id })
                // 分支网关的输入输出连线不调整
                const lines = targetLines.filter(item => {
                    const sourceNode = this.canvasData.locations.find(n => n.id === item.source.id)
                    const targetNode = this.canvasData.locations.find(n => n.id === item.target.id)
                    return sourceNode.type !== 'branchgateway' && targetNode.type !== 'branchgateway'
                })
                const eps = instance.selectEndpoints({ source: id })
                // this.setShortestLine(sourceLines, eps, 'source')
                this.setShortestLine(lines, eps, 'target')
            },
            setShortestLine (lines, eps, type) {
                const instance = this.$refs.jsFlow.instance
                lines.forEach(item => {
                    let cep, oep
                    let minDis = Infinity
                    const cEndpoint = type === 'source' ? item.endpoints[0] : item.endpoints[1]
                    const oEndpoint = type === 'source' ? item.endpoints[1] : item.endpoints[0]
                    const oEps = type === 'source' ? instance.selectEndpoints({ target: item.target.id }) : instance.selectEndpoints({ source: item.source.id })
                    // targetId恒为移动的节点id
                    const targetPosition = this.getNodeEndpointPosition(item.targetId, type)
                    const sourcePosition = this.getNodeEndpointPosition(item.sourceId, type === 'target' ? 'source' : 'target')
                    eps.each(e => {
                        if (targetPosition.includes(e.anchor.cssClass)) return
                        oEps.each(oe => {
                            if (sourcePosition.includes(oe.anchor.cssClass)) return
                            const [eX, eY] = e.anchor.lastReturnValue
                            const [tEpX, tEpY] = oe.anchor.lastReturnValue
                            const distance = Math.sqrt(Math.pow((tEpX - eX), 2) + Math.pow((tEpY - eY), 2))
                            if (distance < minDis) {
                                minDis = distance
                                cep = e
                                oep = oe
                            }
                        })
                    })
                    if (!cep || !oep) return
                    if (cep !== cEndpoint || oep !== oEndpoint) {
                        // 保留分支网关连线上的分支条件
                        let condition, sId, sType, tId, tType
                        if (type === 'source') {
                            sId = cep.elementId
                            sType = cep.anchor.cssClass
                            tId = oep.elementId
                            tType = oep.anchor.cssClass
                        } else {
                            sId = oep.elementId
                            sType = oep.anchor.cssClass
                            tId = cep.elementId
                            tType = cep.anchor.cssClass
                        }
                        const line = this.canvasData.lines.find(item => {
                            return item.source.id === sId && item.target.id === tId
                        })
                        const node = this.$store.state.template.gateways[sId]
                        if (node && node.conditions && node.conditions[line.id]) {
                            condition = Object.assign({}, node.conditions[line.id])
                        } else if (node && node.default_condition && node.default_condition.flow_id === line.id) {
                            condition = Object.assign({}, node.default_condition)
                        }

                        const source = {
                            id: sId,
                            arrow: sType
                        }
                        const target = {
                            id: tId,
                            arrow: tType
                        }
                        this.$refs.jsFlow.instance.deleteConnection(item)
                        this.$nextTick(() => {
                            this.createLine(source, target, condition)
                        })
                    }
                })
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
                const type = edp.anchor.cssClass
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
                // 触发端点拖拽事件
                const endPointDom = event.target.parentNode.parentNode
                Object.values(endPointDom.__ta.mousedown)[0](event)
                this.referenceLine = { x: bX, y: bY, id: edp.elementId, arrow: type }
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
            createLine (source, target, condition) {
                if (source.id === target.id) {
                    return false
                }

                const line = { source, target, condition }
                const validateMessage = validatePipeline.isLineValid(line, this.canvasData)
                if (validateMessage.result) {
                    this.$emit('onLineChange', 'add', line)
                    this.$refs.jsFlow.createConnector(line)
                    this.referenceLine.id = ''
                    return true
                } else {
                    this.$bkMessage({
                        message: validateMessage.message,
                        theme: 'warning'
                    })
                    return false
                }
            },
            onSubflowPauseResumeClick (id, value) {
                this.$emit('onSubflowPauseResumeClick', id, value)
            },
            onToggleHotKeyInfo (val) {
                this.showSmallMap = false
                this.isShowHotKey = !this.isShowHotKey
            },
            onTogglePerspective () {
                this.showSmallMap = false
                this.isShowHotKey = false
                this.isPerspective = !this.isPerspective
                this.$emit('onTogglePerspective', this.isPerspective)
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
                const { name, overlayId, id: lineId, value, loc = -70 } = data
                const line = this.canvasData.lines.find(item => item.id === lineId)
                this.$refs.jsFlow.removeLineOverlay(line, overlayId)
                this.$nextTick(() => {
                    const gatewayInfo = this.$store.state.template.gateways[line.source.id]
                    let defaultCls = ''
                    if (gatewayInfo && gatewayInfo.default_condition && gatewayInfo.default_condition.flow_id === lineId) {
                        defaultCls = 'default-branch'
                    }
                    const labelData = {
                        type: 'Label',
                        name: `<div class="branch-condition ${defaultCls}"
                                title="${tools.escapeStr(name)}(${tools.escapeStr(value)})"
                                data-lineid="${lineId}"
                                data-nodeid="${line.source.id}">${name}</div>`,
                        location: loc,
                        cls: 'branch-condition',
                        id: `condition${lineId}`
                    }
                    this.$refs.jsFlow.addLineOverlay(line, labelData)
                    this.setLabelDraggable(line, { ...data, nodeId: line.source.id })
                    this.conditionInfo = null
                })
            },
            // node mousedown
            onNodeMousedown (id) {
                this.$emit('onNodeMousedown', id)
            },
            // node mouseenter
            onNodeMouseEnter (node) {
                if (this.activeNode && node.id !== this.activeNode.id) {
                    this.closeShortcutPanel()
                }
                // 节点提示面板宽度
                const { x, y, type, id } = node
                // 计算判断节点右边的距离是否够展示气泡卡片
                const nodeDom = document.querySelector(`#${id}`)
                if (!nodeDom) return
                const { left: nodeLeft, right: nodeRight } = nodeDom.getBoundingClientRect()
                const bodyWidth = document.body.offsetWidth
                // 235节点的气泡卡片展示最小宽度
                const isRight = bodyWidth - nodeRight > 235
                // 设置坐标
                const { x: offsetX, y: offsetY } = this.$refs.jsFlow.canvasOffset
                let left, right, padding
                const top = y + offsetY - 10
                const nodeWidth = ['tasknode', 'subflow'].includes(type) ? 154 : 34
                if (isRight) {
                    left = x + offsetX + nodeWidth + (this.editable ? 60 : 0) // 60为画布左边栏的宽度
                    right = null
                    padding = '0 0 0 15px'
                } else {
                    right = bodyWidth - nodeLeft
                    left = null
                    padding = '0 15px 0 0'
                }
                this.nodeTipsPanelPosition = {
                    top: `${top}px`,
                    right: `${right}px`,
                    left: `${left}px`,
                    padding
                }
                this.isPerspectivePanelShow = false
                this.isExecRecordPanelShow = false
                // 节点透视面板展开
                if (this.isPerspective && node.name && ['tasknode', 'subflow'].includes(node.type)) {
                    this.nodeVariable = this.nodeVariableInfo[node.id] || { input: [], output: [] }
                    this.isPerspectivePanelShow = true
                }
                // 展开节点历史执行时间
                if (['RUNNING', 'FINISHED'].includes(node.status) && node.type === 'tasknode') {
                    this.execRecordLoading = true
                    this.isExecRecordPanelShow = true
                    this.$emit('nodeExecRecord', id)
                }
            },
            // 关闭节点历史执行时间
            closeNodeExecRecord () {
                this.isExecRecordPanelShow = false
                this.execRecordLoading = false
                this.$emit('closeNodeExecRecord')
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
                    this.referenceLine = {}
                    return
                }
                // 快捷菜单面板
                if (type !== 'endpoint') {
                    if (this.activeNode && this.activeNode.id) {
                        this.onUpdateNodeInfo(this.activeNode.id, { isActived: false })
                        this.toggleNodeLevel(this.activeNode.id, false)
                        this.onUpdateNodeInfo(id, { isActived: true })
                        this.toggleNodeLevel(id, true)
                    }
                    this.activeCon = null
                    this.activeNode = this.canvasData.locations.find(item => item.id === id)
                    this.openShortcutPanel('node')
                }
            },
            /**
             * 节点双击
            */
            onNodeDblclick (id) {
                this.onShowNodeConfig(id)
                this.closeShortcutPanel()
            },
            // 显示快捷节点面板
            openShortcutPanel (type, e) {
                let left, top
                if (type === 'node') {
                    const { x: offsetX, y: offsetY } = this.$refs.jsFlow.canvasOffset
                    const { x, y } = this.activeNode
                    switch (this.activeNode.type) {
                        case 'tasknode':
                        case 'subflow':
                            left = x + offsetX + NODES_SIZE_POSITION.ACTIVITY_SIZE[0] / 2 + 80
                            top = y + offsetY + NODES_SIZE_POSITION.ACTIVITY_SIZE[1] + 10
                            this.shortcutPanelNodeOperate = true
                            break
                        case 'startpoint':
                            left = x + offsetX + NODES_SIZE_POSITION.EVENT_SIZE[0] / 2 + 80
                            top = y + offsetY + NODES_SIZE_POSITION.EVENT_SIZE[1] + 10
                            break
                        default:
                            left = x + offsetX + NODES_SIZE_POSITION.GATEWAY_SIZE[0] / 2 + 80
                            top = y + offsetY + NODES_SIZE_POSITION.GATEWAY_SIZE[1] + 10
                            this.shortcutPanelNodeOperate = true
                    }
                    this.shortcutPanelDeleteLine = false
                } else {
                    const wrapGap = dom.getElementScrollCoords(this.$refs.jsFlow.$el)
                    const { pageX, pageY } = e
                    const nodeId = this.activeCon.sourceId
                    this.activeNode = this.canvasData.locations.find(item => item.id === nodeId)
                    this.shortcutPanelDeleteLine = true
                    left = pageX - wrapGap.x + 10
                    top = pageY - wrapGap.y + 10
                }
                this.connectorPosition = {}
                this.shortcutPanelPosition = { left, top }
                this.showShortcutPanel = true
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
            // 节点后面追加
            onAppendNode ({ location, line, isFillParam }) {
                const type = isFillParam ? 'copy' : 'add'
                this.$refs.jsFlow.createNode(location)
                this.$emit('onLocationChange', type, location)
                this.$emit('onLineChange', 'add', line)
                this.$nextTick(() => {
                    // 添加网关节点时禁止对该节点操作
                    if (location.type.includes('gateway') > -1) {
                        this.shortcutPanelNodeOperate = false
                    }
                    this.$refs.jsFlow.createConnector(line)
                    this.activeNode = location
                    this.openShortcutPanel('node')
                })
            },
            /**
             * 两个节点间插入一个节点
             * @param {String} startNode -前节点 id
             * @param {String} endNode -后节点 id
             * @param {Object} location -新建节点的 location
             */
            onInsertNode ({ startNodeId, endNodeId, location, isFillParam, startLineArrow = {}, endLineArrow = {} }) {
                const type = isFillParam ? 'copy' : 'add'
                const deleteLine = this.canvasData.lines.find(line => line.source.id === startNodeId && line.target.id === endNodeId)
                if (!deleteLine) {
                    return false
                }
                // 拷贝插入节点前网关的配置
                let gateways = this.$store.state.template.gateways
                gateways = tools.deepClone(gateways)
                this.$refs.jsFlow.removeConnector(deleteLine)
                const startLine = {
                    source: {
                        arrow: startLineArrow.source || 'Right',
                        id: startNodeId
                    },
                    target: {
                        id: location.id,
                        arrow: startLineArrow.target || 'Left'
                    }
                }
                const endLine = {
                    source: {
                        arrow: endLineArrow.source || 'Right',
                        id: location.id
                    },
                    target: {
                        id: endNodeId,
                        arrow: endLineArrow.target || 'Left'
                    }
                }
                this.$refs.jsFlow.createNode(location)
                this.$emit('onLocationChange', type, location)
                this.$emit('onLineChange', 'add', startLine)
                this.$emit('onLineChange', 'add', endLine)
                this.$nextTick(() => {
                    // 添加网关节点时禁止对该节点操作
                    if (location.type.includes('gateway') > -1) {
                        this.shortcutPanelNodeOperate = false
                    }
                    this.$refs.jsFlow.createConnector(startLine)
                    this.$refs.jsFlow.createConnector(endLine)
                    this.activeNode = location
                    this.openShortcutPanel('node')
                })
                // 插入节点时，若起始节点为网关节点则保留分支表达式
                if (startNodeId in gateways) {
                    const branchInfo = gateways[startNodeId]
                    const { conditions, default_condition } = branchInfo
                    if (!conditions) return
                    const tagCode = `branch_${startNodeId}_${location.id}`
                    conditions.tag = tagCode
                    this.conditionInfo = conditions[deleteLine.id]
                    if (default_condition && default_condition.flow_id === deleteLine.id) {
                        default_condition.tag = tagCode
                        this.conditionInfo = { ...default_condition, default_condition }
                    }
                }
            },
            // 通过快捷面板删除连线
            onShortcutDeleteLine () {
                const { sourceId, targetId } = this.activeCon
                const line = this.canvasData.lines.find(item => item.source.id === sourceId && item.target.id === targetId)
                this.$refs.jsFlow.removeConnector(line)
                this.closeShortcutPanel()
            },
            // 隐藏快捷节点面板
            closeShortcutPanel (e) {
                if (e && (dom.parentClsContains('canvas-node', e.target) || e.target.tagName === 'path')) {
                    return
                }
                if (this.activeNode) {
                    this.onUpdateNodeInfo(this.activeNode.id, { isActived: false })
                    this.toggleNodeLevel(this.activeNode.id, false)
                }
                this.activeNode = null
                this.activeCon = null
                this.connectorPosition = {}
                this.showShortcutPanel = false
                this.shortcutPanelNodeOperate = false
                this.shortcutPanelDeleteLine = false
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
                e.preventDefault()
                if (e.ctrlKey) {
                    if (e.deltaY > 0) { // 放大
                        this.onZoomOut(this.zoomOriginPosition)
                    } else {
                        this.onZoomIn(this.zoomOriginPosition)
                    }
                } else {
                    const $canvas = this.$refs.jsFlow.$el.querySelector('#canvas-flow')
                    const { left: leftStr, top: topStr } = window.getComputedStyle($canvas)
                    const left = Number(leftStr.replace('px', ''))
                    const top = Number(topStr.replace('px', ''))
                    this.setCanvasPosition(left - e.deltaX / 2, top - e.deltaY / 2)
                }
            },
            // 记录缩放点
            onCanvasMouseMove (e) {
                const { x: offsetX, y: offsetY } = document.querySelector('.canvas-flow-wrap').getBoundingClientRect()
                this.zoomOriginPosition.x = e.pageX - offsetX
                this.zoomOriginPosition.y = e.pageY - offsetY
                if (!this.editable) {
                    return
                }
                const connectorDom = document.querySelector('svg.bk-sops-connector-hover')
                if (!connectorDom) return
                // 当鼠标hover到新的连线时关闭旧的快捷面板
                const { top, left } = connectorDom.style
                if (tools.isDataEqual({ top, left }, this.connectorPosition)) {
                    return
                } else {
                    this.connectorPosition = { top, left }
                    this.showShortcutPanel = false
                }
                if (!this.showShortcutPanel) {
                    // 手动触发path元素的click事件
                    const pathDom = connectorDom.querySelector('path')
                    const event = document.createEvent('MouseEvent')
                    event.initMouseEvent('click', true, true)
                    pathDom.dispatchEvent(event)
                    // 打开快捷面板
                    const wrapGap = dom.getElementScrollCoords(this.$refs.jsFlow.$el)
                    const { pageX, pageY } = e
                    const nodeId = this.activeCon.sourceId
                    this.activeNode = this.canvasData.locations.find(item => item.id === nodeId)
                    this.shortcutPanelNodeOperate = false
                    this.shortcutPanelDeleteLine = true
                    const left = pageX - wrapGap.x + 10
                    const top = pageY - wrapGap.y - 50
                    this.shortcutPanelPosition = { left, top }
                    this.showShortcutPanel = true
                }
            },
            // 画布整体鼠标移入事件
            onCanvasContainerMouseMove (e) {
                // 节点历史执行时间/透视面板
                if (this.isExecRecordPanelShow || this.isPerspectivePanelShow) {
                    if (!dom.parentClsContains('canvas-node', e.target) && !dom.parentClsContains('node-tips-content', e.target)) {
                        this.nodeTipsPanelPosition = {}
                        this.isPerspectivePanelShow = false
                        this.closeNodeExecRecord()
                    }
                }
                // 监听鼠标是否hover到节点/连线上
                if (this.showShortcutPanel) {
                    const domClass = this.shortcutPanelDeleteLine ? 'jtk-connector' : 'canvas-node'
                    if (!dom.parentClsContains(`${domClass}`, e.target) && !dom.parentClsContains('shortcut-panel', e.target)) {
                        this.connectorPosition = {}
                        this.showShortcutPanel = false
                    }
                }
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
            },
            getLabelPosition (connection, x, y) {
                const segments = connection.connector.getSegments()
                let closest
                let projectionWay
                let totalWay = 0
                for (let i = 0; i < segments.length; i++) {
                    const segment = segments[i]
                    const projection = segment.findClosestPointOnPath(x, y, i, connection.connector.bounds)
                    const segmentWay = segment.getLength()
                    if (closest === undefined || projection.d < closest.d) {
                        closest = projection
                        projectionWay = totalWay + segmentWay * projection.l
                    }
                    totalWay += segmentWay
                }
                closest.totalPercent = projectionWay / totalWay
                return closest
            },
            // 设置连线label可拖动
            setLabelDraggable (line, labelData) {
                const self = this
                let percent
                const intialPos = { left: 0, top: 0 }
                const instance = this.$refs.jsFlow.instance
                const connection = this.$refs.jsFlow.instance.getConnections({ source: line.source.id, target: line.target.id })[0]
                const label = connection.getOverlay(`condition${line.id}`)
                const elLabel = label.getElement()
                instance.draggable(elLabel, {
                    start () {
                        const rect = elLabel.getBoundingClientRect()
                        intialPos.x = rect.x
                        intialPos.y = rect.y
                    },
                    drag () {
                        const pos = instance.getUIPosition(arguments, instance.getZoom())
                        const o1 = instance.getOffset(connection.endpoints[0].canvas)
                        const o2 = instance.getOffset(connection.endpoints[1].canvas)
                        const labelWidth = label.canvas.offsetWidth
                        const labelHeight = label.canvas.offsetHeight
                        const o = {
                            left: Math.min(o1.left, o2.left) + labelWidth / 2,
                            top: Math.min(o1.top, o2.top) + labelHeight / 2
                        }
                        const closest = self.getLabelPosition(connection, pos.left - o.left, pos.top - o.top)
                        label.loc = closest.totalPercent
                        percent = closest.totalPercent
                        if (!instance.isSuspendDrawing()) {
                            label.component.repaint()
                        }
                    },
                    stop () {
                        const rect = elLabel.getBoundingClientRect()
                        if (Math.abs(rect.x - intialPos.x) > 16 || Math.abs(rect.y - intialPos.y) > 16) {
                            const data = Object.assign({}, labelData, { loc: percent })
                            self.$emit('updateCondition', data)
                            self.labelDrag = true
                        }
                    }
                })
            }
        }
    }
</script>
<style lang="scss">
    @import '@/scss/mixins/scrollbar.scss';
    .canvas-container {
        position: relative;
        width: 100%;
        height: 100%;
    }
    .canvas-wrapper.jsflow {
        border: none;
        background: #f5f7fa;
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
                &.default-branch {
                    background: #f0f1f5;
                    border: 1px solid #c4c6cc;
                    &:hover {
                        border-color: #c4c6cc;
                    }
                }
            }
        }
        &.editable {
            .jtk-overlay.jtk-hover {
                display: inline-block;
            }
            .jtk-endpoint {
                cursor: pointer;
                &.template-canvas-endpoint {
                    background-repeat: no-repeat;
                    background-size: 24px;
                    &.jtk-endpoint-highlight {
                        background-image: url('~@/assets/images/endpoint.svg');
                    }
                    &[data-pos="Top"] {
                        transform: rotate(90deg);
                        background-position: bottom 50% left 0;
                    }
                    &[data-pos="Bottom"] {
                        transform: rotate(-90deg);
                        background-position: bottom 50% left 0;
                    }
                    &[data-pos="Left"] {
                        background-position: top 50% left 0;
                    }
                    &[data-pos="Right"] {
                        transform: rotate(180deg);
                        background-position: top 50% left 0;
                    }
                    &:hover {
                        background-image: url('~@/assets/images/endpoint-hover.svg');
                    }
                }
                &.template-canvas-endpoint.jtk-dragging {
                    background-image: url('~@/assets/images/endpoint-dragging.png');
                    background-position: bottom 50% left 50%;
                    z-index: 3;
                }
            }
        }
        &:not(.editable) {
            .jtk-endpoint circle{
                fill: transparent;
                stroke: transparent;
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
        .small-map-body {
            height: 100%;
        }
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
    .node-tips-content {
        position: absolute;
        z-index: 5;
        min-width: 235px;
        .execute-record-tips-content {
            margin-bottom: 8px;
            .content-wrap {
                width: 100%;
                font-size: 12px;
                background: #fff;
                padding: 12px 16px;
                border: 1px solid #dcdee5;
                box-shadow: 0 0 5px 0 rgba(0,0,0,0.09);
            }
            .content-item {
                display: flex;
                align-items: center;
                justify-content: space-between;
                color: #979ba5;
                margin-bottom: 8px;
                &:first-child {
                    color: #699df4;
                    .time {
                        font-weight: 700;
                    }
                }
                &:last-child {
                    margin-bottom: 15px;
                }
                .time {
                    color: #63656e;
                    padding-left: 15px;
                }
            }
            .deadline {
                color: #c4c6cc;
                padding-top: 8px;
                border-top: 1px solid #dcdee5;
            }
        }
        .perspective-tips-context {
            width: 100%;
            .tips-content {
                max-height: 160px;
                padding: 12px 16px;
                font-size: 12px;
                color: #63656e;
                line-height: 16px;
                background: #fff;
                border: 1px solid #dcdee5;
                border-radius: 2px;
                box-shadow: 0px 0px 5px 0px rgba(0, 0, 0, 0.09);
                overflow-y: auto;
                @include scrollbar;
                p {
                    margin-bottom: 4px;
                }
            }
            .tip-label {
                color: #979ba5;
            }
            .dividLine {
                height: 1px;
                background: #dcdee5;
                margin: 10px 0;
            }
        }
        &:hover {
            display: block;
        }
    }
</style>
