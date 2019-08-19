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
        :class="{ 'tool-wrapper-telescopic': showNodeMenu }"
        :data="flowData"
        :show-palette="showPalette"
        :show-tool="showTool"
        :editable="editable"
        :endpoint-options="endpointOptions"
        :connector-options="connectorOptions"
        @onToolClick="onToolClick"
        @onCreateNodeBefore="onCreateNodeBefore"
        @onCreateNodeAfter="onCreateNodeAfter"
        @onConnectionDragStop="onConnectionDragStop"
        @onBeforeDrop="onBeforeDrop"
        @onConnection="onConnection"
        @onConnectionDetached="onConnectionDetached"
        @onNodeMoveStop="onNodeMoveStop"
        @onOverlayClick="onOverlayClick">
        <template
            v-slot:palettePanel>
            <palettePanel
                :atom-type-list="atomTypeList"
                :is-disable-start-point="isDisableStartPoint"
                :is-disable-end-point="isDisableEndPoint"
                @updateNodeMenuState="updateNodeMenuState">
            </palettePanel>
        </template>
        <template v-slot:toolPanel>
            <toolPanel
                :is-preview-mode="isPreviewMode"
                @onZoomIn="onZoomIn"
                @onZoomOut="onZoomOut"
                @onResetPosition="onResetPosition">
            </toolPanel>
        </template>
        <template v-slot:nodeTemplate="{ node }">
            <node-template
                :node="node"
                @onNodeClick="onNodeClick"
                @onNodeRemove="onNodeRemove">
            </node-template>
        </template>
    </js-flow>
</template>
<script>
    import JsFlow from '@/assets/js/jsflow.esm.js'
    import NodeTemplate from './NodeTemplate'
    import PalettePanel from './PalettePanel'
    import ToolPanel from './ToolPanel'
    import tools from '@/utils/tools.js'
    import { endpointOptions, connectorOptions } from './options.js'
    import formatPositionUtils from '@/utils/formatPosition.js'
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
            isSelectAllNode: {
                type: Boolean,
                default: false
            },
            isPreviewMode: {
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
                flowData,
                endpointOptions,
                connectorOptions
            }
        },
        mounted () {
            this.isDisableStartPoint = !!this.canvasData.locations.find((location) => location.type === 'startpoint')
            this.isDisableEndPoint = !!this.canvasData.locations.find((location) => location.type === 'endpoint')
        },
        methods: {
            onToolClick () {},
            onZoomIn () {
                this.$refs.jsFlow.zoomIn()
            },
            onZoomOut () {
                this.$refs.jsFlow.zoomOut()
            },
            onResetPosition () {
                this.$refs.jsFlow.resetPosition()
            },
            formatPositionHandler () {
                const validateMessage = validatePipeline.isDataValid(this.canvasData)
                // 判断是否结构完整
                if (!validateMessage.result) {
                    this.$bkMessage({
                        message: validateMessage.message,
                        theme: 'error'
                    })
                    return false
                }
                // 恢复大小后进行编排
                this.onResetPosition()

                // 需要做深拷贝一次 防止改变vue store内容
                const lines = tools.deepClone(this.canvasData.lines)
                const locations = this.canvasData.locations
                const data = formatPositionUtils.formatPosition(lines, locations)

                this.onNewDraft(gettext('排版自动保存'), false)
                const message = gettext('排版完成，原内容在本地缓存中')
                // 重绘Canvas
                this.dataFlowInstance.updateCanvas(data)
                const { overBorderLine } = data
                if (overBorderLine.length !== 0) {
                    overBorderLine.forEach(line => {
                        const config = [
                            'Flowchart', // 流程图种类
                            {
                                stub: [5, 20], // 起始端点连接线的最小长度
                                gap: 8, // 线与端点点最小间隔
                                cornerRadius: 2, // 折线弧度
                                alwaysRespectStubs: true, // 允许 stub 配置生效
                                midpoint: line.midpoint// 折线比例
                            // todo:需要增加midpoint数据的source,target,midpoint数据进行后台和前端保存
                            }
                        ]
                        this.dataFlowInstance.setConnector(line.source, line.target, config)
                    })
                }
                // 提示信息
                this.$bkMessage({
                    message: message,
                    theme: 'success'
                })
                // 改变store中的line和location内容
                this.onReplaceLineAndLocation(data)
            },
            updateNodeMenuState (val) {
                this.showNodeMenu = val
            },
            onNodeClick (id) {
                this.$emit('onNodeClick', id)
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
                const validateMessage = validatePipeline.isLocationValid(node, this.flowData.nodes)

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
                } else {
                    this.$bkMessage({
                        message: validateMessage.message,
                        theme: 'warning'
                    })
                }
            },
            onBeforeDrop (line) {
                debugger
                console.log('drop')
                this.$nextTick(() => {
                    this.$emit('onLineChange', 'add', line)
                })
                return false
            },
            onConnection (line) {
                console.log('test')
                const lineId = this.canvasData.lines.filter(item => {
                    return item.source.id === line.source.id && item.target.id === line.target.id
                })[0].id
                this.$refs.jsFlow.addLineOverlay(line, {
                    type: 'Label',
                    name: '<i class="common-icon-dark-circle-close"></i>',
                    location: 0.5,
                    id: `close_${lineId}`
                })
                const branchInfo = this.canvasData.branchConditions[line.source.id]
                if (branchInfo) {
                    const labelName = branchInfo[lineId].evaluate
                    const labelData = {
                        type: 'Label',
                        name: labelName,
                        id: `condition${lineId}`
                    }
                    this.$refs.jsFlow.addLineOverlay(line, labelData)
                }
            },
            onConnectionDetached (line) {
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
            }
        }
    }
</script>
<style lang="scss" scoped>
    .jsflow {
        border: none;
        background: #e1e4e8;
        /deep/ .adding-node {
            z-index: 4;
        }
        /depp/ .palette-panel-wrap {
            border-right: 1px solid #cacedb;
        }
        /deep/ .tool-panel-wrap {
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
        /deep/ .jtk-endpoint {
            z-index: 1;
            cursor: pointer;
        }
        /deep/ .jsflow-node {
            z-index: 3;
        }
        /deep/ .jtk-overlay {
            cursor: pointer;
            &:not(.branch-condition) {
                display: none;
            }
            .common-icon-dark-circle-close{
                font-size: 16px;
                color: #ff5757;
                background: #ffffff;
                border-radius: 50%;
            }
        }
        &.editable {
            /deep/ .jtk-overlay.jtk-hover {
                display: inline-block;
            }
        }
        &.tool-wrapper-telescopic {
            /deep/ .tool-panel-wrap {
                top: 20px;
                left: 380px;
                z-index: 5;
            }
        }
    }
</style>
