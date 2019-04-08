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
        :class="['pipeline-canvas', {'is-edit': isEdit}]"
        id="pipelineCanvas"
        ref="pipelineCanvas">
        <ConfigBar
            v-if="isConfigBarShow"
            :name="name"
            :cc_id="cc_id"
            :common="common"
            :templateSaving="templateSaving"
            @onChangeName="onChangeName"
            @onSaveTemplate="onSaveTemplate">
        </ConfigBar>
        <MenuBar
            v-if="isMenuBarShow"
            :singleAtomListLoading="singleAtomListLoading"
            :subAtomListLoading="subAtomListLoading"
            :atomTypeList="atomTypeList"
            :searchAtomResult="searchAtomResult"
            :isDisableStartPoint="isDisableStartPoint"
            :isDisableEndPoint="isDisableEndPoint"
            @show="onMenuBarShow"
            @onSearchAtom="onSearchAtom">
        </MenuBar>
        <div :class="['tool-wrapper',{'tool-wrapper-telescopic ': showNodeList}]">
            <transition name="wrapperLeft">
                <div class="tool-position">
                    <bk-tooltip :content="i18n.zoomIn" :delay="1000">
                        <div class="tool-icon" @click="onZoomIn">
                            <i class="common-icon-zoom-in"></i>
                        </div>
                    </bk-tooltip>
                    <bk-tooltip :content="i18n.zoomOut" :delay="1000">
                        <div class="tool-icon" @click="onZoomOut">
                            <i class="common-icon-zoom-out"></i>
                        </div>
                    </bk-tooltip>
                    <bk-tooltip :content="i18n.resetZoom" :delay="1000">
                        <div class="tool-icon" @click="onResetPosition">
                            <i class="common-icon-reduction"></i>
                        </div>
                    </bk-tooltip>
                    <bk-tooltip :content="i18n.nodeSelection" :delay="1000" v-if="isEdit">
                        <div
                            :class="['tool-icon', {'actived': isSelectionOpen}]"
                            @click="onOpenDragSelection">
                            <i class="common-icon-marquee"></i>
                        </div>
                    </bk-tooltip>
                    <bk-tooltip :content="i18n.formatPosition" :delay="1000" v-if="isEdit">
                        <div
                            class="tool-icon"
                            @click="onFormatPosition">
                            <i class="common-icon-four-square"></i>
                        </div>
                    </bk-tooltip>
                    <bk-tooltip :content="selectNodeName" :delay="1000" v-if="isSelectNode">
                        <div
                            class="tool-icon"
                            @click="onSelectNode">
                            <i :class="[{
                                'common-icon-black-box': !isSelectAll,
                                'common-icon-black-hook': isSelectAll,
                                'tool-disable': isPreviewMode
                                }]"></i>
                        </div>
                    </bk-tooltip>
                </div>
            </transition>
        </div>
        <div class="atom-node" v-show="isEdit">
            <span class="atom-number">{{i18n.added}} {{atomNumber}} {{i18n.node}}</span>
        </div>
        <NodeCanvas id="nodeCanvas"></NodeCanvas>
        <NodeTemplate/>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import '@/assets/js/bkflow.js'
import nodeFilter from '@/utils/nodeFilter.js'
import { uuid } from '@/utils/uuid.js'
import tools from '@/utils/tools.js'
import validatePipeline from '@/utils/validatePipeline.js'
import { NODE_DICT } from '@/constants/index.js'
import NodeTemplate from './NodeTemplate.vue'
import ConfigBar from './ConfigBar.vue'
import MenuBar from './MenuBar.vue'
import NodeCanvas from './NodeCanvas.vue'
import formatPositionUtils from '@/utils/formatPosition.js'
import draft from '@/utils/draft.js'
import toolsUtils from '@/utils/tools.js'

const ENDPOINT_DIRECTION = ['Top', 'Left', 'Right', 'Bottom']
export default {
    name: 'PipelineCanvas',
    props: {
        isMenuBarShow: {
            type: Boolean,
            default () {
                return true
            }
        },
        isConfigBarShow: {
            type: Boolean,
            default () {
                return true
            }
        },
        isEdit: {
            type: Boolean,
            default () {
                return true
            }
        },
        singleAtomListLoading: {
            type: Boolean
        },
        subAtomListLoading: {
            type: Boolean
        },
        templateSaving: {
            type: Boolean
        },
        atomTypeList: {
            type: Object,
            required: false
        },
        searchAtomResult: {
            type: Array
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
        name: {
            type: String,
            required: false
        },
        cc_id: {
            type: String,
            required: false
        },
        common: {
            type: String,
            required: false
        },
        isSelectNode: {
            type: Boolean,
            required: false,
            default () {
                return false
            }
        },
        selectNodeType: {
            type: Boolean,
            required: false,
            default () {
                return false
            }
        },
        isPreviewMode: {
            type: Boolean,
            required: false,
            default () {
                return false
            }
        },
        isSelectAllNode: {
            type: Boolean,
            required: false,
            default () {
                return false
            }
        }
    },
    components: {
        NodeTemplate,
        ConfigBar,
        MenuBar,
        NodeCanvas
    },
    data () {
        return {
            i18n: {
                resetZoom: gettext('复位'),
                zoomIn: gettext('放大'),
                zoomOut: gettext('缩小'),
                nodeSelection: gettext('节点框选'),
                formatPosition: gettext('排版'),
                choiceAll: gettext('全选'),
                cancelChoiceAll: gettext('反选'),
                added: gettext('已添加'),
                node: gettext('个节点')
            },
            zoomRadio: 1,
            nodeTypeUniqueInCanvas: ['startpoint', 'endpoint'],
            limitSingleInput: ['endpoint', 'parallelgateway', 'branchgateway', 'tasknode', 'subflow'],
            limitSingleOutput: ['startponit', 'convergegateway', 'tasknode', 'subflow'],
            opts: {
                canvas: "#nodeCanvas",  // 画布
                template: "#node-template",  // 可配置的模版
                tools: ".node-source",  // 流程拖动源
                locationConfig: {
                    startpoint: ENDPOINT_DIRECTION,
                    endpoint: ENDPOINT_DIRECTION,
                    parallelgateway: ENDPOINT_DIRECTION,
                    convergegateway: ENDPOINT_DIRECTION,
                    branchgateway: ENDPOINT_DIRECTION,
                    tasknode: ENDPOINT_DIRECTION,
                    subflow: ENDPOINT_DIRECTION
                },  // 节点的类型和端点的位置
                lineWidth: 3,  // 线的宽度 默认为2
                fillColor: '#348af3',  // 高亮颜色
                defaultColor: '#a9adb6',  // 默认颜色
                lineRadius: 1, // 线拐弯弧度
                pointColor: 'rgba(52, 138, 243, 0.15)',  // 端点的颜色
                pointWidth: 3,  // 连接端点的半径
                pointDistance: 0,  // 端点与线的距离
                data: tools.deepClone(this.canvasData), // 渲染的数据源,
                id: 'node',  // 配置渲染的节点id
                isEdit: this.isEdit,  // 是否编辑
                dropElevent: null,  // 拖拽的数据源

                getDefaultLocation: this.getDefaultLocation,  // 获取某一类型节点的初始化节点数据
                onCreateLocationBefore: this.onCreateLocationBefore, // 节点创建前事件回调
                onCreateLocationAfter: this.onCreateLocationAfter, // 节点创建初始化后事件回调, 参数为节点id
                onCreateLineAfter: this.onCreateLineAfter, // 创建线条后事件回调
                onRemoveLineAfter: this.onRemoveLineAfter,  // 删除线之后的回调函数
                onNodeMoveAfter: this.onNodeMoveAfter,  // 拖动节点停止后的回调函数
                ondrawData: null,  // 渲染流程后回调
                onLineDragStop: this.onLineDragStop, // 节点端点拖拽连线结束回调
                onNodeClick: this.onNodeClick, // 标准插件节点点击事件回调
                onLabelBlur: this.onLabelBlur, // 标准插件节点点击事件回调
                onLocationMoveAfter: this.onLocationMoveAfter, // 标准插件节点移动事件回调
                onRemoveLocationAfter: this.onRemoveLocationAfter, // 删除标准插件节点事件回调
                onCopyElement: this.onCopyElement, // 复制节点、连线回调
                onPasteElement: this.onPasteElement, // 粘贴节点、连线回调
                onDeleteElement: this.onDeleteElement, // 删除节点、连线回调
                onCloseDragSelection: this.onCloseDragSelection // 关闭节点框选回调
            },
            isDisableStartPoint: false,
            isDisableEndPoint: false,
            showNodeList: '',
            isSelectionOpen: false,
            nodesOfCopyed: [],
            isSelectAll: this.isSelectAllNode
        }
    },
    computed: {
        locationsObj () {
            return this.transformArrayToObj(this.canvasData.locations)
        },
        selectNodeName () {
            return this.isSelectAll ? this.i18n.choiceAll : this.i18n.cancelChoiceAll
        },
        atomNumber () {
            return this.canvasData.activities && this.isEdit ? Object.keys(this.canvasData.activities).length : 0
        }
    },
    watch: {
        zoomRadio (val) {
            this.dataFlowInstance.setZoom(val)
        }
    },
    created () {
        this.onFormatPosition = toolsUtils.debounce(this.formatPositionHandler, 500)
    },
    mounted () {
        const canvasInstance = $("#pipelineCanvas").dataflow(this.opts)
        this.canvasInstance = canvasInstance
        this.dataFlowInstance = $('#pipelineCanvas').data('dataflow')
        this.$refs.pipelineCanvas.addEventListener('click', this.handleDeleteNode, 'false')
        this.isDisableStartPoint = this.canvasData.locations.find((location) => location.type === 'startpoint') ? true : false
        this.isDisableEndPoint = this.canvasData.locations.find((location) => location.type === 'endpoint') ? true : false
    },
    beforeDestroy () {
        this.$refs.pipelineCanvas.removeEventListener('click', this.handleDeleteNode, 'false')
    },
    methods: {
        getDefaultLocation (type) {
            return {
                id: uuid(),
                atomId: '',
                stage_name: gettext('步骤1'),
                optional: false,
                error_ignorable: false,
                mode: 'edit', // edit：编辑模板；select：选择节点；excute：执行任务；preview：预览
                checked: true, // 节点选中状态
                can_retry: true,
                isSkipped: true
            }
        },
        transformArrayToObj (data) {
            const obj = {}
            data.forEach(item => {
                obj[item.id] = tools.deepClone(item)
            })
            return obj
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
        onCreateLocationBefore (loc) {
            const validateMessage = validatePipeline.isLocationValid(loc, this.canvasData.locations)

            if (!validateMessage.result) {
                this.$bkMessage({
                    message: validateMessage.message,
                    theme: 'warning'
                })
                return false
            }
            return true
        },
        onCreateLocationAfter (loc) {
            this.$emit('onLocationChange', 'add', Object.assign({}, loc))
            if (loc.type === 'startpoint') {
                this.isDisableStartPoint = true
            } else if (loc.type === 'endpoint') {
                this.isDisableEndPoint = true
            }
        },
        onLineDragStop (line, event, connection) {
            let validateMessage
            if (!line.target.arrow) {
                const nodeEl = this.getNodeWithEndpoint(event.target)
                if (!nodeEl) { // 无效连线
                    return false
                } else { // 连线端点在节点上自动吸附
                    if (line.source.id === nodeEl.id) {
                        return false // 节点不可以连接自身
                    }
                    let arrow
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
                            arrow = (nodeRects.width - offsetX) > offsetY ? 'Top' : 'right'
                        } else {
                            arrow = (nodeRects.width - offsetX) > (nodeRects.height - offsetY) ? 'Bottom' : 'Right'
                        }
                    }

                    line.target = {
                        arrow,
                        id: nodeEl.id
                    }
                    validateMessage = validatePipeline.isLineValid(line, this.canvasData)
                    validateMessage.result && this.dataFlowInstance.createLine(line)
                }
            } else {
                validateMessage = validatePipeline.isLineValid(line, this.canvasData)
            }

            if (!validateMessage.result) {
                this.$bkMessage({
                    message: validateMessage.message,
                    theme: 'warning'
                })
                return false
            }
            return true
        },
        onCreateLineAfter (line) {
            this.$emit('onLineChange', 'add',  line)
            this.$nextTick(function () {
                const branchInfo = this.canvasData.branchConditions[line.source.id]
                if (branchInfo) {
                    const lineId = this.canvasData.lines.filter(item => {
                        return item.source.id === line.source.id && item.target.id === line.target.id
                    })[0].id
                    const labelName = branchInfo[lineId].evaluate
                    const labelData = {
                        id: lineId,
                        nodeId: line.source.id,
                        name: labelName
                    }
                    this.dataFlowInstance.addLabel(line, labelData)
                }
            })

        },
        onRemoveLineAfter (line) {
            this.$emit('onLineChange', 'delete', line)
        },
        onLocationMoveAfter (loc) {
            this.$emit('onLocationMoveDone', loc)
        },
        onOpenDragSelection () {
            this.dataFlowInstance.setDragSelection(true)
            this.isSelectionOpen = true
        },
        onCloseDragSelection () {
            this.isSelectionOpen = false
        },
        onZoomIn () {
            this.zoomRadio = this.zoomRadio * 1.1
        },
        onZoomOut () {
            this.zoomRadio = this.zoomRadio * 0.9
        },
        onResetPosition () {
            this.dataFlowInstance.resetLocation()
            this.zoomRadio = 1
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
            let lines = tools.deepClone(this.canvasData.lines)
            let locations = this.canvasData.locations
            let data = formatPositionUtils.formatPosition(lines, locations)

            this.onNewDraft(gettext('排版自动保存'), false)
            let message = gettext('排版完成，原内容在本地缓存中')
            // 重绘Canvas
            this.dataFlowInstance.updateCanvas(data)
            const {overBorderLine} = data
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
        handleDeleteNode (event) {
            const node = event.target
            if (!node.classList.contains('common-icon-dark-circle-close')) return
            const id = node.dataset.id
            const type = node.dataset.type
            if (this.canvasInstance && id && type) {
                this.dataFlowInstance.deleteLocation(id)
                this.$emit('onLocationChange', 'delete', {id, type})
            }
            if (type === 'startpoint' ) {
                this.isDisableStartPoint = false
            } else if (type === 'endpoint') {
                this.isDisableEndPoint = false
            }
        },
        onNodeClick (id) {
            this.$emit('onNodeClick', id)
        },
        onLabelBlur (labelData) {
            this.$emit('onLabelBlur', labelData)
        },
        onUpdateNodeInfo (id, data) {
            this.dataFlowInstance.updateLocationById(id, data)
        },
        onUpdateCanvas (data) {
            this.dataFlowInstance.updateCanvas(data)
        },
        onSearchAtom (data) {
            this.$emit('onSearchAtom', data)
        },
        onChangeName (name) {
            this.$emit('onChangeName', name)
        },
        onSaveTemplate () {
            const validateMessage = validatePipeline.isDataValid(this.canvasData)
            if (!validateMessage.result) {
                this.$bkMessage({
                    message: validateMessage.message,
                    theme: 'error'
                })
                return false
            }
            this.$emit('onSaveTemplate')
        },
        onNewDraft (message) {
            this.$emit('onNewDraft', message)
        },
        onReplaceLineAndLocation (data) {
            this.$emit('onReplaceLineAndLocation', data)
        },
        onMenuBarShow (val) {
            this.showNodeList = val
        },
        onCopyElement (data) {
            this.nodesOfCopyed = data
        },
        /**
         * 节点粘贴
         * @param {Number} x 节点 x 坐标偏移量
         * @param {Number} y 节点 y 坐标偏移量
         * @return {Array} 返回新增的节点
         */
        onPasteElement (x, y) {
            const {locations, lines} = this.createCopyOfSelectedNodes()
            locations.forEach(location => {
                location.x += x
                location.y += y
                this.dataFlowInstance.createLocation(location)
            })
            lines.forEach(line => {
                this.dataFlowInstance.createLine(line)
            })
            return locations
        },
        onDeleteElement (data) {
            data.forEach(id => {
                const node = {
                    id,
                    type: this.locationsObj[id].type
                }
                this.dataFlowInstance.deleteLocation(id)
                this.$emit('onLocationChange', 'delete', node)
            })
        },
        createCopyOfSelectedNodes () {
            const lines = []
            const locations = []
            const locationIdReplaceHash = {} // 节点 id 替换映射表
            const lineIdReplaceHash = {} // 连线 id 替换映射表
            this.nodesOfCopyed.forEach((id, index) => {
                const location = tools.deepClone(this.locationsObj[id])
                const activity = tools.deepClone(this.canvasData.activities[id])
                locationIdReplaceHash[id] = location.id = 'node' + uuid()

                // 复制 location 数据
                if (activity) {
                    location.atomId = activity.type === 'ServiceActivity' ? activity.component.code : activity.template_id
                }

                if (location.type !== 'startpoint' && location.type !== 'endpoint') {
                    locations.push(location)
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

            return {locations, lines}
        },
        onSelectNode () {
            if (this.isPreviewMode) {
                return
            }
            this.isSelectAll = !this.isSelectAll
            this.$emit('onSelectNode', this.isSelectAll)
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.pipeline-canvas {
    position: relative;
    height: 100%;
    overflow: hidden;
    .tool-wrapper {
        position: absolute;
        top: 80px;
        left: 80px;
        z-index: 4;
        transition: all 0.5s ease;
        user-select: none;
        .tool-position {
            height: 36px;
            background: #c4c6cc;
            border-radius: 18px;
            opacity: 0.8;
            /deep/ .bk-tooltip:first-child {
                margin-left: 20px;
            }
            /deep/ .bk-tooltip:last-child {
                margin-right: 20px;
            }
            .tool-icon {
                display: inline-block;
                line-height: 36px;
                margin-left: 15px;
                margin-right: 15px;
                color: #ffffff;
                cursor: pointer;
                &:first-child {
                    margin-left: 20px;
                }
                &:last-child {
                    margin-right: 15px;
                }
                &.actived {
                    color: #3480ff;
                }
                .tool-disable {
                    cursor: not-allowed;
                    opacity: 0.3;
                }
            }
        }
    }
    .tool-wrapper-telescopic {
        position: absolute;
        top: 80px;
        left: 380px;
        z-index: 4;
    }
    .atom-node {
        position: absolute;
        top: 86px;
        left: 42%;
        z-index: 4;
        .atom-number {
            color: #a9b2bd;
            font-size: 14px;
        }
    }
}
</style>


