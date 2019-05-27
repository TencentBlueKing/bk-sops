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

    const MOBILE_SUPPORTTED_COMPONENTS = ['input', 'int', 'textarea', 'datetime', 'checkbox', 'radio', 'select']

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
                'getAtomConfig'
            ]),
            async loadData () {
                // 根据sourceCode加载atom配置
                if (this.sourceCode) {
                    const [atomCode, tagCode] = this.sourceCode.split('.')
                    try {
                        if (!global.$.atoms || !global.$.atoms[atomCode]) {
                            await this.getAtomConfig({ atomCode: atomCode })
                        }
                    } catch (e) {
                        errorHandler(e, this)
                    }
                    const atomConfigs = global.$.atoms[atomCode]
                    if (atomConfigs && atomConfigs.length) {
                        atomConfigs.some(item => {
                            if (item['tag_code'] === tagCode) {
                                this.atomConfig = item
                                this.label = item.attrs.name
                                this.domAttr.validation = item.attrs.validation
                                if (this.domAttr.validation) {
                                    this.attrs.required = this.domAttr.validation.some((v) => v.type === 'required')
                                    this.key = this.attrs.required ? 'required' : ''
                                }
                                if (item.attrs.placeholder) {
                                    this.placeholder = item.attrs.placeholder
                                }
                                if (item.type === 'select') {
                                    this.domAttr.select = {
                                        columns: item.attrs.items,
                                        defaultVal: item.attrs.items.findIndex(o => o.text === this.value),
                                        tagCode: this.sourceCode
                                    }
                                } else if (item.type === 'checkbox') {
                                    const checkboxData = item.attrs.items
                                    const checkedList = checkboxData.filter(o => item.attrs['default'].includes(o.value)).map(({ name }) => name)
                                    this.data.value = checkedList.join(',')
                                    console.log(this.data)
                                    this.domAttr.checkbox = {
                                        checkedList: item.attrs['default'],
                                        list: checkboxData.map(({ value }) => value)
                                    }
                                }
                                return true
                            }
                        })
                        // 如果在移动端支持的组件列表，统一用cell做显示
                        this.customType = MOBILE_SUPPORTTED_COMPONENTS.includes(this.atomConfig.type) ? this.atomConfig.type : 'cell'
                    }
                }
                this.fillDomConfig()
            },
            fillDomConfig () {
                this.domName = 'vant-' + this.customType
                this.domAttr.label = this.label
                this.domAttr.placeholder = this.placeholder
                this.domAttr.value = this.customType === 'int' ? (this.value ? Number.parseInt(this.value) : 0) : this.value
                this.domAttr.data = this.data
                this.domAttr.name = this.data.name
                if (this.data.validation) {
                    this.domAttr.validation = {
                        regex: new RegExp(this.data.validation)
                    }
                }
            }
        },
        render (h) {
            const self = this
            return h(this.domName, {
                nativeOn: {
                    change: function (event) {
                        self.$emit('dataChange', event.target.value, self.sourceCode ? self.sourceCode : self.data['key'], self.customType)
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
