<template>
    <bk-table
        ref="ipSeletorTable"
        :row-auto-height="true"
        :class="['ip-seletor-table', { 'disabled': !editable }]"
        :data="listInPage"
        @sort-change="handleSortChange">
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
                :sortable="columnInfo.sortable"
                :prop="columnInfo.id">
                <template slot-scope="{ row }">
                    <div
                        v-if="columnInfo.id === 'agent'"
                        v-bk-overflow-tips
                        :class="!editable ? 'agent-disabled' : row.agent ? 'agent-normal' : 'agent-failed'">
                        {{ row.agent ? 'Agent' + $t('正常') : 'Agent' + $t('异常') }}
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
            listInPage: {
                type: Array,
                default: () => ([])
            }
        },
        data () {
            return {
                tableColumnList: [
                    {
                        name: 'IP',
                        id: 'bk_host_innerip',
                        width: 120,
                        fixed: true,
                        sortable: true,
                        checked: true
                    },
                    {
                        name: 'IPv6',
                        id: 'bk_host_innerip_v6',
                        width: 120,
                        fixed: true,
                        checked: true
                    },
                    {
                        name: this.$t('云区域'),
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
                        sortable: true,
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
                selectedIp: this.defaultSelected.slice(0),
                listAllSelected: false
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
            }
        },
        watch: {
            selectedIp: {
                handler (val) {
                    this.$emit('handleSelectionChange', val)
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
            handleSelectionChange (data) {
                this.$emit('handleSelectionChange', data)
            },
            handleSortChange ({ column, prop, order }) {
                const way = order === 'descending' ? 'down' : 'up'
                if (prop === 'bk_host_innerip') {
                    this.$emit('onIpSort', way)
                } else {
                    this.$emit('onHostNameSort', way)
                }
            },
            renderHeaderCheckbox (h) {
                const self = this
                return h('div', [
                    h('bk-checkbox', {
                        props: {
                            indeterminate: this.judegeIndeterminate(),
                            value: this.listAllSelected
                        },
                        on: {
                            change: function (val) {
                                self.onSelectAllClick(val)
                            }
                        }
                    })
                ])
            },
            judegeIndeterminate () {
                let selectedIp = tools.deepClone(this.selectedIp)
                if (selectedIp.length === 0) {
                    return false
                }
                // 有的主机可能在列表中不存在
                selectedIp = selectedIp.filter(item => {
                    return this.staticIpList.find(el => el.bk_host_id === item.bk_host_id)
                })
                return !!selectedIp.length && selectedIp.length < this.staticIpList.length
            },
            onSelectAllClick () {
                if (this.listAllSelected) {
                    this.selectedIp = []
                    this.listAllSelected = false
                } else {
                    this.selectedIp = [...this.staticIpList]
                    this.listAllSelected = true
                }
            },
            onHostItemClick (host) {
                const index = this.selectedIp.findIndex(el => el.bk_host_id === host.bk_host_id)
                if (index > -1) {
                    this.selectedIp.splice(index, 1)
                } else {
                    this.selectedIp.push(host)
                }
                const half = this.selectedIp.length > 0 && this.selectedIp.length < this.staticIpList.length
                if (half || this.selectedIp.length === 0) {
                    this.listAllSelected = false
                } else {
                    this.listAllSelected = true
                }
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
