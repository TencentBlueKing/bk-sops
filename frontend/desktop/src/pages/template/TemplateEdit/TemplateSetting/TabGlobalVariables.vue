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
    <div class="global-variable-panel">
        <div class="global-title">
            <span>{{i18n.global_varibles}}</span>
            <i
                class="bk-icon icon-info-circle global-variable-tootip"
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
                    <h4>{{ i18n.attrTitle }}</h4>
                    <p>
                        {{ i18n.attrDesc1 }}
                        <i class="common-icon-show-left" style="color: #219f42"></i>
                        {{i18n.attrDesc2}}
                        <i class="common-icon-hide-right" style="color: #de9524"></i>
                        {{i18n.attrDesc3}}
                    </p>
                </div>
                <div class="tips-item">
                    <h4>{{ i18n.outputsTitle }}</h4>
                    <p>{{ i18n.outputsDesc }}</p>
                </div>
            </div>
        </div>
        <div class="add-variable">
            <bk-button theme="default" class="add-variable-btn" @click="onAddVariable">{{ i18n.new }}</bk-button>
        </div>
        <div class="global-variable-content">
            <div class="variable-header clearfix">
                <span class="col-name t-head">{{ i18n.name }}</span>
                <span class="col-key t-head">KEY</span>
                <span class="col-attributes t-head">{{ i18n.attributes }}</span>
                <span class="col-output t-head">{{ i18n.outputs }}</span>
                <span class="col-delete t-head"></span>
            </div>
            <ul class="variable-list" ref="variableList">
                <VariableItem
                    v-for="(constant, index) in context"
                    :key="index"
                    :outputs="outputs"
                    :is-variable-editing="isVariableEditing"
                    :constant="constant"
                    :variable-data="variableData"
                    :variable-type-list="variableTypeList"
                    :the-key-of-editing="theKeyOfEditing"
                    :is-system-var="true"
                    @onEditVariable="onEditVariable"
                    @onChangeVariableOutput="onChangeVariableOutput"
                    @onDeleteVariable="onDeleteVariable" />
                <draggable class="variable-drag" v-model="constantsArray" :options="{ handle: '.col-item-drag' }" @end="onDragEnd">
                    <VariableItem
                        v-for="(constant, index) in constantsArray"
                        :key="index"
                        :outputs="outputs"
                        :is-variable-editing="isVariableEditing"
                        :constant="constant"
                        :variable-data="variableData"
                        :variable-type-list="variableTypeList"
                        :the-key-of-editing="theKeyOfEditing"
                        @onEditVariable="onEditVariable"
                        @onChangeVariableOutput="onChangeVariableOutput"
                        @onDeleteVariable="onDeleteVariable" />
                </draggable>
                <li v-if="isVariableEditing && theKeyOfEditing === ''">
                    <VariableEdit
                        ref="addVariablePanel"
                        :variable-data="variableData"
                        :variable-type-list="variableTypeList"
                        :is-new-variable="true"
                        @scrollPanelToView="scrollPanelToView"
                        @onChangeEdit="onChangeEdit">
                    </VariableEdit>
                </li>
                <li v-if="isShowNodata" class="empty-variable-tip">
                    <NoData>
                        <p>{{i18n.emptyVariableTip}}</p>
                    </NoData>
                </li>
            </ul>
        </div>
        <bk-dialog
            width="400"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :header-position="'left'"
            :title="i18n.tips"
            :value="deleteConfirmDialogShow"
            @confirm="onConfirm"
            @cancel="onCancel">
            <div>{{ i18n.confirm }}</div>
        </bk-dialog>
    </div>
</template>

<script>
    import '@/utils/i18n.js'
    import { mapMutations, mapState } from 'vuex'
    import tools from '@/utils/tools.js'
    import draggable from 'vuedraggable'
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
        props: ['isVariableEditing', 'variableTypeList'],
        data () {
            return {
                i18n: {
                    global_varibles: gettext('全局变量'),
                    new: gettext('新建'),
                    name: gettext('名称'),
                    attributes: gettext('属性'),
                    outputs: gettext('输出'),
                    outputsTitle: gettext('输出：'),
                    attr: gettext('属性'),
                    attrTitle: gettext('属性：'),
                    attrDesc1: gettext('"来源/是否显示"格式，来源是输入类型'),
                    attrDesc2: gettext('表示变量来自用户添加的变量或者标准插件/子流程节点输入参数引用的变量，来源是输出类型'),
                    attrDesc3: gettext('表示变量来自标准插件/子流程节点输出参数引用的变量；是否显示表示该变量在新建任务填写参数时是否展示给用户，输出类型的变量一定是隐藏的。'),
                    outputsDesc: gettext('表示该变量会作为该流程模板的输出参数，在被其他流程模板当做子流程节点时可以引用。'),
                    emptyVariableTip: gettext('无数据，请手动新增变量或者勾选标准插件参数自动生成'),
                    tips: gettext('删除变量'),
                    confirm: gettext('确认删除该变量？')
                },
                theKeyOfEditing: '',
                constantsArray: [],
                deleteConfirmDialogShow: false
            }
        },
        computed: {
            ...mapState({
                'projectBaseInfo': state => state.template.projectBaseInfo,
                'outputs': state => state.template.outputs,
                'constants': state => state.template.constants,
                'context': state => state.template.context,
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
                        source_tag: 'input.input',
                        source_type: 'custom',
                        validation: '^.+$',
                        validator: [],
                        value: ''
                    }
                }
            },
            isShowNodata () {
                return !this.isVariableEditing && !this.constantsArray.length && !this.context.length
            }
        },
        watch: {
            constants: {
                handler () {
                    this.theKeyOfEditing = ''
                    this.constantsArray = this.getConstantsArray()
                    this.onChangeEdit(false)
                },
                deep: true
            }
        },
        created () {
            this.constantsArray = this.getConstantsArray()
        },
        methods: {
            ...mapMutations('template/', [
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
                for (const cKey in this.constants) {
                    const constant = tools.deepClone(this.constants[cKey])
                    arrayList.push(constant)
                }
                const sortedList = arrayList.sort((a, b) => a.index - b.index)
                return sortedList
            },
            saveVariable () {
                if (this.theKeyOfEditing) {
                    return this.$refs.editVariablePanel[0].saveVariable()
                }

                return this.$refs.addVariablePanel.saveVariable()
            },
            scrollPanelToView (index) {
                if (index > 0) {
                    const itemHeight = document.querySelector('.variable-content').offsetHeight
                    this.$refs.variableList.scrollTop = itemHeight * index
                }
            },
            /**
             * 编辑变量
             * @param {String} key 变量key值
             */
            onEditVariable (key) {
                if (key === this.theKeyOfEditing && this.isVariableEditing) {
                    this.onChangeEdit(false)
                } else {
                    this.onChangeEdit(true)
                    this.theKeyOfEditing = key
                }

                this.$emit('variableDataChanged')
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
                    this.editVariable({ key: item.key, variable: item })
                })
                this.$emit('variableDataChanged')
            },
            /**
             * 新增变量
             */
            onAddVariable () {
                this.onChangeEdit(true)
                this.theKeyOfEditing = ''
                this.$emit('variableDataChanged')
            },
            /**
             * 变量输出勾选
             */
            onChangeVariableOutput ({ key, checked }) {
                const changeType = checked ? 'add' : 'delete'
                this.setOutputs({ changeType, key })
                this.$emit('variableDataChanged')
            },
            /**
             *  删除变量
             */
            onDeleteVariable ({ key, index }) {
                this.deleteVarKey = key
                this.deleteVarIndex = index
                this.deleteConfirmDialogShow = true
            },
            onConfirm () {
                const key = this.deleteVarKey
                const index = this.deleteVarIndex
                this.$emit('onDeleteConstant', key)
                const len = this.constantsArray.length
                if (len > 1) {
                    const indexChangedVariable = this.constantsArray.slice(index + 1, len)
                    indexChangedVariable.forEach((item, index) => {
                        item.index -= 1
                        this.editVariable({ key: item.key, variable: item })
                    })
                }
                this.deleteVariable(key)
                this.$emit('variableDataChanged')
                this.deleteConfirmDialogShow = false
            },
            onCancel () {
                this.deleteConfirmDialogShow = false
            },
            onChangeEdit (val) {
                this.$emit('changeVariableEditing', val)
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
$localBorderColor: #d8e2e7;
/deep/ .common-dialog .bk-dialog-body{
    padding: 20px;
}
.tips-item {
    & > h4 {
        margin: 0;
    }
    &:not(:last-child) {
        margin-bottom: 10px;
    }
}
.global-variable-panel {
    height: 100%;
    .global-title {
        height: 35px;
        margin: 20px;
        border-bottom: 1px solid #cacecb;
        span {
            font-size: 14px;
            font-weight:600;
            color:#313238;
        }
    }
    .add-variable {
        margin: 20px;
        .add-variable-btn {
            width: 90px;
        }
        .draft-form {
            display: inline-block;
            input {
                width: 200px;
            }
        }
    }
    .global-variable-tootip {
        vertical-align: middle;
        margin-left: 6px;
        color:#c4c6cc;
        cursor: pointer;
        &:hover {
            color:#f4aa1a;
        }
    }
    .global-variable-content {
        height: calc(100% - 120px);
        border-top: 1px solid $localBorderColor;
    }
    .variable-header, .variable-list {
        position: relative;
        font-size: 12px;
        .col-name {
            width: 100px;
        }
        .col-key {
            width: 128px;
        }
        .col-attributes {
            padding-left: 4px;
            width: 70px;
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
                .color-org{
                    color: #de9524;
                }
            }
        }
        .col-output {
            width: 50px;
        }
    }
    .variable-header {
        padding: 0 20px 0 45px;
        background: #ecf0f4;
        border-bottom: 1px solid $localBorderColor;
        .t-head {
            float: left;
            height: 40px;
            line-height: 40px;
            font-size: 14px;
        }
    }
    .variable-list {
        width: 100%;
        height: calc(100% - 50px);
        overflow-x: hidden;
        overflow-y: auto;
        @include scrollbar;
    }
}
.tooltip-content {
    margin-bottom: 20px;
    &:last-child {
        margin-bottom: 0;
    }
    h4 {
        margin-top: 0;
        margin-bottom: 10px;
    }
}
</style>
