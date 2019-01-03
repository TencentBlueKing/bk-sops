/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div
        :class="{
            'pipeline-canvas': true,
            'is-edit': isEdit
        }"
        id="pipelineCanvas"
        ref="pipelineCanvas">
        <MenuBar
            v-if="isMenuBarShow"
            :singleAtomListLoading="singleAtomListLoading"
            :subAtomListLoading="subAtomListLoading"
            :atomTypeList="atomTypeList"
            :searchAtomResult="searchAtomResult"
            @onSearchAtom="onSearchAtom"
            @onResetPosition="onResetPosition"
            @onZoomOut="onZoomOut"
            @onZoomIn="onZoomIn">
        </MenuBar>
        <div class="tool-wrapper">
            <!-- <div
                class="reset-position"
                @click="onFormatPosition"
                v-bktooltips.right="i18n.format_position">
                <i class="common-icon-adjust-position"></i>
            </div> -->
            <div
                class="reset-position"
                @click="onResetPosition"
                v-bktooltips.right="i18n.reset_zoom">
                <i class="common-icon-adjust-position"></i>
            </div>
            <div class="zoom-area">
                <div
                    class="zoom-in"
                    @click="onZoomOut"
                    v-bktooltips.right="i18n.zoom_in">
                    <i class="common-icon-add"></i>
                </div>
                <div
                    class="zoom-out"
                    @click="onZoomIn"
                    v-bktooltips.right="i18n.zoom_out">
                    <i class="minus"></i>
                </div>
            </div>
        </div>
        <ConfigBar
            v-if="isConfigBarShow"
            :name="name"
            :cc_id="cc_id"
            @onChangeName="onChangeName"
            @onSaveTemplate="onSaveTemplate">
        </ConfigBar>
        <NodeCanvas id="nodeCanvas"></NodeCanvas>
        <NodeTemplate/>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import '@/assets/js/bkflow.js'
import nodeFilter from '@/utils/nodeFilter.js'
import { uuid } from '@/utils/uuid.js'
import validatePipeline from '@/utils/validatePipeline.js'
import { NODE_DICT } from '@/constants/index.js'
import NodeTemplate from './NodeTemplate.vue'
import ConfigBar from './ConfigBar.vue'
import MenuBar from './MenuBar.vue'
import NodeCanvas from './NodeCanvas.vue'

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
                reset_zoom: gettext("复位"),
                zoom_in: gettext("放大"),
                zoom_out: gettext("缩小"),
                format_position: gettext("自动编排")
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
                pointColor: '#348af3',  // 端点的颜色
                pointWidth: 3,  // 连接端点的半径
                pointDistance: 0,  // 端点与线的距离
                data: JSON.parse(JSON.stringify(this.canvasData)), // 渲染的数据源,
                id: 'node',  // 配置渲染的节点id
                isEdit: this.isEdit,  // 是否编辑
                dropElevent: null,  // 拖拽的数据源

                getDefaultLocation: this.getDefaultLocation,  // 获取某一类型节点的初始化节点数据
                onCreateLocationBefore: this.onCreateLocationBefore, // 节点创建前事件回调
                onCreateLocationAfter: this.onCreateLocationAfter, // 节点创建初始化后事件回调, 参数为节点id
                onCreateLineBefore: this.onCreateLineBefore, // 创建线条前事件回调
                onCreateLineAfter: this.onCreateLineAfter, // 创建线条后事件回调
                onRemoveLineAfter: this.onRemoveLineAfter,  // 删除线之后的回调函数
                onNodeMoveAfter: this.onNodeMoveAfter,  // 拖动节点停止后的回调函数
                ondrawData: null,  // 渲染流程后回调
                onLineDragStop: this.onLineDragStop, // 节点端点拖拽连线结束回调
                onNodeClick: this.onNodeClick, // 原子节点点击事件回调
                onLabelBlur: this.onLabelBlur, // 原子节点点击事件回调
                onLocationMoveAfter: this.onLocationMoveAfter
            }
        }
    },
    watch: {
        zoomRadio (val) {
            this.dataFlowInstance.setZoom(val)
        }
    },
    mounted () {
        const canvasInstance = $("#pipelineCanvas").dataflow(this.opts)
        this.canvasInstance = canvasInstance
        this.dataFlowInstance = $('#pipelineCanvas').data('dataflow')
        this.$refs.pipelineCanvas.addEventListener('click', this.handleDeleteNode, 'false')
        // this.onFormatPosition()
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
                checked: true // 节点选中状态
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
        },
        onLineDragStop (line) {
            if (!line.source.arrow || !line.target.arrow) return // 无效连线
            const validateMessage = validatePipeline.isLineValid(line, this.canvasData)
            if (!validateMessage.result) {
                this.$bkMessage({
                    message: validateMessage.message,
                    theme: 'warning'
                })
                return false
            }
            return true
        },
        onCreateLineBefore (line) {
            if (!line.source.arrow || !line.target.arrow) return
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
        onZoomIn () {
            this.zoomRadio = this.zoomRadio * 0.9
        },
        onZoomOut () {
            this.zoomRadio = this.zoomRadio * 1.1
        },
        onResetPosition () {
            this.dataFlowInstance.resetLocation()
            this.zoomRadio = 1
        },
        onFormatPosition () {
            let allData = this.dataFlowInstance.getAllData()
            let lines = allData.lines
            let linesLength = lines.length
            let locations = allData.locations
            let locationsLength = locations.length
            // 判断是否结构完整
            const validateMessage = validatePipeline.isDataValid(this.canvasData)
            if (!validateMessage.result) {
                this.$bkMessage({
                    message: validateMessage.message,
                    theme: 'error'
                })
                return false
            }
            const gatewayShiftX = 210
            // 其实位置
            const startPointX = 60
            const startPointY = 50
            // 每一个偏移大小
            const shiftX = 152
            const halfShiftX = shiftX / 2
            const toolShiftX = 14
            const shiftY = 110
            // 偏差高
            const deviationY = 17
            // 工具栏大小
            const toolsWidth = 60
            const tabContentWidth = 414
            const maxShiftX = 100
            // 浏览器宽度 - 工具栏大小 - 全局变量栏大小
            const maxWidth = document.body.clientWidth - toolsWidth - tabContentWidth - maxShiftX
            var lastNodeX = 60
            var lastNodeY = 50
            // 由于网关排序问题，需要记录最大高度
            var gatewayShiftY = 0
            let group = {}
            
            // 分组进行位置定位
            for (let i = 0 ; i < linesLength; i++) {
                let line = lines[i]
                let source = line.source
                let target = line.target
                try {
                    let groupLength = group[source.id].length
                    group[source.id][groupLength] = target.id
                }
                catch (e) {
                    // 初始化
                    group[source.id] = [target.id]
                }
            }
            
            // 当前节点
            let lastPoint = null
            // 尾节点
            let endPoint = null
            // 循环的当前Id
            let nowId = null
            // 整合所有的除头结点的数据
            let newLocations = {}
            for (let i = 0 ; i < locationsLength; i++) {
                let location = locations[i]
                let type = location['type']
                if (type === 'startpoint') {
                    lastPoint = location
                    nowId = location['id']
                }
                else {
                    if (type === 'endpoint') {
                        endPoint = location
                    }
                    else {
                        newLocations[location['id']] = location
                    }
                }
            }
            // 结束节点放最后一个
            newLocations[endPoint['id']] = endPoint
            locations = [{
                'id': lastPoint['id'],
                'type': 'startpoint',
                'name': lastPoint['name'],
                'status': '',
                'x': startPointX,
                'y': startPointY
            }]
            let gatewayFlag = false
            // 用于控制换行时起始位置
            let isStartPoint = false
            // 用于控制在结束节点之前的原子大小
            let lastPointType = 'startpoint'
            let branchgatewayId = null
            for (let i = 0; i < locationsLength ; i++) {
                let lastList = group[nowId]
                if (lastList  === undefined ) {
                    // 尾节点不需要继续进行了
                    break
                }
                if (lastNodeX + shiftX * 1.6 > maxWidth) {
                    lastNodeX = startPointX
                    if (gatewayShiftY === 0) {
                        gatewayShiftY = shiftY
                    }
                    lastNodeY = lastNodeY + startPointY + gatewayShiftY
                    isStartPoint = true
                }
                let length = lastList.length
                let originX = lastNodeX + shiftX
                let originY = 0
                for (let j = 0; j < length; j++){
                    nowId = lastList[j]
                    let location = newLocations[nowId]
                    let type = location['type']
                    if (type === 'tasknode' || type === 'subflow') {
                        if (isStartPoint) {
                            // 换行的第一个需要删减一定距离
                            lastNodeX = lastNodeX - shiftX - halfShiftX
                            isStartPoint = false
                        }
                        if (gatewayFlag) {
                            let nodeY = lastNodeY + j * shiftY - deviationY
                            locations.push({
                                'id': location['id'],
                                'type': type,
                                'name': location['name'],
                                'stage_name': location['stage_name'],
                                'status': '',
                                'x': lastNodeX + shiftX,
                                'y': nodeY
                            })
                            for (let lineIndex = 0; lineIndex < linesLength; lineIndex++ ) {
                                if (lines[lineIndex].target.id === location.id) {
                                    if (j === 0) {
                                        lines[lineIndex].source.arrow = 'Right'
                                    }
                                    else if (j >= 1){
                                        lines[lineIndex].source.arrow = 'Bottom'
                                    }
                                }
                                // 尾箭头统一
                                if (lines[lineIndex].source.id === location.id) {
                                    if (j === 0) {
                                        lines[lineIndex].target.arrow = 'Left'
                                    }
                                    else if (j >= 1){
                                        lines[lineIndex].target.arrow = 'Bottom'
                                    }
                                }
                            }
                            if (j + 1 === length){
                                // 最后一个节点
                                gatewayFlag = false
                                lastNodeX = lastNodeX + shiftX
                                gatewayShiftY = 2 * nodeY
                            }
                        }
                        else {
                            // 上一个还是tasknode 节点
                            if (lastPointType === type) {
                                lastNodeX = lastNodeX + toolShiftX * 4
                            }
                            locations.push({
                                'id': location['id'],
                                'type': 'tasknode',
                                'name': location['name'],
                                'stage_name': location['stage_name'],
                                'status': '',
                                'x': lastNodeX + shiftX,
                                'y': lastNodeY - deviationY
                            })
                            lastNodeX = lastNodeX + shiftX
                        }
                        lastPointType = type
                    }
                    else if (type === 'parallelgateway' || type === 'branchgateway') {
                        if (lastPointType === 'tasknode') {
                            // 结束节点前是个原子节点需要增加一半距离
                            lastNodeX = lastNodeX + shiftX / 2
                            isStartPoint = false
                        }
                        if (isStartPoint) {
                            // 换行的第一个需要删减一定距离
                            lastNodeX = lastNodeX - shiftX * 2
                            isStartPoint = false
                        }
                        locations.push({
                            'id': location['id'],
                            'type': type,
                            'name': location['name'],
                            'status': '',
                            'x': lastNodeX + shiftX,
                            'y': lastNodeY
                        })
                        // 网关节点标记位，用于排列后续原子节点
                        gatewayFlag = true
                        lastNodeX = lastNodeX + shiftX
                        lastPointType = type
                    }
                    else if (type === 'convergegateway') {
                        if (isStartPoint) {
                            // 换行的第一个需要删减一定距离
                            lastNodeX = lastNodeX - shiftX - gatewayShiftX
                            isStartPoint = false
                        }
                        locations.push({
                            'id': location['id'],
                            'type': type,
                            'name': location['name'],
                            'status': '',
                            'x': lastNodeX + gatewayShiftX,
                            'y': lastNodeY
                        })
                        lastNodeX = lastNodeX + gatewayShiftX
                        lastPointType = type
                    }
                    else if (type === 'endpoint') {
                        if (isStartPoint) {
                            // 换行的第一个需要删减一定距离
                            lastNodeX = lastNodeX - shiftX * 2
                        }
                        if (lastPointType === 'tasknode') {
                            // 结束节点前是个原子节点需要增加一半距离
                            lastNodeX = lastNodeX + shiftX
                            isStartPoint = false
                        }
                        locations.push({
                            'id': location['id'],
                            'type': type,
                            'name': location['name'],
                            'status': '',
                            'x': lastNodeX + shiftX,
                            'y': lastNodeY
                        })
                        break
                    }
                }
            }
            // 重绘Canvas
            this.dataFlowInstance.updateCanvas({'lines': lines, 'locations': locations})
            // 重回界面开始的地方
            this.dataFlowInstance.resetLocation()
            this.zoomRadio = 1
            this.$bkMessage({
                message: gettext('自动编排完成'),
                theme: 'success'
            })
        },
        handleDeleteNode (event) {
            const node = event.target
            if (!node.classList.contains('common-icon-close-circle')) return
            const id = node.dataset.id
            const type = node.dataset.type
            if (this.canvasInstance && id && type) {
                this.dataFlowInstance.deleteLocation(id)
                this.$emit('onLocationChange', 'delete', {id, type})
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
        bottom: 0;
        left: 10px;
        width: 40px;
        color: $black;
        text-align: center;
        z-index: 4;
        .reset-position {
            margin: 0 auto;
            width: 34px;
            height: 34px;
            line-height: 34px;
            font-size: 18px;
            background: $whiteDefault;
            border: 1px solid #d6d6d6;
            border-radius: 2px;
            box-shadow: 0 0 2px rgba(0, 0, 0, 0.15);
            cursor: pointer;
            &:hover {
                color: $blueDefault;
            }
        }
        .zoom-area {
            margin: 10px auto;
            width: 34px;
            background: $whiteDefault;
            border: 1px solid #d6d6d6;
            border-radius: 2px;
            box-shadow: 0 0 2px rgba(0, 0, 0, 0.15);
            .zoom-in, .zoom-out {
                padding: 10px 0;
                font-size: 20px;
                cursor: pointer;
                &:hover {
                    color: $blueDefault;
                }
            }
            .zoom-out {
                padding-top: 0;
                &:hover {
                    .minus {
                        border-color: $blueDefault;
                    }
                }
            }
            .minus {
                display: inline-block;
                width: 8px;
                height: 0;
                border-bottom: 1px solid $black;
            }
        }
    }
}
</style>


