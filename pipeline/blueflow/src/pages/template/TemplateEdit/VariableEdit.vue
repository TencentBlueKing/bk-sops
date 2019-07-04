/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="variable-edit-wrapper">
        <ul class="form-list">
            <li class="form-item clearfix">
                <label class="form-label">{{ i18n.name }}</label>
                <div class="form-content">
                    <BaseInput
                        type="text"
                        name="variableName"
                        v-model="theEditingData.name"
                        v-validate="variableNameRule">
                    </BaseInput>
                    <span v-show="errors.has('variableName')" class="common-error-tip error-msg">{{ errors.first('variableName') }}</span>
                </div>
            </li>
            <li class="form-item clearfix">
                <label class="form-label">KEY</label>
                <div class="form-content">
                    <BaseInput
                        type="text"
                        name="variableKey"
                        v-model="theEditingData.key"
                        v-validate="variableKeyRule"
                        :disabled="isDisabledValType">
                    </BaseInput>
                    <span v-show="errors.has('variableKey')" class="common-error-tip error-msg">{{ errors.first('variableKey') }}</span>
                </div>
            </li>
            <li class="form-item clearfix">
                <label class="form-label">{{ i18n.desc }}</label>
                <div class="form-content">
                    <textarea v-model="theEditingData.desc"></textarea>
                </div>
            </li>
            <li class="form-item clearfix">
                <label class="form-label">{{ i18n.type }}</label>
                <div class="form-content">
                    <bk-selector
                        :list="valTypeList"
                        :selected.sync="currentValType"
                        :disabled="this.isDisabledValType"
                        @item-selected="onValTypeChange">
                    </bk-selector>
                </div>
            </li>
            <li class="form-item clearfix" v-show="isShowDefault">
                <label class="form-label">{{ i18n.default }}</label>
                <div class="form-content" v-if="!isDataTable">
                    <el-input
                        type="text"
                        name="defaultValue"
                        v-if="theEditingData.custom_type === 'input'"
                        v-model="theEditingData.value"
                        v-validate="defaultValueRule">
                    </el-input>
                    <span
                        v-if="theEditingData.custom_type === 'input' && errors.has('defaultValue')"
                        class="common-error-tip error-msg">
                        {{errors.first('defaultValue')}}
                    </span>
                    <el-input
                        type="textarea"
                        v-if="theEditingData.custom_type === 'textarea'"
                        v-model="theEditingData.value">
                    </el-input>
                    <el-date-Picker
                        type="datetime"
                        format="yyyy-MM-dd HH:mm:ss"
                        value-format="yyyy-MM-dd HH:mm:ss"
                        v-if="theEditingData.custom_type === 'datetime'"
                        v-model="theEditingData.value">
                    </el-date-Picker>
                    <el-input
                        type="number"
                        v-if="theEditingData.custom_type === 'int'"
                        v-model="theEditingData.value">
                    </el-input>
                    <RenderForm
                        ref="renderForm"
                        v-if="isRenderAtomForm"
                        :config="renderConfig"
                        :option="renderOption"
                        :data="renderData"
                        @dataChange="onInputDataChange">
                    </RenderForm>
                </div>
                <div class="form-content" v-else>
                    <a class="edit-table" @click="onShowEditDialog">{{ i18n.edit_table }}</a>
                </div>
            </li>
            <li class="form-item clearfix" v-if="theEditingData.custom_type === 'input'">
                <label class="form-label">{{ i18n.validation }}</label>
                <div class="form-content">
                    <el-input
                        name="valueValidation"
                        v-model="theEditingData.validation"
                        v-validate="validationRule">
                    </el-input>
                    <span v-show="errors.has('valueValidation')" class="common-error-tip error-msg">{{errors.first('valueValidation')}}</span>
                </div>
            </li>
            <li class="form-item clearfix">
                <label class="form-label">{{ i18n.show }}</label>
                <div class="form-content">
                    <bk-selector
                        :list="showTypeList"
                        :selected.sync="theEditingData.show_type"
                        :disabled="this.isDisabledShowType"
                        @item-selected="onValShowTypeChange">
                    </bk-selector>
                </div>
            </li>
        </ul>
        <div class="action-wrapper">
            <bk-button type="success" class="common-green-btn" @click.stop="saveEdit">{{ i18n.save }}</bk-button>
            <bk-button class="common-default-btn" type="default" @click.stop="cancelEdit">{{ i18n.cancel }}</bk-button>
        </div>
        <VariableEditDialog
            :isShow="isEditDialogShow"
            :renderConfig="renderConfig"
            :renderOption="renderOption"
            :renderData="renderData"
            @onConfirmDialogEdit="onConfirmDialogEdit"
            @onCancelDialogEdit="onCancelDialogEdit">
        </VariableEditDialog>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapActions, mapMutations } from 'vuex'
import { Validator } from 'vee-validate'
import { NAME_REG } from '@/constants/index.js'
import { errorHandler } from '@/utils/errorHandler.js'
import tools from '@/utils/tools.js'
import atomFilter from '@/utils/atomFilter.js'
import { checkDataType } from '@/utils/checkDataType.js'
import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
import BaseInput from '@/components/common/base/BaseInput.vue'
import VariableEditDialog from './VariableEditDialog.vue'

const CUSTOM_VAL_SHOULD_RENDER_FORM = { // 自定义变量需要加载原子配置项
    'ip': 'var_ip_picker.ip_picker'
}
const VAL_TYPE_LIST = [
    { id: "input", name: gettext("输入框") },
    { id: "textarea", name: gettext("文本框") },
    { id: "datetime", name: gettext("日期时间") },
    { id: "int", name: gettext("整数") },
    { id: "ip", name: gettext("IP选择器") }
]
const SHOW_TYPE_LIST = [
    { id: 'show', name: gettext('显示') },
    { id: 'hide', name: gettext('隐藏') }
]
export default {
    name: 'VariableEdit',
    components: {
        RenderForm,
        VariableEditDialog,
        BaseInput
    },
    props: ['variableData', 'isNewVariable'],
    data () {
        const theEditingData = JSON.parse(JSON.stringify(this.variableData))
        return {
            i18n: {
                name: gettext("名称"),
                desc: gettext("说明"),
                default: gettext("默认值"),
                edit_table: gettext("编辑表格"),
                validation: gettext("校验规则"),
                type: gettext("类型"),
                show: gettext("显示"),
                save: gettext("保存"),
                cancel: gettext("取消")
            },
            atomConfigFeching: false,
            bkMessageInstance: null,
            showTypeList: [...SHOW_TYPE_LIST],
            theEditingData,
            renderOption: {
                showHook: false,
                showGroup: false,
                showLabel: false
            },
            isEditDialogShow: false,
            variableNameRule: {
                required: true,
                max: 20,
                regex: NAME_REG
            },
            variableKeyRule: {
                required: true,
                max: 20,
                regex: /(^\$\{\w+\}$)|(^\w+$)/,
                keyRepeat: true
            },
            // 默认值校验规则（按照用户编辑的合法正则表达式校验）
            defaultValueRule: {
                required: theEditingData.show_type === 'hide',
                customValueCheck: true
            },
            // 正则校验规则
            validationRule: {
                validReg: true
            }
        }
    },
    computed: {
        ...mapState({
            'atomFormConfig': state => state.atomForm.config,
            'constants': state => state.template.constants
        }),
        isShowDefault () {
            const { custom_type, source_type } = this.theEditingData
            return source_type !== 'component_outputs'
        },
        // 是否调用 RenderForm 组件渲染表单
        isRenderAtomForm () {
            const { custom_type, source_type } = this.theEditingData
            return (source_type === 'component_inputs' && !custom_type) || (custom_type in CUSTOM_VAL_SHOULD_RENDER_FORM)
        },
        isDisabledValType () {
            const { source_type } = this.theEditingData
            return source_type === 'component_inputs' || source_type === 'component_outputs'
        },
        isDisabledShowType () {
            return this.theEditingData.source_type === 'component_outputs'
        },
        // 默认值为 datatable 类型
        isDataTable () {
            return !!this.renderConfig && this.renderConfig[0].type === 'datatable'
        },
        currentValType: {
            get () {
                return this.isDisabledValType ? 'component' : this.theEditingData.custom_type
            },
            set (val) {
                this.theEditingData.custom_type = val
            }
        },
        valTypeList () {
            return this.isDisabledValType ? [{ id: "component", name: gettext("组件")}] : [...VAL_TYPE_LIST]
        },
        atomType () {
            const { custom_type, source_type, source_tag } = this.theEditingData
            if (source_tag) {
                return source_tag.split('.')[0]
            } else if (custom_type in CUSTOM_VAL_SHOULD_RENDER_FORM) {
                return CUSTOM_VAL_SHOULD_RENDER_FORM[custom_type].split('.')[0]
            }
            return ''
        },
        renderConfig () {
            const { source_tag, custom_type } = this.theEditingData
            const atomConfig = this.atomFormConfig[this.atomType]
            if (atomConfig && this.isRenderAtomForm && !(custom_type in CUSTOM_VAL_SHOULD_RENDER_FORM)){
                const tag_code = source_tag.split('.')[1]
                return [tools.deepClone(atomFilter.formFilter(tag_code, atomConfig))]
            }
            return atomConfig
        },
        renderData () {
            let data = this.theEditingData.value
            if (!this.theEditingData.value && CUSTOM_VAL_SHOULD_RENDER_FORM[this.currentValType] && this.renderConfig) {
                data = atomFilter.getFormItemDefaultValue(this.renderConfig[0])
            }
            return {
                hook: {},
                value: data
            }
        }
    },
    watch: {
        variableData: {
            handler: function (val) {
                this.theEditingData = JSON.parse(JSON.stringify(val))
            },
            deep: true
        },
        'theEditingData.show_type' (val) {
            if (val === 'hide') {
                this.defaultValueRule = {
                    required: true,
                    customValueCheck: true
                }
            } else {
                this.defaultValueRule = {
                    customValueCheck: true
                }
            }
        }
    },
    created () {
        const self = this
        this.validator = new Validator({})
        // 注册变量 key 校验规则
        this.validator.extend('keyRepeat', (value) => {
            value = /^\$\{\w+\}$/.test(value) ? value : '${' + value + '}'
            if (this.variableData.key === value) {
                return true
            }
            if (value in this.constants) {
                return false
            }
            return true
        })
        // 注册正则表达式校验规则
        this.validator.extend('validReg', (value) => {
            try {
                const reg = new RegExp(value)
            } catch (e) {
                console.error(e)
                return false
            }
            return true
        })
        // 注册默认值校验规则
        this.validator.extend('customValueCheck', (value) => {
            try {
                const reg = new RegExp(this.theEditingData.validation)
                if (!reg.test(value)) {
                    return false
                }
                return true
            } catch (e) {
                console.error(e)
                return false
            }
        })
    },
    mounted () {
        this.isRenderAtomForm && this.getAtomConfig()
    },
    methods: {
        ...mapMutations ('atomForm/', [
            'setAtomConfig'
        ]),
        ...mapActions('atomForm/', [
            'loadAtomConfig'
        ]),
        ...mapMutations ('template/', [
            'addVariable',
            'editVariable',
            'deleteVariable'
        ]),
        onValTypeChange (id, data) {
            this.theEditingData.value = ''
            // input 类型需要校验规则
            if (id === 'input') {
                this.theEditingData.validation = '^.+$'
            } else {
                this.theEditingData.validation = ''
            }
            // ip 选择器类型需要增加 source_tag 字段
            if (CUSTOM_VAL_SHOULD_RENDER_FORM[this.theEditingData.custom_type]) {
                this.theEditingData.source_tag = CUSTOM_VAL_SHOULD_RENDER_FORM[this.theEditingData.custom_type]
            } else {
                this.theEditingData.source_tag = ''
            }

            if (CUSTOM_VAL_SHOULD_RENDER_FORM[id]) {
                if ($.atoms[this.atomType]) return
                this.getAtomConfig()
            }
        },
        onValShowTypeChange (id, data) {
            this.theEditingData.show_type = id
        },
        /**
         * 加载表单原子配置文件
         */
        async getAtomConfig () {
            this.atomConfigFeching = true
            try {
                await this.loadAtomConfig({ atomType: this.atomType })
                this.setAtomConfig({atomType: this.atomType, configData: $.atoms[this.atomType]})
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.atomConfigFeching = false
            }
        },
        /**
         * RenderForm 表单项 value 值 change 时同步
         */
        onInputDataChange (val, tagCode) {
            const variable = this.theEditingData
            if (checkDataType(this.renderData.value) === 'Object') {
                this.$set(this.renderData.value, tagCode, val)
            } else {
                this.renderData.value = val
            }
        },
        /**
         * datatable 编辑弹窗
         */
        onShowEditDialog () {
            this.isEditDialogShow = true
        },
        onConfirmDialogEdit (formData) {
            this.isEditDialogShow = false
            this.renderData.value = formData.value
        },
        onCancelDialogEdit () {
            this.isEditDialogShow = false
        },
        /**
         * 校验并保存变量
         */
        saveEdit () {
            this.$validator.validateAll().then(result => {
                let formValid = true
                if (this.$refs.renderForm) {
                    if (!this.value && this.theEditingData.show_type === 'show') {
                        formValid = true
                    } else {
                        formValid = this.$refs.renderForm.validate()
                    }
                }
                if (!result || !formValid) return

                this.theEditingData.value = this.renderData.value
                const variable = this.theEditingData
                if (!/^\$\{\w+\}$/.test(variable.key)) {
                    variable.key = "${" + variable.key + "}"
                }

                this.$emit('onChangeEdit', false)
                if (this.isNewVariable) {
                    variable.index = Object.keys(this.constants).length
                    this.addVariable(Object.assign(variable))
                } else {
                    this.editVariable({key: this.variableData.key, variable})
                }
            })
        },
        cancelEdit () {
            this.$emit('onChangeEdit', false)
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.variable-edit-wrapper {
    padding: 20px;
    font-size: 14px;
    text-align: left;
    background: $whiteThinBg;
    border-bottom: 1px solid $blueDefault;
    cursor: auto;
}
.error-msg {
    margin-top: 10px;
}
.form-item {
    margin: 15px 0;
    &:first-child {
        margin-top: 0;
    }
}
.form-label {
    float: left;
    margin-top: 8px;
    padding-right: 20px;
    width: 80px;
    text-align: right;
}
.form-content {
    margin-left: 80px;
    input {
        padding: 0 10px;
        width: 100%;
        height: 36px;
        line-height: 36px;
        font-size: 14px;
        border: 1px solid $formBorderColor;
        border-radius: 2px;
        outline: none;
        &:focus {
            border-color: $blueDefault;
        }
        &[disabled] {
            color: #aaa;
            cursor: not-allowed;
            background: #fafafa;
        }
    }
    textarea {
        padding: 10px;
        width: 100%;
        height: 70px;
        border: 1px solid $formBorderColor;
        border-radius: 2px;
        outline: none;
        resize: none;
        &:hover {
            border-color: #c0c4cc;
        }
        &:focus {
            border-color: $blueDefault;
        }
        @include scrollbar;
    }
    .el-input {
        width: 100%;
        .el-input__inner {
            border: 1px solid $formBorderColor;
        }
    }
    /deep/ .tag-form {
        margin-left: 0;
    }
    .edit-table {
        height: 36px;
        line-height: 36px;
        color: $blueDefault;
        cursor: pointer;
    }
}
.action-wrapper {
    text-align: center;
    button:first-child {
        margin-right: 10px;
    }
}
</style>
