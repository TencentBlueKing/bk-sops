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
    <div class="setting-wrapper">
        <section class="setting-section attr-setting">
            <h3>{{ i18n.attr }}</h3>
            <setting-form
                v-if="editingForm.config"
                ref="attrForm"
                :setting="attrForms.setting"
                :value="attrForms.value"
                :rules="attrForms.rules"
                @change="onAttrFormChange">
            </setting-form>
        </section>
        <section class="setting-section event-setting">
            <h3>{{ i18n.relativeEvent }}</h3>
            <setting-form
                v-for="(event, index) in eventList"
                ref="eventForm"
                class="form-block"
                :key="index"
                :setting="eventConfig"
                :value="event"
                :rules="eventRules"
                :show-close="true"
                @change="onSettingItemChange($event, 'event', index)"
                @delete="deleteSettingItem('event', index)">
            </setting-form>
            <add-comp @click="addSettingItem('event')"></add-comp>
        </section>
        <section class="setting-section">
            <h3>{{ i18n.method }}</h3>
            <setting-form
                v-for="(method, index) in methodList"
                ref="methodForm"
                class="form-block"
                :key="index"
                :setting="methodConfig"
                :value="method"
                :rules="methodRules"
                :show-close="true"
                @change="onSettingItemChange($event, 'method', index)"
                @delete="deleteSettingItem('method', index)">
            </setting-form>
            <add-comp @click="addSettingItem('method')"></add-comp>
        </section>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import AddComp from './AddComp.vue'
    import SettingForm from './SettingForm.vue'
    import tools from '@/utils/tools.js'
    import serializeObj from '@/utils/serializeObj.js'

    const REQUIRED_RULE = {
        required: true,
        message: gettext('必填项'),
        trigger: 'blur'
    }

    const NAME_RULE = [
        {
            max: 50,
            message: gettext('不能多于50个字符'),
            trigger: 'blur'
        },
        {
            reg: /^[a-zA-Z_][a-zA-Z0-9_]*/,
            message: gettext('输入字符必须由字母、数字、下划线组成，并且不能以数字开头')
        }
    ]
    const ARRAY_OBJ_FUNC_RULE = {
        validator (val) {
            if (val.trim() !== '') {
                try {
                    eval(`(${val})`)
                    return true
                } catch (error) {
                    return false
                }
            }
            return true
        },
        message: gettext('输入不合法'),
        trigger: 'blur'
    }

    const EVENT_CONFIG = [
        {
            name: 'source',
            comp: 'bk-select',
            required: true,
            props: {
                placeholder: gettext('请选择所监听表单的tag_code')
            }
        },
        {
            name: 'type',
            comp: 'bk-input',
            required: true,
            props: {
                placeholder: gettext('请输入所监听表单的事件类型')
            }
        },
        {
            name: 'action',
            comp: 'bk-input',
            required: true,
            props: {
                type: 'textarea',
                rows: 5,
                placeholder: gettext('请输入所监听事件的回调方法，参数为所监听表单的值，eg: function (value) {}')
            }
        }
    ]

    const EVENT_RULES = {
        source: [
            REQUIRED_RULE,
            ...NAME_RULE
        ],
        type: [
            REQUIRED_RULE,
            ...NAME_RULE
        ],
        action: [
            REQUIRED_RULE,
            Object.assign({}, ARRAY_OBJ_FUNC_RULE, {
                message: gettext('请输入合法的函数')
            })
        ]
    }

    const METHOD_CONFIG = [
        {
            name: 'funcName',
            comp: 'bk-input',
            required: true,
            props: {
                placeholder: gettext('请输入方法名称')
            }
        },
        {
            name: 'funcBody',
            comp: 'bk-input',
            required: true,
            props: {
                type: 'textarea',
                rows: 5,
                placeholder: gettext('请输方法内容, eg: function () { console.log(this.value) }')
            }
        }
    ]

    const METHOD_RULES = {
        funcName: [
            REQUIRED_RULE,
            ...NAME_RULE
        ],
        funcBody: [
            REQUIRED_RULE,
            Object.assign({}, ARRAY_OBJ_FUNC_RULE, {
                message: gettext('请输入合法的函数')
            })
        ]
    }

    export default {
        name: 'AtomSetting',
        components: {
            AddComp,
            SettingForm
        },
        props: {
            showAtomSetting: {
                type: Boolean,
                default: false
            },
            editingForm: {
                type: Object,
                default () {
                    return {}
                }
            },
            tagCodeList: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                attrForms: this.transformAttrs(this.editingForm.config),
                eventConfig: this.getEventConfig(),
                methodConfig: METHOD_CONFIG,
                eventList: this.transformEvents(this.editingForm.config.events),
                methodList: this.transformMethods(this.editingForm.config.methods),
                eventRules: EVENT_RULES,
                methodRules: METHOD_RULES,
                i18n: {
                    attr: gettext('属性'),
                    relativeEvent: gettext('关联事件'),
                    method: gettext('方法'),
                    arrPlaceholder: gettext('请输入数组格式数据'),
                    objPlaceholder: gettext('请输入对象格式数据'),
                    funcPlaceholder: gettext('请输入匿名函数')
                }
            }
        },
        watch: {
            editingForm: {
                deep: true,
                handler (val) {
                    this.attrForms = this.transformAttrs(val.config)
                    this.eventList = this.transformEvents(val.config.events)
                    this.methodList = this.transformMethods(val.config.methods)
                    this.eventConfig = this.getEventConfig()
                }
            },
            tagCodeList (val) {
                this.eventConfig = this.getEventConfig()
                this.attrForms = this.transformAttrs(val.config)
            }
        },
        methods: {
            transformAttrs (config = {}) {
                const { tag_code, attrs } = config
                const value = {}
                const setting = []
                const rules = {}
                const tagCodeList = this.tagCodeList.filter(item => item !== tag_code)

                value['tag_code'] = tag_code
                setting.push({
                    name: 'tag_code',
                    comp: 'bk-input',
                    required: true,
                    props: {
                        placeholder: gettext('表单项唯一标识，单个标准插件内不能重复')
                    }
                })
                rules['tag_code'] = [
                    REQUIRED_RULE,
                    ...NAME_RULE,
                    {
                        validator (val) {
                            return !tagCodeList.includes(val)
                        },
                        message: gettext('单个标准插件里表单项 tag_code 不能重复'),
                        trigger: 'blur'
                    }
                ]
                
                Object.keys(attrs || {}).forEach(item => {
                    const attr = attrs[item]
                    // 默认取设定的第一种数据类型
                    // 部分 Tag 的 value 属性的 type 为包含 String 的数组，是为了兼容表单勾选到全局变量的情况
                    const type = Array.isArray(attr.type) ? attr.type[0] : attr.type

                    switch (type) {
                        case String:
                            value[item] = attr.value
                            setting.push({
                                name: item,
                                comp: 'bk-input',
                                required: attr.required,
                                props: {
                                    placeholder: attr.desc
                                }
                            })
                            break
                        case Number:
                            value[item] = attr.value
                            setting.push({
                                name: item,
                                comp: 'bk-input',
                                required: attr.required,
                                props: {
                                    type: 'number',
                                    placeholder: attr.desc
                                }
                            })
                            break
                        case Boolean:
                            value[item] = attr.value
                            setting.push({
                                name: item,
                                comp: 'bk-switcher',
                                required: attr.required,
                                props: {
                                    size: 'small'
                                }
                            })
                            break
                        case Array:
                            value[item] = attr.value.length > 0 ? serializeObj(attr.value) : ''
                            setting.push({
                                name: item,
                                comp: 'bk-input',
                                required: attr.required,
                                props: {
                                    type: 'textarea',
                                    rows: 5,
                                    placeholder: attr.desc
                                }
                            })
                            rules[item] = [Object.assign({}, ARRAY_OBJ_FUNC_RULE, {
                                message: gettext('请输入合法的数组')
                            })]
                            break
                        case Function:
                            value[item] = serializeObj(attr.value)
                            setting.push({
                                name: item,
                                comp: 'bk-input',
                                required: attr.required,
                                props: {
                                    type: 'textarea',
                                    rows: 5,
                                    placeholder: attr.desc
                                }
                            })
                            rules[item] = [Object.assign({}, ARRAY_OBJ_FUNC_RULE, {
                                message: gettext('请输入合法的函数')
                            })]
                            break
                        case Object:
                            value[item] = Object.keys(attr.value).length > 0 ? serializeObj(attr.value) : ''
                            setting.push({
                                name: item,
                                comp: 'bk-input',
                                required: attr.required,
                                props: {
                                    type: 'textarea',
                                    rows: 5,
                                    placeholder: attr.desc
                                }
                            })
                            rules[item] = [Object.assign({}, ARRAY_OBJ_FUNC_RULE, {
                                message: gettext('请输入合法的对象')
                            })]
                            break
                        default:
                            break
                    }

                    if (attr.required) {
                        rules[item] = [REQUIRED_RULE]
                    }
                })
                return {
                    setting,
                    value,
                    rules
                }
            },
            getEventConfig () {
                return EVENT_CONFIG.map(item => {
                    const config = tools.deepClone(item)
                    if (config.name === 'source' && this.editingForm.config) {
                        const tagCodeList = this.tagCodeList.filter(item => item !== this.editingForm.config.tag_code)
                        config.props.list = tagCodeList.map(tagCode => {
                            return { id: tagCode, name: tagCode }
                        })
                    }
                    return config
                })
            },
            transformEvents (events = []) {
                if (Array.isArray(events)) {
                    return events.map(item => {
                        const { source, type, action } = item
                        return {
                            source,
                            type,
                            action: serializeObj(action)
                        }
                    })
                }
                return []
            },
            transformMethods (methods = []) {
                if (methods) {
                    return Object.keys(methods).map(key => {
                        return {
                            funcName: key,
                            funcBody: serializeObj(methods[key])
                        }
                    })
                }
                return []
            },
            // 将编辑的表单项转换成原始 config 格式
            getFormConfig () {
                const form = tools.deepClone(this.editingForm)
                form.config.tag_code = this.attrForms.value.tag_code
                Object.keys(this.attrForms.value).forEach(item => {
                    if (item !== 'tag_code') {
                        const value = tools.deepClone(this.attrForms.value[item])
                        const attr = form.config.attrs[item]
                        const type = Array.isArray(attr.type) ? attr.type[0] : attr.type
                        if ([Array, Object, Function].includes(type)) {
                            if (value.trim() !== '') {
                                attr.value = eval(`(${value})`)
                            }
                        } else {
                            attr.value = value
                        }
                    }
                })
                if (this.eventList.length > 0) {
                    form.config.events = []
                    this.eventList.forEach(item => {
                        if (item.action.trim() !== '') {
                            form.config.events.push({
                                source: item.source,
                                type: item.type,
                                action: eval(`(${item.action})`)
                            })
                        }
                    })
                }
                if (this.methodList.length > 0) {
                    this.methodList.forEach(item => {
                        if (item.funcBody.trim() !== '') {
                            form.config.methods[item.funcName] = eval(`(${item.funcBody})`)
                        }
                    })
                }
                return form
            },
            onAttrFormChange (val) {
                this.attrForms.value = val
            },
            onSettingItemChange (val, type, index) {
                const list = type === 'event' ? this.eventList : this.methodList
                list.splice(index, 1, val)
            },
            addSettingItem (type) {
                let config, list
                if (type === 'event') {
                    config = {
                        source: '',
                        type: '',
                        action: ''
                    }
                    list = this.eventList
                } else {
                    config = {
                        funcName: '',
                        funcBody: ''
                    }
                    list = this.methodList
                }
                list.push(config)
            },
            deleteSettingItem (type, index) {
                const list = type === 'event' ? this.eventList : this.methodList
                list.splice(index, 1)
            },
            async validate () {
                try {
                    await this.$refs.attrForm.validate()
                    if (this.$refs.eventForm && this.$refs.eventForm.length > 0) {
                        await Promise.all(this.$refs.eventForm.map(item => item.validate()))
                    }
                    if (this.$refs.methodForm && this.$refs.methodForm.length > 0) {
                        await Promise.all(this.$refs.methodForm.map(item => item.validate()))
                    }
                    const formConfig = this.getFormConfig()
                    this.$emit('onCloseSettingPanel', formConfig)
                } catch (err) {
                    console.log(err)
                    this.$bkMessage({
                        theme: 'warning',
                        message: gettext('请检查表单配置项')
                    })
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .setting-wrapper {
        padding: 10px 20px;
    }
    .setting-section {
        & > h3 {
            font-size: 14px;
        }
    }
    .setting-form {
        margin-bottom: 10px;
        &.form-block {
            padding: 20px 30px;
            background: #f0f1f5;
        }
    }
</style>
