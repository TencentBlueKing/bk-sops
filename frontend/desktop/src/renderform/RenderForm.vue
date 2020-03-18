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
    <div class="render-form">
        <component
            :is="atom.type === 'combine' ? 'FormGroup' : 'FormItem'"
            v-for="(atom, index) in formConfig"
            :key="`${atom.tag_code}_${index}`"
            :scheme="atom"
            :option="option"
            :value="getFormValue(atom)"
            :hook="hooked[atom.tag_code]"
            @change="updateForm"
            @onHook="updateHook">
        </component>
    </div>
</template>
<script>
    /**
     * 标准插件表单渲染函数
     * param {Array} scheme 标准插件表单配置项
     * param {Object} formOption 表单 UI 选项(label、checkbox、groupName)
     * param {Object} formData 表单值
     * param {Object} hooked 表单是否勾选
     */
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
    import atomFilter from '@/utils/atomFilter.js'
    import FormGroup from './FormGroup.vue'
    import FormItem from './FormItem.vue'

    const DEFAUTL_OPTION = {
        showRequired: true, // 是否展示必填icon
        showHook: false, // 是否可以勾选
        showGroup: false, // 是否显示 combine 类型标准插件名称
        showLabel: false, // 是否显示标准插件名称
        formEdit: true, // 是否可编辑
        formMode: true, // 是否为表单模式（查看参数时，input、textarea等不需要用表单展示）
        formViewHidden: false, // 改表单项为非编辑状态时，是否隐藏
        cols: 0, // 横向栅格占有的格数，总数为 12 格
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
        props: {
            scheme: {
                type: Array,
                default () {
                    return []
                }
            },
            constants: {
                type: Array,
                default () {
                    return []
                }
            },
            context: {
                type: Object,
                default () {
                    return {}
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
            }
        },
        data () {
            return {
                formConfig: tools.deepClone(this.scheme),
                value: tools.deepClone(this.formData),
                atomsConfig: {} // 变量表单配置项完整配置项
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
                    this.formConfig = tools.deepClone(val)
                    this.setDefaultValue(val, this.formData)
                },
                deep: true
            },
            constants: {
                handler: function (val) {
                    if (this.scheme.length === 0 && val) {
                        this.handleConstants(val)
                    }
                },
                deep: true
            },
            context: {
                handler: function (val) {
                    this.setContext()
                },
                deep: true
            },
            formData: {
                handler: function (val) {
                    this.value = tools.deepClone(val)
                },
                deep: true
            }
        },
        created () {
            if (this.scheme) {
                this.setDefaultValue(this.scheme, this.formData)
            } else if (this.constants){
                this.handleConstants(this.constants)
            }
            this.setContext()
        },
        methods: {
            async handleConstants (constants) {
                this.formConfig = []
                this.value = []

                let variableArray = constants.filter(item => item.show_type === 'show')

                this.isNoData = !variableArray.length

                variableArray = variableArray.sort((a, b) => {
                    return a.index - b.index
                })

                for (const variable of variableArray) {
                    const { key } = variable
                    const { atomType, atom, tagCode, classify } = atomFilter.getVariableArgs(variable)
                    // custom_type 可以判断是手动新建节点还是组件勾选
                    const version = variable.version || 'legacy'
                    if (!atomFilter.isConfigExists(atomType, version, this.atomsConfig)) {
                        this.isConfigLoading = true
                        await this.loadAtomConfig({ atomType, classify, version, saveName: atom })
                    }
                    const atomConfig = this.atomsConfig[atom][version]
                    let currentFormConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))

                    if (currentFormConfig) {
                        // 若该变量是元变量则进行转换操作
                        if (variable.is_meta || currentFormConfig.meta_transform) {
                            currentFormConfig = currentFormConfig.meta_transform(variable.meta || variable)
                            this.metaConfig[key] = tools.deepClone(variable)
                            if (!variable.meta) {
                                variable.value = currentFormConfig.attrs.value
                            }
                        }
                        currentFormConfig.tag_code = key
                        currentFormConfig.attrs.name = variable.name
                        currentFormConfig.attrs.desc = variable.desc
                        if (
                            variable.custom_type === 'input'
                            && variable.validation !== ''
                        ) {
                            currentFormConfig.attrs.validation.push({
                                type: 'regex',
                                args: variable.validation,
                                error_message: gettext('参数值不符合正则规则：') + variable.validation
                            })
                        }
                        this.formConfig.push(currentFormConfig)
                    }
                    this.value[key] = tools.deepClone(variable.value)
                }
            },
            async loadAtomConfig (payload) {
                const { atomType, classify, isMeta, saveName } = payload
                const atomClassify = classify || 'component'
                const setTypeName = saveName || atomType
                let version = payload.version
                version = atomClassify === 'variable' ? 'legacy' : version

                if (!$.atoms) {
                    $.atoms = {}
                }

                await this.getAtomFormURL(atomType, atomClassify, version, isMeta).then(async response => {
                    const { form: formResource, form_is_embedded: embedded } = response

                    // 标准插件配置项内嵌到 form 字段
                    if (embedded) {
                        /*eslint-disable */
                        eval(formResource)
                        /*eslint-disable */
                        this.setAtomsConfig(setTypeName, $.atoms[setTypeName], version)
                        return Promise.resolve({ data: $.atoms[setTypeName] })
                    }

                    return await new Promise ((resolve, reject) => {
                        $.getScript(`${$.context.site_url}${formResource}`).then(response => {
                            this.setAtomsConfig(setTypeName, $.atoms[setTypeName], version)
                            resolve(response)
                        })
                    })
                })
            },
            getAtomFormURL (type, classify, version = '', isMeta) {
                let url = ''
                // 变量暂时没有版本系统
                if (classify === 'variable') {
                    url = isMeta ? `api/v3/variable/?meta=1` : `api/v3/variable/${type}/`
                } else {
                    url = isMeta
                        ? `api/v3/component/${type}/?meta=1&version=${version}`
                        : `api/v3/component/${type}/?version=${version}`
                }

                return $.get({ url: `${$.context.site_url}${url}` })
            },
            setAtomsConfig (name, config, version) {
                if (this.atomsConfig[name]) {
                    this.atomsConfig[name][version] = config
                } else {
                    this.atomsConfig[name] = {
                        [version]: config
                    }
                }
            },
            setContext () {
                const { project, bk_biz_id, site_url } = this.context
                $.context = {
                    project,
                    bk_biz_id,
                    site_url,
                    get (attr) { // 获取 $.context 对象上属性
                        return $.context[attr]
                    },
                    getBkBizId () { // 项目来自 cmdb，则获取对应的业务 id
                        if ($.context.project) {
                            return $.context.project.from_cmdb ? $.context.project.bk_biz_id : ''
                        }
                        return ''
                    },
                    getProjectId () { // 获取项目 id
                        if ($.context.project) {
                            return $.context.project.id
                        }
                        return ''
                    },
                    canSelectBiz () { // 是否可以选择业务
                        if ($.context.project) {
                            return !$.context.project.from_cmdb
                        }
                        return true
                    }
                }
            },
            /**
             * 设置表单默认值
             * 若传入的 formData 不包含表单项的值，取值顺序为：标准插件配置项 value 字段 -> 标准插件配置项 default 字段 -> tag 类型默认值
             * @param {Array} scheme 表单配置项
             * @param {Object} data 表单值
             */
            setDefaultValue (scheme, data) {
                if (!scheme || !Array.isArray(scheme)) return

                scheme.forEach(item => {
                    const key = item.tag_code

                    /** warning 前端tag结构变化数据兼容 */
                    if (item.tag_code === 'job_task') {
                        data[item.tag_code] = this.reloadValue(item, data)
                    }

                    if (item.type === 'combine') {
                        if (!this.hooked || !this.hooked[item.tag_code]) {
                            if (!(key in data)) {
                                this.$set(data, key, {})
                                this.$set(this.value, key, {})
                            }
                            this.setDefaultValue(item.attrs.children, data[key])
                        }
                    } else {
                        if (!(key in data)) {
                            let val
                            if ('value' in item.attrs) {
                                val = tools.deepClone(item.attrs.value)
                            } else if ('default' in item.attrs) {
                                val = tools.deepClone(item.attrs.default)
                            } else {
                                switch (item.type) {
                                    case 'input':
                                    case 'textarea':
                                    case 'radio':
                                    case 'text':
                                    case 'datetime':
                                    case 'password':
                                    case 'member_selector':
                                        val = ''
                                        break
                                    case 'checkbox':
                                    case 'datatable':
                                    case 'tree':
                                    case 'upload':
                                        val = []
                                        break
                                    case 'select':
                                        val = item.attrs.multiple ? [] : ''
                                        break
                                    case 'int':
                                        val = 0
                                        break
                                    case 'ip_selector':
                                        val = {
                                            selectors: [],
                                            ip: [],
                                            topo: [],
                                            filters: [],
                                            excludes: [],
                                            with_cloud_id: false
                                        }
                                        break
                                    default:
                                        val = ''
                                }
                            }
                            this.$set(data, key, val)
                        }
                    }
                })
            },
            getFormValue (atom) {
                /** warning 前端tag结构变化数据兼容 */
                if (atom.tag_code === 'job_task') {
                    this.value[atom.tag_code] = this.reloadValue(atom, this.value)
                }
                return this.formData[atom.tag_code]
            },
            updateForm (fieldArr, val) {
                const fieldDataObj = tools.deepClone(this.formData)
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
                this.$emit('change', fieldDataObj)
            },
            updateHook (field, val) {
                this.$emit('onHookChange', field, val)
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
<style lang="scss" scoped>
.render-form {
    /deep/ .rf-group-name {
        margin-bottom: 12px;
        .name {
            display: inline-block;
            margin: 0;
            margin-bottom: -1px;
            padding: 5px 14px;
            font-size: 12px;
            font-weight: 600;
            color: #313238;
        }
        &:before {
            content: '';
            display: inline-block;
            position: relative;
            top: 4px;
            width: 2px;
            height: 20px;
            background: #a3c5fd;
        }
        .rf-group-desc {
            color: #c4c6cc;
            font-size: 14px;
            cursor: pointer;
            &:hover {
                color: #f4aa1a;
            }
        }
    }
    
}
</style>
