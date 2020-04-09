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
    <div class="output-params">
        <bk-table :data="list" :border="true">
            <bk-table-column :label="i18n.name" :width="250" align="center" prop="name"></bk-table-column>
            <bk-table-column label="KEY" align="center" prop="key"></bk-table-column>
            <bk-table-column :label="i18n.cite" :width="100" align="center">
                <template slot-scope="props">
                    <bk-checkbox
                        :value="props.row.hooked"
                        @change="onHookChange(props, $event)">
                    </bk-checkbox>
                </template>
            </bk-table-column>
        </bk-table>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapMutations } from 'vuex'
    import { random4 } from '@/utils/uuid.js'
    export default {
        name: 'OutputParams',
        props: {
            params: Array,
            isSubflow: Boolean,
            nodeId: String,
            version: String // 标准插件版本或子流程版本
        },
        data () {
            const list = this.getOutputsList(this.params)
            return {
                list,
                i18n: {
                    name: gettext('名称'),
                    cite: gettext('引用')
                }
            }
        },
        computed: {
            ...mapState({
                'constants': state => state.template.constants
            })
        },
        watch: {
            params (val) {
                this.list = this.getOutputsList(val)
            }
        },
        methods: {
            ...mapMutations('template/', [
                'addVariable',
                'deleteVariable'
            ]),
            getOutputsList () {
                const list = []
                const constants = this.$store.state.template.constants
                const varKeys = Object.keys(constants)
                this.params.forEach(param => {
                    let key = param.key
                    const isHooked = varKeys.some(item => {
                        const varItem = constants[item]
                        if (varItem.source_type === 'component_outputs') {
                            const sourceInfo = varItem.source_info[this.nodeId]
                            if (sourceInfo && sourceInfo.includes(param.key)) {
                                key = item
                                return true
                            }
                        }
                    })
                    list.push({
                        key,
                        name: param.name,
                        version: param.version,
                        hooked: isHooked
                    })
                })
                return list
            },
            /**
             * 输出参数勾选切换
             */
            onHookChange (props, val) {
                const { key, name } = props.row
                const version = this.isSubflow ? props.version : this.version
                const index = props.$index
                const variableKey = this.generateRandomKey(key)
                if (val) { // 勾选到全局变量，不同节点间的相同变量没有复用逻辑，每次勾选用生成新的随机数拼接
                    const config = {
                        name,
                        key: variableKey,
                        source_info: {
                            [this.nodeId]: [key]
                        },
                        version
                    }
                    this.list[index].key = variableKey
                    this.createVariable(config)
                } else { // 取消勾选
                    this.list[index].key = this.params[index].key
                    this.deleteVariable(key)
                }
                this.$emit('globalVariableUpdate')
            },
            // 随机生成变量 key，长度为 14，不可重复
            generateRandomKey (key) {
                let variableKey = key.replace(/^\$\{/, '').replace(/(\}$)/, '').slice(0, 14)
                do {
                    variableKey = '${' + variableKey + '_' + random4() + '}'
                } while (this.constants[variableKey])
                return variableKey
            },
            createVariable (variableOpts) {
                const len = Object.keys(this.constants).length
                const defaultOpts = {
                    name: '',
                    key: '',
                    desc: '',
                    custom_type: '',
                    source_info: {},
                    source_tag: '',
                    value: '',
                    show_type: 'hide',
                    source_type: 'component_outputs',
                    validation: '',
                    index: len,
                    version: ''
                }
                const variable = Object.assign({}, defaultOpts, variableOpts)
                this.addVariable(variable)
            }
        }
    }
</script>
