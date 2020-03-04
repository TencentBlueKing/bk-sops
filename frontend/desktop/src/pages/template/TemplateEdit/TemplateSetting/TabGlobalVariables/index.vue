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
        <bk-sideslider
            ext-cls="common-template-setting-sideslider"
            :width="800"
            :is-show="isShow"
            :before-close="onBeforeClose"
            :quick-close="true">
            <div slot="header">
                <span class="close-panel-icon"></span>
                <span class="global-variable-text">{{i18n.global_varibles}}</span>
                <i
                    class="common-icon-info global-variable-tootip"
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
                            {{ i18n.attrDesc2 }}
                            <i class="common-icon-hide-right" style="color: #de9524"></i>
                            {{ i18n.attrDesc3 }}
                            <i class="common-icon-eye-show" style="color: #219f42;vertical-align: middle;"></i>
                            {{ i18n.attrDesc4 }}
                            <i class="common-icon-eye-hide" style="color: #de9524;vertical-align: middle;"></i>
                            {{ i18n.attrDesc5 }}
                        </p>
                    </div>
                    <div class="tips-item">
                        <h4>{{ i18n.outputsTitle }}</h4>
                        <p>{{ i18n.outputsDesc }}</p>
                    </div>
                </div>
                <div :class="['panel-fixed-pin', { 'actived': isFixedVarMenu }]" @click.stop="onClickPin">
                    <i class="common-icon-pin"></i>
                </div>
            </div>
            <template slot="content">
                <div class="add-variable">
                    <bk-button theme="default" class="add-variable-btn" @click="onAddVariable">{{ i18n.new }}</bk-button>
                    <div class="toggle-system-var">
                        <bk-checkbox v-model="isHideSystemVar">{{ i18n.hideSystemVar }}</bk-checkbox>
                    </div>
                </div>
                <div class="global-variable-content">
                    <div class="variable-header clearfix">
                        <span class="col-name t-head">{{ i18n.name }}</span>
                        <span class="col-key t-head">KEY</span>
                        <span class="col-attributes t-head">{{ i18n.attributes }}</span>
                        <span class="col-output t-head">{{ i18n.outputs }}</span>
                        <span class="col-quote t-head">
                            {{ i18n.cited }}
                            <i
                                class="common-icon-info global-variable-tootip quote-info"
                                v-bk-tooltips="{
                                    allowHtml: true,
                                    content: i18n.citedTips,
                                    placement: 'bottom-end',
                                    duration: 0,
                                    width: 200
                                }">
                            </i>
                        </span>
                        <span class="col-operation t-head">{{ i18n.operation }}</span>
                        <span class="col-delete t-head"></span>
                    </div>
                    <div v-if="isVarTipsShow" class="variable-operating-tips">{{ varOperatingTips }}</div>
                    <ul class="variable-list" ref="variableList">
                        <draggable class="variable-drag" v-model="variableList" :options="{ handle: '.col-item-drag' }" @end="onDragEnd">
                            <VariableItem
                                v-for="(constant, index) in variableList"
                                :ref="`variableKey_${constant.key}`"
                                :key="index"
                                :outputs="outputs"
                                :is-variable-editing="isVariableEditing"
                                :constant="constant"
                                :constants-cited="constantsCited"
                                :variable-data="variableData"
                                :variable-list="variableList"
                                :variable-type-list="variableTypeList"
                                :the-key-of-editing="theKeyOfEditing"
                                :the-key-of-view-cited="theKeyOfViewCited"
                                :is-hide-system-var="isHideSystemVar"
                                :system-constants="systemConstants"
                                :var-operating-tips="varOperatingTips"
                                @onChangeEdit="onChangeEdit"
                                @onCitedNodeClick="onCitedNodeClick"
                                @onEditVariable="onEditVariable"
                                @onViewCitedList="onViewCitedList"
                                @onChangeVariableOutput="onChangeVariableOutput"
                                @onDeleteVariable="onDeleteVariable" />
                        </draggable>
                        <!-- 新建变量 -->
                        <li v-if="isVariableEditing && theKeyOfEditing === ''">
                            <VariableEdit
                                ref="addVariablePanel"
                                :system-constants="systemConstants"
                                :variable-data="variableData"
                                :variable-type-list="variableTypeList"
                                :is-new-variable="true"
                                :var-operating-tips="varOperatingTips"
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
                    ext-cls="common-dialog delete-variable-dialog"
                    :theme="'primary'"
                    :mask-close="false"
                    :header-position="'left'"
                    :title="i18n.tips"
                    :value="deleteConfirmDialogShow"
                    @confirm="onConfirm"
                    @cancel="onCancel">
                    <div>{{ i18n.confirm }}</div>
                </bk-dialog>
            </template>
        </bk-sideslider>
    </div>
</template>

<script>
    import '@/utils/i18n.js'
    import { mapMutations, mapState, mapGetters } from 'vuex'
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
        props: ['isVariableEditing', 'variableTypeList', 'isShow', 'isFixedVarMenu'],
        data () {
            return {
                isHideSystemVar: false,
                i18n: {
                    global_varibles: gettext('全局变量'),
                    new: gettext('新建'),
                    edit: gettext('编辑'),
                    hideSystemVar: gettext('隐藏系统变量'),
                    name: gettext('名称'),
                    attributes: gettext('属性'),
                    outputs: gettext('输出'),
                    cited: gettext('引用'),
                    citedTips: gettext('引用全局变量的节点数量，点击数量可展开显示具体有哪些节点'),
                    operation: gettext('操作'),
                    outputsTitle: gettext('输出：'),
                    attr: gettext('属性'),
                    attrTitle: gettext('属性：'),
                    attrDesc1: gettext('"来源/是否显示"格式，来源是输入类型'),
                    attrDesc2: gettext('表示变量来自用户添加的变量或者标准插件/子流程节点输入参数引用的变量，来源是输出类型'),
                    attrDesc3: gettext('表示变量来自标准插件/子流程节点输出参数引用的变量；是否显示表示该变量在新建任务填写参数时是否展示给用户，'),
                    attrDesc4: gettext('表示显示，'),
                    attrDesc5: gettext('表示隐藏，输出类型的变量一定是隐藏的。'),
                    outputsDesc: gettext('表示该变量会作为该流程模板的输出参数，在被其他流程模板当做子流程节点时可以引用。'),
                    emptyVariableTip: gettext('无数据，请手动新增变量或者勾选标准插件参数自动生成'),
                    tips: gettext('删除变量'),
                    confirm: gettext('确认删除该变量？')
                },
                theKeyOfEditing: '',
                theKeyOfViewCited: '',
                constantsArray: [],
                deleteConfirmDialogShow: false,
                isVarTipsShow: false
            }
        },
        computed: {
            ...mapState({
                'projectBaseInfo': state => state.template.projectBaseInfo,
                'outputs': state => state.template.outputs,
                'constants': state => state.template.constants,
                'systemConstants': state => state.template.systemConstants,
                'timeout': state => state.template.time_out
            }),
            ...mapGetters('template/', [
                'constantsCited'
            ]),
            variableData () {
                if (this.theKeyOfEditing) {
                    return this.constants[this.theKeyOfEditing] || this.systemConstants[this.theKeyOfEditing]
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
                if (this.isVariableEditing) {
                    return false
                }
                return this.constantsArray.length === 0 ? (this.isHideSystemVar || this.systemConstants.length === 0) : false
            },
            /**
             * 变量列表（系统变量+普通变量）
             * 系统变量：index范围 （-1 => -n）
             * 普通变量：index范围 （0 => n）
             */
            variableList: {
                get () {
                    if (this.isHideSystemVar) {
                        return this.getConstantsArray(this.constants)
                    }
                    return [
                        ...this.getConstantsArray(this.systemConstants),
                        ...this.getConstantsArray(this.constants)
                    ]
                },
                set (val) {
                    this.constantsArray = val
                }
            },
            // 操作变量提示 title
            varOperatingTips () {
                const { new: newText, edit, global_varibles } = this.i18n
                if (this.theKeyOfEditing) {
                    return edit + global_varibles
                }
                return newText + global_varibles
            },
            systemConstantsList () {
                const list = []
                Object.keys(this.systemConstants).forEach(key => {
                    list.push(this.systemConstants[key])
                })
                list.sort((a, b) => b.index - a.index)
                return list
            }
        },
        watch: {
            constants: {
                handler () {
                    this.theKeyOfEditing = ''
                    this.constantsArray = this.getConstantsArray(this.constants)
                    this.onChangeEdit(false)
                },
                deep: true
            }
        },
        created () {
            this.constantsArray = this.getConstantsArray(this.constants)
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
            getConstantsArray (obj) {
                const arrayList = []
                for (const cKey in obj) {
                    const constant = tools.deepClone(obj[cKey])
                    arrayList.push(constant)
                }
                const sortedList = arrayList.sort((a, b) => a.index - b.index)
                return sortedList
            },
            saveVariable () {
                if (this.theKeyOfEditing) {
                    const target = `variableKey_${this.theKeyOfEditing}`
                    const targetComponent = this.$refs[target][0].$refs.editVariablePanel
                    return targetComponent && targetComponent.saveVariable()
                }

                return this.$refs.addVariablePanel.saveVariable()
            },
            // 滚动到可视区域
            scrollPanelToView (index) {
                if (index > 0) {
                    this.$nextTick(() => {
                        const itemHeight = document.querySelector('.variable-content').offsetHeight
                        this.$refs.variableList.scrollTop = itemHeight * (index + 1)
                    })
                }
            },
            /**
             * 获取变量在 variableList 中的 index
             * 注意:非 item.index
             * @param {String} key 变量的 key
             */
            getSortIndex (key) {
                return this.variableList.findIndex(m => m.key === key)
            },
            /**
             * 编辑变量
             * @param {String} key 变量key值
             * @param {String} version 变量版本
             */
            onEditVariable (key, index, version) {
                if (key === this.theKeyOfEditing && this.isVariableEditing) {
                    this.onChangeEdit(false)
                } else {
                    this.onChangeEdit(true)
                    this.theKeyOfEditing = key
                    this.theVersionOfEditing = version
                }
                this.$emit('variableDataChanged')

                const sortIndex = this.getSortIndex(key)
                this.scrollPanelToView(sortIndex)
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
                // 滚到到底部
                const allVarLen = this.variableList.length - 1
                this.scrollPanelToView(allVarLen)
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
                this.$nextTick(() => {
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
                })
            },
            onCancel () {
                this.deleteConfirmDialogShow = false
            },
            // 添加滚动监听
            addContentScroll () {
                const variableList = document.querySelector('.global-variable-content .variable-list')
                variableList && variableList.addEventListener('scroll', this.handleVariableListScroll)
            },
            // 移除滚动监听
            removeContentScroll () {
                const variableList = document.querySelector('.global-variable-content .variable-list')
                variableList && variableList.removeEventListener('scroll', this.handleVariableListScroll)
            },
            // 变量列表滚动监听
            handleVariableListScroll (event) {
                setTimeout(() => {
                    const itemHeight = document.querySelector('.global-variable-content .variable-item .variable-content').getBoundingClientRect().height
                    let sortIndex = 0
                    if (!this.theKeyOfEditing) { // new var
                        sortIndex = this.variableList.length
                    } else { // edit var
                        this.variableList.forEach((m, i) => {
                            if (m.key === this.variableData.key) {
                                sortIndex = i + 1
                                return true
                            }
                        })
                    }
                    this.isVarTipsShow = event.srcElement.scrollTop > sortIndex * itemHeight
                }, 100)
            },
            onChangeEdit (val) {
                this.$emit('changeVariableEditing', val)
                // 编辑变量、新建变量监听滚动判断是否显示浮动 title
                if (val) {
                    this.theKeyOfViewCited = ''
                    this.addContentScroll()
                } else {
                    this.isVarTipsShow = false
                    this.removeContentScroll()
                }
            },
            onBeforeClose () {
                this.$emit('onColseTab', 'globalVariableTab')
            },
            onCitedNodeClick (nodeId) {
                this.$emit('onCitedNodeClick', nodeId)
            },
            /**
             * 展示引用节点列表
             * @param {String} key 变量 key
             * @param {Number} nums 变量被引用次数
             */
            onViewCitedList (key, nums) {
                if (!nums) {
                    this.theKeyOfViewCited = ''
                    return
                }
                if (this.theKeyOfViewCited === key) {
                    this.theKeyOfViewCited = ''
                    return
                }
                this.onChangeEdit(false)
                this.theKeyOfViewCited = key
            },
            onClickPin () {
                this.$emit('update:isFixedVarMenu', !this.isFixedVarMenu)
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
$localBorderColor: #dcdee5;
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
    .add-variable {
        margin: 30px 30px 20px 28px;
        .add-variable-btn {
            width: 90px;
        }
        .toggle-system-var {
            float: right;
            margin-top: 4px;
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
        &.quote-info {
            margin-left: 0px;
        }
    }
    .panel-fixed-pin {
        position: absolute;
        top: 16px;
        right: 30px;
        width: 32px;
        height: 32px;
        line-height: 32px;
        border: 1px solid #c4c6cc;
        border-radius: 2px;
        font-size: 14px;
        text-align: center;
        color: #999999;
        cursor: pointer;
        z-index: 1;
        &:hover {
            color: #707379;
        }
        &.actived {
            color: #52699d;
        }
    }
    .global-variable-content {
        position: relative;
        margin: 0 28px 30px;
        height: calc(100% - 82px);
        border: 1px solid $localBorderColor;
    }
    .variable-header, .variable-list {
        position: relative;
        font-size: 12px;
        .col-name {
            margin-left: 50px;
            width: 242px;
        }
        .col-key {
            width: 174px;
        }
        .col-attributes {
            width: 77px;
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
            width: 58px;
        }
        .col-quote {
            width: 54px;
        }
    }
    .variable-header {
        height: 42px;
        line-height: 42px;
        background: #fafbfd;
        border-bottom: 1px solid $localBorderColor;
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
        z-index: 1;
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
        height: calc(100% - 50px);
        overflow-x: hidden;
        overflow-y: auto;
        @include scrollbar;
    }
    .empty-variable-tip {
        margin-top: 120px;
        /deep/ .no-data-wording {
            font-size: 12px;
        }
    }
}
</style>
