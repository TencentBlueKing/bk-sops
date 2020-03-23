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
        <bk-table :data="params" :border="true">
            <bk-table-column :label="i18n.name" :width="250" align="center" prop="name"></bk-table-column>
            <bk-table-column label="KEY" align="center" prop="key"></bk-table-column>
            <bk-table-column :label="i18n.cite" :width="100" align="center">
                <template slot-scope="props">
                    <bk-checkbox :value="getHookStatus(props.row)" @change="onToggleCheck(props, $event)"></bk-checkbox>
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
            params: {
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
            }
        },
        data () {
            return {
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
        methods: {
            ...mapMutations('template/', [
                'addVariable',
                'deleteVariable'
            ]),
            /**
             * 输出参数勾选切换
             */
            onToggleCheck (props, checked) {
                const { key, name, version } = props.row
                const index = props.$index
                const vs = this.nodeConfig.type === 'ServiceActivity'
                    ? (this.nodeConfig.component.version || 'legacy')
                    : (version || 'legacy')
                const variableKey = this.generateRandomKey(key)
                if (checked) { // hook
                    const variableOpts = {
                        name,
                        key: variableKey,
                        source_type: 'component_outputs',
                        source_info: {
                            [this.nodeConfig.id]: [key]
                        },
                        source_tag: '',
                        custom_type: '',
                        show_type: 'hide',
                        version: vs
                    }
                    this.$set(this.params[index], 'key', variableKey)
                    this.hookToGlobal(variableOpts)
                } else { // cancel
                    const constant = this.constants[key]
                    if (constant) {
                        this.deleteVariable(key)
                    }
                }
            },
            generateRandomKey (key) {
                let variableKey = key.replace(/^\$\{/, '').replace(/(\}$)/, '').slice(0, 14)
                do {
                    variableKey = '${' + variableKey + '_' + random4() + '}'
                } while (this.constants[variableKey])
                return variableKey
            },
            /**
             * 获取输出参数勾选状态
             * 变量全局变量中 source_info 里是否含有该变量
             */
            getHookStatus (row) {
                const key = row.key
                for (const cKey in this.constants) {
                    const constant = this.constants[cKey]
                    if (constant.source_type === 'component_outputs'
                        && constant.source_info[this.nodeConfig.id]
                        && constant.source_info[this.nodeConfig.id].indexOf(key) > -1
                    ) {
                        return true
                    }
                }
                return false
            },
            /**
             * 勾选到全局变量变量，不同节点间的相同变量没有复用逻辑，每次勾选用生成新的随机数拼接
             */
            hookToGlobal (variableOpts) {
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
            }
        }
    }
</script>
