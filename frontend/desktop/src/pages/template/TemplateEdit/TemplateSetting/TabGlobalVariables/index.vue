/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
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
                    <bk-button theme="primary" class="add-variable-btn" @click="onAddVariable">{{ $t('新建') }}</bk-button>
                    <bk-button v-if="!common" theme="default" class="manager-project-variable-btn" @click="onManagerProjectVariable">{{ $t('管理项目变量') }}</bk-button>
                    <div class="toggle-system-var">
                        <bk-checkbox :value="isHideSystemVar" @change="onToggleSystemVar">{{ $t('隐藏系统变量') }}</bk-checkbox>
                    </div>
                </div>
                <div class="global-variable-content">
                    <div class="variable-header clearfix">
                        <span class="col-name t-head">{{ $t('名称') }}</span>
                        <span class="col-key t-head">KEY</span>
                        <span class="col-attributes t-head">{{ $t('属性') }}</span>
                        <span class="col-output t-head">{{ $t('输出') }}</span>
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
                        <span class="col-operation t-head">{{ $t('操作') }}</span>
                        <span class="col-delete t-head"></span>
                    </div>
                    <div class="variable-list">
                        <draggable
                            class="variable-drag"
                            handle=".col-item-drag"
                            :list="variableList"
                            @end="onDragEnd($event)">
                            <variable-item
                                v-for="constant in variableList"
                                :key="constant.key"
                                :outputed="outputs.indexOf(constant.key) > -1"
                                :variable-data="constant"
                                :variable-cited="variableCited"
                                :common="common"
                                @onEditVariable="onEditVariable"
                                @onDeleteVariable="onDeleteVariable"
                                @onCloneVariable="onCloneVariable"
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
            <variable-edit
                v-if="variableData"
                ref="variableEdit"
                :variable-data="variableData"
                :common="common"
                @closeEditingPanel="closeEditingPanel"
                @onSaveEditing="onSaveEditing">
            </variable-edit>
            <bk-dialog
                width="400"
                ext-cls="common-dialog delete-variable-dialog"
                :theme="'primary'"
                :mask-close="false"
                :header-position="'left'"
                :title="$t('删除变量')"
                :value="deleteConfirmDialogShow"
                @confirm="onDeleteConfirm"
                @cancel="onDeleteCancel">
                <div>{{ $t('确认删除该变量？') }}</div>
            </bk-dialog>
        </div>
    </bk-sideslider>
</template>
<script>
    import draggable from 'vuedraggable'
    import { mapMutations, mapState, mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import VariableEdit from './VariableEdit.vue'
    import VariableItem from './VariableItem.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'TabGlobalVariables',
        components: {
            VariableEdit,
            VariableItem,
            draggable,
            NoData
        },
        props: {
            common: [String, Number]
        },
        data () {
            return {
                isHideSystemVar: false,
                variableList: [], // 变量列表，包含系统内置变量和用户变量
                variableData: null, // 编辑中的变量
                deleteConfirmDialogShow: false,
                deleteVarKey: '',
                variableCited: {} // 全局变量被任务节点、网关节点以及其他全局变量引用情况
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'gateways': state => state.template.gateways,
                'outputs': state => state.template.outputs,
                'constants': state => state.template.constants,
                'internalVariable': state => state.template.internalVariable
            })
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
                'getVariableCite'
            ]),
            ...mapMutations('template/', [
                'editVariable',
                'deleteVariable',
                'setOutputs'
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
            setVariableList () {
                const userVars = Object.keys(this.constants)
                    .map(key => tools.deepClone(this.constants[key]))
                    .sort((a, b) => a.index - b.index)
                if (this.isHideSystemVar) {
                    this.variableList = userVars
                } else {
                    const sysVars = Object.keys(this.internalVariable)
                        .map(key => tools.deepClone(this.internalVariable[key]))
                        .sort((a, b) => b.index - a.index)
                    this.variableList = [...sysVars, ...userVars]
                }
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
                    console.log(item.index)
                    this.editVariable({ key: item.key, variable: tools.deepClone(item) })
                })
            },
            /**
             * 打开编辑变量面板
             * @param {String} key 变量key值
             */
            onEditVariable (key) {
                this.variableData = tools.deepClone(this.constants[key] || this.internalVariable[key])
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
             * 变量输出勾选
             */
            onChangeVariableOutput ({ key, checked }) {
                const changeType = checked ? 'add' : 'delete'
                this.setOutputs({ changeType, key })
                this.$emit('templateDataChanged')
            },
            /**
             * 显示删除变量弹窗
             */
            onDeleteVariable (key) {
                this.deleteVarKey = key
                this.deleteConfirmDialogShow = true
            },
            // 确认删除
            onDeleteConfirm () {
                this.deleteConfirmDialogShow = false
                this.deleteVariable(this.deleteVarKey)
                this.deleteVarKey = ''
                this.$emit('templateDataChanged')
                this.getVariableCitedData() // 删除变量后更新引用数据
            },
            // 取消删除
            onDeleteCancel () {
                this.deleteConfirmDialogShow = false
                this.deleteVarKey = ''
            },
            onCloneVariable (data) {
                const variableData = tools.deepClone(data)
                variableData.source_info = {}
                variableData.key = ''
                variableData.index = Object.keys(this.constants).length + 1
                this.variableData = variableData
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
                if (!this.variableData) {
                    this.$emit('closeTab')
                } else {
                    if (this.variableData.source_type === 'system') {
                        this.closeEditingPanel()
                        return
                    }
                    this.$refs.variableEdit.handleMaskClick()
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
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
    .add-variable {
        padding: 30px 30px 20px;
        .add-variable-btn {
            width: 90px;
        }
        .manager-project-variable-btn {
            padding: 0 20px;
        }
        .toggle-system-var {
            float: right;
            margin-top: 4px;
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
        .col-name {
            margin-left: 50px;
            width: 242px;
        }
        .col-key {
            width: 180px;
        }
        .col-attributes {
            width: 64px;
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
        .col-output {
            width: 54px;
        }
        .col-cited {
            width: 50px;
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
        min-height: 300px;
        max-height: calc(100vh - 214px);
        border-top: none;
        overflow-y: auto;
        @include scrollbar;
    }
    .empty-variable-tips {
        margin-top: 120px;
        /deep/ .no-data-wording {
            font-size: 12px;
        }
    }
}
/deep/ .delete-variable-dialog .bk-dialog-body {
    padding: 20px;
}
</style>
