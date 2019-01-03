/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="template-page" v-bkloading="{isLoading: templateDataLoading}">
        <div v-if="!templateDataLoading && !exception.code" class="pipeline-canvas-wrapper">
            <PipelineCanvas
                ref="pipelineCanvas"
                :singleAtomListLoading="singleAtomListLoading"
                :subAtomListLoading="subAtomListLoading"
                :canvasData="canvasData"
                :name="name"
                :cc_id="cc_id"
                :atomTypeList="atomTypeList"
                :searchAtomResult="searchAtomResult"
                @onChangeName="onChangeName"
                @onSaveTemplate="onSaveTemplate"
                @onSearchAtom="onSearchAtom"
                @onBackToList="onBackToList"
                @onNodeClick="onNodeClick"
                @onLabelBlur="onLabelBlur"
                @onLocationChange="onLocationChange"
                @onLineChange="onLineChange"
                @onLocationMoveDone="onLocationMoveDone">
            </PipelineCanvas>
            <NodeConfig
                ref="nodeConfig"
                v-if="isNodeConfigPanelShow"
                :template_id="template_id"
                :singleAtom="singleAtom"
                :subAtom="subAtom"
                :isSettingPanelShow="isSettingPanelShow"
                :isNodeConfigPanelShow="isNodeConfigPanelShow"
                :idOfNodeInConfigPanel="idOfNodeInConfigPanel"
                @hideConfigPanel="hideConfigPanel"
                @onUpdateNodeInfo="onUpdateNodeInfo">
            </NodeConfig>
            <GlobalVariables
                :businessInfoLoading="businessInfoLoading"
                :isTemplateConfigValid="isTemplateConfigValid"
                :isSettingPanelShow="isSettingPanelShow"
                @toggleSettingPanel="toggleSettingPanel"
                @onDeleteConstant="onDeleteConstant"
                @varibleDataChanged="varibleDataChanged"
                @onSelectCategory="onSelectCategory">
            </GlobalVariables>
            <bk-dialog
                :is-show.sync="isLeaveDialogShow"
                :quick-close="false"
                :ext-cls="'common-dialog'"
                :title="i18n.leave"
                width="400"
                padding="30px"
                @confirm="onLeaveConfirm"
                @cancel="onLeaveCancel">
                <div slot="content">{{ i18n.tips }}</div>
            </bk-dialog>
        </div>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapGetters, mapActions, mapMutations } from "vuex"
import moment from 'moment'
import { uuid } from '@/utils/uuid.js'
import tools from '@/utils/tools.js'
import { errorHandler } from '@/utils/errorHandler.js'
import PipelineCanvas from '@/components/common/PipelineCanvas/index.vue'
import NodeConfig from './NodeConfig.vue'
import GlobalVariables from './GlobalVariables.vue'
export default {
    name: 'TemplateEdit',
    components: {
        PipelineCanvas,
        NodeConfig,
        GlobalVariables
    },
    props: ['cc_id', 'template_id', 'type'],
    data () {
        return {
            i18n: {
                leave: gettext("离开页面"),
                tips: gettext("系统可能不会保存您所做的更改，确认离开？")
            },
            bkMessageInstance: null,
            exception: {},
            singleAtomListLoading: false,
            subAtomListLoading: false,
            businessInfoLoading: false,
            templateDataLoading: false,
            templateSaving: false,
            isTemplateConfigValid: true, // 模板基础配置是否合法
            isTemplateDataChanged: false,
            isSettingPanelShow: true,
            isNodeConfigPanelShow: false,
            isLeaveDialogShow: false,
            allowLeave: false,
            leaveToPath: '',
            idOfNodeInConfigPanel: '',
            subAtomGrouped: []
        }
    },
    computed: {
        ...mapState({
            'singleAtom': state => state.atomList.singleAtom,
            'subAtom': state => state.atomList.subAtom,
            'searchAtomResult': state => state.atomList.searchAtomResult,
            'atomConfig': state => state.atomForm.config,
            'name': state => state.template.name,
            'activities': state => state.template.activities,
            'locations': state => state.template.location,
            'lines': state => state.template.line,
            'constants': state => state.template.constants,
            'gateways': state => state.template.gateways,
            'businessBaseInfo': state => state.template.businessBaseInfo,
            'category': state => state.template.category
        }),
        ...mapGetters('atomList/',[
            'singleAtomGrouped'
        ]),
        atomTypeList () {
            const subAtomGrouped = tools.deepClone(this.subAtomGrouped)
            if (this.type !== 'new') {
                let theSameAtomIndex
                this.subAtomGrouped.some((group, groupIndex) => {
                    const inTheGroup = group.list.some((item, index) => {
                        if (item.id === Number(this.template_id)) {
                            theSameAtomIndex = index
                            return true
                        }
                    })
                    if (inTheGroup) {
                        subAtomGrouped[groupIndex].list.splice(theSameAtomIndex, 1)
                    }
                    return inTheGroup
                })
            }
            return {
                'tasknode': this.singleAtomGrouped,
                'subflow': subAtomGrouped
            }
        },
        canvasData () {
            const branchConditions = {}
            for (let gKey in this.gateways) {
                const item = this.gateways[gKey]
                if (item.conditions) {
                    branchConditions[item.id] = Object.assign({}, item.conditions)
                }
            }
            return {
                activities: this.activities,
                lines: this.lines,
                locations: this.locations.map(item => { return {...item, mode: 'edit'}}),
                branchConditions
            }
        }
    },
    created () {
        this.initTemplateData()
    },
    mounted () {
        this.getSingleAtomList()
        this.getBusinessBaseInfo()
        if (this.type === 'edit' || this.type === 'clone') {
            this.getTemplateData(this.template_id)
        } else {
            const name = 'new' + moment().format('YYYYMMDDHHmmss')
            this.setTemplateName(name)
        }
    },
    beforeDestroy () {
        this.resetTemplateData()
    },
    methods: {
        ...mapActions('atomList/', [
            'loadSingleAtomList',
            'loadSubAtomList'
        ]),
        ...mapActions('template/', [
            'loadBusinessBaseInfo',
            'loadTemplateData',
            'saveTemplateData'
        ]),
        ...mapActions('atomForm/', [
            'loadAtomConfig',
            'loadSubflowConfig'
        ]),
        ...mapMutations('atomList/', [
            'setSingleAtom',
            'setSubAtom',
            'searchAtom'
        ]),
        ...mapMutations('template/', [
            'initTemplateData',
            'resetTemplateData',
            'setBusinessBaseInfo',
            'setTemplateName',
            'setTemplateData',
            'setLocation',
            'setLocationXY',
            'setLine',
            'setActivities',
            'setGateways',
            'setStartpoint',
            'setEndpoint',
            'setBranchCondition'
        ]),
        ...mapMutations('atomForm/', [
            'setAtomConfig'
        ]),
        async getSingleAtomList () {
            this.singleAtomListLoading = true
            try {
                const data = await this.loadSingleAtomList()
                this.setSingleAtom(data)
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.singleAtomListLoading = false
            }
        },
        async getBusinessBaseInfo () {
            this.businessInfoLoading = true
            try {
                const data = await this.loadBusinessBaseInfo()
                this.setBusinessBaseInfo(data)
                this.getSubAtomList(this.cc_id)
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.businessInfoLoading = false
            }
        },
        async getSubAtomList (cc_id) {
            this.subAtomListLoading = true
            try {
                const data = await this.loadSubAtomList(cc_id)
                this.setSubAtom(data)
                this.handleSubflowGroup()
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.subAtomListLoading = false
            }
        },
        async getTemplateData () {
            this.templateDataLoading = true
            try {
                const data = await this.loadTemplateData(this.template_id)
                if (this.type === 'clone') {
                    data.name = data.name.slice(0, 24) + '_clone'
                }
                this.setTemplateData(data)
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.templateDataLoading = false
            }
        },
        async getSingleAtomConfig (location) {
            const atomType = location.atomId
            if ($.atoms[atomType]) {
                this.addSingleAtomActivities(location, $.atoms[atomType])
                return
            }
            this.atomConfigLoading = true
            try {
                await this.loadAtomConfig({atomType})
                this.setAtomConfig({atomType, configData: $.atoms[atomType]})
                this.addSingleAtomActivities(location, $.atoms[atomType])
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.atomConfigLoading = false
            }
        },
        async getSubflowConfig (location) { // get subflow constants and add node
            try {
                const subflowConfig = await this.loadSubflowConfig({id: location.atomId})
                const constants = tools.deepClone(subflowConfig.form)
                const activities = tools.deepClone(this.activities[location.id])
                activities.constants = constants || {}
                this.setActivities({type: 'edit', location: activities})
            } catch (e) {
                errorHandler(e, this)
            }
        },
        async saveTemplate () {
            this.templateSaving = true
            const template_id = this.type === 'edit' ? this.template_id : undefined
            try {
                const data = await this.saveTemplateData(template_id)
                this.$bkMessage({
                    message: gettext('保存成功'),
                    theme: 'success'
                })
                this.isTemplateDataChanged = false
                if (this.type !== 'edit') {
                    this.allowLeave = true
                    this.$router.push({path: `/template/edit/${this.cc_id}/`, query: {'template_id': data.template_id}})
                }
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.templateSaving = false
            }
        },
        addSingleAtomActivities (location, config) {
            const data = {}
            config.forEach(item => {
                let value = ''
                if (item.type === 'combine') {
                    value = {}
                }
                data[item.tag_code] = {
                    hook: false,
                    value
                }
            })
            const activities = tools.deepClone(this.activities[location.id])
            activities.component.data = data || {}
            this.setActivities({type: 'edit', location: activities})
        },
        // 子流程分组
        handleSubflowGroup () {
            const primaryData = this.subAtom
            const groups = []
            const atomGrouped = []
            this.businessBaseInfo.task_categories.forEach(item => {
                groups.push(item.value)
                atomGrouped.push({
                    type: item.value,
                    group_name: item.name,
                    group_icon: '',
                    list: []
                })
            })
            primaryData.forEach(item => {
                const type = item.category
                const index = groups.indexOf(type)
                if (index > -1) {
                    atomGrouped[index].list.push(item)
                }
            })

            this.subAtomGrouped = atomGrouped
        },
        toggleSettingPanel (isSettingPanelShow){
            this.isSettingPanelShow = isSettingPanelShow
        },
        showConfigPanel (id) {
            this.varibleDataChanged()
            this.isNodeConfigPanelShow = true
            this.idOfNodeInConfigPanel = id
        },
        hideConfigPanel () {
            this.isNodeConfigPanelShow = false
            this.idOfNodeInConfigPanel = ''
        },
        /**
         * 标识模板是否被编辑
         */
        varibleDataChanged () {
            this.isTemplateDataChanged = true
        },
        /**
         * 普通原子节点校验，不包括子流程节点
         * 校验项包含：原子类型，节点名称，输入参数
         * @return isAllValid {Boolean} 节点是否合法
         */
        validateAtomNode () {
            let isAllValid = true
            Object.keys(this.activities).forEach(id => {
                let isNodeValid = true
                const node = this.activities[id]
                if (node.type === 'ServiceActivity') {
                    if (!node.name) { // 节点名称为空
                        isNodeValid = false
                    }
                    if (node.component.code) {
                        if (!this.validateAtomInputForm(node.component)) {
                            isNodeValid = false // 输入参数校验不通过
                        }
                    } else {
                        isNodeValid = false // 节点原子类型为空
                    }
                }
                if (!isNodeValid) {
                    isAllValid = false
                    this.markInvalidNode(id)
                }
            })
            if (!isAllValid) {
                this.$bkMessage({
                    message: gettext('任务节点参数错误，请点击错误节点查看详情'),
                    theme: 'error'
                })
            }
            return isAllValid
        },
        // 校验输入参数是否满足原子配置文件校验规则
        validateAtomInputForm (component) {
            const { code, data } = component
            const config = this.atomConfig[code]
            if (!data) return false
            if (config) {
                return this.checkAtomData(config, data)
            }
            return true
        },
        // tag 表单校验
        checkAtomData (config, data) {
            let isValid = true
            config.forEach(item => {
                const { tag_code, type, attrs } = item
                const value = data[tag_code] && data[tag_code].value
                if (type === 'combine') {
                    if (!this.checkAtomData(attrs.children, value)) {
                        isValid = false
                    }
                } else {
                    if (attrs.validation && attrs.validation.length) {
                        attrs.validation.forEach(item => {
                            if (item.type === 'required') {
                                if (tools.isEmpty(value)) {
                                    isValid = false
                                }
                            }
                            if (item.type === 'regex') {
                                const reg = new RegExp(item.args)
                                if (!reg.test(value)) {
                                    isValid = false
                                }
                            }
                            if (item.type === 'custom') {
                                if (!/^\${[^${}]+}$/.test(value)) { // '${xxx}'格式的值不校验
                                    const validateInfo = item.args.call(this, value)
                                    if (!validateInfo.result) {
                                        isValid = false
                                    }
                                }
                            }
                        })
                    }
                }
            })
            return isValid
        },
        /**
         * 参数错误节点标记为红色
         */
        markInvalidNode (id) {
            this.onUpdateNodeInfo(id, {status: 'FAILED'})
        },
        /**
         * 节点搜索
         */
        onSearchAtom (data) {
            const payload = {
                ...data,
                exclude: this.type !== 'new' ? [Number(this.template_id)] : []
            }
            this.searchAtom(payload)
        },
        /**
         * 任务节点点击
         */
        onNodeClick (id) {
            const currentId = this.idOfNodeInConfigPanel
            const nodeType = this.locations.filter(item => {return item.id === id})[0].type
            if (nodeType === 'tasknode' || nodeType === 'subflow'){
                if (this.isNodeConfigPanelShow) {
                    this.$refs.nodeConfig.syncNodeDataToActivities().then(isValid => {
                        this.showConfigPanel(id)
                    })
                } else {
                    this.showConfigPanel(id)
                }
            }
        },
        // 分支网关失焦
        onLabelBlur (labelData) {
            this.varibleDataChanged()
            this.setBranchCondition(labelData)
        },
        onLocationChange (changeType, location) {
            this.setLocation({type: changeType, location})
            switch (location.type) {
                case 'tasknode':
                    if (changeType === 'add' && location.atomId) {  // drag new single node
                        this.setActivities({type: 'add', location})
                        this.getSingleAtomConfig(location)
                        return
                    }
                    if (changeType === 'delete') {
                        this.hideConfigPanel()
                    }
                    this.setActivities({type: changeType, location})
                    break
                case 'subflow':
                    if (changeType === 'add' && location.atomId) { // drag new subflow node
                        this.setActivities({type: 'add', location})
                        this.getSubflowConfig(location)
                        return
                    }
                    if (changeType === 'delete') {
                        this.hideConfigPanel()
                    }
                    this.setActivities({type: changeType, location})
                    break
                case 'branchgateway':
                case 'parallelgateway':
                case 'convergegateway':
                    this.setGateways({type: changeType, location})
                    break
                case 'startpoint':
                    this.setStartpoint({type: changeType, location})
                    break
                case 'endpoint':
                    this.setEndpoint({type: changeType, location})
                    break
            }
        },
        onLineChange (changeType, line) {
            this.setLine({type: changeType, line})
        },
        onLocationMoveDone (location) {
            this.varibleDataChanged()
            this.setLocationXY(location)
        },
        onUpdateNodeInfo (id, data) {
            this.$refs.pipelineCanvas.onUpdateNodeInfo(id, data)
        },
        onDeleteConstant (key) {
            this.varibleDataChanged()
            if (this.isNodeConfigPanelShow) {
                const constant = this.constants[key]
                this.$refs.nodeConfig.onDeleteConstant(constant)
            }
        },
        // 流程名称修改
        onChangeName (name) {
            this.varibleDataChanged()
            this.setTemplateName(name)
        },
        // 基础属性-->模板分类修改
        onSelectCategory (value) {
            if (value) {
                this.isTemplateConfigValid = true
            }
        },
        // 点击保存模板按钮回调
        onSaveTemplate () {
            if (this.templateSaving) return
            // 模板分类是否选择
            if (!this.category) {
                this.isTemplateConfigValid = false
                this.isSettingPanelShow = true
                return
            }
            
            if (this.isNodeConfigPanelShow) {
                this.$refs.nodeConfig.syncNodeDataToActivities().then((isValid) => {
                    if (!isValid) return
                    this.onCheckNodeAndSaveTemplate()
                })
            } else {
                this.onCheckNodeAndSaveTemplate()
            }
        },
        // 保存时校验节点配置
        onCheckNodeAndSaveTemplate () {
            // 节点配置是否错误
            const nodeWithErrors = document.querySelectorAll('.node-with-text.FAILED')
            if (nodeWithErrors && nodeWithErrors.length) {
                this.templateSaving = false
                errorHandler({message: gettext('任务节点参数错误，请点击错误节点查看详情')}, this)
                return
            }
            const isAllNodeValid = this.validateAtomNode()

            if (isAllNodeValid) {
                this.saveTemplate()
            }
        },
        onBackToList () {
            this.$router.push({path: `/template/home/${this.cc_id}/`})
        },
        onLeaveConfirm () {
            this.allowLeave = true
            this.$router.push({path: this.leaveToPath})
        },
        onLeaveCancel () {
            this.allowLeave = false
            this.leaveToPath = ''
            this.isLeaveDialogShow = false
        }
    },
    beforeRouteLeave (to, from, next) { // leave or reload page
        if (this.allowLeave || !this.isTemplateDataChanged) {
            next()
        } else {
            this.leaveToPath = to.path
            this.isLeaveDialogShow = true
        }
    }
}
</script>
<style lang="scss" scoped>
    @import '../../../scss/config.scss';
    .template-page {
        position: relative;
        min-width: $minWidth;
        min-height: 600px;
        height: calc(100% - 60px);
        overflow: hidden;
    }
    .pipeline-canvas-wrapper {
        height: 100%;
    }
</style>

