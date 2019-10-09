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
    <div class="select-node-wrapper" v-bkloading="{ isLoading: loading, opacity: 1 }">
        <div class="canvas-content">
            <TemplateCanvas
                v-if="!loading && !isPreviewMode"
                ref="templateCanvas"
                :preview-data-loading="previewDataLoading"
                :show-palette="false"
                :editable="false"
                :is-node-check-open="isSchemeShow"
                :is-all-selected="isAllSelected"
                :is-show-select-all-tool="viewMode !== 'appmaker'"
                :canvas-data="canvasData"
                @onNodeCheckClick="onNodeCheckClick"
                @onToggleAllNode="onToggleAllNode">
            </TemplateCanvas>
            <NodePreview
                v-else
                ref="nodePreview"
                :preview-data-loading="previewDataLoading"
                :canvas-data="formatCanvasData('perview', previewData)"
                :preview-bread="previewBread"
                @onNodeClick="onNodeClick"
                @onSelectSubflow="onSelectSubflow">
            </NodePreview>
            <task-scheme
                :project_id="project_id"
                :template_id="template_id"
                :template-name="templateName"
                :is-scheme-show="isSchemeShow"
                :is-preview-mode="isPreviewMode"
                :selected-nodes="selectedNodes"
                :tpl-actions="tplActions"
                :tpl-operations="tplOperations"
                :tpl-resource="tplResource"
                @selectScheme="selectScheme"
                @togglePreviewMode="togglePreviewMode">
            </task-scheme>
        </div>
        <div class="action-wrapper" slot="action-wrapper">
            <bk-button
                class="next-button"
                @click="onGotoParamFill">
                {{ i18n.next }}
            </bk-button>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import tools from '@/utils/tools.js'
    import TaskScheme from './TaskScheme.vue'
    import TemplateCanvas from '@/components/common/TemplateCanvas/index.vue'
    import NodePreview from '@/pages/task/NodePreview.vue'

    export default {
        name: 'TaskSelectNode',
        components: {
            TaskScheme,
            TemplateCanvas,
            NodePreview
        },
        props: ['project_id', 'template_id', 'common', 'excludeNode', 'entrance'],
        data () {
            return {
                i18n: {
                    all: gettext('全选'),
                    cancel: gettext('取消全选'),
                    next: gettext('下一步')
                },
                loading: true,
                selectedNodes: [],
                allSelectableNodes: [],
                selectedScheme: '',
                isPreviewMode: false,
                previewDataLoading: false,
                version: '',
                previewBread: [],
                previewData: {
                    location: [],
                    line: [],
                    gateways: {},
                    constants: []
                },
                templateName: '',
                pipelineData: '',
                isPreview: false,
                isAllSelected: true,
                tplActions: [],
                tplOperations: [],
                tplResource: {}
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
                'viewMode': state => state.view_mode
            }),
            canvasData () {
                let mode = 'select'
                if (this.viewMode === 'appmaker') {
                    mode = 'selectDisabled'
                }
                return this.formatCanvasData(mode, this)
            },
            isSchemeShow () {
                return this.viewMode !== 'appmaker' && this.location.some(item => item.optional)
            },
            isCommonProcess () {
                return Number(this.$route.query.common) === 1
            }
        },
        created () {
            this.getTemplateData()
        },
        methods: {
            ...mapActions('template/', [
                'loadTemplateData',
                'saveTemplateData',
                'getLayoutedPipeline'
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
                this.loading = true
                try {
                    const data = {
                        templateId: this.template_id,
                        common: this.common
                    }
                    const selectedNodes = []
                    const templateData = await this.loadTemplateData(data)
                    this.tplActions = templateData.auth_actions
                    this.tplOperations = templateData.auth_operations
                    this.tplResource = templateData.auth_resource
                    this.version = templateData.version
                    this.templateName = templateData.name

                    if (this.viewMode === 'appmaker') {
                        const appmakerData = await this.loadAppmakerDetail(this.app_id)
                        const schemeId = Number(appmakerData.template_scheme_id)
                        schemeId && this.onSelectScheme(schemeId)
                    }
                    this.setTemplateData(templateData)
                    this.allSelectableNodes = this.location.filter(item => item.optional)
                    this.allSelectableNodes.forEach(item => {
                        if (this.excludeNode.indexOf(item.id) === -1) {
                            selectedNodes.push(item.id)
                        }
                    })
                    this.selectedNodes = selectedNodes
                    this.canvasData.locations.forEach(item => {
                        if (this.selectedNodes.indexOf(item.id) > -1) {
                            this.$set(item, 'checked', true)
                        }
                    })
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.loading = false
                }
            },
            /**
             * 获取画布预览节点和全局变量表单项(接口已去掉未选择的节点、未使用的全局变量)
             * @params {String} templateId  模板 ID
             * @params {Boolean} isSubflow  是否为子流程预览
             */
            async getPreviewNodeData (templateId, isSubflow = false, inExcludeNode) {
                this.previewDataLoading = true
                const excludeNode = isSubflow ? [] : this.getExcludeNode()
                const templateSource = this.common ? 'common' : 'business'
                const params = {
                    templateId: templateId,
                    excludeTaskNodesId: JSON.stringify(excludeNode),
                    common: this.common,
                    cc_id: this.cc_id,
                    template_source: templateSource,
                    version: this.version
                }
                try {
                    const resp = await this.loadPreviewNodeData(params)
                    if (resp.result) {
                        const previewNodeData = resp.data.pipeline_tree
                        const layoutedData = await this.getLayoutedPosition(previewNodeData)
                        previewNodeData['line'] = layoutedData.line
                        previewNodeData['location'] = layoutedData.location
                        this.previewData = previewNodeData

                        if (!isSubflow) {
                            this.pipelineData = tools.deepClone(previewNodeData)
                        }
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.previewDataLoading = false
                }
            },
            /**
             * 从接口获取编排后的画布数据
             * @params {Object} data pipeline_tree 数据
             */
            async getLayoutedPosition (data) {
                try {
                    const canvasEl = document.getElementsByClassName('canvas-wrapper')[0]
                    const width = canvasEl.offsetWidth
                    const res = await this.getLayoutedPipeline({ width, pipelineTree: data })
                    if (res.result) {
                        return res.data.pipeline_tree
                    } else {
                        errorHandler(res, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                }
            },
            /**
             * 进入参数填写阶段，设置执行节点
             */
            async onGotoParamFill () {
                this.loading = true
                const excludeNode = this.getExcludeNode()
                try {
                    if (!this.isPreviewMode) {
                        await this.getPreviewNodeData(this.template_id)
                    }
                
                    this.$emit('setExcludeNode', excludeNode)
                
                    this.loading = false
                    if (this.viewMode === 'appmaker') {
                        if (this.common) {
                            this.$router.push({ path: `/appmaker/${this.app_id}/newtask/${this.project_id}/paramfill/`, query: { 'template_id': this.template_id, common: this.common } })
                        } else {
                            this.$router.push({ path: `/appmaker/${this.app_id}/newtask/${this.project_id}/paramfill/`, query: { 'template_id': this.template_id } })
                        }
                    } else {
                        this.$router.push({
                            path: `/template/newtask/${this.project_id}/paramfill/`,
                            query: {
                                template_id: this.template_id,
                                common: this.common || undefined,
                                entrance: this.entrance
                            }
                        })
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            /**
             * 格式化pipelineTree的数据，只输出一部分数据
             * @params {Object} data  需要格式化的pipelineTree
             * @return {Object} {lines（线段连接）, locations（节点默认都被选中）, branchConditions（分支条件）}
             */
            formatCanvasData (mode, data) {
                const { line, location, gateways } = data
                const branchConditions = {}
                for (const gKey in gateways) {
                    const item = gateways[gKey]
                    if (item.conditions) {
                        branchConditions[item.id] = Object.assign({}, item.conditions)
                    }
                }
                return {
                    lines: line,
                    locations: location.map(item => {
                        return { ...item, mode }
                    }),
                    branchConditions
                }
            },
            /**
             * 更新画布信息，触发v-if重新渲染
             */
            updateCanvas () {
                this.loading = true
                this.previewDataLoading = true
                this.$nextTick(() => {
                    this.loading = false
                    this.previewDataLoading = false
                })
            },
            /**
             * 在没有画布时，获取执行节点
             */
            getExecuteNodeList () {
                return this.allSelectableNodes.filter(item => {
                    return !this.selectedNodes.includes(item)
                })
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
            },
            /**
             * 点击子流程节点，并进入新的canvas画面
             * @params {String} id  点击的子流程节点id
             */
            onNodeClick (id) {
                const activity = this.previewData.activities[id]
                if (!activity || activity.type !== 'SubProcess') {
                    return
                }
                const templateId = activity.template_id
                this.previewBread.push({
                    data: templateId,
                    name: activity.name
                })
                this.getPreviewNodeData(templateId, true)
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
            },
            /**
             * 点击预览模式下的面包屑
             * @params {String} id  点击的节点id（可能为父节点或其他子流程节点）
             * @params {Number} index  点击的面包屑的下标
             */
            onSelectSubflow (id, index) {
                if (id === this.template_id) {
                    this.previewData = this.pipelineData
                    this.updateCanvas()
                } else {
                    this.getPreviewNodeData(id, true)
                }
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
            /**
             * 选择执行方案
             */
            async selectScheme (scheme) {
                if (scheme === undefined) {
                    if (this.isPreviewMode) {
                        await this.getPreviewNodeData(this.template_id, true)
                    }
                } else {
                    try {
                        const data = await this.getSchemeDetail({ id: scheme, isCommon: this.isCommonProcess })
                        this.selectedNodes = JSON.parse(data.data)
                        const excludeNode = this.getExcludeNode()
                        this.$emit('setExcludeNode', excludeNode)
                        this.canvasData.locations.forEach(item => {
                            if (this.isSelectableNode(item.id)) {
                                const checked = this.selectedNodes.indexOf(item.id) > -1
                                this.$set(item, 'checked', checked)
                            }
                        })
                        if (this.isPreviewMode) {
                            await this.getPreviewNodeData(this.template_id, false, excludeNode)
                        }
                    } catch (e) {
                        errorHandler(e, this)
                    }
                }
            },
            togglePreviewMode (isPreview) {
                this.isPreviewMode = isPreview
                if (isPreview) {
                    const excludeNode = this.getExcludeNode()
                    this.$emit('setExcludeNode', excludeNode)
                    this.previewBread.push({
                        data: this.template_id,
                        name: this.templateName
                    })
                    this.getPreviewNodeData(this.template_id)
                } else {
                    this.previewBread = []
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';

.select-node-wrapper {
    height: calc(100% - 90px);
}
.canvas-content {
    position: relative;
    height: calc(100% -72px);
    min-height: 500px;
    border-bottom: 1px solid $commonBorderColor;
    overflow: hidden;
    /deep/ .jsflow .tool-panel-wrap {
        left: 40px;
    }
    .node-preview-wrapper {
        height: 100%;
    }
}
.next-button {
    width:140px;
    height:32px;
    line-height: 32px;
    margin-left: 40px;
    background-color: #2dcb56;
    border-radius:2px;
    border-color: #2dcb56;
    vertical-align: middle;
    /deep/ span {
        color: #ffffff;
        font-size: 14px;
    }
}
.action-wrapper {
    border-top: 1px solid #cacedb;
    background-color: #e1e4e8;
}
/deep/ .pipeline-canvas {
    .tool-wrapper {
        top: 19px;
        left: 40px;
    }
}
</style>
