<template>
    <bk-table
        ref="ipSeletorTable"
        :row-auto-height="true"
        :class="['ip-seletor-table', { 'disabled': !editable }]"
        :data="staticIpList">
        <bk-table-column v-if="selection" width="60" fixed="left" :render-header="renderHeaderCheckbox">
            <template slot-scope="props">
                <bk-checkbox :value="selectedIp.findIndex(el => el.bk_host_id === props.row.bk_host_id) > -1" @change="onHostItemClick(props.row)"></bk-checkbox>
            </template>
        </bk-table-column>
        <template v-for="columnInfo in tableColumnList">
            <bk-table-column
                v-if="columnInfo.checked"
                :key="columnInfo.id"
                :label="columnInfo.name"
                :width="columnInfo.width"
                :min-width="columnInfo.minWidth"
                :fixed="columnInfo.fixed"
                :prop="columnInfo.id">
                <template slot-scope="{ row }">
                    <div v-if="columnInfo.id === 'bk_host_innerip'" class="host-inner-ip">
                        <div class="inner-ip" v-bk-overflow-tips>{{ row.bk_host_innerip }}</div>
                        <span class="invalid" :class="{ 'disabled': !editable }" v-if="row.diff">{{ $t('失效') }}</span>
                    </div>
                    <div
                        v-else-if="columnInfo.id === 'agent'"
                        v-bk-overflow-tips
                        :class="!editable ? 'agent-disabled' : row.diff ? '' : row.agent === 1 ? 'agent-normal' : 'agent-failed'">
                        {{ row.diff ? '--' : row.agent === 1 ? $t('正常') : $t('异常') }}
                    </div>
                    <div v-else-if="columnInfo.id === 'cloud'">
                        {{ row.cloud[0] && row.cloud[0].bk_inst_name }}
                    </div>
                    <div v-bk-overflow-tips v-else>
                        {{ row[columnInfo.id] || '--' }}
                    </div>
                </template>
            </bk-table-column>
        </template>
        <bk-table-column v-if="operate" :label="$t('操作')" width="80" fixed="right">
            <template slot-scope="{ row }">
                <a
                    :class="['remove-ip-btn', { 'disabled': !editable }]"
                    @click.stop="onRemoveIpClick(row.bk_host_id)">
                    {{ $t('移除') }}
                </a>
            </template>
        </bk-table-column>
        <bk-table-column type="setting" width="42">
            <column-setting
                :editable="editable"
                :column-list="tableColumnList"
                @change="handleSettingChange">
            </column-setting>
        </bk-table-column>
        <div class="static-ip-empty" slot="empty">
            <span v-if="!isSearchMode && editable">
                {{ $t('无数据，可') }}
                <span class="add-ip-btn" @click="onAddPanelShow('select')">{{ $t('选择添加') }}</span>
                {{ $t('或者') }}
                <span class="add-ip-btn" @click="onAddPanelShow('manual')">{{ $t('手动添加') }}</span>
            </span>
            <span v-else><NoData></NoData></span>
        </div>
    </bk-table>
</template>

<script>
    import ColumnSetting from './ColumnSetting.vue'
    import tools from '@/utils/tools.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        components: {
            ColumnSetting,
            NoData
        },
        props: {
            selection: {
                type: Boolean,
                default: false
            },
            editable: {
                type: Boolean,
                default: false
            },
            operate: {
                type: Boolean,
                default: true
            },
            isSearchMode: {
                type: Boolean,
                default: false
            },
            defaultSelected: {
                type: Array,
                default: () => ([])
            },
            staticIpTableConfig: {
                type: Array,
                default: () => ([])
            },
            staticIpList: {
                type: Array,
                default: () => ([])
            },
            listCount: {
                type: Number,
                default: 0
            }
        },
        data () {
            return {
                tableColumnList: [
                    {
                        name: 'IP',
                        id: 'bk_host_innerip',
                        width: 180,
                        fixed: true,
                        checked: true
                    },
                    {
                        name: 'IPv6',
                        id: 'bk_host_innerip_v6',
                        width: 120,
                        fixed: true,
                        checked: false
                    },
                    {
                        name: this.$t('管控区域'),
                        id: 'cloud',
                        minWidth: 120,
                        checked: true
                    },
                    {
                        name: this.$t('Agent 状态'),
                        id: 'agent',
                        minWidth: 160,
                        checked: true
                    },
                    {
                        name: this.$t('主机名称'),
                        id: 'bk_host_name',
                        minWidth: 120,
                        checked: true
                    },
                    {
                        name: 'Host ID',
                        id: 'bk_host_id',
                        minWidth: 120,
                        checked: false
                    }
                ],
                ipSortActive: '', // ip 排序方式
                hostNameSortActive: '', // hostname 排序方式
                selectedIp: this.defaultSelected.slice(0)
            }
        },
        computed: {
            firstRenderColumnKey: () => {
                let key = ''
                for (const field of this.tableColumnList) {
                    if (field.checked) {
                        key = field.id
                        return
                    }
                }
                return key
            },
            isIndeterminate () {
                let selectedIp = tools.deepClone(this.selectedIp)
                if (selectedIp.length === 0) {
                    return false
                }
                // 有的主机可能在列表中不存在
                selectedIp = selectedIp.filter(item => !item.diff)
                return !!selectedIp.length && selectedIp.length < this.listCount
            },
            isAllSelected () {
                const half = this.selectedIp.length > 0 && this.selectedIp.length < this.listCount
                return this.selectedIp.length !== 0 && !half
            }
        },
        watch: {
            defaultSelected: {
                handler () {
                    this.selectedIp = this.defaultSelected.slice(0)
                },
                deep: true
            }
        },
        created () {
            if (this.staticIpTableConfig.length) {
                this.tableColumnList.forEach(item => {
                    item.checked = this.staticIpTableConfig.includes(item.id)
                })
            }
        },
        methods: {
            renderHeaderCheckbox (h) {
                const self = this
                return h('div', [
                    h('bk-checkbox', {
                        props: {
                            indeterminate: this.isIndeterminate,
                            value: this.isAllSelected
                        },
                        on: {
                            change: function (val) {
                                self.onSelectAllClick(val)
                            }
                        }
                    })
                ])
            },
            onSelectAllClick (val) {
                this.$emit('onSelectAllClick', val)
            },
            onHostItemClick (host) {
                this.$emit('onHostItemClick', host)
            },
            handleSettingChange (selectedList) {
                this.tableColumnList.forEach(item => {
                    item.checked = selectedList.includes(item.id)
                })
                this.$emit('onTableConfigChange', selectedList)
            },
            onRemoveIpClick (hostId) {
                this.$emit('onRemoveIpClick', hostId)
            },
            onAddPanelShow (type) {
                this.$emit('onAddPanelShow', type)
            }
        }
    }
</script>

<style lang='scss' scoped>
.ip-seletor-table {
    /deep/th {
        background: #fff;
    }
    /deep/.cell > div {
        overflow:hidden;
        text-overflow:ellipsis;
        white-space:nowrap;
    }
    .host-inner-ip {
        display: flex;
        align-items: center;
        .inner-ip {
            overflow:hidden;
            text-overflow:ellipsis;
            white-space:nowrap;
        }
        .invalid {
            flex-shrink: 0;
            padding: 2px 5px;
            margin-left: 5px;
            transform: scale(0.8);
            color: #63656e;
            background: #f0f1f5;
            border: 1px solid #c4c6cc;
            border-radius: 2px;
            &.disabled {
                color: #ccc;
                background-color: #fafbfd;
                border-color: #dcdee5;
            }
        }
    }
    .agent-disabled {
        color: #ccc;
    }
    .agent-normal {
        color: #22a945;
    }
    .agent-failed {
        color: #ea3636;
    }
    .remove-ip-btn {
        color: #3a84ff;
        cursor: pointer;
        &.disabled {
            color: #cccccc;
            cursor: not-allowed;
        }
    }
    .static-ip-empty {
        text-align: center;
        color: #c4c6cc;
        .add-ip-btn {
            margin: 0 -2px 0 -2px;
            color: #3a84ff;
            cursor: pointer;
        }
    }
    &.disabled {
        /deep/th .bk-table-header-label,
        /deep/td {
            color: #cccccc !important;
        }
    }
}
</style>
