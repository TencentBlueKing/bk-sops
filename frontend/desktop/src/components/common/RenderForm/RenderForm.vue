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
    <div class="render-form">
        <component
            :is="atom.type === 'combine' ? 'FormGroup' : 'FormItem'"
            v-for="(atom, index) in scheme"
            :key="`${atom.tag_code}_${index}`"
            :scheme="atom"
            :option="option"
            :value="getFormValue(atom)"
            :hook="hooked[atom.tag_code]"
            :render="renderConfig[atom.tag_code]"
            :constants="constants"
            @change="updateForm"
            @onHook="updateHook"
            @onRenderChange="updateRender">
        </component>
    </div>
</template>
<script>
/**
 * 标准插件表单渲染函数
 * param {Array} scheme 标准插件表单配置项
 * param {Object} formOption 表单 UI 选项(label、checkbox、groupName)
 * param {Object} formData 表单值
 * param {Object} hooked 已被勾选的表单项
 */
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
    import FormGroup from './FormGroup.vue'
    import FormItem from './FormItem.vue'

    const DEFAUTL_OPTION = {
        showRequired: true, // 是否展示必填icon
        showHook: false, // 是否可以勾选
        showGroup: false, // 是否显示 combine 类型标准插件名称
        showLabel: false, // 是否显示标准插件名称
        formEdit: true, // 是否可编辑
        formMode: true, // 是否为表单模式（查看参数时，input、textarea等不需要用表单展示）
        validateSet: ['required', 'custom', 'regex'] // 选择开启的校验类型，默认都开启
    }

    export default {
        name: 'RenderForm',
        components: {
            FormGroup,
            FormItem
        },
        model: {
            prop: 'formData',
            event: 'change'
        },
        provide () {
            return {
                getFormData: () => this.formData
            }
        },
        props: {
            scheme: {
                type: Array,
                default () {
                    return []
                }
            },
            formOption: {
                type: Object,
                default () {
                    return {
                        ...DEFAUTL_OPTION
                    }
                }
            },
            formData: {
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
            renderConfig: { // 输入参数是否配置渲染豁免
                type: Object,
                default: () => ({})
            },
            constants: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            return {
                value: tools.deepClone(this.formData),
                watchVarInfo: {}, // 监听的变量
                changeVarInfo: {} // 隐藏的变量
            }
        },
        computed: {
            option () {
                return Object.assign({}, DEFAUTL_OPTION, this.formOption)
            }
        },
        watch: {
            scheme: {
                handler: function (val) {
                    this.checkValue(val, this.value)
                },
                deep: true
            },
            formData: {
                handler: function (val, oldVal) {
                    this.value = tools.deepClone(val)
                },
                deep: true
            }
        },
        created () {
            this.checkValue(this.scheme, this.value)
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
        },
        mounted () {
            if (!Object.keys(this.watchVarInfo).length) return
            for (const [key, value] of Object.entries(this.formData)) {
                this.setVariableHideLogic(key, value)
            }
        },
        methods: {
            /**
             * 检查表单的 formData 是否有字段空缺
             * 如果有空缺则给补上
             * @param {Array} scheme 表单配置项
             * @param {Object} data 表单值
             */
            checkValue (scheme, data) {
                if (!scheme || !Array.isArray(scheme)) return

                const isSetValueToFormData = this.traverseSchemeAndFillData(scheme, data)
                if (isSetValueToFormData) {
                    this.$emit('change', tools.deepClone(data))
                }
            },
            /**
             * 遍历 scheme，填充缺失字段的值，并返回检查是否存在缺失的结果布尔值
             */
            traverseSchemeAndFillData (scheme, data) {
                if (!scheme || !Array.isArray(scheme)) return

                let hasValMissing = false // 传入的 data 是否存在 scheme 中对应属性的值有缺失
                scheme.forEach(item => {
                    const key = item.tag_code

                    /** warning 前端tag结构变化数据兼容 */
                    if (item.tag_code === 'job_task') {
                        data[item.tag_code] = this.reloadValue(item, data)
                    }

                    if (item.type === 'combine') {
                        if (!this.hooked || !this.hooked[item.tag_code]) {
                            if (!(key in data)) {
                                hasValMissing = true
                                this.$set(data, key, {})
                            }
                            const checkResult = this.traverseSchemeAndFillData(item.attrs.children, data[key])
                            if (checkResult) {
                                hasValMissing = true
                            }
                        }
                    } else {
                        if (!(key in data)) {
                            hasValMissing = true
                            const value = this.getDefaultValue(item)
                            this.$set(data, key, value)
                        }
                    }
                })
                return hasValMissing
            },
            /**
             * 若传入的 formData 不包含表单项的值，取值顺序为：标准插件配置项 value 字段 -> 标准插件配置项 default 字段 -> tag 类型默认值
             */
            getDefaultValue (scheme) {
                let val
                if ('value' in scheme.attrs) {
                    val = tools.deepClone(scheme.attrs.value)
                } else if ('default' in scheme.attrs) {
                    val = tools.deepClone(scheme.attrs.default)
                } else {
                    switch (scheme.type) {
                        case 'input':
                        case 'textarea':
                        case 'radio':
                        case 'text':
                        case 'datetime':
                        case 'member_selector':
                        case 'section':
                        case 'code_editor':
                        case 'log_display':
                            val = ''
                            break
                        case 'checkbox':
                        case 'datatable':
                        case 'tree':
                        case 'upload':
                            val = []
                            break
                        case 'select':
                            val = scheme.attrs.multiple ? [] : ''
                            break
                        case 'time':
                            val = scheme.attrs.isRange ? ['00:00:00', '23:59:59'] : ''
                            break
                        case 'int':
                            val = 0
                            break
                        case 'ip_selector':
                            val = {
                                static_ip_table_config: [],
                                selectors: [],
                                ip: [],
                                topo: [],
                                group: [],
                                filters: [],
                                excludes: [],
                                with_cloud_id: false
                            }
                            break
                        case 'set_allocation':
                            val = {
                                config: {
                                    set_count: 1,
                                    set_template_id: '',
                                    host_resources: [],
                                    module_detail: []
                                },
                                data: [],
                                separator: ','
                            }
                            break
                        case 'host_allocation':
                            val = {
                                config: {
                                    host_count: 0,
                                    host_screen_value: '',
                                    host_resources: [],
                                    host_filter_detail: []
                                },
                                data: [],
                                separator: ','
                            }
                            break
                        case 'password':
                            val = {
                                tag: 'value',
                                value: ''
                            }
                            break
                        default:
                            val = ''
                    }
                }
                return val
            },
            getFormValue (atom) {
                /** warning 前端tag结构变化数据兼容 */
                if (atom.tag_code === 'job_task') {
                    this.value[atom.tag_code] = this.reloadValue(atom, this.value)
                }
                return this.value[atom.tag_code]
            },
            updateForm (fieldArr, val) {
                const fieldDataObj = tools.deepClone(this.value)
                fieldArr.reduce((acc, cur, index, arr) => {
                    if (index === arr.length - 1) {
                        acc[cur] = val
                        return
                    }
                    if (!acc.hasOwnProperty(cur)) {
                        acc[cur] = {}
                    }
                    return acc[cur]
                }, fieldDataObj)
                this.value = tools.deepClone(fieldDataObj) // 更新 value，通过下面触发 change 更新父组件 formData 后，watch 具有滞后性，导致 value 值不是最新的
                this.$emit('change', fieldDataObj)
                // 变量隐藏逻辑
                if (!Object.keys(this.watchVarInfo).length) return
                const key = fieldArr[0]
                this.setVariableHideLogic(key, val)
            },
            updateHook (field, val) {
                this.$emit('onHookChange', field, val)
            },
            updateRender (field, val) {
                this.$emit('onRenderChange', field, val)
            },
            // 设置变量隐藏逻辑
            setVariableHideLogic (key, val) {
                if (key in this.watchVarInfo) {
                    const values = this.watchVarInfo[key]
                    values.forEach(item => {
                        let isEqual = JSON.stringify(val) === JSON.stringify(item.value)
                        const index = this.scheme.findIndex(config => config.tag_code === item.target_key)
                        const targetTag = this.$children[index]
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
                            targetTag.onHideForm()
                        } else {
                            targetTag.onShowForm()
                        }
                    })
                }
            },
            /**
             * 获取 combine 类型组件的子组件实例
             * @param {String} tagCode 标准插件 tag_code，值空时，返回全部子组件
             */
            get_child (tagCode) {
                let childComponent
                if (typeof tagCode === 'string' && tagCode !== '') {
                    this.$children.some(item => {
                        if (item.scheme && item.scheme.tag_code === tagCode) {
                            // combine组件或tag组件
                            childComponent = tagCode === 'combine' ? item : item.$refs.tagComponent
                            return true
                        }
                    })
                } else {
                    childComponent = this.$children.map(item => {
                        return item.scheme.tag_code === 'combine' ? item : item.$refs.tagComponent
                    })
                }
                return childComponent
            },
            /**
             * 表单校验函数
             * @TODO: 改写为 promise 异步机制
             */
            validate () {
                let isValid = true
                this.$children.forEach(childComp => {
                    const singleItemValid = childComp.validate()
                    if (isValid) {
                        isValid = singleItemValid
                    }
                })
                return isValid
            },
            /**
             * 表单参数重载
             * 前端tag结构变化数据兼容
             */
            reloadValue (atom, rawData) {
                if (typeof atom.reloadValue === 'function') {
                    const reloadValue = atom.reloadValue(rawData)
                    if (reloadValue) {
                        return reloadValue[atom.tag_code]
                    }
                }
                return rawData[atom.tag_code]
            }
        }
    }
</script>
<style lang="scss">
.rf-tag-used {
    .el-input__inner,
    .el-select__inner,
    .el-textarea__inner {
        border-color: #ff5656;
    }
}
.html-used-tippy-popper {
    .tippy-tooltip {
        font-style: 12px;
        padding: 8px 12px;
        border: 1px solid #dcdee5;
        box-shadow: 0 0 5px 0 rgba(0,0,0,0.09);
        .bk-tooltip-content {
            .tip-title {
                color: #63656e;
                font-size: 12px;
                margin-bottom: 9px;
                i {
                    font-size: 14px;
                    color: #ff9c01;
                }
            }
            .tip-content {
                color: #979ba5;
                margin: 0 0 8px 18px;
            }
            .tip-btn {
                text-align: right;
                color: #3a84ff;
                cursor: pointer;
            }
        }
    }
}
</style>
<style lang="scss" scoped>
.render-form {
    /deep/ .rf-group-name {
        margin-bottom: 8px;
        .scheme-name,
        .scheme-code {
            font-size: 14px;
            color: #63656e;
            line-height: 22px;
        }
        .scheme-code {
            color: #979ba5;
            margin-left: 16px;
        }
        &.not-reuse {
            &:before {
                background: #ffd695;
            }
        }
        .common-icon-dark-circle-warning {
            position: absolute;
            right: 8px;
            top: 39px;
            z-index: 2;
            font-size: 14px;
            color: #ff9c01;
        }
    }
    /deep/ .scheme-desc-wrap {
        position: relative;
        color: #979ba5;
        .hide-html-text {
            position: absolute;
            z-index: -1;
            left: -99999px;
            top: -99999px;
            width: 100%;
        }
        .hide-html-text,
        .rf-group-desc {
            width: 100%;
            font-size: 12px;
            line-height: 1.5;
            margin-top: 8px;
            padding: 0;
            white-space: pre-wrap;
        }
        .is-fold {
            max-height: 36px;
            overflow: hidden;
        }
        .expand-btn {
            color: #3a84ff;
            background: #fff;
            cursor: pointer;
            font-size: 12px;
        }
    }
}
</style>
