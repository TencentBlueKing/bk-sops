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
    <div class="select-node-wrapper" :class="{ 'edit-scheme-mode': isEditSchemeMode }" v-bkloading="{ isLoading: templateLoading, opacity: 1, zIndex: 100 }">
        <div class="canvas-content">
            <TemplateCanvas
                v-if="!isPreviewMode && !templateLoading"
                ref="templateCanvas"
                :preview-data-loading="previewDataLoading"
                :show-palette="false"
                :editable="false"
                :is-node-check-open="isSchemeShow"
                :is-all-selected="isAllSelected"
                :is-show-select-all-tool="isSelectAllShow"
                :canvas-data="canvasData"
                :node-variable-info="nodeVariableInfo"
                @onTogglePerspective="onTogglePerspective"
                @onExportScheme="onExportScheme"
                @onNodeCheckClick="onNodeCheckClick"
                @onToggleAllNode="onToggleAllNode">
            </TemplateCanvas>
            <NodePreview
                v-else-if="isPreviewMode"
                ref="nodePreview"
                :preview-data-loading="previewDataLoading"
                :canvas-data="previewCanvasData"
                :preview-bread="previewBread"
                :preview-data="previewData"
                :common="common"
                @onNodeClick="onNodeClick"
                @onSelectSubflow="onSelectSubflow">
            </NodePreview>
            <!--模板详情加载完成后再打开执行方案面板-->
            <component
                v-if="!templateLoading"
                :is="schemeTemplate"
                ref="taskScheme"
                :project_id="project_id"
                :template_id="template_id"
                :template-name="templateName"
                :is-scheme-show="isSchemeShow"
                :view-mode="viewMode"
                :is-scheme-editable="viewMode !== 'appmaker'"
                :is-preview-mode="isPreviewMode"
                :is-common-process="isCommonProcess"
                :selected-nodes="selectedNodes"
                :ordered-node-data="orderedNodeData"
                :tpl-actions="tplActions"
                :appmaker-scheme-id="appmakerSchemeId"
                :selected-scheme="selectedScheme"
                :is-step-change="isStepChange"
                @updateSelectedNodes="updateSelectedNodes"
                @onImportTemporaryPlan="onImportTemporaryPlan"
                @onExportScheme="onExportScheme"
                @importTextScheme="importTextScheme"
                @togglePreviewMode="togglePreviewMode" />
        </div>
        <div class="action-wrapper" slot="action-wrapper" v-if="!isEditSchemeMode">
            <bk-button
                theme="primary"
                class="next-button"
                data-test-id="createTask_form_nextStep"
                @click="onGotoParamFill">
                {{ $t('下一步') }}
            </bk-button>
            <bk-button
                v-if="viewMode !== 'appmaker'"
                class="preview-button"
                data-test-id="createTask_form_togglePreview"
                @click="togglePreviewMode(!isPreviewMode)">
                {{ isPreviewMode ? $t('关闭预览') : $t('预览')}}
            </bk-button>
        </div>
        <bk-sideslider
            :is-show="isEditSchemeShow"
            :width="800"
            :quick-close="true"
            :before-close="onCloseEditScheme">
            <div slot="header">
                <span class="title-back" @click="onCloseEditScheme">{{$t('执行方案')}}</span>
                >
                <span>{{ isEditSchemeMode ? $t('导入选择节点') : $t('临时方案') }}</span>
            </div>
            <edit-scheme
                ref="editScheme"
                slot="content"
                :is-show.sync="isEditSchemeShow"
                :ordered-node-data="orderedNodeData"
                @importTextScheme="importTextScheme">
            </edit-scheme>
        </bk-sideslider>
    </div>
</template>
<script>
    import { mapState, mapMutations, mapActions } from 'vuex'
    import * as XLSX from 'xlsx'
    import TaskScheme from './TaskScheme.vue'
    import EditTaskScheme from './EditTaskScheme.vue'
    import TemplateCanvas from '@/components/common/TemplateCanvas/index.vue'
    import NodePreview from '@/pages/task/NodePreview.vue'
    import EditScheme from './EditScheme.vue'
    import tplPerspective from '@/mixins/tplPerspective.js'
    import { formatCanvasData } from '@/utils/checkDataType'

    export default {
        components: {
            TaskScheme,
            EditTaskScheme,
            EditScheme,
            TemplateCanvas,
            NodePreview
        },
        mixins: [tplPerspective],
        props: {
            project_id: [String, Number],
            template_id: [String, Number],
            common: String,
            excludeNode: {
                type: Array,
                default: () => ([])
            },
            selectedScheme: {
                type: Array,
                default: () => ([])
            },
            entrance: String,
            isEditSchemeMode: {
                type: Boolean,
                default: false
            },
            isStepChange: {
                type: Boolean,
                default: true
            }
        },
        data () {
            return {
                selectedNodes: [], // 已选中节点
                allSelectableNodes: [], // 所有可选节点
                isAllSelected: true,
                isPreviewMode: false,
                isAppmakerHasScheme: true,
                appmakerSchemeId: '',
                version: '',
                previewBread: [],
                previewData: {
                    location: [],
                    line: [],
                    gateways: {},
                    constants: []
                },
                orderedNodeData: [],
                templateName: '',
                templateLoading: true,
                previewDataLoading: true,
                tplActions: [],
                isDefaultSchemeIng: false,
                isEditSchemeShow: false
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'location': state => state.template.location,
                'line': state => state.template.line,
                'constants': state => state.template.constants,
                'gateways': state => state.template.gateways,
                'taskScheme': state => state.task.taskScheme,
                'app_id': state => state.app_id,
                'viewMode': state => state.view_mode,
                'infoBasicConfig': state => state.infoBasicConfig
            }),
            canvasData () {
                return formatCanvasData('select', this)
            },
            previewCanvasData () {
                return formatCanvasData('preview', this.previewData)
            },
            isSelectAllShow () {
                return this.viewMode === 'app' && this.location.some(item => item.optional)
            },
            isSchemeShow () {
                if (this.location.some(item => item.optional)) {
                    return this.viewMode === 'appmaker' ? !this.isAppmakerHasScheme : true
                }
                return false
            },
            schemeTemplate () {
                return this.isEditSchemeMode ? 'EditTaskScheme' : 'TaskScheme'
            },
            isCommonProcess () {
                return Number(this.$route.query.common) === 1
            },
            loading () {
                return this.isPreviewMode ? (this.previewDataLoading || this.templateLoading) : this.templateLoading
            }
        },
        created () {
            if (this.viewMode === 'appmaker') {
                this.isPreviewMode = true
            }
            this.getTemplateData()
        },
        methods: {
            ...mapActions('template/', [
                'loadTemplateData'
            ]),
            ...mapActions('task/', [
                'getSchemeDetail',
                'loadPreviewNodeData'
            ]),
            ...mapActions('appmaker/', [
                'loadAppmakerDetail'
            ]),
            ...mapMutations('template/', [
                'setTemplateData'
            ]),
            /**
             * 获取模板数据，并设置至store中
             */
            async getTemplateData () {
                this.templateLoading = true
                try {
                    const data = {
                        templateId: this.template_id,
                        common: this.common
                    }
                    const templateData = await this.loadTemplateData(data)
                    this.tplActions = templateData.auth_actions
                    this.version = templateData.version
                    this.templateName = templateData.name
                    this.orderedNodeData = this.getOrderedNodeData(templateData)
                    this.setTemplateData(templateData)
                    this.allSelectableNodes = this.location.filter(item => item.optional)

                    if (this.viewMode === 'appmaker') {
                        const appmakerData = await this.loadAppmakerDetail(this.app_id)
                        const schemeId = appmakerData.template_scheme_id
                        this.previewBread = [{
                            id: this.template_id,
                            name: this.templateName,
                            version: this.version
                        }]
                        if (schemeId === '') {
                            this.isAppmakerHasScheme = false
                        } else {
                            this.appmakerSchemeId = schemeId
                        }
                    }
                } catch (e) {
                    if (e.status === 404) {
                        this.$router.push({ name: 'notFoundPage' })
                    }
                    console.log(e)
                } finally {
                    this.templateLoading = false
                }
            },
            /**
             * 获取画布预览节点和全局变量表单项(接口已去掉未选择的节点、未使用的全局变量)
             * @params {Number|String} templateId  模板 ID
             * @params {String} version  模板版本
             */
            async getPreviewNodeData (templateId, version) {
                this.previewDataLoading = true
                const excludeNodes = this.getExcludeNode()
                const params = {
                    templateId: Number(templateId),
                    excludeTaskNodesId: excludeNodes,
                    common: this.common,
                    version
                }
                try {
                    const resp = await this.loadPreviewNodeData(params)
                    if (resp.result) {
                        this.previewData = resp.data.pipeline_tree
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.previewDataLoading = false
                }
            },
            /**
             * 进入参数填写阶段，设置执行节点
             */
            async onGotoParamFill () {
                let hasSelectNode = !!this.selectedNodes.length
                hasSelectNode = hasSelectNode || Object.values(this.activities).some(item => !item.optional)
                if (!hasSelectNode) {
                    this.$bkMessage({
                        message: this.$t('请至少选择一个节点'),
                        theme: 'error'
                    })
                    return
                }
                // 记录已选中的执行方案
                const taskSchemeDom = this.$refs.taskScheme
                if (taskSchemeDom) {
                    const schemes = taskSchemeDom.schemeList.reduce((acc, cur) => {
                        if (cur.isChecked) {
                            acc.push(cur.id)
                        }
                        return acc
                    }, [])
                    this.$emit('setSelectedScheme', schemes)
                }

                const { type, task_id = undefined } = this.$route.query
                const url = {
                    name: 'taskCreate',
                    params: { project_id: this.project_id, step: 'paramfill' },
                    query: { template_id: this.template_id, common: this.common, entrance: this.entrance, task_id }
                }
                if (this.entrance === 'function') {
                    url.name = 'functionTemplateStep'
                }
                if (this.viewMode === 'appmaker') {
                    url.name = 'appmakerTaskCreate'
                }
                if (type) {
                    url.query.type = type
                }
                this.$router.push(url)
            },
            getOrderedNodeData (data) {
                const pipelineTree = JSON.parse(data.pipeline_tree)
                const fstLine = pipelineTree.start_event.outgoing
                const orderedData = []
                const passedNodes = []
                this.retrieveLines(pipelineTree, fstLine, orderedData, passedNodes)
                orderedData.sort((a, b) => a.level - b.level)
                return orderedData
            },
            /**
             * 根据节点连线遍历任务节点，返回按广度优先排序的节点数据
             * @param {Object} data 画布数据
             * @param {Array} lineId 连线ID
             * @param {Array} ordered 排序后的节点数据
             * @param {Array} passedNodes 遍历过的节点
             * @param {Number} level 任务节点与开始节点的距离
             *
             */
            retrieveLines (data, lineId, ordered, passedNodes, level = 0) {
                const { activities, gateways, flows } = data
                const currentNode = flows[lineId].target
                const activity = activities[currentNode]
                const gateway = gateways[currentNode]
                const node = activity || gateway

                if (node && !passedNodes.includes(node.id)) {
                    passedNodes.push(node.id)

                    if (activity) {
                        const isExistInList = ordered.find(item => item.id === activity.id)
                        if (!isExistInList) {
                            activity.level = level
                            ordered.push(activity)
                        }
                    }

                    const outgoing = Array.isArray(node.outgoing) ? node.outgoing : [node.outgoing]
                    // 分支网关
                    if (gateway) {
                        level += 1
                    }
                    outgoing.forEach((line, index, arr) => {
                        this.retrieveLines(data, line, ordered, passedNodes, level)
                    })
                }
            },
            onToggleAllNode (val) {
                this.isAllSelected = val
                this.canvasData.locations.forEach(item => {
                    if (this.isSelectableNode(item.id)) {
                        this.$set(item, 'checked', val)
                    }
                })
                const selectableNodes = this.allSelectableNodes.map(item => item.id)
                if (val) {
                    this.selectedNodes = selectableNodes
                } else {
                    this.selectedNodes = []
                }
                this.updateExcludeNodes()
                // 清空已选择的方案
                const taskSchemeDom = this.$refs.taskScheme
                taskSchemeDom && taskSchemeDom.schemeList.forEach(item => {
                    item.isChecked = false
                })
            },
            /**
             * 点击子流程节点，并进入新的canvas画面
             * @params {String} id  点击的子流程节点id
             */
            onNodeClick (id) {
                const activity = this.previewData.activities[id]
                if (this.viewMode === 'appmaker' || !activity || activity.type !== 'SubProcess') {
                    return
                }
                const { template_id, name, version } = activity
                this.previewBread.push({
                    id: template_id,
                    name,
                    version
                })
                this.getPreviewNodeData(template_id, activity.version)
            },
            /**
             * 选中节点
             */
            onNodeCheckClick (id, val) {
                this.canvasData.locations.some(item => {
                    if (item.id === id) {
                        this.$set(item, 'checked', val)
                        return true
                    }
                })
                if (!val) {
                    this.isAllSelected = false
                    this.selectedNodes = this.selectedNodes.filter(item => item !== id)
                } else {
                    if (this.selectedNodes.length === this.allSelectableNodes.length - 1) {
                        this.isAllSelected = true
                    }
                    this.selectedNodes.push(id)
                }
                this.updateExcludeNodes()
            },
            /**
             * 点击预览模式下的面包屑
             * @params {String} id  点击的节点id（可能为父节点或其他子流程节点）
             * @params {Number} index  点击的面包屑的下标
             */
            onSelectSubflow (id, version, index) {
                this.getPreviewNodeData(id, version)
                this.previewBread.splice(index + 1, this.previewBread.length)
            },
            getExcludeNode () {
                const nodes = []
                this.allSelectableNodes.filter(item => {
                    if (this.selectedNodes.indexOf(item.id) === -1) {
                        nodes.push(item.id)
                    }
                })
                return nodes
            },
            isSelectableNode (id) {
                return this.allSelectableNodes.findIndex(item => item.id === id) > -1
            },
            // 设置默认勾选值
            async updateSelectedNodes (selectNodes = [], isAll = false) {
                this.isAllSelected = isAll
                if (isAll) {
                    this.selectedNodes = this.allSelectableNodes
                        .filter(item => !this.excludeNode.includes(item.id))
                        .map(item => item.id)
                } else {
                    this.selectedNodes = selectNodes
                }
                this.updateDataAndCanvas()
            },
            // 跟新数据和画布
            updateDataAndCanvas () {
                this.updateExcludeNodes()
                this.canvasData.locations.forEach(item => {
                    if (this.isSelectableNode(item.id)) {
                        const checked = this.selectedNodes.indexOf(item.id) > -1
                        this.$set(item, 'checked', checked)
                    }
                })
                if (this.isPreviewMode) {
                    this.getPreviewNodeData(this.template_id, this.version)
                }
            },
            // 临时方案
            importTextScheme (selectedNodes) {
                this.selectedNodes = selectedNodes.slice(0)
                this.updateExcludeNodes()
                this.canvasData.locations.forEach(item => {
                    if (this.isSelectableNode(item.id)) {
                        const checked = this.selectedNodes.indexOf(item.id) > -1
                        this.$set(item, 'checked', checked)
                    }
                })
                if (this.isPreviewMode) {
                    this.getPreviewNodeData(this.template_id, this.version)
                }
            },
            // 临时方案
            onImportTemporaryPlan () {
                this.isEditSchemeShow = true
            },
            // 导出当前方案
            onExportScheme () {
                window.reportInfo({
                    page: 'taskSelectNode',
                    zone: 'exportCanvas',
                    event: 'click'
                })
                const text = []
                this.orderedNodeData.forEach(item => {
                    const { stage_name, name, optional } = item
                    const status = optional ? (this.excludeNode.includes(item.id) ? 0 : 1) : 2
                    text.push([`${stage_name === '' ? '' : stage_name + '：'}${name} ${status}`])
                })
                const wsName = 'task_scheme'
                const wb = XLSX.utils.book_new()
                const ws = XLSX.utils.aoa_to_sheet(text)
                XLSX.utils.book_append_sheet(wb, ws, wsName)
                XLSX.writeFile(wb, `bk_sops_tpl_task_scheme_${+new Date()}.xlsx`)
            },
            togglePreviewMode (isPreview) {
                this.isPreviewMode = isPreview
                if (isPreview) {
                    this.previewBread.push({
                        id: this.template_id,
                        name: this.templateName,
                        version: this.version
                    })
                    this.getPreviewNodeData(this.template_id, this.version)
                } else {
                    this.previewBread = []
                }
                this.$emit('togglePreviewMode', isPreview)
            },
            updateExcludeNodes () {
                const excludeNodes = this.getExcludeNode()
                this.$emit('setExcludeNode', excludeNodes)
            },
            onCloseEditScheme () {
                const editScheme = this.$refs.editScheme
                const isEqual = editScheme.judgeDataEqual()
                if (isEqual) {
                    this.isEditSchemeShow = false
                } else {
                    this.$bkInfo({
                        ...this.infoBasicConfig,
                        confirmFn: () => {
                            this.isEditSchemeShow = false
                        }
                    })
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';

.select-node-wrapper {
    flex: 1;
}
.edit-scheme-mode {
    .canvas-content {
        height: 100%;
    }
}
.canvas-content {
    position: relative;
    height: calc(100% - 72px);
    min-height: 500px;
    overflow: hidden;
    ::v-deep .jsflow {
        background: #f5f7fa;
        .tool-panel-wrap {
            left: 40px;
        }
    }
    .node-preview-wrapper {
        height: 100%;
    }
}
::v-deep .pipeline-canvas {
    .tool-wrapper {
        top: 19px;
        left: 40px;
    }
}
.action-wrapper {
    padding-left: 40px;
    height: 72px;
    line-height: 72px;
    border-top: 1px solid #cacedb;
    background-color: #ffffff;
    .next-button {
        width: 140px;
    }
}
.title-back {
    color: #3a84ff;
    cursor: pointer;
}
</style>
