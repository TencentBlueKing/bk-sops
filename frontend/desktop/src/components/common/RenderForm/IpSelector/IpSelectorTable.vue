<template>
    <bk-table
        :row-auto-height="true"
        :class="['ip-seletor-table', { 'disabled': !editable }]"
        :data="listInPage"
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange">
        <bk-table-column v-if="selection" type="selection" width="60" fixed="left"></bk-table-column>
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
                        {{ row.agent ? 'Agent' + i18n.normal : 'Agent' + i18n.error }}
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
        <bk-table-column v-if="operate" label="操作" width="80" fixed="right">
            <template slot-scope="{ row }">
                <a
                    :class="['remove-ip-btn', { 'disabled': !editable }]"
                    @click.stop="onRemoveIpClick(row.bk_host_id)">
                    {{ i18n.remove }}
                </a>
            </template>
        </bk-table-column>
        <bk-table-column type="setting">
            <column-setting
                :editable="editable"
                :column-list="tableColumnList"
                @change="handleSettingChange">
            </column-setting>
        </bk-table-column>
        <div class="static-ip-empty" slot="empty">
            <span v-if="!isSearchMode && editable">
                {{ i18n.noDataCan }}
                <span class="add-ip-btn" @click="onAddPanelShow('select')">{{ i18n.selectAdd }}</span>
                {{ i18n.or }}
                <span class="add-ip-btn" @click="onAddPanelShow('manual')">{{ i18n.manualAdd }}</span>
            </span>
            <span v-else>{{ i18n.noData }}</span>
        </div>
    </bk-table>
</template>

<script>
    import '@/utils/i18n.js' // ip选择器兼容标准运维国际化
    import ColumnSetting from './ColumnSetting.vue'

    const i18n = {
        selectAdd: gettext('选择添加'),
        manualAdd: gettext('手动添加'),
        cloudArea: gettext('云区域'),
        status: gettext('状态'),
        error: gettext('异常'),
        operation: gettext('操作'),
        remove: gettext('移除'),
        normal: gettext('正常'),
        noData: gettext('无数据'),
        noDataCan: gettext('无数据，可'),
        or: gettext('或者'),
        hostName: gettext('主机名')
    }
    export default {
        components: {
            ColumnSetting
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
                        name: '云区域',
                        id: 'cloud',
                        minWidth: 120,
                        checked: true
                    },
                    {
                        name: 'Agent 状态',
                        id: 'agent',
                        minWidth: 160,
                        checked: true
                    },
                    {
                        name: '主机名称',
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
                i18n,
                ipSortActive: '', // ip 排序方式
                hostNameSortActive: '' // hostname 排序方式
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
            handleSettingChange (selectedList) {
                this.tableColumnList.forEach(item => {
                    item.checked = selectedList.includes(item.id)
                })
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
