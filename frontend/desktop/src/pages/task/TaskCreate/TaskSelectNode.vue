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
            <div
                v-if="isSchemeShow"
                :class="[
                    'scheme-right-header',
                    { 'scheme-toggle-right-header': !showPanel }
                ]">
                <div class="scheme-combine-shape" @click="togglePanel">
                    <i class="common-icon-paper" v-bk-tooltips="{
                        content: i18n.schema,
                        placements: ['top']
                    }"></i>
                </div>
            </div>
            <div class="node-select-scheme" v-if="isSchemeShow && showPanel">
                <div class="scheme-title">
                    <span> {{i18n.schemaList}}</span>
                </div>
                <div class="scheme-header">
                    <div class="scheme-form" v-if="taskActionShow">
                        <bk-input
                            v-model="schemeName"
                            v-validate="schemeNameRule"
                            name="schemeName"
                            class="bk-input-inline"
                            :clearable="true"
                            :placeholder="i18n.schemaName">
                        </bk-input>
                        <bk-button theme="success" @click="onAddScheme">{{i18n.affirm}}</bk-button>
                        <bk-button @click="onCancelScheme">{{i18n.actionCancel}}</bk-button>
                        <span v-if="errors.has('schemeName')" class="common-error-tip error-msg">{{ errors.first('schemeName') }}</span>
                    </div>
                    <bk-button theme="primary" v-else :class="['save-scheme-btn', { 'disabled-btn': isPreviewMode }]" @click="onShowSchemeDialog">{{ i18n.newSchema }}</bk-button>
                </div>
                <div class="scheme-content">
                    <ul class="schemeList">
                        <li
                            v-for="item in taskScheme"
                            :class="{
                                'scheme-item': true,
                                'selected': item.id === selectedScheme && lastSelectSchema === item.id
                            }"
                            :key="item.id"
                            @click="onSelectScheme(item.id)">
                            <a class="scheme-name" :title="item.name">{{item.name}}</a>
                            <i class="bk-icon icon-close-circle-shape" @click.stop="onDeleteScheme(item.id)"></i>
                        </li>
                    </ul>
                </div>
                <div class="scheme-preview-mode">
                    <div class="scheme-header-division-line scheme-header-division-line-last"></div>
                    <div class="preview-mode-switcher">
                        <span>
                            {{i18n.previewMode}}
                        </span>
                        <bk-switcher size="small" v-model="isPreviewMode" @change="onChangePreviewNode"></bk-switcher>
                    </div>
                </div>
            </div>
            <pipelineCanvas
                v-if="!loading && !isPreviewMode"
                ref="pipelineCanvas"
                :preview-data-loading="previewDataLoading"
                :is-menu-bar-show="false"
                :is-config-bar-show="false"
                :is-edit="false"
                :is-select-node="isSchemeShow"
                :is-select-all-node="isSelectAllNode"
                :canvas-data="canvasData"
                @onToggleAllNode="onToggleAllNode">
            </pipelineCanvas>
            <NodePreview
                v-else
                ref="nodePreview"
                :preview-data-loading="previewDataLoading"
                :canvas-data="formatCanvasData(previewData)"
                :preview-bread="previewBread"
                :is-select-node="isSchemeShow"
                :is-select-all-node="isSelectAllNode"
                :is-preview-mode="isPreviewMode"
                @onNodeClick="onNodeClick"
                @onSelectSubflow="onSelectSubflow">
            </NodePreview>
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
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import PipelineCanvas from '@/components/common/PipelineCanvas/index.vue'
    import NodePreview from '@/pages/task/NodePreview.vue'
    import formatPositionUtils from '@/utils/formatPosition.js'
    export default {
        name: 'TaskSelectNode',
        components: {
            PipelineCanvas,
            NodePreview
        },
        props: ['cc_id', 'template_id', 'common', 'excludeNode', 'entrance'],
        data () {
            return {
                i18n: {
                    schemaList: gettext('执行方案列表'),
                    newSchema: gettext('新建'),
                    all: gettext('全选'),
                    affirm: gettext('保存'),
                    cancel: gettext('取消全选'),
                    actionCancel: gettext('取消'),
                    next: gettext('下一步'),
                    save: gettext('执行方案保存'),
                    schemaName: gettext('方案名称'),
                    previewMode: gettext('预览模式：'),
                    schema: gettext('执行方案')
                },
                loading: true,
                bkMessageInstance: null,
                isSubmit: false,
                isDelete: false,
                showPanel: true,
                selectedNodes: [],
                selectedScheme: '',
                schemeName: '',
                schemeNameRule: {
                    required: true,
                    max: STRING_LENGTH.SCHEME_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
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
                taskName: '',
                pipelineData: '',
                isPreview: false,
                lastSelectSchema: '',
                allSelectedNode: [],
                isSelectAllNode: true,
                taskActionShow: false
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'locations': state => state.template.location,
                'lines': state => state.template.line,
                'constants': state => state.template.constants,
                'gateways': state => state.template.gateways,
                'taskScheme': state => state.task.taskScheme,
                'app_id': state => state.app_id,
                'viewMode': state => state.view_mode
            }),
            canvasData () {
                const branchConditions = {}
                let mode
                for (const gKey in this.gateways) {
                    const item = this.gateways[gKey]
                    if (item.conditions) {
                        branchConditions[item.id] = Object.assign({}, item.conditions)
                    }
                }
                if (this.viewMode === 'appmaker') {
                    mode = 'selectDisabled'
                } else {
                    mode = 'select'
                }
                return {
                    lines: this.lines,
                    locations: this.locations.map(item => {
                        return { ...item, mode, checked: true }
                    }),
                    branchConditions
                }
            },
            isSchemeShow () {
                return this.viewMode !== 'appmaker' && this.locations.some(item => item.optional)
            },
            isCommonProcess () {
                return Number(this.$route.query.common) === 1
            }
        },
        mounted () {
            this.getTemplateData()
        },
        methods: {
            ...mapActions('template/', [
                'loadTemplateData',
                'saveTemplateData'
            ]),
            ...mapActions('task/', [
                'loadTaskScheme',
                'createTaskScheme',
                'deleteTaskScheme',
                'getSchemeDetail',
                'loadPreviewNodeData'
            ]),
            ...mapActions('appmaker/', [
                'loadAppmakerDetail'
            ]),
            ...mapMutations('template/', [
                'setTemplateData'
            ]),
            ...mapMutations('task/', [
                'setTaskScheme'
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
                    const templateData = await this.loadTemplateData(data)
                    this.version = templateData.version
                    this.taskName = templateData.name
                    const schemeData = await this.loadTaskScheme({ 'cc_id': this.cc_id, 'template_id': this.template_id, 'isCommon': this.isCommonProcess })
                    if (this.viewMode === 'appmaker') {
                        const appmakerData = await this.loadAppmakerDetail(this.app_id)
                        const schemeId = Number(appmakerData.template_scheme_id)
                        schemeId && this.onSelectScheme(schemeId)
                    }
                
                    this.setTaskScheme(schemeData)
                    this.setTemplateData(templateData)
                    this.modifySelectedLocation()
                    this.allSelectedNode = this.selectedNodes
                    this.updateSelectedLocation()
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.loading = false
                }
            },
            /**
             * 面板是否显示
             */
            togglePanel () {
                this.showPanel = !this.showPanel
            },
            /**
             * 显示任务方案面板
             */
            onShowSchemeDialog () {
                if (!this.isPreviewMode) {
                    this.taskActionShow = true
                }
            },
            /**
             * 显示任务方案面板
             * @return {Array} nodeId  被选中的ID数组
             */
            getExcludeNode () {
                let canvasEl
                if (this.$refs.pipelineCanvas === undefined) {
                    canvasEl = this.$refs.nodePreview.$el
                } else {
                    canvasEl = this.$refs.pipelineCanvas.$el
                }
                const optionalNode = canvasEl.querySelectorAll('.node-checkbox input[type="checkbox"]')
                const nodeId = []
                Array.prototype.forEach.call(optionalNode, function (item) {
                    if (!item.checked) {
                        nodeId.push(item.dataset.id)
                    }
                })
                return nodeId
            },
            /**
             * 通过已选节点数据，获取排除节点的数组
             */
            getExcludeNodeBySelectId (data) {
                const excludeNode = []
                this.canvasData.locations.forEach(item => {
                    if (
                        this.isCanSelectNode(item)
                        && item.optional
                        && data.indexOf(item.id) === -1
                    ) {
                        excludeNode.push(item.id)
                    }
                })
                return excludeNode
            },
            /**
             * 添加方案
             */
            onAddScheme () {
                if (this.isSubmit) return
                const isSchemeNameExist = this.taskScheme.some(item => item.name === this.schemeName)
                if (isSchemeNameExist) {
                    errorHandler({ message: gettext('方案名称已存在') }, this)
                    return
                }
                this.isSubmit = true
                this.$validator.validateAll().then(async (result) => {
                    if (!result) {
                        this.isSubmit = false
                        return
                    }
                    const excludeNode = this.getExcludeNode()
                    const selectedNodes = []
                    this.canvasData.locations.forEach(item => {
                        if (this.isCanSelectNode(item)) {
                            if (excludeNode.indexOf(item.id) === -1) {
                                selectedNodes.push(item.id)
                            }
                        }
                    })
                    this.selectedNodes = selectedNodes.slice()
                    this.schemeName = this.schemeName.trim()
                    const scheme = {
                        cc_id: this.cc_id,
                        template_id: this.template_id,
                        name: this.schemeName,
                        data: JSON.stringify(selectedNodes),
                        isCommon: this.isCommonProcess
                    }
                    try {
                        const newScheme = await this.createTaskScheme(scheme)
                        const schemeData = await this.loadTaskScheme({
                            'cc_id': this.cc_id,
                            'template_id': this.template_id,
                            'isCommon': this.isCommonProcess
                        })
                        this.setTaskScheme(schemeData)
                        this.selectedScheme = newScheme.id
                        this.lastSelectSchema = newScheme.id
                        this.schemeName = ''
                        this.taskActionShow = false
                        this.$bkMessage({
                            message: gettext('方案添加成功'),
                            theme: 'success'
                        })
                    } catch (e) {
                        errorHandler(e, this)
                    } finally {
                        this.isSubmit = false
                    }
                })
            },
            /**
             * 更新选择节点
             */
            updateSelectedLocation () {
                const pipelineCanvas = this.$refs.pipelineCanvas
                this.canvasData.locations.forEach((item) => {
                    if (this.isCanSelectNode(item)) {
                        const checkState = this.selectedNodes.indexOf(item.id) > -1
                        this.$set(item, 'checked', checkState)
                        pipelineCanvas && pipelineCanvas.onUpdateNodeInfo(item.id, item)
                    }
                })
            },
            modifySelectedLocation () {
                const selectedNodes = []
                this.locations.forEach(item => {
                    if (
                        this.isCanSelectNode(item)
                        && this.excludeNode.indexOf(item.id) === -1
                    ) {
                        selectedNodes.push(item.id)
                    }
                })
                this.selectedNodes = selectedNodes
            },
            /**
             * 选择方案并进行切换更新选择的节点
             */
            async onSelectScheme (id) {
                this.selectedScheme = id
                if (this.lastSelectSchema === id) {
                    this.lastSelectSchema = ''
                    if (this.isPreviewMode) {
                        await this.getPreviewNodeData(this.template_id, true)
                    } else {
                        this.modifySelectedLocation()
                        this.updateSelectedLocation()
                    }
                } else {
                    this.lastSelectSchema = id
                    try {
                        const data = await this.getSchemeDetail({ id: id, isCommon: this.isCommonProcess })
                        this.selectedNodes = tools.deepClone(data.data)
                        const excludeNode = this.getExcludeNodeBySelectId(JSON.parse(this.selectedNodes))
                        this.$emit('setExcludeNode', excludeNode)
                        this.updateSelectedLocation()
                        if (this.isPreviewMode) {
                            await this.getPreviewNodeData(this.template_id, false, excludeNode)
                        }
                    } catch (e) {
                        errorHandler(e, this)
                    }
                }
            },
            /**
             * 删除方案
             */
            async onDeleteScheme (id) {
                if (this.isDelete) return
                this.isDelete = true
                try {
                    await this.deleteTaskScheme({ id: id, isCommon: this.isCommonProcess })
                    const schemeData = await this.loadTaskScheme({ 'cc_id': this.cc_id, 'template_id': this.template_id, isCommon: this.isCommonProcess })
                    this.setTaskScheme(schemeData)
                    this.$bkMessage({
                        message: gettext('方案删除成功'),
                        theme: 'success'
                    })
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.isDelete = false
                }
            },
            /**
             * 全选可选节点
             */
            onSelectAllNode () {
                const list = []
                this.canvasData.locations.forEach(item => {
                    if (this.isCanSelectNode(item)) {
                        item.checked = true
                        list.push(item.id)
                    }
                })
                this.selectedNodes = list
                this.updateSelectedLocation()
            },
            /**
             * 取消所有可选节点
             */
            onSelectNoneNode () {
                this.canvasData.locations.forEach(item => {
                    if (this.isCanSelectNode(item)) {
                        item.checked = false
                    }
                })
                this.selectedNodes = []
                this.updateSelectedLocation()
            },
            /**
             * 进入参数填写阶段，设置执行节点
             */
            async onGotoParamFill () {
                this.loading = true
                let excludeNode = []
                if (this.isPreviewMode) {
                    excludeNode = this.excludeNode
                } else {
                    excludeNode = this.getExcludeNode()
                }
                try {
                    if (!this.isPreview) {
                        await this.getPreviewNodeData(this.template_id)
                    }
                
                    this.$emit('setExcludeNode', excludeNode)
                    this.updateSelectedLocation()
                    this.$emit('setPreviewData', this.pipelineData)
                
                    this.loading = false
                    if (this.viewMode === 'appmaker') {
                        if (this.common) {
                            this.$router.push({ path: `/appmaker/${this.app_id}/newtask/${this.cc_id}/paramfill/`, query: { 'template_id': this.template_id, common: this.common } })
                        } else {
                            this.$router.push({ path: `/appmaker/${this.app_id}/newtask/${this.cc_id}/paramfill/`, query: { 'template_id': this.template_id } })
                        }
                    } else {
                        if (this.common) {
                            this.$router.push({ path: `/template/newtask/${this.cc_id}/paramfill/`, query: { template_id: this.template_id, common: this.common } })
                        } else {
                            if (this.entrance !== undefined) {
                                this.$router.push({ path: `/template/newtask/${this.cc_id}/paramfill/`, query: { template_id: this.template_id, entrance: this.entrance } })
                            } else {
                                this.$router.push({ path: `/template/newtask/${this.cc_id}/paramfill/`, query: { template_id: this.template_id } })
                            }
                        }
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            /**
             * 预览模式的点击事件
             * @params {Boolean} isPreview  是否是预览模式
             */
            onChangePreviewNode (isPreview) {
                if (isPreview) {
                    const excludeNode = this.getExcludeNode()
                    this.$emit('setExcludeNode', excludeNode)
                    this.isPreviewMode = true
                    this.previewBread.push({
                        data: this.template_id,
                        name: this.taskName
                    })
                    this.getPreviewNodeData(this.template_id)
                } else {
                    this.isPreviewMode = false
                    this.previewBread = []
                }
            },
            /**
             * 获取画布预览节点和全局变量表单项(接口已去掉未选择的节点、为使用的全局变量)
             * @params {String} templateId  模板 ID
             * @params {Boolean} isSubflow  是否为子流程预览
             */
            async getPreviewNodeData (templateId, isSubflow = false, inExcludeNode) {
                this.previewDataLoading = true
                this.isPreview = true
                let excludeNode
                try {
                    excludeNode = this.getExcludeNode()
                } catch (e) {
                    excludeNode = this.getExecuteNodeList()
                }
                excludeNode = isSubflow ? [] : (inExcludeNode || excludeNode)
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
                        // let compareNodeData = JSON.stringify(previewNodeData)
                        // while (true) {
                        //     this.clearUnnecessaryGateway(previewNodeData)
                        //     if (compareNodeData === JSON.stringify(previewNodeData)) {
                        //         break
                        //     }
                        //     compareNodeData = JSON.stringify(previewNodeData)
                        // }
                        const { line, location } = previewNodeData
                        if (formatPositionUtils.isLocationAllNode(location)) {
                            const data = formatPositionUtils.formatPosition(line, location)
                            previewNodeData['line'] = data['lines']
                            previewNodeData['location'] = data['locations']
                        }
                        this.previewData = previewNodeData
                        // 改变预览前的选择节点
                        this.canvasData.locations.forEach(item => {
                            // 先还原为全部选中
                            item.checked = true
                            if (this.isCanSelectNode(item) && !(item.id in previewNodeData.activities)) {
                                item.checked = false
                            }
                        })
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
             * 清空没有被选中的节点
             * @params {Object} previewNodeData  整个pipelineTree
             * @return {Object} previewNodeData  清空了需要使用的节点的pipelineTree
             */
            clearUnnecessaryGateway (previewNodeData) {
                const { line, location } = previewNodeData
                // 数据分组 用于获取线段的后置连线
                const group = []
                for (const nowLine of line) {
                    const sourceId = nowLine.source.id
                    const targetId = nowLine.target.id
                    if (group[sourceId]) {
                        group[sourceId].push(targetId)
                    } else {
                        group[sourceId] = [targetId]
                    }
                }
                location.forEach((nowLocation) => {
                    const { type, id } = nowLocation
                    if (type === 'parallelgateway' || type === 'branchgateway') {
                        // 用于判断是否是有需要删除的线和内容
                        const lineArray = []
                        // 检验Array的每一个项相同
                        group[id].forEach((targetId) => {
                            if (lineArray.indexOf(targetId) === -1) {
                                lineArray.push(targetId)
                            }
                        })
                        const lineArrayLength = lineArray.length
                        const deleteLocation = location.find(location => location.id === lineArray[0])
                        let deleteLocationType
                        if (deleteLocation !== undefined) {
                            deleteLocationType = deleteLocation.type
                        }
                        // 长度为1 需要删除节点和线段
                        if (lineArrayLength === 1 && deleteLocationType !== 'subflow' && deleteLocationType !== 'tasknode') {
                            // 汇聚网关的id
                            const convergegatewayId = group[id][0]
                            const convergegateway = location.find(location => location.id === convergegatewayId)
                            if (!convergegateway || convergegateway.type !== 'convergegateway') {
                                // 如果不是汇聚网关就不需要删除了
                                return
                            }
                            // 获取后置节点
                            const lastId = line.find((newLine) => newLine.source.id === convergegatewayId).target.id
                            // 将并行或分支网关的前一个节点连线线段和汇聚网关的下一个节点连接
                            const preId = line.find((newLine) => newLine.target.id === id).source.id
                            line.find((newLine) => newLine.source.id === preId && newLine.target.id === id).target.id = lastId
                            // 删除节点
                            while (true) {
                                // 并行网关的前节点
                                const frontLineSourceIndex = line.findIndex(item => item.source.id === id)
                                if (frontLineSourceIndex !== -1) {
                                    line.splice(frontLineSourceIndex, 1)
                                }
                                // 汇聚网关的后节点
                                const lastLineTargetIndex = line.findIndex(item => item.target.id === convergegatewayId)
                                if (lastLineTargetIndex !== -1) {
                                    line.splice(lastLineTargetIndex, 1)
                                }
                                // 汇聚网关的前节点
                                const lastLineSourceIndex = line.findIndex(item => item.source.id === convergegatewayId)
                                if (lastLineSourceIndex !== -1) {
                                    line.splice(lastLineSourceIndex, 1)
                                }
                            
                                if (frontLineSourceIndex === -1 && lastLineTargetIndex === -1 && lastLineSourceIndex === -1) {
                                    break
                                }
                            }
                            // 删除节点的内容
                            const lastLocationIndex = location.findIndex(item => item.id === convergegatewayId)
                            location.splice(lastLocationIndex, 1)
                            const frontLocationIndex = location.findIndex(item => item.id === id)
                            location.splice(frontLocationIndex, 1)
                        // 获取节点
                        } else {
                            // 可能需要删除空的连线
                            lineArray.forEach((newLocationId) => {
                                const deleteLocation = location.find((newLocation) => newLocation.id === newLocationId && newLocation.type === 'convergegateway')
                                if (deleteLocation) {
                                    for (const locationId of group[id]) {
                                        // 使用
                                        if (locationId === newLocationId) {
                                            const frontLineSourceIndex = line.findIndex(item => item.target.id === newLocationId && item.source.id === id)
                                            line.splice(frontLineSourceIndex, 1)
                                        }
                                    }
                                }
                            })
                        }
                    }
                })
                // 数据内容更新
                return Object.assign(previewNodeData, { line, location })
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
            /**
             * 格式化pipelineTree的数据，只输出一部分数据
             * @params {Object} data  需要格式化的pipelineTree
             * @return {Object} {lines（线段连接）, locations（节点默认都被选中）, branchConditions（分支条件）}
             */
            formatCanvasData (data) {
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
                        return { ...item, mode: 'preview', checked: true }
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
                return this.allSelectedNode.filter(item => {
                    return !this.selectedNodes.includes(item)
                })
            },
            onToggleAllNode (value) {
                this.isSelectAllNode = value
                if (value) {
                    this.onSelectAllNode()
                } else {
                    this.onSelectNoneNode()
                }
            },
            // 取消添加执行方案
            onCancelScheme () {
                this.schemeName = ''
                this.taskActionShow = false
            },
            isCanSelectNode (node) {
                return node.type === 'tasknode' || node.type === 'subflow'
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
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
    /deep/ .node-canvas {
        width: 100%;
        height: 100%;
        background: #e1e4e8;
        border-top: 1px solid #dcdee5;
    }
}
.node-select-scheme {
    position: absolute;
    top: 0;
    right: 56px;
    width: 420px;
    height: 100%;
    background: $whiteDefault;
    border-left: 1px solid $commonBorderColor;
    box-shadow: 0 0 8px rgba(0, 0, 0, 0.15);
    z-index: 4;
    transition: right 0.5s ease-in-out;
    .scheme-title {
        height: 35px;
        margin: 20px;
        border-bottom: 1px solid #cacecb;
    }
    .scheme-header {
        margin: 20px;
        .scheme-form {
            display: inline-block;
            input {
                width: 200px;
            }
        }
        .save-scheme-btn {
            width: 90px;
            height: 32px;
            line-height: 32px;
            background-color: #ffffff;
            border: 1px solid #c4c6cc;
            border-radius: 2px;
            color: #313238;
            font-size: 14px;
            font-weight: 400;
        }
        .disabled-btn {
            opacity: 0.3;
            cursor: not-allowed;
        }
        .base-input {
            height: 32px;
            line-height: 32px;
            padding-bottom: 2px;
        }
    }
    .scheme-content {
        height: calc(100% - 127px- 63px);
        overflow: hidden;
        overflow-y: auto;
        @include scrollbar;
        .scheme-item {
            margin: 0 20px;
            height: 42px;
            font-weight: 400;
            line-height: 42px;
            font-size: 14px;
            cursor: pointer;
            border-bottom: 1px solid #ebebeb;
            &:hover {
                margin: 0;
                padding: 0 20px;
                background-color: #f0f1f5;
                .icon-close-circle-shape {
                    opacity: 1;
                }
            }
            &.selected {
                margin: -1px 0 0 0;
                padding: 0 20px;
                background-color: #3a84ff;
                .scheme-name {
                    color: #ffffff;
                }
                .scheme-division-line {
                    background-color: #3a84ff;
                }
                .icon-close-circle-shape {
                    color: #ffffff;
                    opacity: 1;
                }
            }
            .scheme-name {
                display: inline-block;
                width: 240px;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
                color: #313238;
            }
            .icon-close-circle-shape {
                float: right;
                margin-top: 15px;
                margin-right: 5px;
                width: 12px;
                height: 12px;
                text-align: center;
                line-height: 12px;
                color: #cecece;
                opacity: 0;
                cursor: pointer;
            }
        }
        li:first-child {
            border-top: 1px solid $commonBorderColor;
        }
    }
    .scheme-preview-mode {
        position: relative;
        width: 420px;
        .scheme-header-division-line-last {
            margin: 0 25px 0 20px;
            border: 0;
            height: 1px;
            background-color:#cacedb;
        }
        .preview-mode-switcher {
            position: relative;
            top: 19px;
            left: 20px;
            span {
                font-size: 14px;
                font-weight: 400;
                color: #313238;
            }
        }
    }
}
.quick-select {
    position: absolute;
    top: 15px;
    left: 10px;
    z-index: 5;
}
.toggle-button {
    position: absolute;
    top: 0;
    left: -20px;
    width: 20px;
    height: 50px;
    line-height: 50px;
    color: $whiteDefault;
    background: $blueThinBg;
    text-align: center;
    cursor: pointer;
    &:hover {
        background: $blueDefault;
    }
    .common-icon-arrow-left {
        display: inline-block;
        &.arrow-right {
            transform: rotate(180deg);
        }
    }
}

.scheme-right-header {
    position: absolute;
    right: 0;
    float: right;
    width: 56px;
    background: #ffffff;
    border-left: 1px solid #cacedb;
    height: 100%;
    z-index: 5;
    .scheme-combine-shape {
        margin: 27px 0 0 12px;
        width: 32px;
        height: 32px;
        background-color: #525F77;
        border-radius:2px;
        text-align: center;
        line-height: 32px;
        cursor: pointer;
        .common-icon-paper {
            color: #ffffff;
        }
    }
}
.scheme-toggle-right-header {
    height: 86px;
    border: 1px solid #cacedb;
    border-top: 0px;
    .scheme-combine-shape {
        background-color: #ffffff;
        .common-icon-paper {
            color: #546a9e;
        }
    }
}
.disable-item {
    cursor: not-allowed;
    &:hover {
        background: inherit ;
    }
}
.scheme-name-wrapper {
    padding: 10px 0;
    label {
        float: left;
        margin-top: 6px;
        width: 100px;
        text-align: right;
    }
    .scheme-name-input {
        margin: 0 35px 0 120px;
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
.bk-input-inline {
    display: inline-block;
    width: 200px;
}
</style>
