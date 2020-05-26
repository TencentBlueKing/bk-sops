/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<script>

    import { JSEncrypt } from 'jsencrypt'

    const MOBILE_SUPPORTTED_COMPONENTS = ['input', 'int', 'textarea', 'datetime', 'checkbox', 'radio', 'select', 'password']

    const components = require.context(
        '.',
        false,
        /Vant[A-Z]\w+\.(vue|js)$/
    )

    const registry = {}

    const register = (fileName, context) => {
        const componentConfig = context(fileName)
        const comp = componentConfig.default
        const name = 'vant-' + comp.name.slice(4).toLowerCase()
        registry[name] = comp
    }

    components.keys().forEach(fileName => {
        register(fileName, components)
    })

    export default {
        name: 'VantForm',
        components: {
            ...registry
        },
        props: {
            renderConfig: {
                type: Array
            },
            // 如果tagCode不为空，则为原子表单组件，需要加载atom的配置文件
            sourceCode: {
                type: String,
                default: ''
            },
            // 客户自己定义的表单参数类型，例如Input,int,datetime,textarea等，默认cell只做展示
            customType: {
                type: String,
                default: 'cell'
            },
            label: {
                type: String,
                default: ''
            },
            placeholder: {
                type: String,
                default: ''
            },
            value: {
                type: String,
                default: ''
            },
            data: {
                type: Object
            }
        },
        data () {
            return {
                componentTag: 'cell',
                domName: 'vant-cell',
                domAttr: {},
                atomConfig: {},
                key: '',
                attrs: {
                    required: false
                }
            }
        },
        created () {
            this.beforeRender()
        },
        methods: {
            beforeRender () {
                const tagCode = this.sourceCode.split('.')[1]
                this.renderConfig.some(item => {
                    if (item['tag_code'] === tagCode) {
                        this.atomConfig = item
                        if (!this.customType) {
                            this.label = item.attrs.name
                            this.componentTag = item.type
                        } else {
                            this.componentTag = tagCode
                        }
                        // 处理元变量的情况
                        this.processMetaVariable(item)
                        if (item.attrs.validation) {
                            this.attrs.required = item.attrs.validation.some((v) => v.type === 'required')
                            this.domAttr.validation = { required: this.attrs.required }
                        }
                        if (item.attrs.placeholder) {
                            this.placeholder = item.attrs.placeholder
                        }
                        if (item.type === 'select') {
                            const defaultIndex = item.attrs.items.findIndex(o => o.text === this.value)
                            this.domAttr.select = {
                                multiple: item.attrs.multiple,
                                columns: item.attrs.items,
                                defaultVal: item.attrs.multiple ? item.attrs.value : [defaultIndex],
                                tagCode: this.customType ? this.customType : this.sourceCode
                            }
                            if (!item.attrs.multiple) {
                                this.domAttr.select.defaultIndex = defaultIndex
                            }
                        } else if (item.type === 'radio') {
                            // radio用picker代替
                            const radioDefaultVal = this.value ? this.value : item.attrs.default
                            const defaultIndex = item.attrs.items.findIndex((value) => {
                                if (typeof value === 'object') {
                                    return value.value === radioDefaultVal
                                } else {
                                    return value === item.attrs.default
                                }
                            })
                            this.domAttr.select = {
                                multiple: false,
                                columns: item.attrs.items,
                                defaultIndex: defaultIndex,
                                tagCode: this.customType ? this.customType : this.sourceCode
                            }
                        } else if (item.type === 'checkbox') {
                            const checkboxData = []
                            const checkValueList = this.data.value
                            const checkedNameList = []
                            item.attrs.items.forEach(i => {
                                const selected = this.data.value.includes(i.value)
                                if (selected) {
                                    checkedNameList.push(i.name)
                                }
                                checkboxData.push(Object.assign({}, { selected: selected, text: i.name }, i))
                            })
                            this.value = checkedNameList.join(',')
                            this.domAttr.select = {
                                multiple: true,
                                columns: checkboxData,
                                defaultVal: checkValueList,
                                tagCode: this.customType ? this.customType : this.sourceCode
                            }
                        } else if (item.type === 'int') {
                            this.value = this.value ? Number.parseInt(this.value) : 0
                        } else if (item.type === 'meta') {
                            this.componentTag = 'cell'
                        } else if (!MOBILE_SUPPORTTED_COMPONENTS.includes(item.type)) {
                            this.componentTag = 'cell'
                            this.value = JSON.stringify(this.data.value)
                        }
                        return true
                    }
                })
                this.fillDomConfig()
            },

            processMetaVariable (variable) {
                if (variable.meta_transform && this.data.is_meta) {
                    const metaConfig = variable.meta_transform(this.data.meta || this.data)
                    variable.attrs = metaConfig.attrs
                    variable.type = metaConfig.type
                    this.value = metaConfig.attrs.items.filter(item => metaConfig.attrs.value.includes(item.value)).map(obj => obj.text).join(',')
                }
            },

            fillDomConfig () {
                if (this.componentTag === 'radio' || this.componentTag === 'checkbox') {
                    this.domName = 'vant-select'
                } else {
                    this.domName = 'vant-' + this.componentTag
                }
                this.domAttr.label = this.label
                this.domAttr.placeholder = this.placeholder
                this.domAttr.value = this.value
                this.$set(this.domAttr, 'data', this.data)
                this.domAttr.name = this.data.name
                if (this.data.validation && this.domAttr.validation) {
                    this.$set(this.domAttr.validation, 'regex', new RegExp(this.data.validation))
                }
            }
        },

        render (h) {
            const self = this
            return h(this.domName, {
                nativeOn: {
                    change: function (event) {
                        if (self.componentTag !== 'password') {
                            self.$emit('dataChange', event.target.value, self.data.key)
                        } else {
                            const crypt = new JSEncrypt()
                            const cryptVal = crypt.encrypt(event.target.value)
                            self.$emit('dataChange', cryptVal || event.target.value, self.data.key)
                        }
                    },
                    click: function (event) {
                        if (self.componentTag === 'datetime') {
                            self.$emit('dataChange', event.target.value, self.data.key, self.componentTag)
                        } else if (self.componentTag === 'select' || self.componentTag === 'checkbox') {
                            let val = self.$refs[self.data.key].value
                            if (self.componentTag === 'checkbox') {
                                val = self.$refs[self.data.key].checkedValue
                            }
                            if (val !== self.data.value) {
                                val = val ? val.split(',') : []
                                self.$emit('dataChange', val, self.data.key, self.componentTag)
                            }
                        } else if (self.componentTag === 'radio') {
                            const radioVal = self.$refs[self.data.key].choseKey
                            self.$emit('dataChange', radioVal, self.data.key, self.componentTag)
                        }
                    }
                },
                props: this.domAttr,
                ref: this.data.key
            })
        }
    }
</script>
