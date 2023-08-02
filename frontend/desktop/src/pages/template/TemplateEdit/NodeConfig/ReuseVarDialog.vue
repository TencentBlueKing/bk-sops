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
    <bk-dialog
        ext-cls="common-dialog"
        :theme="'primary'"
        :mask-close="false"
        :render-directive="'if'"
        :header-position="'left'"
        :title="$t('变量配置')"
        :auto-close="false"
        :value="isShow"
        width="600"
        :cancel-text="$t('取消')"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div class="reuse-variable-dialog">
            <bk-alert
                v-if="sameKeyExist && variables.length === 0"
                style="margin-bottom: 14px;"
                type="warning"
                :title="$t('已存在相同KEY的变量，请新建变量')">
            </bk-alert>
            <bk-form
                ref="form"
                :model="formData"
                :rules="rules">
                <bk-form-item :label="$t('创建方式')">
                    <bk-select
                        v-model="createMethod"
                        :clearable="false"
                        @selected="handleCreateMethodChange">
                        <bk-option v-if="!sameKeyExist" id="autoCreate" :name="$t('自动创建')"></bk-option>
                        <bk-option v-if="variables.length > 0" id="reuse" :name="$t('变量复用')"></bk-option>
                        <bk-option id="manualCreate" :name="$t('手动创建')"></bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item v-if="createMethod === 'reuse'" :label="$t('复用变量')" property="reused">
                    <bk-select
                        v-model="formData.reused"
                        :popover-options="{ appendTo: 'parent' }"
                        :clearable="false">
                        <bk-option
                            v-for="(option, index) in variables"
                            :key="index"
                            :id="option.id"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <template v-else-if="['manualCreate', 'autoCreate'].includes(createMethod)">
                    <bk-form-item
                        property="name"
                        :label="$t('变量名称')"
                        :required="true">
                        <bk-input
                            name="variableName"
                            :disabled="createMethod === 'autoCreate'"
                            v-model="formData.name"
                            :maxlength="stringLength.VARIABLE_NAME_MAX_LENGTH"
                            :show-word-limit="true">
                        </bk-input>
                    </bk-form-item>
                    <bk-form-item
                        property="key"
                        :label="$t('变量KEY')"
                        :required="true">
                        <bk-input
                            name="variableKey"
                            :disabled="createMethod === 'autoCreate'"
                            v-model="formData.key"
                            :maxlength="stringLength.VARIABLE_KEY_MAX_LENGTH"
                            :show-word-limit="true">
                        </bk-input>
                    </bk-form-item>
                </template>
            </bk-form>
        </div>
    </bk-dialog>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'
    import { NAME_REG, STRING_LENGTH, INVALID_NAME_CHAR } from '@/constants/index.js'

    export default {
        name: 'ReuseVarDialog',
        props: {
            isShow: {
                type: Boolean,
                default: false
            },
            variables: { // 可复用变量列表
                type: Array,
                default: () => []
            },
            sameKeyExist: { // 全局变量中存在与被勾选表单相同key的变量
                type: Boolean,
                default: false
            },
            newVarKeyName: { // 自动创建变量时展示的key、name
                type: Object,
                default: () => {
                    return { key: '', name: '' }
                }
            }
        },
        data () {
            const $this = this
            const createMethod = this.getDefaultCreateMethod()
            const reused = this.variables.length > 0 ? this.variables[0].id : ''
            return {
                createMethod,
                formData: {
                    reused,
                    name: this.newVarKeyName.name,
                    key: this.newVarKeyName.key
                },
                stringLength: STRING_LENGTH,
                rules: {
                    name: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.VARIABLE_NAME_MAX_LENGTH,
                            message: i18n.t('变量名称长度不能超过') + STRING_LENGTH.VARIABLE_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        },
                        {
                            regex: NAME_REG,
                            message: i18n.t('变量名称不能包含') + INVALID_NAME_CHAR + i18n.t('非法字符'),
                            trigger: 'blur'
                        }
                    ],
                    key: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            validator (val) {
                                const reqLenth = /^\$\{\w+\}$/.test(val) ? (STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH + 3) : STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH
                                return val.length <= reqLenth
                            },
                            message: i18n.t('变量KEY值长度不能超过') + STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        },
                        {
                            // 合法变量key正则，eg:${fsdf_f32sd},fsdf_f32sd
                            regex: /(^\${(?!_env_|_system\.)[a-zA-Z_]\w*}$)|(^(?!_env_|_system\.)[a-zA-Z_]\w*$)/,
                            message: i18n.t('变量KEY由英文字母、数字、下划线组成，不允许使用系统变量及业务环境变量命名规则，且不能以数字开头'),
                            trigger: 'blur'
                        },
                        {
                            validator (val) {
                                const value = /^\$\{\w+\}$/.test(val) ? val : `\${${val}}`
                                if (value in $this.constants) {
                                    return false
                                }
                                return true
                            },
                            message: i18n.t('变量KEY值已存在'),
                            trigger: 'blur'
                        }
                    ]
                }
            }
        },
        computed: {
            ...mapState({
                constants: state => state.template.constants
            })
        },
        watch: {
            variables () {
                this.createMethod = this.getDefaultCreateMethod()
                this.formData.reused = this.variables.length > 0 ? this.variables[0].id : ''
            },
            newVarKeyName (val) {
                const { name, key } = val
                this.formData.name = name
                this.formData.key = key
            }
        },
        methods: {
            ...mapActions('template/', [
                'checkKey'
            ]),
            getDefaultCreateMethod () {
                if (this.variables.length > 0) {
                    return this.sameKeyExist ? 'reuse' : 'autoCreate'
                }
                return 'manualCreate'
            },
            handleCreateMethodChange (val) {
                if (val === 'autoCreate') {
                    this.formData.reused = ''
                    this.formData.name = this.newVarKeyName.name
                    this.formData.key = this.newVarKeyName.key
                } else if (val === 'reuse') {
                    this.formData.reused = this.variables.length > 0 ? this.variables[0].id : ''
                } else {
                    this.formData.reused = ''
                    this.formData.name = ''
                    this.formData.key = ''
                }
            },
            onConfirm () {
                const { name, key, reused } = this.formData

                if (this.createMethod === 'autoCreate') {
                    this.$emit('confirm', 'autoCreate', { name, key })
                } else if (this.createMethod === 'reuse') {
                    this.$emit('confirm', 'reuse', reused)
                } else {
                    this.$refs.form.validate().then(async (result) => {
                        if (result) {
                            const checkKeyResult = await this.checkKey({ key })
                            if (!checkKeyResult.result) {
                                this.$bkMessage({
                                    message: i18n.t('变量KEY为特殊标志符变量，请修改'),
                                    theme: 'warning'
                                })
                                return
                            }
                            this.$emit('confirm', 'manualCreate', { name, key })
                        }
                    })
                }
            },
            onCancel () {
                this.$emit('cancel')
            }
        }
    }
</script>
<style lang="scss" scoped>
    .reuse-variable-dialog {
        padding: 20px 30px 30px;
        .new-var-notice {
            margin-bottom: 10px;
            font-size: 14px;
            color: #ff9c01;
        }
        .bk-form:not(.bk-form-vertical) {
            /deep/ .bk-form-content {
                margin-right: 30px;
            }
        }
    }
</style>
