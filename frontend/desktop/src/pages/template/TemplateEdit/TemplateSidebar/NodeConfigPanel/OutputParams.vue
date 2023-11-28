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
    <div class="output-params">
        <bk-table :data="outputsList" :col-border="false" :row-class-name="getRowClassName">
            <bk-table-column :label="$t('名称')" :width="150" prop="name">
                <p
                    slot-scope="props"
                    class="output-name"
                    v-bk-tooltips="props.row.description">
                    {{ props.row.name }}
                </p>
            </bk-table-column>
            <bk-table-column label="Key">
                <div slot-scope="props" class="output-key">
                    <div v-bk-overflow-tips class="key">{{ props.row.key }}</div>
                    <div
                        v-if="props.row.hooked"
                        class="hooked-input"
                        :class="{ 'disabled': isViewMode, 'active': isHookingVariable === props.row.key }">
                        <span class="key" v-bk-overflow-tips>{{ props.row.varKey }}</span>
                        <i class="bk-icon icon-edit-line" @click="handleVariableHook(props.row.key)"></i>
                    </div>
                    <i
                        :class="['common-icon-variable-hook hook-icon', {
                            actived: props.row.hooked,
                            disabled: isViewMode
                        }]"
                        v-bk-tooltips="{
                            content: props.row.hooked ? $t('取消接收输出') : $t('使用变量接收输出'),
                            placement: 'top',
                            zIndex: 3000
                        }"
                        @click="onHookChange(props)">
                    </i>
                </div>
            </bk-table-column>
        </bk-table>
    </div>
</template>
<script>
    import { random4 } from '@/utils/uuid.js'
    import bus from '@/utils/bus.js'
    import { mapState } from 'vuex'
    export default {
        name: 'OutputParams',
        props: {
            params: Array,
            hook: {
                type: Boolean,
                default: true
            },
            basicInfo: Object,
            constants: Object,
            thirdPartyCode: String,
            isSubFlow: Boolean,
            isViewMode: Boolean,
            nodeId: String,
            version: String // 标准插件版本或子流程版本
        },
        data () {
            return {
                isHookingVariable: '',
                unhookingVarIndex: 0 // 正被取消勾选的表单下标
            }
        },
        computed: {
            ...mapState({
                'varPanelActivated': state => state.template.varPanelActivated
            }),
            outputsList () {
                const list = []
                const varKeys = Object.keys(this.constants)
                this.params.forEach(param => {
                    let { key: varKey } = param
                    const isHooked = varKeys.some(item => {
                        const varItem = this.constants[item]
                        if (varItem.source_type === 'component_outputs') {
                            const sourceInfo = varItem.source_info[this.nodeId]
                            if (sourceInfo && sourceInfo.includes(param.key)) {
                                varKey = item
                                return true
                            }
                        }
                    })
                    list.push({
                        key: param.key,
                        varKey,
                        name: param.name,
                        description: param.schema ? param.schema.description : '--',
                        version: param.version,
                        status: param.status,
                        hooked: isHooked
                    })
                })
                return list
            }
        },
        watch: {
            varPanelActivated (val) {
                if (!val) {
                    this.isHookingVariable = ''
                }
            }
        },
        created () {
            // 表单项使用变量
            bus.$on('useVariable', (data) => {
                const { variable = {} } = data
                if (variable.cited_info?.source !== 'output') return

                this.$emit('updateConstants', 'edit', data.variable)
            })
        },
        beforeDestroy () {
            bus.$off('useVariable')
        },
        methods: {
            getRowClassName ({ row }) {
                return row.status || ''
            },
            /**
             * 输出参数勾选切换
             */
            onHookChange (props) {
                if (this.isViewMode) return
                const index = props.$index
                this.unhookingVarIndex = index
                if (!props.row.hooked) {
                    props.row.hooked = true
                    // 输出选中默认新建不弹窗，直接生成变量。 如果有冲突则key+随机数
                    const { key, version, plugin_code } = props.row
                    const value = /^\$\{\w+\}$/.test(key) ? key : `\${${key}}`
                    const isExist = value in this.constants
                    let setKey = ''
                    if ((/^\$\{((?!\{).)*\}$/).test(key)) {
                        setKey = isExist ? key.slice(0, -1) + `_${random4()}}` : key
                        props.row.varKey = setKey
                    } else {
                        setKey = isExist ? `\$\{${key + '_' + random4()}\}` : `\$\{${key}\}`
                        props.row.varKey = setKey
                    }
                    const config = {
                        name: props.row.name,
                        key: setKey,
                        source_info: {
                            [this.nodeId]: [this.params[index].key]
                        },
                        version,
                        plugin_code: this.isSubFlow ? plugin_code : (this.thirdPartyCode || '')
                    }
                    this.createVariable(config)
                } else {
                    const config = ({
                        id: this.nodeId,
                        key: props.row.varKey,
                        tagCode: props.row.varKey,
                        source: 'output'
                    })
                    this.$emit('updateConstants', 'delete', config)
                }
            },
            handleVariableHook (key) {
                if (this.isViewMode) return
                this.isHookingVariable = key
                const config = Object.values(this.constants).find(item => {
                    const { source_type: sourceType, source_info: sourceInfo = {} } = item
                    return sourceType === 'component_outputs' && sourceInfo[this.nodeId]?.includes(key)
                })
                const scheme = this.outputsList.find(item => item.key === key)
                bus.$emit('variableHook', {
                    ...config,
                    cited_info: {
                        key: scheme.varKey,
                        type: 'edit',
                        source: 'output',
                        plugin: this.basicInfo.name,
                        field: scheme.name,
                        tagCode: scheme.key,
                        nodeId: this.nodeId,
                        nodeName: this.basicInfo.nodeName,
                        isSubFlow: this.isSubFlow
                    }
                })
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
                    version: '',
                    plugin_code: ''
                }
                const variable = Object.assign({}, defaultOpts, variableOpts)
                this.$emit('updateConstants', 'create', variable)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .output-params {
        padding: 16px 30px 32px;
    }
    .bk-table {
        /deep/ .bk-table-row {
            &.deleted {
                background: #fff5f4;
            }
            &.added {
                background: rgba(220,255,226,0.30);
            }
            .param-key .cell {
                padding-right: 50px;
            }
        }
    }
    .output-name {
        display: inline-block;
        max-width: 100%;
        border-bottom: 1px dashed #979ba5;
        cursor: default;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
    }
    .output-key {
      display: flex;
      align-items: center;
      justify-content: space-between;
      .key {
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }
      .hooked-input {
        flex: 1;
        height: 32px;
        min-width: 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 8px;
        margin: 0 15px;
        background: #fafbfd;
        border: 1px solid #dcdee5;
        border-radius: 2px;
        &.disabled {
            cursor: not-allowed;
            .icon-edit-line {
                color: #c4c6cc;
                &:hover {
                    background: #f0f1f5;
                    cursor: not-allowed;
                }
            }
        }
        &.active {
            border-color: #3a84ff;
        }
      }
      .icon-edit-line {
        width: 24px;
        height: 24px;
        display: inline-block;
        text-align: center;
        line-height: 24px;
        font-size: 16px;
        color: #979ba5;
        background: #f0f1f5;
        border-radius: 2px;
        cursor: pointer;
        &:hover {
          color: #3a84ff;
          background: #e1ecff;
        }
      }
    }
    .hook-icon {
        flex-shrink: 0;
        display: inline-block;
        width: 32px;
        height: 32px;
        line-height: 32px;
        font-size: 16px;
        color: #979ba5;
        background: #f0f1f5;
        text-align: center;
        border-radius: 2px;
        cursor: pointer;
        &.disabled {
            color: #c4c6cc;
            cursor: not-allowed;
        }
        &.actived {
            color: #3a84ff;
        }
    }
</style>
