* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="input-params">
        <render-form
            ref="renderForm"
            v-model="formData"
            :scheme="scheme"
            :form-option="option"
            :hooked="hooked"
            @change="onInputsChange"
            @onHookChange="onInputHookChange">
        </render-form>
        <reuse-var-dialog
            :is-reuse-var-dialog-show="isReuseVarDialogShow"
            :reuse-variable="reuseVariable"
            :reuseable-var-list="reuseableVarList"
            @onConfirmReuseVar="onConfirmReuseVar"
            @onCancelReuseVar="onCancelReuseVar">
        </reuse-var-dialog>
    </div>
</template>
<script>
    import tools from '@/utils/tools.js'
    import formSchema from '@/utils/formSchema.js'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import ReuseVarDialog from './ReuseVarDialog.vue'
    import { mapState, mapMutations } from 'vuex'
    export default {
        name: 'InputParams',
        components: {
            RenderForm,
            ReuseVarDialog
        },
        props: {
            scheme: {
                type: Array,
                default () {
                    return []
                }
            },
            nodeConfig: {
                type: Object,
                default () {
                    return {}
                }
            },
            value: {
                type: Object,
                default () {
                    return {}
                }
            },
            hooked: {
                type: Object,
                default () {
                    return {}
                }
            },
            isSubflow: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                isReuseVarDialogShow: false,
                reuseVariable: {},
                reuseableVarList: [],
                formData: tools.deepClone(this.value),
                option: {
                    showGroup: false,
                    showHook: true,
                    showLabel: true,
                    showVarList: true
                }
            }
        },
        computed: {
            ...mapState({
                'constants': state => state.template.constants
            })
        },
        watch: {
            value (val) {
                this.formData = tools.deepClone(val)
            }
        },
        created () {
            this.onInputsChange = tools.debounce(this.inputsChange, 800)
        },
        methods: {
            ...mapMutations('template/', [
                'setNodeInputData',
                'addVariable',
                'setVariableSourceInfo'
            ]),
            // 输入参数值改变
            inputsChange (val) {
                const setVals = Object.keys(val).reduce((acc, cur) => {
                    acc[cur] = {
                        value: val[cur]
                    }
                    return acc
                }, {})
                this.setNodeInputData({
                    id: this.nodeConfig.id,
                    type: this.nodeConfig.type,
                    setVals: setVals
                })
            },
            // 输入勾选值改变
            // inputsHookChange (code, value) {
            //     // 更新页面数据
            //     this.$set(this.hooked, code, true)
            //     this.$set(this.formData, code, value)
            // },
            // 输入勾选，取消勾选
            onInputHookChange (code, val) {
                // <----start 获取创建变量所需参数
                const VAR_KEY_REG = /^\$\{(\w+)\}$/
                const variable = {
                    name: '',
                    key: '',
                    source_info: {},
                    custom_type: '',
                    value: '',
                    validation: '',
                    version: ''
                }
                const curCodeScheme = this.scheme.find(m => m.tag_code === code)
                const correctKey = VAR_KEY_REG.test(code) ? code : '${' + code + '}'
                variable.name = curCodeScheme.attrs.name.replace(/\s/g, '')
                if (this.isSubflow) {
                    const constants = this.nodeConfig.constants
                    variable.key = correctKey
                    variable.source_tag = constants.source_tag
                    variable.source_info = { [this.nodeConfig.id]: [correctKey] }
                    variable.custom_type = constants.custom_type
                    variable.value = tools.deepClone(this.value[code])
                    variable.version = constants[code].version || 'legacy'
                    if (curCodeScheme.type !== 'combine') {
                        variable.validation = constants[code].validation
                    }
                } else {
                    const component = this.nodeConfig.component
                    variable.key = correctKey
                    variable.source_tag = `${component.code}.${code}`
                    variable.source_info = { [this.nodeConfig.id]: [code] }
                    variable.custom_type = ''
                    variable.value = tools.deepClone(this.value[code])
                    variable.version = component.version || 'legacy'
                }
                //  获取创建变量所需参数 end------->
                if (val) { // hook
                    if (!variable.source_tag) { // custom variable not include ip selector
                        this.hookToGlobal(variable)
                        this.setNodeInputData({
                            id: this.nodeConfig.id,
                            type: this.nodeConfig.type,
                            setVals: { [code]: { value: correctKey, hook: true } }
                        })
                        return
                    }
                    const reuseableVarList = this.getReuseableVarList(code, variable.version)
                    const isKeyUsed = variable.key in this.constants
                    if (reuseableVarList.length || isKeyUsed) { // 复用变量
                        const useNewKey = !reuseableVarList.length && isKeyUsed
                        this.reuseVariable = Object.assign({}, variable, { useNewKey: useNewKey })
                        this.reuseableVarList = reuseableVarList
                        this.isReuseVarDialogShow = true
                    } else { // 新增变量
                        console.log(correctKey, 'correctKey')
                        variable.form_schema = formSchema.getSchema(code, this.scheme)
                        this.hookToGlobal(variable, code)
                        this.setNodeInputData({
                            id: this.nodeConfig.id,
                            type: this.nodeConfig.type,
                            setVals: { [code]: { value: correctKey, hook: true } }
                        })
                    }
                } else { // cancel hook
                    const value = this.constants[correctKey]
                    // this.$set(this.hooked, code, true)
                    this.$emit('inputsHookChange', { code, val: false })
                    this.$set(this.formData, code, value)
                    this.setNodeInputData({
                        id: this.nodeConfig.id,
                        type: this.nodeConfig.type,
                        setVals: { [code]: { value: value, hook: false } }
                    })
                    this.setVariableSourceInfo({ type: 'delete', id: this.nodeConfig.id, key: correctKey, tagCode: code })
                }
            },
            /**
             * 获取复用变量列表
             * 获取全局变量中已有的 key + version 相同项列表
             */
            getReuseableVarList (tagCode, version) {
                const variableList = []
                for (const cKey in this.constants) {
                    const constant = this.constants[cKey]
                    const sVersion = constant.version
                    const sTag = constant.source_tag
                    if (sTag) {
                        const tCode = sTag.split('.')[1]
                        tCode === tagCode && sVersion === version && variableList.push({
                            name: `${constant.name}(${constant.key})`,
                            id: constant.key
                        })
                    }
                }
                return variableList
            },
            /**
             * 参数不复用，创建新变量
             */
            hookToGlobal (variableOpts, code) {
                // 更新页面数据
                // this.$set(this.hooked, code, true)
                this.$emit('inputsHookChange', { code, val: true })
                this.$set(this.formData, code, variableOpts.key)
                // 创建新变量
                const len = Object.keys(this.constants).length
                const defaultOpts = {
                    name: '',
                    key: '',
                    desc: '',
                    custom_type: '',
                    source_info: {},
                    source_tag: '',
                    value: '',
                    show_type: 'show',
                    source_type: 'component_inputs',
                    validation: '',
                    index: len,
                    version: 'legacy'
                }
                const variable = Object.assign({}, defaultOpts, variableOpts)
                this.addVariable(Object.assign({}, variable))
            },
            // 复用变量
            reuseVar (variableOpts, code) {
                const { varKey, key, value } = variableOpts
                // 更新页面数据
                // this.$set(this.hooked, code, true)
                this.$emit('inputsHookChange', { code, val: true })
                this.$set(this.formData, code, variableOpts.key)
                this.setVariableSourceInfo({ type: 'add', id: this.nodeConfig.id, key: varKey, tagCode: key, value })
            },
            // 复用变量确认回调
            onConfirmReuseVar (varConfig) {
                const { type, name, key, varKey, source_tag, source_info, value } = varConfig
                const code = source_tag.split('.')[1]
                if (type === 'create') { // 新建
                    if (this.constants[varKey]) {
                        this.$bkMessage({
                            message: gettext('变量KEY已存在'),
                            theme: 'error'
                        })
                        return false
                    }
                    const variableOpts = { name, key: varKey, source_tag, source_info, value }
                    variableOpts.form_schema = formSchema.getSchema(key, this.scheme)
                    this.hookToGlobal(variableOpts, code)
                } else { // 复用
                    this.reuseVar(varConfig, code)
                }
                this.setNodeInputData({
                    id: this.nodeConfig.id,
                    type: this.nodeConfig.type,
                    setVals: { [key]: { value: key, hook: true } }
                })
            },
            // 取消复用变量回调
            onCancelReuseVar (reuseVariable) {
                const { source_tag } = reuseVariable
                const code = source_tag.split('.')[1]
                // this.$set(this.hooked, code, false)
                this.$emit('inputsHookChange', { code, val: false })
                this.$set(this.formData, code, reuseVariable.key)
            }
        }
    }
</script>
