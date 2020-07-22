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
            <bk-table-column :label="$t('名称')" :width="250" align="center" prop="name"></bk-table-column>
            <bk-table-column label="KEY" align="center" prop="key"></bk-table-column>
            <bk-table-column :label="$t('引用')" :width="100" align="center">
                <template slot-scope="props">
                    <bk-checkbox
                        v-model="props.row.hooked"
                        @change="onHookChange(props, $event)">
                    </bk-checkbox>
                </template>
            </bk-table-column>
        </bk-table>
        <on-hook-dialog
            :is-show="isShow"
            :data="formData"
            @confirm="onConfirmReuseVar"
            @cancel="onCancelReuseVar">
        </on-hook-dialog>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapMutations } from 'vuex'
    import onHookDialog from './onHookDialog'
    export default {
        name: 'OutputParams',
        components: {
            onHookDialog
        },
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
                isShow: false,
                formData: {},
                selectIndex: '',
                propsInfo: {}
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
                    let name = param.name
                    const isHooked = varKeys.some(item => {
                        const varItem = constants[item]
                        if (varItem.source_type === 'component_outputs') {
                            const sourceInfo = varItem.source_info[this.nodeId]
                            if (sourceInfo && sourceInfo.includes(param.key)) {
                                key = item
                                name = varItem.name
                                return true
                            }
                        }
                    })
                    list.push({
                        key,
                        name,
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
                if (val) {
                    this.isShow = true
                    this.formData = props.row
                    this.selectIndex = props.$index
                    this.propsInfo = props
                } else {
                    this.deleteVariable(props.row.key)
                    this.list[props.$index].key = this.params[props.$index].key
                    this.list[props.$index].name = this.params[props.$index].name
                }
            },
            onConfirmReuseVar (type, data) {
                this.isShow = false
                const version = this.isSubflow ? this.propsInfo.version : this.version
                const config = {
                    name: data.name,
                    key: `\$\{${data.key}\}`,
                    source_info: {
                        [this.nodeId]: [this.formData.key]
                    },
                    version
                }
                this.list[this.selectIndex].name = data.name
                this.list[this.selectIndex].key = `\$\{${data.key}\}`
                this.createVariable(config)
            },
            /**
             * 取消复用变量回调
             */
            onCancelReuseVar (key) {
                this.isShow = false
                this.list[this.selectIndex].hooked = false
                console.log(this.list[this.selectIndex])
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
