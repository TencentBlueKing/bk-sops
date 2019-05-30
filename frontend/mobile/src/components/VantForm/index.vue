/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<script>
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'

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
                } // 普通的 HTML 特性
            }
        },
        created () {
            this.loadData()
        },
        methods: {
            ...mapActions('component', [
                'getVariableConfig',
                'getAtomConfig'
            ]),
            async loadData () {
                const [configKey, tagCode] = this.sourceCode.split('.')
                // customType参数加载配置文件
                if (this.customType) {
                    try {
                        if (!global.$.atoms || !global.$.atoms[this.customType]) {
                            await this.getVariableConfig({ customType: this.customType })
                        }
                    } catch (e) {
                        errorHandler(e, this)
                    }
                } else {
                    try {
                        if (!global.$.atoms || !global.$.atoms[configKey]) {
                            await this.getAtomConfig({ atomCode: configKey })
                        }
                    } catch (e) {
                        errorHandler(e, this)
                    }
                }
                const atomConfigs = global.$.atoms[configKey]
                if (atomConfigs && atomConfigs.length) {
                    atomConfigs.some(item => {
                        if (item['tag_code'] === tagCode) {
                            this.atomConfig = item
                            if (!this.customType) {
                                this.label = item.attrs.name
                                this.componentTag = item.type
                            } else {
                                this.componentTag = tagCode
                            }
                            if (item.attrs.validation) {
                                this.attrs.required = item.attrs.validation.some((v) => v.type === 'required')
                                this.domAttr.validation = { required: true }
                            }
                            if (item.attrs.placeholder) {
                                this.placeholder = item.attrs.placeholder
                            }
                            if (item.type === 'select') {
                                this.domAttr.select = {
                                    columns: item.attrs.items,
                                    defaultVal: item.attrs.items.findIndex(o => o.text === this.value),
                                    tagCode: this.customType ? this.customType : this.sourceCode
                                }
                            } else if (item.type === 'checkbox') {
                                const checkboxData = item.attrs.items
                                const checkedList = checkboxData.filter(o => item.attrs['default'].includes(o.value)).map(({ name }) => name)
                                this.data.value = checkedList.join(',')
                                this.domAttr.checkbox = {
                                    checkedList: item.attrs['default'],
                                    list: checkboxData.map(({ value }) => value)
                                }
                            } else if (item.type === 'int') {
                                this.value = this.value ? Number.parseInt(this.value) : 0
                            } else if (!MOBILE_SUPPORTTED_COMPONENTS.includes(item.type)) {
                                this.componentTag = 'cell'
                                this.value = JSON.stringify(this.data.value)
                            } else if (item.type === 'password') {
                                this.domAttr.type = item.type
                                this.componentTag = 'input'
                            }
                            return true
                        }
                    })
                }
                this.fillDomConfig()
            },
            fillDomConfig () {
                this.domName = 'vant-' + this.componentTag
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
            console.log(this.domAttr)
            return h(this.domName, {
                nativeOn: {
                    change: function (event) {
                        self.$emit('dataChange', event.target.value, self.customType ? self.data['key'] : self.sourceCode, self.customType)
                    },
                    click: function (event) {
                        if (self.customType === 'datetime') {
                            self.$emit('dataChange', event.target.value, self.data['key'], self.customType)
                        } else if (self.customType === 'select') {
                            self.$emit('onSelect', self.domAttr.select)
                        }
                    }
                },
                props: this.domAttr
            })
        }
    }
</script>
