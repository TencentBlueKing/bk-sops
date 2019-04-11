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
        </div>
        <div class="add-variable">
            <bk-button type="default" class="add-variable-btn" size="small" @click="onAddVariable">{{ i18n.new }}</bk-button>
            <bk-tooltip placement="bottom-end" class="global-variable-tootip">
                <i class="bk-icon icon-info-circle"></i>
                <div slot="content">
                    <div class="tips-item">
                        <h4>{{ i18n.attr }}</h4>
                        <p>{{ i18n.attr_desc }}</p>
                    </div>
                    <div class="tips-item">
                        <h4>{{ i18n.outputs2 }}</h4>
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
                <span class="col-attributes t-head">{{ i18n.attributes }}</span>
                <span class="col-output t-head">{{ i18n.outputs }}</span>
                <span class="col-delete t-head"></span>
            </div>
            <ul class="variable-list">
                <draggable class="variable-drag" v-model="constantsArray" :options="{handle:'.col-drag'}" @end="onDragEnd">
                    <li
                        v-for="(constant, index) in constantsArray"
                        :key="constant.key"
                        :class="['clearfix',
                        'variable-item',
                        {'variable-editing': isVariableEditing && theKeyOfEditing === constant.key}]"
                        @click="onEditVariable(constant.key)">
                        <div class="variable-content">
                            <span class="col-item col-drag">
                                <i class="bk-icon icon-sort"></i>
                            </span>
                            <span class="col-item col-name">
                                <p class="col-constant-name">{{constant.name}}</p>
                            </span>
                            <span class="col-item col-key">
                                <p class="col-constant-key">{{constant.key}}</p>
                                <a
                                    class="col-key-copy"
                                    href="javascript:void(0)"
                                    v-bktooltips.click="{
                                        content: i18n.copied,
                                        placements: ['bottom']
                                    }"
                                    @click.stop="onCopyKey(constant.key)">
                                    {{ i18n.copy }}
                                </a>
                            </span>
                            <span class="col-item col-source">
                                <span>
                                    {{constant.source_type !== 'component_outputs' ? i18n.inputs : i18n.outputs}}/{{ constant.show_type === 'show' ? i18n.show : i18n.hide}}
                                </span>
                            </span>
                            <span class="col-item col-output col-switcher">
                                <div @click="onPreventDefalut">
                                    <bk-switcher
                                        size="small"
                                        on-text="ON"
                                        off-text="OFF"
                                        :selected="outputs.indexOf(constant.key) > -1"
                                        @change="onChangeVariableOutput(constant.key, $event)">
                                    </bk-switcher>
                                </div>
                            </span>
                            <span class="col-item col-delete" @click.stop="onDeleteVariable(constant.key, index)">
                                <i class="bk-icon icon-close-circle"></i>
                            </span>
                        </div>
                        <div
                            v-if="isVariableEditing && theKeyOfEditing === constant.key"
                            :key="`${constant.key}-edit`">
                            <VariableEdit
                                ref="editVariablePanel"
                                :variableData="variableData"
                                :isNewVariable="false"
                                @onChangeEdit="onChangeEdit">
                            </VariableEdit>
                        </div>
                    </li>
                </draggable>
                <li v-if="isVariableEditing && theKeyOfEditing === ''">
                    <VariableEdit
                        ref="addVariablePanel"
                        :variableData="variableData"
                        :isNewVariable="true"
                        @onChangeEdit="onChangeEdit">
                    </VariableEdit>
                </li>
                <li v-if="!isVariableEditing && !constantsArray.length" class="empty-variable-tip">
                    <NoData>
                        <p>{{i18n.empty_variable_tip}}</p>
                    </NoData>
                </li>
            </ul>
        </div>
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
import { mapMutations, mapState } from 'vuex'
import tools from '@/utils/tools.js'
import draggable from 'vuedraggable'
import BaseCheckbox from '@/components/common/base/BaseCheckbox.vue'
import BaseInput from '@/components/common/base/BaseInput.vue'
import VariableEdit from './VariableEdit.vue'
import NoData from '@/components/common/base/NoData.vue'
export default {
    name: 'TabGlobalVariables',
    components: {
        BaseInput,
        BaseCheckbox,
        VariableEdit,
        draggable,
        NoData
    },
    props: ['isVariableEditing'],
    data () {
        return {
            i18n: {
                global_varibles: gettext('全局变量'),
                new: gettext('新建'),
                name: gettext('名称'),
                attributes: gettext('属性'),
                inputs: gettext('输入'),
                outputs: gettext('输出'),
                attr: gettext('属性：'),
                attr_desc: gettext('"来源/是否显示"格式，来源是输入类型表示变量来自用户添加的变量或者标准插件/子流程节点输入参数引用的变量，来源是输出类型表示变量来自标准插件/子流程节点输出参数引用的变量；是否显示表示该变量在新建任务填写参数时是否展示给用户，输出类型的变量一定是隐藏的。'),
                outputs2: gettext('输出：'),
                outputs_desc: gettext('表示该变量会作为该流程模板的输出参数，在被其他流程模板当做子流程节点时可以引用。'),
                empty_variable_tip: gettext('无数据，请手动新增变量或者勾选标准插件参数自动生成'),
                tips: gettext('删除变量'),
                confirm: gettext('确认删除该变量？'),
                copied: gettext('已复制'),
                copy: gettext('复制'),
                show: gettext('显示'),
                hide: gettext('隐藏')
            },
            copyText: '',
            theKeyOfEditing: '',
            constantsArray: [],
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
        }
    },
    watch: {
        constants: {
            handler () {
                this.theKeyOfEditing = ''
                this.constantsArray = this.getConstantsArray()
                this.changeVariableEditing(false)
            },
            deep: true
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
        /**
         * 编辑变量
         */
        onEditVariable (key) {
            this.$emit('changeVariableEditing', true)
            this.theKeyOfEditing = key
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
                this.editVariable({key: item.key, variable: item})
            })
            this.$emit('variableDataChanged')
        },
        changeVariableEditing (val) {
            this.$emit('changeVariableEditing', val)
        },
        /**
         * 新增变量
         */
        onAddVariable () {
            this.$emit('changeVariableEditing', true)
            this.theKeyOfEditing = ''
            this.$emit('variableDataChanged')
        },
        /**
         * 变量 key 复制
         */
        onCopyKey (key) {
            this.copyText = key
            document.addEventListener("copy", this.copyHandler)
            document.execCommand("copy")
            document.removeEventListener("copy", this.copyHandler)
            this.copyText = ''
        },
        /**
         * 复制操作回调函数
         */
        copyHandler (e) {
            e.clipboardData.setData("text/html", this.copyText)
            e.clipboardData.setData("text/plain", this.copyText)
            e.preventDefault()
        },
        /**
         * 变量输出勾选
         */
        onChangeVariableOutput (key, checked) {
            const changeType = checked ? 'add' : 'delete'
            this.setOutputs({changeType, key})
            this.$emit('variableDataChanged')
        },
        /**
         *  删除变量
         */
        onDeleteVariable (key, index) {
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
                    this.editVariable({key: item.key, variable: item})
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
        },
        onPreventDefalut () {
            window.event ? window.event.cancelBubble = true : e.stopPropagation()
        }
    }
}
</script>

<style lang="scss">
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
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
            height: 32px;
            line-height: 32px;
        }
        .draft-form {
            display: inline-block;
            input {
                width: 200px;
            }
        }
    }
    .global-variable-tootip {
        float: right;
        margin-top: 8px;
        .icon-info-circle {
            margin-top: 20px;
            color:#c4c6cc;
            cursor: pointer;
            &:hover {
                color:#f4aa1a;
            }
        }
        .bk-tooltip-popper {
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
            .tips-item-content {
                margin-bottom: 20px;
                &:last-child {
                    margin-bottom: 0;
                }
                h4 {
                    margin-top: 0;
                    margin-bottom: 10px;
                }
                p {
                     margin-top: -18px;
                }
            }
        }
        .bk-tooltip-arrow {
            right: 2px;
        }
        .bk-tooltip-inner {
            margin-right: -18px;
        }
    }
    .global-variable-content {
        height: calc(100% - 120px);
        border-top: 1px solid $commonBorderColor;
    }
    .variable-header {
        .t-head {
            float: left;
            height: 40px;
            line-height: 40px;
            font-size: 14px;
            border-bottom: 1px solid $commonBorderColor;
            background: #ECF0F4;
        }
    }
    .variable-list {
        width: 100%;
        height: calc(100% - 50px);
        text-align: center;
        overflow-x: hidden;
        overflow-y: auto;
        @include scrollbar;
        .variable-item, .draft-item  {
            position: relative;
            border-bottom: 1px solid #ebebeb;
            background: $whiteDefault;
            cursor: pointer;
            &:hover {
                background: $blueStatus;
                .icon-sort {
                    display: inline-block;
                }
                .icon-close-circle {
                    display: inline-block;
                }
            }
            .variable-content, .draft-content {
                display: table;
                height: 40px;
                line-height: 20px;
            }
            .col-item {
                display: table-cell;
                padding: 8px 4px;
                font-size: 12px;
                vertical-align: middle;
                word-break: break-all;
            }
            &.variable-editing {
                background: $blueStatus;
            }
            .col-source {
                width: 90px;
                font-size: 12px;
                text-align: left;
            }
            .col-show-type {
                font-size: 12px;
            }
            .col-delete {
                width: 10px;
                cursor: pointer;
                .icon-close-circle {
                    position: absolute;
                    right: 10px;
                    top: 15px;
                    font-size: 12px;
                }
            }
        }
        .variable-edit-td {
            padding: 0;
            width: 412px;
        }
        .empty-variable-tip {
            margin-top: 120px;
        }
    }
    .variable-header, .variable-list {
        position: relative;
        font-size: 12px;
        .col-drag {
            width: 20px;
            padding: 10px 0;
            cursor: pointer;
            .icon-sort {
                position: absolute;
                top: 15px;
                left: 5px;
                display: none;
            }
        }
        .col-name {
            width: 78px;
            text-align: left;
            .col-constant-name {
                width: 70px;
                overflow: hidden;
                text-overflow:ellipsis;
                white-space: nowrap;
            }
        }
        .col-key {
            position: relative;
            width: 138px;
            text-align: left;
            .col-constant-key {
                display: inline-block;
                width: 90px;
                vertical-align: middle;
                overflow: hidden;
                text-overflow:ellipsis;
                white-space: nowrap;
            }
            .col-key-copy {
                position: absolute;
                bottom: 10px;
                color: #52699D;
            }
        }
        .col-attributes {
            width: 83px;
        }
        .col-show-type {
            width: 45px;
        }
        .col-delete {
            width: 10px;
            cursor: pointer;
            .icon-close-circle {
                position: absolute;
                display: none;
                // right: 10px;
                top: 13px;
                font-size: 12px;
            }
        }
        .col-output {
            width: 90px;
            text-align: center;
            .col-switcher {
                width: 84px;
            }
            .bk-switcher .bk-switcher-small {
                margin-left: 32px;
            }
            .bk-switcher.bk-switcher-small {
                width: 40px;
                height: 19px;
                line-height: 10px;
            }
            .bk-switcher.bk-switcher-small:after {
                width: 16px;
                height: 16px;
            }
            .bk-switcher.bk-switcher-small.is-checked:after {
                margin-left: -18px;
            }
        }
    }
}

</style>
