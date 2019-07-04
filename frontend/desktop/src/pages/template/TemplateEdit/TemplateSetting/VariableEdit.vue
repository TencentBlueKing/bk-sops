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
    <div class="variable-edit-wrapper" @click="e => e.stopPropagation()">
        <ul class="form-list">
            <li class="form-item clearfix">
                <label class="required">{{ i18n.name }}</label>
                <div class="form-content">
                    <bk-input
                        name="variableName"
                        v-model="theEditingData.name"
                        v-validate="variableNameRule">
                    </bk-input>
                    <span v-show="errors.has('variableName')" class="common-error-tip error-msg">{{ errors.first('variableName') }}</span>
                </div>
            </li>
            <li class="form-item clearfix">
                <label class="required">KEY</label>
                <div class="form-content">
                    <bk-input
                        name="variableKey"
                        v-model="theEditingData.key"
                        v-validate="variableKeyRule"
                        :disabled="isDisabledValType">
                    </bk-input>
                    <span v-show="errors.has('variableKey')" class="common-error-tip error-msg">{{ errors.first('variableKey') }}</span>
                </div>
            </li>
            <li class="form-item clearfix">
                <label class="form-label">{{ i18n.desc }}</label>
                <div class="form-content">
                    <bk-input type="textarea" v-model="theEditingData.desc"></bk-input>
                </div>
            </li>
            <li class="form-item clearfix">
                <label class="required">{{ i18n.type }}</label>
                <div class="form-content">
                    <bk-select
                        v-model="currentValType"
                        :disabled="isDisabledValType"
                        @change="onValTypeChange">
                        <template v-if="isDisabledValType">
                            <bk-option
                                v-for="(option, optionIndex) in valTypeList"
                                :key="optionIndex"
                                :id="option.code"
                                :name="option.name">
                            </bk-option>
                        </template>
                        <template v-else>
                            <bk-option-group
                                v-for="(group, groupIndex) in valTypeList"
                                :key="groupIndex"
                                :name="group.name">
                                <bk-option
                                    v-for="(option, optionIndex) in group.children"
                                    :key="optionIndex"
                                    :id="option.code"
                                    :name="option.name">
                                </bk-option>
                            </bk-option-group>
                        </template>
                    </bk-select>
                </div>
            </li>
            <li class="form-item clearfix" v-if="!isOutputVar">
                <label class="form-label">{{ theEditingData.is_meta ? i18n.meta : i18n.default }}</label>
                <div class="form-content" v-bkloading="{ isLoading: atomConfigLoading, opacity: 1 }">
                    <template v-if="!atomConfigLoading && renderConfig.length">
                        <RenderForm
                            ref="renderForm"
                            v-if="!isEditInDialog"
                            :scheme="renderConfig"
                            :form-option="renderOption"
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
            <li class="form-item clearfix" v-show="theEditingData.custom_type === 'input'">
                <label class="form-label">{{ i18n.validation }}</label>
                <div class="form-content">
                    <bk-input
                        name="valueValidation"
                        v-model="theEditingData.validation"
                        v-validate="validationRule"
                        @blur="onBlurValidation">
                    </bk-input>
                    <span v-show="errors.has('valueValidation')" class="common-error-tip error-msg">{{errors.first('valueValidation')}}</span>
                </div>
            </li>
            <li class="form-item clearfix">
                <label class="required">{{ i18n.show }}</label>
                <div class="form-content">
                    <bk-select
                        v-model="theEditingData.show_type"
                        :disabled="isOutputVar"
                        @change="onValShowTypeChange">
                        <bk-option
                            v-for="(option, index) in showTypeList"
                            :key="index"
                            :id="option.id"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                </div>
            </li>
        </ul>
        <div class="action-wrapper">
            <bk-button
                theme="success"
                size="small"
                :disabled="atomConfigLoading"
                @click.stop="saveVariable">
                {{ i18n.save }}
            </bk-button>
            <bk-button
                theme="default"
                size="small"
                @click.stop="cancelVariable">
                {{ i18n.cancel }}
            </bk-button>
        </div>
        <VariableEditDialog
            :is-show="isEditDialogShow"
            :render-config="renderConfig"
            :render-option="renderOption"
            :render-data="renderData"
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
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import VariableEditDialog from './VariableEditDialog.vue'

    const SHOW_TYPE_LIST = [
        { id: 'show', name: gettext('显示') },
        { id: 'hide', name: gettext('隐藏') }
    ]

    const VALIDATE_SET = ['required', 'custom', 'regex']

    export default {
        name: 'VariableEdit',
        components: {
            RenderForm,
            VariableEditDialog
        },
        props: ['variableData', 'isNewVariable', 'variableTypeList'],
        data () {
            const theEditingData = tools.deepClone(this.variableData)
            const renderData = ('value' in theEditingData) ? { 'customVariable': theEditingData.value } : {}
            return {
                i18n: {
                    name: gettext('名称'),
                    desc: gettext('说明'),
                    default: gettext('默认值'),
                    meta: gettext('配置'),
                    edit_table: gettext('编辑表格'),
                    validation: gettext('正则校验'),
                    type: gettext('类型'),
                    show: gettext('显示'),
                    save: gettext('保存'),
                    cancel: gettext('取消')
                },
                atomConfigLoading: false,
                bkMessageInstance: null,
                showTypeList: [...SHOW_TYPE_LIST],
                theEditingData,
                metaTag: undefined, // 元变量tag名称
                varType: '', // 变量类型，general、meta
                renderData,
                renderConfig: [],
                renderOption: {
                    showHook: false,
                    showGroup: false,
                    showLabel: false,
                    showVarList: true,
                    validateSet: ['custom', 'regex']
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
            isEditInDialog () {
                return this.renderConfig[0].type
                    && (this.renderConfig[0].type === 'datatable' || this.renderConfig[0].type === 'ip_selector')
            },
            isDisabledValType () {
                const { source_type } = this.theEditingData
                return source_type === 'component_inputs' || source_type === 'component_outputs'
            },
            isOutputVar () {
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
                return this.isDisabledValType ? [{ code: 'component', name: gettext('组件') }] : [...this.variableTypeList]
            },
            /**
             * 变量配置项code
             */
            atomType () {
                const { custom_type, source_tag, source_type } = this.theEditingData

                if (source_type === 'component_inputs') {
                    return custom_type || source_tag.split('.')[0]
                } else {
                    return custom_type
                }
            },
            validateSet () {
                return this.theEditingData.show_type ? VALIDATE_SET.slice(1) : VALIDATE_SET
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
                    /* eslint-disable */
                    new RegExp(value)
                    /* eslint-enable */
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
            const { is_meta, custom_type } = this.theEditingData

            // 若当前编辑变量为元变量，则取meta_tag
            if (is_meta) {
                this.variableTypeList[1].children.some(item => {
                    if (item.code === custom_type) {
                        this.metaTag = item.meta_tag
                        return true
                    }
                })
            }
            // 非输出参数变量需要加载标准插件配置项
            if (!this.isOutputVar) {
                this.getAtomConfig()
            }
        },
        methods: {
            ...mapMutations('atomForm/', [
                'setAtomConfig'
            ]),
            ...mapActions('atomForm/', [
                'loadAtomConfig'
            ]),
            ...mapMutations('template/', [
                'addVariable',
                'editVariable',
                'deleteVariable'
            ]),
            /**
             * 加载表单标准插件配置文件
             */
            async getAtomConfig () {
                const { source_tag, custom_type } = this.theEditingData
                const tagStr = this.metaTag ? this.metaTag : source_tag

                // 兼容旧数据自定义变量勾选为输入参数 source_tag 为空
                const atom = tagStr.split('.')[0] || custom_type

                const isMeta = this.varType === 'meta' ? 1 : 0
                if ($.atoms[atom]) {
                    this.getRenderConfig()
                    return
                }
                this.atomConfigLoading = true
                let classify = ''
                if (this.theEditingData.custom_type) {
                    classify = 'variable'
                } else {
                    classify = 'component'
                }
                try {
                    await this.loadAtomConfig({ atomType: this.atomType, classify, isMeta: isMeta })
                    this.setAtomConfig({ atomType: atom, configData: $.atoms[atom] })
                    this.getRenderConfig()
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.atomConfigLoading = false
                }
            },
            getRenderConfig () {
                const { source_tag, custom_type } = this.theEditingData
                const tagStr = this.metaTag || source_tag
                let [atom, tag] = tagStr.split('.')

                // 兼容旧数据自定义变量勾选为输入参数 source_tag 为空
                if (custom_type) {
                    atom = atom || custom_type
                    tag = tag || custom_type
                }
                
                const atomConfig = this.atomFormConfig[atom]
                const config = tools.deepClone(atomFilter.formFilter(tag, atomConfig))
                config.tag_code = 'customVariable'

                this.renderConfig = [config]
            },
            getValidateSet () {
                return this.theEditingData.show_type === 'show' ? VALIDATE_SET.slice(1) : VALIDATE_SET
            },
            /**
             * 切换变量类型
             */
            onValTypeChange (val) {
                let data
                this.valTypeList.some(group => {
                    const option = group.children.find(item => item.code === val)
                    if (option) {
                        data = option
                        return true
                    }
                })
                console.log(data)
                this.renderData = {}
                // input 类型需要正则校验
                if (val === 'input') {
                    this.theEditingData.validation = '^.+$'
                } else {
                    this.theEditingData.validation = ''
                }

                this.theEditingData.source_tag = data.tag
                this.theEditingData.is_meta = data.type === 'meta'
                this.metaTag = data.meta_tag
                this.varType = data.type

                this.getAtomConfig()
            },
            /**
             * 变量显示/隐藏切换
             */
            onValShowTypeChange (showType, data) {
                this.theEditingData.show_type = showType
                const validateSet = this.getValidateSet()
                this.$set(this.renderOption, 'validateSet', validateSet)
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
                    const constantsLength = Object.keys(this.constants).length
                    
                    // 名称、key等校验，renderform表单校验
                    if (this.$refs.renderForm) {
                        formValid = this.$refs.renderForm.validate()
                    }
                    if (this.atomConfigLoading || !result || !formValid) {
                        const index = this.isNewVariable ? constantsLength : this.theEditingData.index
                        this.$emit('scrollPanelToView', index)
                        return false
                    }

                    const variable = this.theEditingData
                    let varValue = {}
                    this.theEditingData.name = this.theEditingData.name.trim()

                    // value为空且不渲染RenderForm组件的变量取表单默认值
                    if (this.renderData.hasOwnProperty('customVariable')) {
                        varValue = this.renderData
                    } else {
                        varValue = atomFilter.getFormItemDefaultValue(this.renderConfig)
                    }
                    
                    // 变量key值格式统一
                    if (!/^\$\{\w+\}$/.test(variable.key)) {
                        variable.key = '${' + variable.key + '}'
                    }

                    this.theEditingData.value = varValue['customVariable']
                    
                    this.$emit('onChangeEdit', false)

                    if (this.isNewVariable) { // 新增变量
                        variable.index = constantsLength
                        this.addVariable(tools.deepClone(variable))
                    } else { // 编辑变量
                        this.editVariable({ key: this.variableData.key, variable })
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
$localBorderColor: #d8e2e7;
.variable-edit-wrapper {
    padding: 20px;
    font-size: 14px;
    text-align: left;
    background: $whiteThinBg;
    border-bottom: 1px solid $localBorderColor;
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
        width: 60px;
        margin-top: 8px;
        font-size: 12px;
        color: $greyDefault;
        text-align: right;
        word-wrap: break-word;
        word-break: break-all;
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
        font-size: 12px;
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
