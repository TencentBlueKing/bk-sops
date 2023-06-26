<template>
    <bk-dialog
        width="800"
        ext-cls="common-dialog inject-variable-dialog"
        header-position="left"
        :mask-close="false"
        :auto-close="false"
        :render-directive="'if'"
        :title="$t('注入全局变量')"
        :value="isInjectVarDialogShow"
        data-test-id="taskExcute_form_injectVariableDialog"
        :cancel-text="$t('取消')"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div class="inject-variable-dialog-content">
            <ul class="variable-list">
                <li v-for="(variable, index) in variableList" :key="index" class="variable-item">
                    <bk-form class="key-form" :model="variable" :rules="variable.rules" ref="variableForm">
                        <bk-form-item :required="true" property="key">
                            <bk-input v-model="variable.key" :placeholder="$t('请输入变量的KEY,如${KEY}')"></bk-input>
                        </bk-form-item>
                        <bk-form-item :required="true" property="value" ref="variableValue">
                            <bk-input
                                v-model="variable.value"
                                :type="variable.type === 'number' ? 'number' : 'text'"
                                :placeholder="$t('请输入变量的值')">
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item :required="true" property="type">
                            <bk-select v-model="variable.type" :placeholder="$t('请选择变量值的类型')" @selected="onVarTypeSelected($event, index)">
                                <bk-option id="string" :name="$t('字符串')"></bk-option>
                                <bk-option id="number" :name="$t('整数')"></bk-option>
                                <bk-option id="object" :name="$t('字典')"></bk-option>
                            </bk-select>
                        </bk-form-item>
                    </bk-form>
                    <bk-icon class="plus-icon mr15 ml5" type="plus-circle-shape" @click="updateVarList()" />
                    <bk-icon class="minus-icon" type="minus-circle-shape" @click="updateVarList(index)" />
                </li>
            </ul>
        </div>
    </bk-dialog>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import tools from '@/utils/tools.js'
    import { STRING_LENGTH } from '@/constants/index.js'

    export default {
        name: 'injectVariableDialog',
        props: {
            isInjectVarDialogShow: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                variableList: [],
                rules: {
                    key: [
                        {
                            required: true,
                            message: i18n.t('变量KEY值不能为空'),
                            trigger: 'blur'
                        },
                        {

                            regex: /(^\${(?!_env_|_system\.)[a-zA-Z_]\w*}$)|(^(?!_env_|_system\.)[a-zA-Z_]\w*$)/,
                            message: i18n.t('变量KEY由英文字母、数字、下划线组成，不允许使用系统变量及业务环境变量命名规则，且不能以数字开头'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH,
                            message: i18n.t('变量KEY值长度不能超过') + STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        },
                        {
                            validator: (val) => {
                                return this.variableList.some(item => item.key === val)
                            },
                            message: i18n.t('变量KEY值已存在'),
                            trigger: 'blur'
                        }
                    ],
                    value: [
                        {
                            required: true,
                            message: i18n.t('变量Value值不能为空'),
                            trigger: 'blur'
                        }
                    ]
                }
            }
        },
        watch: {
            isInjectVarDialogShow (val) {
                if (val) {
                    this.getVaribaleList()
                } else {
                    this.variableList = []
                }
            }
        },
        methods: {
            getVaribaleList () {
                this.variableList.push({
                    key: '',
                    value: '',
                    type: 'string',
                    rules: tools.deepClone(this.rules)
                })
            },
            onVarTypeSelected (type, index) {
                const variableInfo = this.variableList[index]
                variableInfo.type = type
                if (variableInfo.type === 'string') {
                    variableInfo.rules = tools.deepClone(this.rules)
                } else {
                    variableInfo.rules.value.push({
                        validator: (val) => {
                            return variableInfo.type === 'object' ? this.checkIsJSON(val) : Number(val)
                        },
                        message: i18n.t('变量Value格式不正确'),
                        trigger: 'blur'
                    })
                }
                this.$nextTick(() => {
                    this.$refs.variableValue[index].validate()
                })
            },
            checkIsJSON (str) {
                if (typeof str === 'string') {
                    try {
                        const obj = JSON.parse(str)
                        if (obj && Object.prototype.toString.call(obj) === '[object Object]') {
                            return true
                        } else {
                            return false
                        }
                    } catch (e) {
                        return false
                    }
                }
                return false
            },
            updateVarList (index) {
                if (index !== undefined) {
                    if (this.variableList.length === 1) {
                        this.$bkMessage({
                            message: i18n.t('至少保留一条全局变量'),
                            theme: 'warning'
                        })
                    } else {
                        this.$refs.variableForm[index].clearError()
                        this.variableList.splice(index, 1)
                    }
                } else {
                    this.variableList.push({
                        key: '',
                        value: '',
                        type: 'string',
                        rules: tools.deepClone(this.rules)
                    })
                }
            },
            onConfirm () {
                try {
                    const formValidations = this.$refs.variableForm.map(formRef => {
                        return formRef.validate()
                    })
                    Promise.all(formValidations).then(results => {
                        if (results.every(item => item)) {
                            const context = this.variableList.reduce((acc, cur) => {
                                if (cur.type === 'number') {
                                    acc[cur.key] = Number(cur.value)
                                } else if (cur.type === 'object') {
                                    acc[cur.key] = eval('(' + cur.value + ')')
                                } else {
                                    acc[cur.key] = cur.value
                                }
                                return acc
                            }, {})
                            this.$emit('onConfirmInjectVar', context)
                        }
                    })
                } catch (error) {
                    console.warn(error)
                }
            },
            onCancel () {
                this.$emit('onCancelInjectVar')
            }
        }
    }
</script>

<style lang="scss" scoped>
    .inject-variable-dialog {
        .variable-list {
            padding: 30px;
        }
        .variable-item {
            display: flex;
            align-items: center;
            &:not(:first-child) {
                margin-top: 15px;
            }
            /deep/.bk-form {
                display: flex;
                align-items: center;
                margin-right: 27px;
                .bk-form-item {
                    margin-top: 0;
                    &:not(:last-child) {
                        margin-right: 20px;
                    }
                }
                .bk-form-content {
                    margin-left: 0 !important;
                }
                .bk-input-text, .bk-select, .bk-input-number {
                    width: 200px;
                }
            }
            .plus-icon, .minus-icon {
                font-size: 20px !important;
                color: #c4c6cc;
                cursor: pointer;
                &:hover {
                    color: #3a84ff;
                }
            }
        }
    }
</style>
