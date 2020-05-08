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
            :scheme="scheme"
            :hooked="hooked"
            :form-option="option"
            :form-data="formData"
            @change="onInputsValChange"
            @onHookChange="onInputHookChange">
        </render-form>
        <reuse-var-dialog
            :is-show="isReuseDialogShow"
            :variables="reuseableVarList"
            :create-new="isKeyExist"
            @confirm="onConfirmReuseVar"
            @cancel="onCancelReuseVar">
        </reuse-var-dialog>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
    import formSchema from '@/utils/formSchema.js'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import ReuseVarDialog from './ReuseVarDialog.vue'
    import { mapState, mapMutations } from 'vuex'

    const varKeyReg = /^\$\{(\w+)\}$/

    export default {
        name: 'InputParams',
        components: {
            RenderForm,
            ReuseVarDialog
        },
        props: {
            scheme: Array,
            value: Object,
            plugin: String, // 标准插件
            version: String, // 标准插件版本或子流程版本
            isSubflow: Boolean,
            subflowForms: Object, // 子流程模板输入参数变量配置
            nodeId: String
        },
        data () {
            return {
                formData: tools.deepClone(this.value),
                hookingVarForm: '', // 正被勾选的表单项
                isKeyExist: false, // 勾选的表单生成的 key 是否在全局变量列表中存在
                isReuseDialogShow: false,
                reuseableVarList: [],
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
            }),
            hooked () {
                const hooked = {}
                const keys = Object.keys(this.constants)
                this.scheme.forEach(form => {
                    // 已勾选到全局变量中
                    const isHooked = keys.some(item => {
                        const varItem = this.constants[item]
                        if (varItem.source_type === 'component_inputs') {
                            const sourceInfo = varItem.source_info[this.nodeId]
                            if (sourceInfo && sourceInfo.includes(form.tag_code)) {
                                return true
                            }
                        }
                    })
                    // 勾选中的状态，变量复用弹窗出现时
                    const isHooking = this.hookingVarForm === form.tag_code
                    hooked[form.tag_code] = isHooked || isHooking
                })
                return hooked
            }
        },
        watch: {
            value (val) {
                this.formData = tools.deepClone(val)
            }
        },
        methods: {
            ...mapMutations('template/', [
                'addVariable',
                'deleteVariable',
                'setVariableSourceInfo'
            ]),
            onInputsValChange (val) {
                this.$emit('update', tools.deepClone(val))
            },
            onInputHookChange (form, val) {
                if (val) {
                    this.hookForm(form)
                } else {
                    this.unhookForm(form)
                }
            },
            /**
             * 勾选表单
             *
             * 1.判断表单全局变量 source_tag 中 tag_code 和勾选表单 tag_code 相同的项：
             * a.不存在
             * 判断全局变量中是否存在和勾选表单相同的 key，存在则弹出变量复用弹窗，只提供新建变量选项，若不存在则新建全局变量
             * b.存在
             * 弹出是否变量复用弹窗，提供复用或新建选项
             *
             * 2.新建全局变量时，勾选表单项已有的表单值需要同步到全局变量中，注意带上后来版本加上的 version、fromScheme 字段
             */
            hookForm (form) {
                const reuseList = []
                const variableKey = this.isSubflow ? form : `\${${form}}`
                const formCode = this.isSubflow ? form.match(varKeyReg)[1] : form
                const version = this.isSubflow ? this.subflowForms[form].version : this.version
                let isKeyInVariables = false
                this.hookingVarForm = form

                Object.keys(this.constants).forEach(keyItem => {
                    const constant = this.constants[keyItem]
                    const sourceTag = constant.source_tag
                    // 变量的版本需要和勾选表单一致，判断 sourceTag 是否存在是为了兼容旧数据自定义全局变量 source_tag 为空
                    if (constant.version === version && sourceTag) {
                        const tagCode = sourceTag.split('.')[1]
                        if (tagCode === formCode) {
                            reuseList.push({
                                name: `${constant.name}(${constant.key})`,
                                id: constant.key
                            })
                        }
                    }
                    if (keyItem === variableKey) {
                        isKeyInVariables = true
                    }
                })

                if (reuseList.length > 0) { // 复用变量
                    this.reuseableVarList = reuseList
                    this.isKeyExist = false
                    this.isReuseDialogShow = true
                } else if (isKeyInVariables) { // 创建变量(手动填写变量name、key)
                    this.isKeyExist = true
                    this.isReuseDialogShow = true
                } else { // 自动创建新变量
                    const formConfig = this.scheme.find(item => item.tag_code === form)
                    const config = this.getNewVarConfig(formConfig.attrs.name, variableKey)
                    this.createVariable(config)
                }
            },
            /**
             * 取消勾选表单
             *
             * 去掉包含该表单的全局变量 source_info 对应的信息，若对应全局变量只包含这一个表单项，则删除全局变量
             * 取消勾选后全局变量的值需要同步当前表单项
             */
            unhookForm (form) {
                const variableKey = this.formData[form]
                const constant = this.constants[variableKey]
                if (constant) { // 标准插件里(如：job_execute_task)可能会修改表单的勾选状态，需要做一个兼容处理
                    this.formData[form] = tools.deepClone(constant.value)
                    this.$emit('update', tools.deepClone(this.formData))
                    this.setVariableSourceInfo({
                        type: 'delete',
                        id: this.nodeId,
                        key: variableKey,
                        tagCode: form
                    })
                    this.$emit('globalVariableUpdate')
                }
            },
            getNewVarConfig (name, key) {
                const variableKey = varKeyReg.test(key) ? key : `\${${key}}`
                const config = {
                    name,
                    key: variableKey,
                    source_info: { [this.nodeId]: [this.hookingVarForm] },
                    value: tools.deepClone(this.formData[this.hookingVarForm]),
                    formSchema: formSchema.getSchema(this.hookingVarForm, this.scheme)
                }
                if (this.isSubflow) {
                    const constant = this.subflowForms[this.hookingVarForm]
                    const { desc, custom_type, source_tag, validation, version } = constant
                    Object.assign(config, {
                        desc,
                        custom_type,
                        source_tag,
                        validation,
                        version
                    })
                } else {
                    Object.assign(config, {
                        custom_type: '',
                        source_tag: `${this.plugin}.${this.hookingVarForm}`,
                        version: this.version
                    })
                }
                return config
            },
            // 创建新变量
            createVariable (config = {}) {
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
                    version: 'legacy',
                    formSchema: {}
                }
                const variable = Object.assign({}, defaultOpts, config)
                this.formData[this.hookingVarForm] = variable.key
                this.hookingVarForm = ''
                this.addVariable(variable)
                this.$emit('update', tools.deepClone(this.formData))
                this.$emit('globalVariableUpdate')
            },
            /**
             * 复用变量弹窗点击确认回调
             *
             * @param {String} type 复用已有全局变量(reuse)或者创建新变量(new)
             * @param {String, Obejct} data 复用时为 formcode，新建时为 {name, key}
             */
            onConfirmReuseVar (type, data) {
                this.isReuseDialogShow = false
                if (type === 'new') { // 创建新变量
                    const { name, key } = data
                    const config = this.getNewVarConfig(name, key)
                    this.createVariable(config)
                } else { // 复用已有全局变量
                    const variableKey = data
                    this.setVariableSourceInfo({
                        type: 'add',
                        id: this.nodeId,
                        key: variableKey,
                        tagCode: this.hookingVarForm
                    })
                    this.formData[this.hookingVarForm] = variableKey
                    this.$emit('update', tools.deepClone(this.formData))
                    this.hookingVarForm = ''
                }
            },
            /**
             * 取消复用变量回调
             */
            onCancelReuseVar (reuseVariable) {
                this.hooked[this.hookingVarForm] = false
                this.isReuseDialogShow = false
                this.isKeyExist = false
                this.hookingVarForm = ''
                this.reuseableVarList = []
            },
            validate () {
                return this.$refs.renderForm.validate()
            }
        }
    }
</script>
