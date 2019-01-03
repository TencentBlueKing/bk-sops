/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div :class="['setting-panel', {'actived': this.showPanel}]">
        <div class="toggle-button" @click="togglePanel">
            <i :class="['common-icon-arrow-left', {'arrow-right': this.showPanel}]"></i>
        </div>
        <bk-tab class="panel-content" :active-name="activeTab" @tab-changed="onTabChange">
            <bk-tabpanel name="global-variable-tab" :title="i18n.global_varibles">
                <div class="add-variable">
                    <bk-button type="primary" @click="onAddVariable">{{ i18n.new }}</bk-button>
                    <bk-tooltip placement="bottom-end" class="globle-variable-tootip">
                        <i class="common-icon-warning"></i>
                        <div slot="content">
                            <div class="tips-item" style="white-space: normal;">
                                <h4>{{ i18n.source }}</h4>
                                <p>
                                    {{ i18n.two_types }}
                                    <span class="common-icon-source-out"></span> {{ i18n.outputs_type }}
                                    <span class="common-icon-source-in"></span> {{ i18n.desc }}
                                </p>
                            </div>
                            <div class="tips-item">
                                <h4>{{ i18n.show }}</h4>
                                <p>{{ i18n.show_desc }}</p>
                            </div>
                            <div class="tips-item">
                                <h4>{{ i18n.outputs }}</h4>
                                <p>{{ i18n.outputs_desc }}</p>
                            </div>
                        </div>
                    </bk-tooltip>
                </div>
                <div class="global-variable-content">
                    <div class="variable-header clearfix">
                        <span class="col-drag t-head"></span>
                        <span class="col-name t-head">{{ i18n.name }}</span>
                        <span class="col-key t-head">KEY</span>
                        <span class="col-source t-head">{{ i18n.source2 }}</span>
                        <span class="col-show-type t-head">{{ i18n.show2 }}</span>
                        <span class='col-delete t-head'>{{ i18n.delete }}</span>
                        <span class="col-output t-head">{{ i18n.outputs2 }}</span>
                    </div>
                    <ul class="variable-list">
                        <draggable
                            v-model="constantsArray"
                            :options="{handle:'.col-drag'}"
                            @end="onDragEnd">
                                <li
                                    v-for="(constant, index) in constantsArray"
                                    :key="constant.key"
                                    :class="{
                                        'clearfix': true,
                                        'variable-item': true,
                                        'variable-editing': isVariableEditing && theKeyOfEditing === constant.key
                                    }"
                                    @click="onEditVariable(constant.key)">
                                    <div class="variable-content">
                                        <span class="col-item col-drag">
                                            <i class="common-icon-drag"></i>
                                        </span>
                                        <span class="col-item col-name">
                                            {{constant.name}}
                                        </span>
                                        <span class="col-item col-key">{{constant.key}}</span>
                                        <span class="col-item col-source">
                                            <i
                                                v-bktooltips.bottom="constant.source_type !== 'component_outputs' ? i18n.inputs : i18n.outputs2"
                                                :class="constant.source_type !== 'component_outputs' ? 'common-icon-source-in' : 'common-icon-source-out'">
                                            </i>
                                            </span>
                                        <span class="col-item col-show-type">
                                            <i
                                                v-bktooltips.bottom="constant.show_type === 'show' ? i18n.show2 : i18n.hide"
                                                :class="constant.show_type === 'show' ? 'common-icon-eye-open' : 'common-icon-eye-close'">
                                            </i>
                                            </span>
                                        <span class="col-item col-delete" @click.stop="onDeleteVariable(constant.key, index)">
                                            <i class="common-icon-close"></i>
                                        </span>
                                        <span class="col-item col-output">
                                            <BaseCheckbox
                                                v-bktooltips.left="outputs.indexOf(constant.key) > -1 ? i18n.varCancelHook : i18n.varHook"
                                                :isChecked="outputs.indexOf(constant.key) > -1"
                                                @checkCallback="onChangeVariableOutput(constant.key, $event)">
                                            </BaseCheckbox>
                                        </span>
                                    </div>
                                    <div
                                        v-if="isVariableEditing && theKeyOfEditing === constant.key"
                                        :key="`${constant.key}-edit`">
                                        <VariableEdit
                                            :variableData="variableData"
                                            :isNewVariable="false"
                                            @onChangeEdit="onChangeEdit">
                                        </VariableEdit>
                                    </div>
                                </li>
                        </draggable>
                        <li v-if="isVariableEditing && theKeyOfEditing === ''">
                            <VariableEdit
                                :variableData="variableData"
                                :isNewVariable="true"
                                @onChangeEdit="onChangeEdit">
                            </VariableEdit>
                        </li>
                    </ul>
                </div>
            </bk-tabpanel>
            <bk-tabpanel name="template-config-tab" :title="i18n.common">
                <div class="config-wrapper" v-bkloading="{isLoading: businessInfoLoading, opacity: 1}">
                    <div class="common-form-item">
                        <label>{{ i18n.type }}</label>
                        <div class="common-form-content">
                            <bk-selector
                                :list="taskCategories"
                                :selected.sync="category"
                                @item-selected="onChangeTaskCategories">
                            </bk-selector>
                            <span v-show="!isTemplateConfigValid" class="common-error-tip error-msg">{{ i18n.categoryTip}}</span>
                        </div>
                    </div>
                    <div class="common-form-item">
                        <label>{{ i18n.notify_type }}</label>
                        <div class="common-form-content">
                            <el-checkbox-group v-model="notifyType">
                                <el-checkbox v-for="item in notifyTypeList" :key="item.id" :label="item.id">{{item.name}}</el-checkbox>
                            </el-checkbox-group>
                        </div>
                    </div>
                    <div class="common-form-item hide">
                        <label>{{ i18n.timeout }}</label>
                        <div class="common-form-content">
                            <BaseInput :value="timeout" @input="onChangeTimeout"/>
                        </div>
                    </div>
                    <div class="common-form-item">
                        <label>{{ i18n.receiver_group }}</label>
                        <div class="common-form-content">
                            <el-checkbox-group v-model="receiverGroup">
                                <el-checkbox v-for="item in notifyGroup" :key="item.id" :label="item.id">{{item.name}}</el-checkbox>
                            </el-checkbox-group>
                        </div>
                    </div>
                </div>
            </bk-tabpanel>
        </bk-tab>
        <bk-dialog
            :is-show.sync="deleteConfirmDialogShow"
            :quick-close="false"
            :ext-cls="'common-dialog'"
            :title="i18n.tips"
            width="400"
            padding="30px"
            @confirm="onConfirm"
            @cancel="onCancel">
            <div slot="content">{{ i18n.confirm }}</div>
        </bk-dialog>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapMutations } from 'vuex'
import draggable from 'vuedraggable'
import BaseCheckbox from '@/components/common/base/BaseCheckbox.vue'
import BaseInput from '@/components/common/base/BaseInput.vue'
import VariableEdit from './VariableEdit.vue'
export default {
    name: 'GlobalVariables',
    components: {
        BaseInput,
        BaseCheckbox,
        VariableEdit,
        draggable
    },
    props: ['businessInfoLoading', 'isTemplateConfigValid', 'isSettingPanelShow'],
    data () {
        return {
            i18n: {
                global_varibles: gettext("全局变量"),
                new: gettext("新建变量"),
                source: gettext("来源："),
                two_types: gettext("分两种，输入类型"),
                outputs_type: gettext("或输出类型"),
                desc: gettext("。输入类型变量来自用户添加的变量或者原子/子流程节点输入参数引用的变量；输出类型变量来自原子/子流程节点输出参数引用的变量。"),
                show: gettext("显示："),
                show_desc: gettext("表示该变量在创建任务填写参数时是否展示给用户，输出类型的变量一定是隐藏的。"),
                outputs: gettext("输出："),
                outputs_desc: gettext("表示该变量会作为该流程模板的输出参数，在被其他流程模板当做子流程节点时可以引用。"),
                name: gettext("名称"),
                source2: gettext("来源"),
                hide: gettext("隐藏"),
                show2: gettext("显示"),
                // 区别于其他地方的删除翻译，这里为了简写英文翻译，所以是"变量删除"
                delete: gettext("变量删除"),
                inputs: gettext("输入"),
                outputs2: gettext("输出"),
                varHook: gettext("勾选变量作为流程输出参数"),
                varCancelHook: gettext("取消勾选"),
                common: gettext("基础属性"),
                type: gettext("分类"),
                notify_type: gettext("通知方式"),
                timeout: gettext("超时时长"),
                receiver_group: gettext("通知分组"),
                tips: gettext("删除变量"),
                confirm: gettext("确认删除该变量？"),
                categoryTip: gettext("必填项")
            },
            showPanel: true,
            isVariableEditing: false,
            theKeyOfEditing: '',
            constantsArray: [],
            selectedTaskCategory: '',
            activeTab: 'global-variable-tab',
            deleteVarKey: '',
            deleteVarIndex: '',
            deleteConfirmDialogShow: false
        }
    },
    computed: {
        ...mapState({
            'businessBaseInfo': state => state.template.businessBaseInfo,
            'outputs': state => state.template.outputs,
            'constants': state => state.template.constants,
            'timeout': state => state.template.time_out
        }),
        variableData () {
            if (this.theKeyOfEditing) {
                return this.constants[this.theKeyOfEditing]
            } else {
                return {
                    custom_type: 'input',
                    desc: '',
                    key: '',
                    name: '',
                    show_type: 'show',
                    source_info: {},
                    source_tag: '',
                    source_type: 'custom',
                    validation: '^.+$',
                    validator: [],
                    value: ''
                }
            }
        },
        notifyGroup () {
            if (this.businessBaseInfo.notify_group) {
                return this.businessBaseInfo.notify_group.map(item => {
                    return {
                        id: item.value,
                        name: item.text
                    }
                })
            }
            return []
        },
        notifyTypeList () {
            if (this.businessBaseInfo.notify_type_list) {
                return this.businessBaseInfo.notify_type_list.map(item => {
                    return {
                        id: item.value,
                        name: item.name
                    }
                })
            }
            return []
        },
        taskCategories () {
            if (this.businessBaseInfo.task_categories) {
                return this.businessBaseInfo.task_categories.map(item => {
                    return {
                        id: item.value,
                        name: item.name
                    }
                })
            }
            return []
        },
        receiverGroup: {
            get () {
                return this.$store.state.template.notify_receivers.receiver_group
            },
            set (value) {
                this.setReceiversGroup(value)
            }
        },
        notifyType: {
            get () {
                return this.$store.state.template.notify_type
            },
            set (value) {
                this.setNotifyType(value)
            }
        },
        category: {
            get () {
                return this.$store.state.template.category
            },
            set (value) {
                this.setCategory(value)
                this.$emit('onSelectCategory', value)
            }
        }
    },
    watch: {
        constants: {
            handler () {
                this.theKeyOfEditing = ''
                this.isVariableEditing = false
                this.constantsArray = this.getConstantsArray()
            },
            deep: true
        },
        isTemplateConfigValid (val) {
            if (!val) {
                this.activeTab = 'template-config-tab'
            }
        },
        isSettingPanelShow (val) {
            this.showPanel = val
        }
    },
    created () {
        this.constantsArray = this.getConstantsArray()
    },
    methods: {
        ...mapMutations ('template/', [
            'editVariable',
            'deleteVariable',
            'setOutputs',
            'setReceiversGroup',
            'setNotifyType',
            'setOvertime',
            'setCategory'
        ]),
        getConstantsArray () {
            const arrayList = []
            for (let cKey in this.constants) {
                const constant = JSON.parse(JSON.stringify(this.constants[cKey]))
                arrayList.push(constant)
            }
            const sortedList = arrayList.sort((a, b) => a.index - b.index)
            return sortedList
        },
        togglePanel () {
            this.$emit('toggleSettingPanel', !this.showPanel)
        },
        updateVariableIndex (start, end) {
            const indexChangedVariable = this.constantsArray.slice(start, end)
            indexChangedVariable.forEach((item, index) => {
                item.index = index
                this.editVariable({key: item.key, variable: item})
            })
        },
        onTabChange (tabName) {
            this.activeTab = tabName
        },
        /**
         * 新增变量
         */
        onAddVariable () {
            this.isVariableEditing = true
            this.theKeyOfEditing = ''
            this.$emit('varibleDataChanged')
        },
        /**
         * 编辑变量
         */
        onEditVariable (key) {
            this.isVariableEditing = true
            this.theKeyOfEditing = key
            this.$emit('varibleDataChanged')
        },
        /**
         * 删除变量
         */
        onDeleteVariable (key, index) {
            this.deleteVarKey = key
            this.deleteVarIndex = index
            this.deleteConfirmDialogShow = true
        },
        onChangeEdit (val) {
            this.isVariableEditing = val
        },
        /**
         * 变量输出勾选
         */
        onChangeVariableOutput (key ,checked) {
            const changeType = checked ? 'add' : 'delete'
            this.setOutputs({changeType, key})
            this.$emit('varibleDataChanged')
        },
        /**
         * 变量顺序拖拽
         */
        onDragEnd (event) {
            const { newIndex, oldIndex } = event
            const start = Math.min(newIndex, oldIndex)
            const end = Math.max(newIndex, oldIndex) + 1
            const indexChangedVariable = this.constantsArray.slice(start, end)
            indexChangedVariable.forEach((item, index) => {
                item.index = index + start
                this.editVariable({key: item.key, variable: item})
            })
            this.$emit('varibleDataChanged')
        },
        onChangeTimeout (val) {
            this.setOvertime(val)
        },
        onChangeTaskCategories (id) {
            this.selectedTaskCategory = id
        },
        /**
         * 变量删除弹窗确认
         */
        onConfirm () {
            const key = this.deleteVarKey
            const index = this.deleteVarIndex
            this.$emit('onDeleteConstant', key)
            const len = this.constantsArray.length
            if (len > 1) {
                const indexChangedVariable = this.constantsArray.slice(index + 1, len)
                indexChangedVariable.forEach((item, index) => {
                    item.index -= 1
                    this.editVariable({key: item.key, variable: item})
                })
            }
            this.deleteVariable(key)
            this.$emit('varibleDataChanged')
            this.deleteConfirmDialogShow = false
        },
        onCancel () {
            this.deleteConfirmDialogShow = false
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.hide {
    display: none;
}
.setting-panel {
    position: absolute;
    top: 50px;
    right: -415px;
    width: 415px;
    height: calc(100% - 50px);
    background: $whiteDefault;
    border-left: 1px solid $commonBorderColor;
    // box-shadow: -1px 0 4px #dfdfdf;
    z-index: 4;
    transition: right 0.5s ease-in-out;
    &.actived {
        right: 0;
    }
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
.panel-content {
    height: 100%;
    border: none;
    /deep/ .bk-tab2-head {
        height: 50px;
        .bk-tab2-nav .tab2-nav-item {
            height: 50px;
            line-height: 50px;
        }
    }
    /deep/ .bk-tab2-content {
        height: calc(100% - 50px);
        section {
            height: 100%;
        }
    }
    .add-variable {
        padding: 10px;
    }
    .globle-variable-tootip {
        float: right;
        margin-top: 10px;
        .common-icon-warning {
            color: #cac8c8;
            cursor: pointer;
        }
        /deep/ .bk-tooltip-popper {
            .bk-tooltip-arrow {
                border-bottom-color: #f2f2f2;
            }
            .bk-tooltip-inner {
                background: #f2f2f2;
                color: #666;
                border: 1px solid $commonBorderColor;
                border-radius: 3px;
            }
            .tips-item {
                margin-bottom: 20px;
                &:last-child {
                    margin-bottom: 0;
                }
                h4 {
                    margin-top: 0;
                    margin-bottom: 10px;
                }
                p {
                    white-space: normal;
                    word-wrap: break-word;
                    word-break: break-all;
                }
            }
        }
    }
    .global-variable-content {
        height: calc(100% -56px);
        border-top: 1px solid $commonBorderColor;
    }
    .variable-header {
        .t-head {
            float: left;
            padding: 0 8px;
            height: 40px;
            line-height: 40px;
            font-size: 14px;
            border-bottom: 1px solid $commonBorderColor;
            background: $greyDash;
        }
    }
    .variable-list {
        width: 100%;
        height: calc(100% - 50px);
        text-align: center;
        overflow-x: hidden;
        overflow-y: auto;
        @include scrollbar;
        .variable-item {
            border-bottom: 1px solid #ebebeb;
            background: $whiteDefault;
            cursor: pointer;
            &:hover {
                background: $blueStatus;
            }
            .variable-content {
                display: table;
            }
            .col-item {
                display: table-cell;
                padding: 14px 4px;
                font-size: 12px;
                vertical-align: middle;
                word-break: break-all;
            }
            &.variable-editing {
                background: $blueStatus;
            }
            .col-source {
                font-size: 16px;
            }
            .col-show-type {
                font-size: 18px;
            }
            .col-delete {
                font-size: 12px;
                cursor: pointer;
                &:hover {
                    color: $redDark;
                }
            }
        }
        .variable-edit-td {
            padding: 0;
            width: 412px;
        }
    }
    .variable-header, .variable-list {
        font-size: 12px;
        .col-drag {
            width: 20px;
            padding: 10px 0;
            cursor: move;
        }
        .col-name {
            width: 107px;
            text-align: left;
        }
        .col-key {
            width: 95px;
            text-align: left;
        }
        .col-source {
            width: 45px;
        }
        .col-show-type {
            width: 45px;
        }
        .col-delete {
            width: 45px;
        }
        .col-output {
            width: 55px;
        }
    }
    .config-wrapper {
        padding: 20px;
        .common-form-item > label {
            width: 70px;
            font-weight: normal;
        }
        .common-form-content {
            margin-left: 90px;
            line-height: 32px;
        }
        .el-checkbox {
            margin-left: 0;
            margin-right: 14px;
        }
        /deep/ .el-checkbox__input.is-checked + .el-checkbox__label {
            color: $greyDefault;
        }
    }
}
</style>


