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
    <div class="variable-edit-wrapper">
        <ul class="form-list">
            <li class="form-item clearfix">
                <label class="required">{{ i18n.name }}</label>
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
                <label class="required">KEY</label>
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
                <label class="required">{{ i18n.type }}</label>
                <div class="form-content">
                    <bk-selector
                        :list="valTypeList"
                        :has-children='true'
                        :selected.sync="currentValType"
                        :disabled="this.isDisabledValType"
                        @item-selected="onValTypeChange">
                    </bk-selector>
                </div>
            </li>
            <li class="form-item clearfix" v-if="isShowDefault">
                <label class="form-label">{{ theEditingData.is_meta ? i18n.meta : i18n.default }}</label>
                <div class="form-content" v-bkloading="{isLoading: atomConfigLoading, opacity: 1}">
                    <template v-if="!atomConfigLoading && renderConfig.length">
                        <RenderForm
                            ref="renderForm"
                            v-if="!isEditInDialog"
                            :scheme="renderConfig"
                            :formOption="renderOption"
                            v-model="renderData">
                        </RenderForm>
                        <a
                            v-else
                            class="edit-table"
                            @click="onShowEditDialog">
                            {{ i18n.edit_table }}
                        </a>
                    </template>
                </div>
            </li>
            <li class="form-item clearfix" v-if="theEditingData.custom_type === 'input'">
                <label class="form-label">{{ i18n.validation }}</label>
                <div class="form-content">
                    <el-input
                        name="valueValidation"
                        v-model="theEditingData.validation"
                        v-validate="validationRule"
                        @blur="onBlurValidation">
                    </el-input>
                    <span v-show="errors.has('valueValidation')" class="common-error-tip error-msg">{{errors.first('valueValidation')}}</span>
                </div>
            </li>
            <li class="form-item clearfix">
                <label class="required">{{ i18n.show }}</label>
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
            <bk-button
                type="success"
                size="small"
                @click.stop="saveVariable">
                {{ i18n.save }}
            </bk-button>
            <bk-button
                type="default"
                size="small"
                @click.stop="cancelVariable">
                {{ i18n.cancel }}
            </bk-button>
        </div>
        <VariableEditDialog
            v-if="isEditDialogShow"
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
import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
import { errorHandler } from '@/utils/errorHandler.js'
import tools from '@/utils/tools.js'
import atomFilter from '@/utils/atomFilter.js'
import { checkDataType } from '@/utils/checkDataType.js'
import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
import BaseInput from '@/components/common/base/BaseInput.vue'
import VariableEditDialog from './VariableEditDialog.vue'
const ATOM_FORM = {
    'ip': 'var_ip_picker.ip_picker',
    'password': 'password.password',
    'select': 'select.select',
    'ip_selector': 'var_cmdb_ip_selector.ip_selector'
}
const META_ATOM_FORM = {
    'select': 'select_meta'
}
// const META_FORM_TYPE = {
//     'var_ip_picker': 'var_ip_picker',
//     'password': 'password',
//     'select': 'select_meta'
// }
const VAL_TYPE_LIST = [
    {
        name: gettext('普通变量'),
        children: [
            { id: "input", name: gettext("输入框") },
            { id: "textarea", name: gettext("文本框") },
            { id: "datetime", name: gettext("日期时间") },
            { id: "int", name: gettext("整数") },
            { id: "ip", name: gettext("IP选择器(简单版)") },
            { id: "password", name: gettext("密码")}
        ]
    },
    {
        name: gettext('元变量'),
        children: [
            { id: "select", name: gettext("下拉框")}
        ]
    }
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
        const theEditingData = tools.deepClone(this.variableData)
        const renderData = ('value' in theEditingData) ? {'customVariable': theEditingData.value} : {}
        return {
            i18n: {
                name: gettext("名称"),
                desc: gettext("说明"),
                default: gettext("默认值"),
                meta: gettext("配置"),
                edit_table: gettext("编辑表格"),
                validation: gettext("正则校验"),
                type: gettext("类型"),
                show: gettext("显示"),
                save: gettext("保存"),
                cancel: gettext("取消")
            },
            atomConfigLoading: false,
            bkMessageInstance: null,
            showTypeList: [...SHOW_TYPE_LIST],
            theEditingData,
            renderData,
            renderConfig: [],
            renderOption: {
                showHook: false,
                showGroup: false,
                showLabel: false,
                showVarList: true
            },
            isEditDialogShow: false,
            // 变量名称校验规则
            variableNameRule: {
                required: true,
                max: STRING_LENGTH.VARIABLE_NAME_MAX_LENGTH,
                regex: NAME_REG
            },
            // 变量 Key 校验规则
            variableKeyRule: {
                required: true,
                max: STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH,
                regex: /(^\${[a-zA-Z_]\w*}$)|(^[a-zA-Z_]\w*$)/, // 合法变量key正则，eg:${fsdf_f32sd},fsdf_f32sd
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
        // 是否渲染标准插件表单
        isRenderAtomForm () {
            const { custom_type, source_type } = this.theEditingData
            return (source_type === 'component_inputs' && !custom_type) || (custom_type in ATOM_FORM)
        },
        isEditInDialog () {
            return this.renderConfig[0].type &&
                (this.renderConfig[0].type === 'datatable' || this.renderConfig[0].type === 'ip_selector')
        },
        isDisabledValType () {
            const { source_type } = this.theEditingData
            return source_type === 'component_inputs' || source_type === 'component_outputs'
        },
        isDisabledShowType () {
            return this.theEditingData.source_type === 'component_outputs'
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
            } else if (custom_type in ATOM_FORM) {
                return ATOM_FORM[custom_type].split('.')[0]
            }
            return ''
        }
    },
    watch: {
        variableData: {
            handler: function (val) {
                this.theEditingData = tools.deepClone(val)
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
        if (this.isRenderAtomForm) {
            this.getAtomConfig()
        } else {
            this.getRenderConfig()
        }
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
        /**
         * 加载表单标准插件配置文件
         */
        async getAtomConfig () {
            let realAtomType = META_ATOM_FORM[this.atomType] || this.atomType
            let isMeta = META_ATOM_FORM[this.atomType] ? 1 : 0
            if ($.atoms[realAtomType]) {
                this.getRenderConfig()
                return
            }

            this.atomConfigLoading = true
            try {
                await this.loadAtomConfig({ atomType: this.atomType, isMeta: isMeta })
                this.setAtomConfig({atomType: realAtomType, configData: $.atoms[realAtomType]})
                this.getRenderConfig()
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.atomConfigLoading = false
            }
        },
        getRenderConfig () {
            const { source_tag, custom_type } = this.theEditingData
            let realAtomType = META_ATOM_FORM[this.atomType] || this.atomType
            let atom = this.atomFormConfig[realAtomType]
            let config
            if (this.isRenderAtomForm) {
                if (atom && this.isRenderAtomForm && !(custom_type in ATOM_FORM)){
                    const tag_code = source_tag.split('.')[1]
                    config = tools.deepClone(atomFilter.formFilter(tag_code, atom))
                    config.tag_code = 'customVariable'
                } else {
                    config = tools.deepClone(atom[0])
                    config.tag_code = 'customVariable'
                }
            } else {
                config = {
                    tag_code: 'customVariable',
                    type: custom_type,
                    attrs: {}
                }
                if (custom_type === 'input') {
                    config.attrs.validation = []
                    if (this.theEditingData.show_type === 'hide') {
                        config.attrs.validation.push({ type: 'required'})
                    }
                    config.attrs.validation.push({
                        type: 'regex',
                        args: this.theEditingData.validation,
                        error_message: gettext('默认值不满足正则校验')
                    })
                }
            }

            this.renderConfig = [config]
        },
        /**
         * 切换变量类型
         */
        onValTypeChange (id, data) {
            this.renderData = {}
            // input 类型需要正则校验
            if (id === 'input') {
                this.theEditingData.validation = '^.+$'
            } else {
                this.theEditingData.validation = ''
            }
            // 普通原子类型变量需要增加 source_tag 字段
            if (ATOM_FORM[this.theEditingData.custom_type]) {
                this.theEditingData.source_tag = ATOM_FORM[this.theEditingData.custom_type]
            } else {
                this.theEditingData.source_tag = ''
            }

            // 元变量需要增加 meta 字段
            if (META_ATOM_FORM[this.theEditingData.custom_type]) {
                this.theEditingData.is_meta = true
            } else {
                this.theEditingData.is_meta = false
            }

            if (ATOM_FORM[id]) {
                this.getAtomConfig()
            } else {
                this.getRenderConfig()
            }
        },
        /**
         * 变量显示/隐藏切换
         */
        onValShowTypeChange (id, data) {
            this.theEditingData.show_type = id
            this.getRenderConfig()
        },
        onBlurValidation () {
            this.getRenderConfig()
        },
        /**
         * datatable 编辑弹窗
         */
        onShowEditDialog () {
            this.isEditDialogShow = true
        },
        onConfirmDialogEdit (formData) {
            this.isEditDialogShow = false
            this.theEditingData.value = formData['customVariable']
            this.renderData['customVariable'] = formData['customVariable']
        },
        onCancelDialogEdit () {
            this.isEditDialogShow = false
        },
        /**
         * 校验并保存变量
         */
        saveVariable () {
            return this.$validator.validateAll().then(result => {
                let formValid = true
                // 名称、key等校验，renderform表单校验
                if (this.$refs.renderForm) {
                    if (!this.value && this.theEditingData.show_type === 'show') {
                        formValid = true
                    } else {
                        formValid = this.$refs.renderForm.validate()
                    }
                }
                if (!result || !formValid) {
                    return false
                }

                const variable = this.theEditingData
                if (!/^\$\{\w+\}$/.test(variable.key)) {
                    variable.key = "${" + variable.key + "}"
                }
                this.$emit('onChangeEdit', false)
                this.theEditingData.name = this.theEditingData.name.trim()
                this.theEditingData.value = this.renderData['customVariable']
                if (this.isNewVariable) { // 新增
                    variable.index = Object.keys(this.constants).length
                    this.addVariable(Object.assign(variable))
                } else { // 编辑
                    this.editVariable({key: this.variableData.key, variable})
                }

                return true
            })
        },
        cancelVariable () {
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
    label {
        position: relative;
        float: left;
        min-width: 55px;
        margin-top: 8px;
        font-size: 14px;
        color: $greyDefault;
        text-align: right;
        &.required:before {
            content: '*';
            position: absolute;
            top: 0px;
            right: -10px;
            color: $redDark;
            font-family: "SimSun";
        }
    }
}
.form-content {
    margin-left: 80px;
    min-height: 36px;
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
    /deep/ .el-input {
        .el-input__inner {
            padding: 0 10px;
            height: 36px;
            line-height: 36px;
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
