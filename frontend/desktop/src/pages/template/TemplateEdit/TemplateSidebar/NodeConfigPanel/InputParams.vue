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
    <div class="input-params">
        <render-form
            ref="renderForm"
            :class="{ 'sub-flow-form': isSubFlow }"
            :scheme="formsScheme"
            :hooked="hooked"
            :constants="constants"
            :form-option="option"
            :form-data="formData"
            :render-config="renderConfig"
            @change="onInputsValChange">
            <template v-slot:hook="props">
                <FormHook
                    :params="props.params"
                    @onHook="onHookChange"
                    @change="updateForm"
                    @handleVariableHook="handleVariableHook"
                    @onRenderChange="$emit('renderConfigChange', arguments)">
                </FormHook>
            </template>
        </render-form>
        <bk-collapse v-if="formsNotReferredScheme.length > 0" :class="['not-referred-forms', { expand: notReferredExpand }]">
            <bk-collapse-item>
                {{ $t('查看未引用变量') }}
                <div slot="content" class="forms-wrapper" style="padding: 10px 64px 10px 0;">
                    <render-form
                        :scheme="formsNotReferredScheme"
                        :form-option="{ showLabel: true, showHook: false, formEdit: false }"
                        :form-data="formData">
                    </render-form>
                </div>
            </bk-collapse-item>
        </bk-collapse>
    </div>
</template>
<script>
    import bus from '@/utils/bus.js'
    import tools from '@/utils/tools.js'
    import { random4 } from '@/utils/uuid.js'
    import formSchema from '@/utils/formSchema.js'
    import FormHook from '@/components/common/FormHook.vue'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'

    const varKeyReg = /^\$\{(\w+)\}$/

    export default {
        name: 'InputParams',
        components: {
            FormHook,
            RenderForm
        },
        props: {
            scheme: Array,
            showHook: {
                type: Boolean,
                default: true
            },
            editable: {
                type: Boolean,
                default: true
            },
            value: Object,
            renderConfig: { // 输入参数是否配置渲染豁免
                type: Object,
                default: () => ({})
            },
            plugin: String, // 标准插件
            version: String, // 标准插件版本或子流程版本
            isSubFlow: Boolean,
            subFlowForms: Object, // 子流程模板输入参数变量配置
            formsNotReferred: { // 子流程未引用的变量
                type: Object,
                default: () => ({})
            },
            nodeId: String,
            basicInfo: Object,
            activities: Object,
            constants: Object,
            thirdPartyCode: String,
            isViewMode: Boolean
        },
        data () {
            return {
                formData: tools.deepClone(this.value),
                hooked: {},
                hookingVarForm: '', // 正被勾选的表单项
                unhookingVarForm: '', // 正被取消勾选的表单项
                notReferredExpand: false, // 未引用变量是否展开
                option: {
                    showGroup: true,
                    showHook: this.showHook,
                    showLabel: true,
                    showVarList: true,
                    formEdit: this.isViewMode ? false : this.editable
                },
                watchVarInfo: {}, // 监听的变量
                changeVarInfo: {} // 隐藏的变量
            }
        },
        computed: {
            formsScheme () {
                if (this.isSubFlow && Object.keys(this.formsNotReferred).length > 0) {
                    // 过滤掉子流程未被引用的变量
                    return this.scheme.filter(item => !this.formsNotReferred.hasOwnProperty(item.tag_code))
                }
                return this.scheme
            },
            formsNotReferredScheme () {
                if (this.isSubFlow && Object.keys(this.formsNotReferred).length > 0) {
                    return this.scheme.filter(item => this.formsNotReferred.hasOwnProperty(item.tag_code))
                }
                return []
            }
        },
        watch: {
            value (val) {
                this.formData = tools.deepClone(val)
            },
            isViewMode (val) {
                this.option.formEdit = !val
            }
        },
        created () {
            $.context.exec_env = 'NODE_CONFIG'
            this.hooked = this.getFormsHookState()
            // 设置变量自动隐藏对象
            const watchVarInfo = {}
            const changeVarInfo = {}
            Object.values(this.constants).forEach(item => {
                if (!item.hide_condition || !item.hide_condition.length) return
                item.hide_condition.forEach(val => {
                    const { constant_key: key, operator, value } = val
                    // 隐藏的变量和对应的监听变量
                    if (!(item.key in changeVarInfo)) {
                        changeVarInfo[item.key] = {}
                    }
                    changeVarInfo[item.key][key] = false
                    // 监听的变量和对应的隐藏变量
                    const params = {
                        target_key: item.key,
                        operator,
                        value,
                        isOr: true // 与逻辑或或逻辑 默认或逻辑
                    }
                    if (key in watchVarInfo) {
                        watchVarInfo[key].push(params)
                    } else {
                        watchVarInfo[key] = [params]
                    }
                })
            })
            this.watchVarInfo = watchVarInfo
            this.changeVarInfo = changeVarInfo

            // 表单项使用变量
            bus.$on('useVariable', (data) => {
                const { type, code, key, variable } = data
                if (!(code in this.formData)) return
                let updateType = 'create'
                let updateValue = variable
                if (type === 'insert') {
                    const value = this.formData[code] + key
                    this.updateForm(code, value)
                } else {
                    this.updateForm(code, key)
                    this.hooked[code] = true
                    updateType = variable.type === 'reuse' ? 'reuse' : 'edit'
                    updateValue = variable
                }
                // 更新变量列表
                this.$emit('updateConstants', updateType, updateValue)
                this.$emit('update', tools.deepClone(this.formData))
                this.hookingVarForm = ''
            })
        },
        mounted () {
            if (!Object.keys(this.watchVarInfo).length) return
            for (const [key, value] of Object.entries(this.formData)) {
                this.setVariableHideLogic(key, value)
            }
        },
        beforeDestroy () {
            $.context.exec_env = ''
        },
        methods: {
            getFormsHookState () {
                const hooked = {}
                const keys = Object.keys(this.constants)
                this.scheme.forEach(form => {
                    // 已勾选到全局变量中, 判断勾选的输入参数生成的变量及自定义全局变量source_info是否包含该节点对应表单tag_code
                    // 可能存在表单勾选时已存在相同key的变量，选择复用自定义变量
                    const isHooked = keys.some(item => {
                        const varItem = this.constants[item]
                        if (['component_inputs', 'custom'].includes(varItem.source_type)) {
                            const sourceInfo = varItem.source_info[this.nodeId]
                            if (sourceInfo && sourceInfo.includes(form.tag_code)) {
                                return true
                            }
                        }
                    })
                    hooked[form.tag_code] = isHooked
                })
                return hooked
            },
            onInputsValChange (val) {
                this.$emit('update', tools.deepClone(val))
            },
            onHookChange (form, val) {
                if (val) {
                    this.hookForm(form)
                } else {
                    this.unhookForm(form)
                }
            },
            /**
             * 输入参数勾选
             *
             * 勾选逻辑：
             * 1.判断是否存在类型相同的变量(表单项的tag_code是否相同)，存在则打开【插件字段配置】面板，
             * 2.判断是否存在相同key的变量，不存在则自动创建变量，存在则在key后面添加随机数并自动创建变量
             */
            hookForm (form) {
                let variableKey, formCode, hasReuse

                if (this.isSubFlow) {
                    const variable = this.subFlowForms[form]
                    variableKey = form
                    formCode = variable.source_tag.split('.')[1]
                } else {
                    variableKey = `\${${form}}`
                    formCode = form
                }
                this.hookingVarForm = form

                Object.keys(this.constants).forEach(keyItem => {
                    const constant = this.constants[keyItem]
                    const sourceTag = constant.source_tag
                    if (sourceTag) { // 判断 sourceTag 是否存在是为了兼容旧数据自定义全局变量 source_tag 为空
                        const tagCode = sourceTag.split('.')[1]
                        // 判断全局变量中是否有与被勾选表单项存在相同类型的，输入参数和输出参数不做比较
                        if (tagCode === formCode && constant.source_type !== 'component_outputs') {
                            hasReuse = true
                        }
                    }

                    if (keyItem === variableKey) {
                        variableKey = variableKey.slice(0, -1) + `_${random4()}}`
                    }
                })

                if (hasReuse) { // 存在类型相同的全局变量
                    // 向上抛出边框勾选事件
                    this.handleVariableHook({ type: 'reuse', code: formCode })
                } else { // 自动创建新变量
                    const formConfig = this.scheme.find(item => item.tag_code === form)
                    const config = this.getNewVarConfig(formConfig.attrs.name, variableKey)
                    this.createVariable(config)
                    this.hooked[form] = true
                }
            },
            // 向上抛出边框勾选事件
            handleVariableHook ({ type, code }) {
                let config = {}
                const scheme = this.formsScheme.find(item => item.tag_code === code)
                if (type === 'reuse') {
                    config = this.getNewVarConfig('', '')
                } else if (type === 'create') {
                    let key = code[0] === '$' ? code : `\${${code}}`
                    key = key in this.constants ? key.slice(0, -1) + `_${random4()}}` : key
                    config = {
                        name: scheme.attrs.name,
                        key,
                        source_type: 'custom'
                    }
                } else {
                    config = this.constants[this.formData[code]]
                }
                const tagCode = code[0] === '$' ? code.slice(2, -1) : code
                const reuseList = this.getReuseList(tagCode)
                bus.$emit('variableHook', {
                    source_type: 'component_inputs',
                    ...config,
                    cited_info: {
                        key: config.key,
                        type,
                        plugin: this.basicInfo.name,
                        field: scheme.attrs.name,
                        tagCode,
                        nodeId: this.nodeId,
                        nodeName: this.basicInfo.nodeName,
                        reuseList,
                        isSubFlow: this.isSubFlow
                    }
                })
            },
            getReuseList (code) {
                return Object.keys(this.constants).reduce((acc, cur) => {
                    const {
                        name,
                        key,
                        source_tag: sourceTag,
                        source_type: sourceType,
                        source_info: sourceInfo = {}
                    } = this.constants[cur]
                    if (sourceTag) { // 判断 sourceTag 是否存在是为了兼容旧数据自定义全局变量 source_tag 为空
                        const tagCode = sourceTag.split('.')[1]
                        // 判断全局变量中是否有与被勾选表单项存在相同类型的，输入参数和输出参数不做比较
                        if (tagCode === code && sourceType !== 'component_outputs') {
                            const list = Object.keys(sourceInfo).map(id => {
                                if (id === this.nodeId) {
                                    return {
                                        id,
                                        name: this.basicInfo.nodeName
                                    }
                                }
                                return this.activities[id]
                            })
                            acc.push({
                                name: `${name}(${key})`,
                                key: key,
                                list
                            })
                        }
                    }
                    return acc
                }, [])
            },
            /**
             * 取消勾选表单
             *
             * 去掉包含该表单的全局变量 source_info 对应的信息，若对应全局变量只包含这一个表单项，则删除全局变量
             * 取消勾选后全局变量的值需要同步当前表单项
             */
            unhookForm (form) {
                this.unhookingVarForm = form
                const variableKey = this.formData[form]
                const constant = this.constants[variableKey]
                if (constant) { // 标准插件里(如：job_execute_task)可能会修改表单的勾选状态，需要做一个兼容处理
                    const config = ({
                        id: this.nodeId,
                        key: variableKey,
                        tagCode: form,
                        source: 'input'
                    })
                    this.$emit('updateConstants', 'delete', config)
                }
            },
            // 变量勾选/取消勾选后，需重新对form进行赋值
            setFormData (data = {}) {
                const form = this.unhookingVarForm
                this.formData[form] = tools.deepClone(data.value) || ''
                this.hooked[form] = false
                this.$emit('update', tools.deepClone(this.formData))
            },
            getNewVarConfig (name, key) {
                const variableKey = varKeyReg.test(key) ? key : `\${${key}}`
                const config = {
                    name,
                    key: variableKey,
                    source_info: { [this.nodeId]: [this.hookingVarForm] },
                    value: tools.deepClone(this.formData[this.hookingVarForm]) || '',
                    form_schema: formSchema.getSchema(this.hookingVarForm, this.scheme),
                    plugin_code: this.thirdPartyCode || ''
                }
                if (this.isSubFlow) {
                    const constant = this.subFlowForms[this.hookingVarForm]
                    const { desc, custom_type, source_tag, validation, is_meta, meta, version, plugin_code } = constant
                    Object.assign(config, {
                        desc,
                        custom_type,
                        source_tag,
                        validation,
                        version,
                        plugin_code
                    })
                    if (is_meta) {
                        config.is_meta = true
                        config.meta = tools.deepClone(meta)
                    }
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
                    form_schema: {},
                    plugin_code: ''
                }
                const variable = Object.assign({}, defaultOpts, config)
                this.formData[this.hookingVarForm] = variable.key
                this.$emit('updateConstants', 'create', variable)
                this.$emit('update', tools.deepClone(this.formData))
                this.hookingVarForm = ''
            },
            validate () {
                return this.$refs.renderForm.validate()
            },
            updateForm (key, val) {
                this.formData[key] = val
                // 变量隐藏逻辑
                if (!Object.keys(this.watchVarInfo).length) return
                this.setVariableHideLogic(key, val)
            },
            // 设置变量隐藏逻辑
            setVariableHideLogic (key, val) {
                if (key in this.watchVarInfo) {
                    const values = this.watchVarInfo[key]
                    values.forEach(item => {
                        let isEqual = JSON.stringify(val) === JSON.stringify(item.value)
                        const scheme = this.formsScheme.find(config => config.tag_code === item.target_key)
                        const relatedVarInfo = this.changeVarInfo[item.target_key]
                        // 计算输入值是否匹配
                        isEqual = (item.operator === '=' && isEqual) || (item.operator === '!=' && !isEqual)
                        relatedVarInfo[key] = isEqual
                        // 相关运算逻辑
                        let isMatch = false
                        const relatedVarValues = Object.values(relatedVarInfo)
                        if (item.isOr) {
                            isMatch = relatedVarValues.some(option => option)
                        } else {
                            isMatch = relatedVarValues.every(option => option)
                        }
                        // 显示隐藏
                        if (isMatch) {
                            scheme.attrs.hidden = true
                        } else {
                            scheme.attrs.hidden = false
                        }
                    })
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
.input-params {
    padding: 16px 30px 34px;
}
.not-referred-forms {
    margin-top: 20px;
    background: #f0f1f5;
    & >>> .bk-collapse-item {
        .bk-collapse-item-header {
            color: #333333;
            &:hover {
                background: #e4e6ed;
            }
        }
    }
}

/deep/ .render-form,
/deep/.sub-flow-form {
    .scheme-name {
        font-size: 12px !important;
    }
    .rf-form-item {
        /deep/.el-radio {
            height: 24px;
            line-height: 24px;
        }
        .el-input-number {
            line-height: 32px;
        }
        .tag-input .div-input {
            height: 30px;
        }
        &:last-child {
            margin-bottom: 0;
        }
    }
    .form-item-group {
        padding: 16px;
        background: #f5f7fa;
        .rf-form-item:not(:first-child) {
            margin: 24px 0 0 0;
        }
        .rf-form-group .rf-tag-label{
            display: none;
        }
        .form-item-group {
            padding: 0;
        }
    }
    .rf-form-group {
        margin-bottom: 24px;
        >.rf-tag-label {
            display: block;
        }
    }
    .tag-ip-selector-wrap,
    .resource-allocation {
        border: none;
        padding: 0;
    }
    .show-render {
        .form-item-group {
            margin-right: 64px;
        }
    }
}
</style>
