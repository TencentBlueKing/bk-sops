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
    <bk-sideslider
        :is-show="true"
        :width="800"
        :quick-close="true"
        :before-close="closeTab">
        <div class="setting-header" slot="header">
            <span :class="[variableData ? 'active' : '']" @click="onBackToList">{{ $t('全局变量') }}</span>
            <span v-if="variableData"> > {{ variableData.source_type !== 'system' && variableData.source_type !== 'project' ? (variableData.key ? $t('编辑') : $t('新建')) : $t('查看') }}</span>
            <div
                v-if="!common"
                class="manager-project-variable-btn mr5"
                data-test-id="templateEdit_form_managerVariable"
                @click="onManagerProjectVariable">
                <span :class="['manager-item', { 'r30': isViewMode }]">{{ $t('管理项目变量') }}</span>
            </div>
            <div
                v-if="!isViewMode"
                class="process-project-variable-btn"
                data-test-id="templateEdit_form_variableProcessing"
                @click="quickOperateVariableVisable = true">
                <div class="manager-item">{{ $t('变量快捷处理') }}
                    <quick-operate-variable
                        v-if="quickOperateVariableVisable"
                        :variable-list="variableList"
                        @closePanel="quickOperateVariableVisable = false">
                    </quick-operate-variable>
                </div>
            </div>
            <div id="var-desc">
                <div class="tips-item">
                    <h4>{{ $t('属性：') }}</h4>
                    <p>
                        {{ $t('"来源/是否显示"格式，来源是输入类型') }}
                        <i class="common-icon-show-left" style="color: #219f42"></i>
                        {{ $t('表示变量来自用户添加的变量或者标准插件/子流程节点输入参数引用的变量，来源是输出类型') }}
                        <i class="common-icon-hide-right" style="color: #de9524"></i>
                        {{ $t('表示变量来自标准插件/子流程节点输出参数引用的变量；是否显示表示该变量在新建任务填写参数时是否展示给用户，') }}
                        <i class="common-icon-eye-show" style="color: #219f42;vertical-align: middle;"></i>
                        {{ $t('表示显示，') }}
                        <i class="common-icon-eye-hide" style="color: #de9524;vertical-align: middle;"></i>
                        {{ $t('表示隐藏，输出类型的变量一定是隐藏的。') }}
                    </p>
                </div>
                <div class="tips-item">
                    <h4>{{ $t('输出：') }}</h4>
                    <p>{{ $t('表示该变量会作为该流程模板的输出参数，在被其他流程模板当做子流程节点时可以引用。') }}</p>
                </div>
                <div class="tips-item">
                    <h4>{{ $t('模板预渲染：') }}</h4>
                    <p>
                        {{ $t('模板预渲染为“是”时，任务会在执行前将变量中的 MAKO 段进行渲染，') }}
                        {{ $t('而不是在第一个引用该变量的节点执行前才进行渲染；') }}
                        {{ $t('如果需要预渲染的变量引用了别的变量，') }}
                        {{ $t('那么被引用变量的预渲染也要设置为“是”，否则预渲染不生效。') }}
                    </p>
                </div>
            </div>
        </div>
        <div class="global-variable-panel" slot="content">
            <div v-show="!variableData" :class="{ 'is-hidden': variableData }">
                <div class="add-variable">
                    <bk-button
                        theme="primary"
                        :class="['add-variable-btn mr5', { 'scale0': isViewMode }]"
                        data-test-id="templateEdit_form_creatVariable"
                        @click="onAddVariable">
                        {{ $t('新建') }}
                    </bk-button>
                    <bk-button
                        theme="default"
                        :class="['clone-variable-btn mr5', { 'scale0': isViewMode }]"
                        data-test-id="templateEdit_form_cloneVariable"
                        @click="isVarCloneDialogShow = true">
                        {{ $t('跨流程克隆') }}
                    </bk-button>
                    <template v-if="deleteVarListLen">
                        <bk-button
                            theme="default"
                            class="delete-variable-btn"
                            data-test-id="templateEdit_form_deleteVariable"
                            @click="onDeleteVarList">
                            {{ $t('删除') }}
                        </bk-button>
                        <span class="delete-variable-txt">{{ $t('已选择x项', { num: deleteVarListLen }) }}</span>
                        <bk-button :text="true" class="f12" @click="deleteVarList = []">{{ $t('清空' )}}</bk-button>
                    </template>
                    <div class="toggle-system-var">
                        <bk-checkbox :value="isHideSystemVar" @change="onToggleSystemVar">{{ $t('隐藏系统变量') }}</bk-checkbox>
                    </div>
                    <i
                        class="common-icon-info"
                        v-bk-tooltips="{
                            allowHtml: true,
                            content: '#var-desc',
                            placement: 'bottom-end',
                            duration: 0,
                            width: 400
                        }">
                    </i>
                </div>
                <div class="global-variable-content" data-test-id="templateEdit_table_variableList">
                    <div class="variable-header clearfix">
                        <bk-checkbox v-if="!isViewMode && editVarList.length" :value="editVarList.length === deleteVarListLen" class="variable-checkbox" @change="onSelectAll">
                        </bk-checkbox>
                        <span class="col-name t-head">{{ $t('名称') }}</span>
                        <span class="col-key t-head">KEY</span>
                        <span class="col-cited t-head">
                            {{ $t('引用') }}
                            <i
                                class="common-icon-info global-variable-tootip quote-info"
                                v-bk-tooltips="{
                                    allowHtml: true,
                                    content: $t('直接引用全局变量的节点数量，点击数字查看引用详情'),
                                    placement: 'bottom-end',
                                    duration: 0,
                                    width: 200
                                }">
                            </i>
                        </span>
                        <span class="col-type t-head">
                            {{ $t('类型') }}
                            <thead-popover
                                :content-list="globalVarTypeList"
                                type="type"
                                @handleFilter="handleFilter">
                            </thead-popover>
                        </span>
                        <!-- 隐藏来源字段 -->
                        <!-- <span class="col-attributes t-head">
                            {{ $t('来源') }}
                            <thead-popover
                                :content-list="varAttrList"
                                type="attributes"
                                @handleFilter="handleFilter">
                            </thead-popover>
                        </span> -->
                        <span class="col-show t-head">
                            {{ $t('显示（入参）') }}
                            <thead-popover
                                :content-list="varShowList"
                                type="show"
                                @handleFilter="handleFilter">
                            </thead-popover>
                        </span>
                        <span class="col-output t-head">{{ $t('输出') }}</span>
                        <span class="col-operation t-head">{{ $t('操作') }}</span>
                        <span class="col-more t-head"></span>
                    </div>
                    <!-- 加一层div用来放bkLoading -->
                    <div v-bkloading="{ isLoading: varListLoading, zIndex: 10 }">
                        <div class="variable-list">
                            <draggable
                                class="variable-drag"
                                handle=".col-item-drag"
                                :list="variableList"
                                :disabled="isViewMode"
                                @end="onDragEnd($event)">
                                <variable-item
                                    v-for="constant in variableList"
                                    :key="constant.key"
                                    :outputed="outputs.indexOf(constant.key) > -1"
                                    :variable-data="constant"
                                    :variable-cited="variableCited"
                                    :variable-checked="!!(deleteVarList.find(item => item.key === constant.key))"
                                    :common="common"
                                    :is-view-mode="isViewMode"
                                    :new-clone-keys="newCloneKeys"
                                    @viewClick="viewClick"
                                    @onEditVariable="onEditVariable"
                                    @onDeleteVariable="onDeleteVariable"
                                    @onCloneVariable="onCloneVariable"
                                    @onChooseVariable="onChooseVariable"
                                    @onChangeVariableShow="onChangeVariableShow"
                                    @onChangeVariableOutput="onChangeVariableOutput"
                                    @onCitedNodeClick="onCitedNodeClick">
                                </variable-item>
                            </draggable>
                            <div v-if="variableList.length === 0" class="empty-variable-tips">
                                <NoData>
                                    <p>{{$t('无数据，请手动新增变量或者勾选标准插件参数自动生成')}}</p>
                                </NoData>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <variable-edit
                v-if="variableData"
                ref="variableEdit"
                :variable-data="variableData"
                :common="common"
                :is-view-mode="isViewMode"
                @setNewCloneKeys="setNewCloneKeys"
                @closeEditingPanel="closeEditingPanel"
                @onSaveEditing="onSaveEditing">
            </variable-edit>
            <variable-clone
                :is-var-clone-dialog-show="isVarCloneDialogShow"
                :var-type-list="varTypeList"
                :global-variable-list="variableList"
                @onCloneVarConfirm="onCloneVarConfirm"
                @onCloneVarCancel="isVarCloneDialogShow = false">
            </variable-clone>
        </div>
    </bk-sideslider>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import draggable from 'vuedraggable'
    import { mapMutations, mapState, mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import VariableEdit from './VariableEdit.vue'
    import VariableItem from './VariableItem.vue'
    import VariableClone from './VariableClone.vue'
    import TheadPopover from './TheadPopover.vue'
    import QuickOperateVariable from '../../../common/QuickOperateVariable.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'TabGlobalVariables',
        components: {
            VariableEdit,
            VariableItem,
            VariableClone,
            TheadPopover,
            draggable,
            NoData,
            QuickOperateVariable
        },
        props: {
            common: [String, Number],
            isViewMode: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const varAttrList = [
                {
                    name: i18n.t('全选'),
                    checked: false,
                    code: 'all'
                }, {
                    name: i18n.t('输入'),
                    checked: false,
                    code: 'input'
                }, {
                    name: i18n.t('输出'),
                    checked: false,
                    code: 'output'
                }
            ]
            const varShowList = [
                {
                    name: i18n.t('全选'),
                    checked: false,
                    code: 'all'
                }, {
                    name: i18n.t('是'),
                    checked: false,
                    code: 'show'
                }, {
                    name: i18n.t('否'),
                    checked: false,
                    code: 'hide'
                }
            ]
            return {
                isHideSystemVar: false,
                variableList: [], // 变量列表，包含系统内置变量和用户变量
                cloneVariableList: [],
                varListLoading: false,
                varTypeList: [],
                globalVarTypeList: [],
                checkedTypeList: [],
                varAttrList,
                checkedAttrList: [],
                varShowList,
                checkedShowList: [],
                variableData: null, // 编辑中的变量
                deleteVarKey: '',
                variableCited: {}, // 全局变量被任务节点、网关节点以及其他全局变量引用情况
                deleteVarList: [], // 批量删除变量
                quickOperateVariableVisable: false,
                isVarCloneDialogShow: false,
                newCloneKeys: [] // 新增/跨流程克隆的变量key值
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'gateways': state => state.template.gateways,
                'outputs': state => state.template.outputs,
                'constants': state => state.template.constants,
                'internalVariable': state => state.template.internalVariable
            }),
            deleteVarListLen () {
                return this.deleteVarList.length
            },
            editVarList () {
                return this.variableList.filter(item => item.source_type !== 'system' && item.source_type !== 'project')
            }
        },
        watch: {
            constants () {
                // 增加、删除变量后，更新变量列表
                this.setVariableList()
            },
            internalVariable () {
                this.setVariableList()
            }
        },
        created () {
            this.setVariableList()
            this.getVariableCitedData()
        },
        methods: {
            ...mapActions('template', [
                'getVariableCite',
                'loadCustomVarCollection'
            ]),
            ...mapMutations('template/', [
                'editVariable',
                'deleteVariable',
                'setOutputs',
                'addVariable'
            ]),
            async getVariableCitedData () {
                try {
                    const data = {
                        activities: this.activities,
                        gateways: this.gateways,
                        constants: { ...this.internalVariable, ...this.constants }
                    }
                    const resp = await this.getVariableCite(data)
                    if (resp.result) {
                        this.variableCited = resp.data.defined
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            async setVariableList () {
                try {
                    this.varListLoading = true
                    const userVars = Object.keys(this.constants)
                        .map(key => tools.deepClone(this.constants[key]))
                        .sort((a, b) => a.index - b.index)
                    if (this.isHideSystemVar) {
                        this.variableList = [...userVars]
                    } else {
                        const sysVars = Object.keys(this.internalVariable)
                            .map(key => {
                                const values = tools.deepClone(this.internalVariable[key])
                                values.isSysVar = true
                                return values
                            }).sort((a, b) => b.index - a.index)
                        this.variableList = [...sysVars, ...userVars]
                    }
                    // 获取变量类型
                    await this.getVarTypeList()
                    // 克隆变量列表来进行过滤
                    this.cloneVariableList = tools.deepClone(this.variableList)
                    // 过滤
                    this.handleFilter()
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.varListLoading = false
                }
            },
            // 获取变量类型
            async getVarTypeList () {
                try {
                    if (!this.varTypeList.length) {
                        this.varTypeList = await this.loadCustomVarCollection()
                    }
                    const varTypeList = tools.deepClone(this.varTypeList)
                    const nodeCheckVarList = new Set()
                    const listData = this.variableList.reduce((acc, cur) => {
                        if (cur.key in this.internalVariable) {
                            const varInfo = this.internalVariable[cur.key]
                            this.$set(cur, 'type', varInfo.source_type === 'system' ? i18n.t('系统变量') : i18n.t('项目变量'))
                        } else {
                            const result = varTypeList.find(item => item.code === cur.custom_type && item.tag === cur.source_tag)
                            const checkTypeList = ['component_inputs', 'component_outputs']
                            if (result && !checkTypeList.includes(cur.source_type)) {
                                this.$set(cur, 'type', result.name)
                                result.checked = this.checkedTypeList.includes(cur.custom_type)
                                acc.push(result)
                            } else {
                                const name = cur.source_type === 'component_outputs' ? i18n.t('节点输出') : i18n.t('节点输入')
                                this.$set(cur, 'type', name)
                                nodeCheckVarList.add(cur.source_type)
                            }
                        }
                        return acc
                    }, [])
                    if (nodeCheckVarList.size) {
                        [...nodeCheckVarList].forEach(code => {
                            const name = code === 'component_outputs' ? i18n.t('节点输出') : i18n.t('节点输入')
                            listData.unshift({ checked: this.checkedTypeList.includes(code), name, code })
                        })
                    }
                    if (!this.isHideSystemVar) {
                        const internalVar = [
                            { checked: this.checkedTypeList.includes('system'), name: i18n.t('系统变量'), code: 'system' },
                            { checked: this.checkedTypeList.includes('project'), name: i18n.t('项目变量'), code: 'project' }
                        ]
                        listData.unshift(...internalVar)
                    }
                    listData.unshift({ checked: this.checkedTypeList.includes('all'), name: i18n.t('全部'), code: 'all' })
                    this.globalVarTypeList = [...new Set(listData)]
                } catch (e) {
                    console.log(e)
                }
            },
            // 过滤变量列表
            handleFilter (type, list) {
                if (type === 'type') {
                    this.checkedTypeList = list
                } else if (type === 'attributes') {
                    this.checkedAttrList = list
                } else if (type === 'show') {
                    this.checkedShowList = list
                }
                const checkObj = {
                    'custom_type': this.checkedTypeList,
                    'source_type': this.checkedAttrList,
                    'show_type': this.checkedShowList
                }
                const filterList = this.cloneVariableList.filter(item => {
                    let match = true
                    for (const [key, values] of Object.entries(checkObj)) {
                        if (values.length) {
                            const hasAll = values.includes('all')
                            if (hasAll) {
                                match = true
                            } else {
                                let str = ''
                                if (key === 'custom_type') {
                                    const isComponent = item.key in this.internalVariable
                                    if (isComponent) {
                                        const varInfo = this.internalVariable[item.key]
                                        str = varInfo.source_type === 'system' ? 'system' : 'project'
                                    } else {
                                        str = item[key] || item.source_type
                                    }
                                } else if (key === 'source_type') {
                                    const isInput = item.source_type !== 'component_outputs'
                                    str = isInput ? 'input' : 'output'
                                } else {
                                    str = item[key]
                                }
                                match = values.includes(str)
                            }
                        }
                        if (!match) break
                    }
                    return match
                })
                this.variableList = filterList || []
            },
            // 点击面包屑返回变量列表
            onBackToList () {
                if (this.variableData) {
                    this.closeEditingPanel()
                }
            },
            /**
             * 新增变量
             */
            onAddVariable () {
                this.variableData = {
                    custom_type: 'input',
                    desc: '',
                    form_schema: {},
                    index: Object.keys(this.constants).length + 1,
                    key: '',
                    name: '',
                    show_type: 'show',
                    source_info: {},
                    source_tag: 'input.input',
                    source_type: 'custom',
                    validation: '^.+$',
                    is_condition_hide: 'false',
                    pre_render_mako: false,
                    value: '',
                    version: 'legacy'
                }
                this.$emit('templateDataChanged')
            },
            // 点击跳转项目管理-管理项目变量
            onManagerProjectVariable () {
                const url = this.$router.resolve({
                    path: `/project/config/${this.$route.params.project_id}/`
                })
                window.open(url.href)
            },
            // 显示/隐藏系统变量
            onToggleSystemVar (val) {
                this.isHideSystemVar = val
                this.setVariableList()
            },
            // 变量拖拽，改变顺序
            onDragEnd (event) {
                const { newIndex, oldIndex } = event
                if (newIndex === oldIndex) {
                    return
                }
                const start = Math.min(newIndex, oldIndex)
                const end = Math.max(newIndex, oldIndex) + 1
                const delta = this.isHideSystemVar ? start : start - Object.keys(this.internalVariable).length
                const indexChangedVar = this.variableList.slice(start, end)

                indexChangedVar.forEach((item, index) => {
                    item.index = index + delta
                    if (item.key in this.internalVariable) return
                    this.editVariable({ key: item.key, variable: tools.deepClone(item) })
                })
            },
            viewClick (id) {
                this.$emit('viewClick', id)
                this.$emit('onCitedNodeClick', { group: 'activities', id })
            },
            /**
             * 打开编辑变量面板
             * @param {String} key 变量key值
             */
            onEditVariable (key) {
                const variableData = tools.deepClone(this.constants[key] || this.internalVariable[key])
                if (!('is_condition_hide' in variableData)) { // 添加自动隐藏默认值
                    variableData.is_condition_hide = 'false'
                }
                this.variableData = variableData
                this.newCloneKeys = []
            },
            onCitedNodeClick (data) {
                const { group, id } = data
                if (group === 'constants') {
                    this.onEditVariable(id)
                } else {
                    this.$emit('onCitedNodeClick', data)
                }
            },
            /**
             * 变量显示勾选
             */
            onChangeVariableShow ({ key, checked }) {
                const variableData = tools.deepClone(this.constants[key] || this.internalVariable[key])
                if (variableData) {
                    variableData.show_type = checked ? 'show' : 'hide'
                    this.editVariable({ key, variable: variableData })
                    this.$emit('templateDataChanged')
                }
            },
            /**
             * 变量输出勾选
             */
            onChangeVariableOutput ({ key, checked }) {
                const changeType = checked ? 'add' : 'delete'
                this.setOutputs({ changeType, key })
                this.$emit('templateDataChanged')
            },
            /**
             * 删除变量
             */
            onDeleteVariable (key) {
                this.deleteVarKey = key
                this.deleteVariable(this.deleteVarKey)
                this.deleteVarKey = ''
                this.$emit('templateDataChanged')
                this.getVariableCitedData() // 删除变量后更新引用数据
                this.$bkMessage({
                    theme: 'success',
                    message: i18n.t('变量') + i18n.t('删除成功！')
                })
            },
            onCloneVariable (data) {
                const variableData = tools.deepClone(data)
                variableData.source_info = {}
                variableData.key = ''
                variableData.index = Object.keys(this.constants).length + 1
                this.variableData = variableData
            },
            onChooseVariable (variable, isChecked) {
                if (isChecked) {
                    this.deleteVarList.push(variable)
                } else {
                    const index = this.deleteVarList.findIndex(item => item.key === variable.key)
                    if (index > -1) {
                        this.deleteVarList.splice(index, 1)
                    }
                }
            },
            onDeleteVarList () {
                let title = ''
                if (this.deleteVarListLen === 1) {
                    title = i18n.t('确认删除') + i18n.t('全局变量') + `"${this.deleteVarList[0].key}"?`
                } else {
                    title = i18n.t('确认删除所选的x个变量?', { num: this.deleteVarListLen })
                }
                this.$bkInfo({
                    title,
                    subTitle: i18n.t('若该变量被节点引用，请及时检查并更新节点配置'),
                    maskClose: false,
                    width: 450,
                    confirmLoading: true,
                    confirmFn: async () => {
                        await this.getVariableCitedData() // 删除变量后更新引用数据
                        this.deleteVarList.forEach(variableData => {
                            this.deleteVariable(variableData.key)
                        })
                        this.deleteVarList = []
                        this.$emit('templateDataChanged')
                    }
                })
            },
            // 编辑变量后点击保存
            onSaveEditing () {
                this.closeEditingPanel()
                this.$emit('templateDataChanged')
                this.getVariableCitedData() // 新增或者编辑变量后更新引用数据
            },
            // 关闭变量编辑面板
            closeEditingPanel () {
                this.variableData = null
            },
            // 关闭全局变量侧滑
            closeTab () {
                if (this.isViewMode || !this.variableData) {
                    this.$emit('closeTab')
                } else {
                    if (this.variableData.source_type === 'system') {
                        this.closeEditingPanel()
                        return
                    }
                    this.$refs.variableEdit.handleMaskClick()
                }
            },
            // 全选删除变量
            onSelectAll (isChecked) {
                if (isChecked) {
                    this.deleteVarList = tools.deepClone(this.editVarList)
                } else {
                    this.deleteVarList = []
                }
            },
            // 跨流程克隆变量
            onCloneVarConfirm (constants = []) {
                constants.forEach(item => {
                    this.newCloneKeys.push(item.key)
                    this.addVariable(item)
                })
                this.isVarCloneDialogShow = false
            },
            setNewCloneKeys (key) {
                this.newCloneKeys = [key]
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
.process-project-variable-btn {
    .manager-item {
        position: absolute;
        top: 14px;
        right: 30px;
        font-weight: normal;
        line-height: 19px;
        font-size: 14px;
        padding: 6px 13px;
        background: #f0f1f5;
        border-radius: 4px;
        cursor: pointer;
    }
}
.manager-project-variable-btn {
    .manager-item {
        position: absolute;
        top: 20px;
        right: 160px;
        font-size: 14px;
        line-height: 19px;
        font-weight: normal;
        cursor: pointer;
        &:hover {
            color: #3a84ff;
        }
    }
    .r30 {
        right: 30px;
    }
}
.setting-header {
    & > span.active {
        color: #3a84ff;
        cursor: pointer;
    }
    .common-icon-info {
        position: absolute;
        top: 22px;
        right: 30px;
        font-size: 16px;
        color: #c4c6cc;
        &:hover {
            color: #f4aa1a;
        }
    }
    #var-desc {
        .tips-item {
            & > h4 {
                margin: 0;
            }
            &:not(:last-child) {
                margin-bottom: 10px;
            }
        }
    }
}
.global-variable-panel {
    height: calc(100vh - 60px);
    .is-hidden {
        transform: scale(0)
    }
    .delete-variable-btn {
        width: 90px;
    }
    .delete-variable-txt {
        font-size: 12px;
        padding: 0 10px;
    }
    .add-variable {
        position: relative;
        padding: 30px 30px 20px;
        .add-variable-btn {
            width: 90px;
        }
        .toggle-system-var {
            float: right;
            margin-top: 4px;
            margin-right: 35px;
        }
        .common-icon-info {
            position: absolute;
            top: 39px;
            right: 30px;
            font-size: 16px;
            color: #c4c6cc;
            &:hover {
                color: #f4aa1a;
            }
        }
        .scale0 {
            transform: scale(0);
        }
    }
    .global-variable-tootip {
        margin-left: 6px;
        color:#c4c6cc;
        font-size: 16px;
        cursor: pointer;
        &:hover {
            color:#f4aa1a;
        }
        &.quote-info {
            margin-left: 0px;
        }
    }
    .global-variable-content {
        position: relative;
        margin: 0 30px;
        border: 1px solid #dcdee5;
    }
    .variable-header, .variable-list {
        position: relative;
        font-size: 12px;
        .variable-checkbox {
            position: absolute;
            top: 11px;
            left: 27px;
        }
        .col-name {
            margin-left: 55px;
            width: 170px;
        }
        .col-key {
            width: 150px;
        }
        .col-type {
            width: 80px;
        }
        .col-attributes {
            width: 50px;
            .icon-wrap {
                vertical-align: middle;
                line-height: 1;
                display: inline-block;
                .common-icon-show-left {
                    color: #219f42;
                    font-size: 14px;
                }
                .common-icon-hide-right {
                    font-size: 14px;
                }
                .common-icon-eye-show {
                    margin-left: 8px;
                    color: #219f42;
                    font-size: 15px;
                }
                .common-icon-eye-hide {
                    margin-left: 8px;
                    font-size: 15px;
                }
            }
        }
        .col-show {
            width: 100px;
        }
        .col-output {
            width: 50px;
        }
        .col-cited {
            width: 50px;
            margin: 0 5px 0 -5px;
        }
        .col-operation,
        .col-more {
            width: 40px;
        }
        /deep/.icon-funnel {
            font-size: 13px;
            color: #c4c6cc;
            cursor: pointer;
            &.active {
                color: #63656e;
            }
        }
    }
    .variable-header {
        height: 42px;
        line-height: 42px;
        background: #fafbfd;
        border-bottom: 1px solid #dcdee5;
        .t-head {
            float: left;
            height: 40px;
            line-height: 40px;
        }
    }
    .variable-operating-tips {
        position: absolute;
        left: 0;
        top: 42px;
        z-index: 101;
        width: 100%;
        height: 43px;
        line-height: 43px;
        color: #63656e;
        font-size: 12px;
        text-align: center;
        border-bottom: 1px solid #dcdee5;
        background: #f0f1f5;
    }
    .variable-list {
        width: 100%;
        max-height: calc(100vh - 214px);
        border-top: none;
        overflow-y: auto;
        @include scrollbar;
    }
    .empty-variable-tips {
        height: 280px;
        /deep/ .no-data-wording {
            font-size: 12px;
        }
    }
}
</style>
