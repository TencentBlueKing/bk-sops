<template>
    <div class="operate-flow">
        <bk-table
            ext-cls="operate-flow-table"
            :data="operateFlowData"
            v-bkloading="{ isLoading: isFlowLoading }">
            <bk-table-column width="160" show-overflow-tooltip :label="$t('操作时间')" prop="operate_date"></bk-table-column>
            <bk-table-column width="100" show-overflow-tooltip :label="$t('操作人')" prop="operator"></bk-table-column>
            <bk-table-column width="120" show-overflow-tooltip :label="$t('来源')" :prop="$store.state.lang === 'en' ? 'operate_source' : 'operate_source_name'"></bk-table-column>
            <bk-table-column width="100" show-overflow-tooltip :label="$t('操作类型')" :prop="$store.state.lang === 'en' ? 'operate_type' : 'operate_type_name'"></bk-table-column>
            <bk-table-column width="130" show-overflow-tooltip v-if="!nodeId" :label="$t('节点')" prop="node_name">
                <div slot-scope="{ row }" v-bk-overflow-tips>
                    {{ row.node_name}}
                </div>
            </bk-table-column>
            <bk-table-column :label="$t('参数明细')">
                <template slot-scope="{ row, $index }">
                    <div v-if="Object.keys(row.extra_info).length" class="params-info">
                        <div
                            class="params-info-item"
                            v-for="(params, index) in row.paramsList"
                            :key="index">
                            <div class="name">
                                <span class="name-text" v-bk-overflow-tips>{{ params.name + ' (' + params.key + ') ' }}</span>
                                <span>{{ '：' }}</span>
                            </div>
                            <span class="value" v-bk-overflow-tips>{{ params.value || '--' }}</span>
                        </div>
                        <span v-if="'isExpand' in row" class="expand" @click="toggleExpand($index)">{{ row.isExpand ? $t('收起') : $t('展开全部') }}</span>
                    </div>
                    <span v-else>{{ '--' }}</span>
                </template>
            </bk-table-column>
        </bk-table>
    </div>
</template>

<script>
    import { mapActions } from 'vuex'
    import moment from 'moment'
    import NoData from '@/components/common/base/NoData.vue'
    export default {
        components: {
            NoData
        },
        props: {
            locations: {
                type: Array,
                default: () => []
            },
            nodeId: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                isFlowLoading: false,
                operateFlowData: []
            }
        },
        watch: {
            nodeId (val) {
                this.getOperationTaskData()
            }
        },
        mounted () {
            this.getOperationTaskData()
        },
        methods: {
            ...mapActions('task/', [
                'getOperationRecordTask'
            ]),
            async getOperationTaskData () {
                const { params, query } = this.$route
                try {
                    this.isFlowLoading = true
                    const resp = await this.getOperationRecordTask({
                        project_id: params.project_id,
                        instance_id: query.instance_id,
                        node_id: this.nodeId || undefined
                    })
                    this.operateFlowData = resp.data.map(item => {
                        item.operate_date = moment(item.operate_date).format('YYYY-MM-DD HH:mm:ss')
                        let nodeName = '--'
                        if (item.node_id) {
                            const node = this.locations.find(node => node.id === item.node_id)
                            if (node) {
                                nodeName = node.name
                            }
                        }
                        item.node_name = nodeName
                        item.paramsList = []
                        const paramsLength = item.extra_info && Object.keys(item.extra_info).length
                        if (paramsLength) {
                            item.paramsList = Object.keys(item.extra_info).map(key => {
                                return { key, ...item.extra_info[key] }
                            })
                            if (paramsLength > 3) { // 默认展开三条
                                item.isExpand = false
                                item.paramsList = item.paramsList.slice(0, 3)
                            }
                        }
                        return item
                    }) || []
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isFlowLoading = false
                }
            },
            toggleExpand (index) {
                const selectedRow = this.operateFlowData[index]
                selectedRow.isExpand = !selectedRow.isExpand
                selectedRow.paramsList = Object.keys(selectedRow.extra_info).map(key => {
                    return { key, ...selectedRow.extra_info[key] }
                })
                if (!selectedRow.isExpand) {
                    selectedRow.paramsList = selectedRow.paramsList.slice(0, 3)
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
/deep/ .operate-flow-table {
    .bk-table-body-wrapper {
        max-height: calc(100vh - 145px);
        color: #63656e;
        overflow-y: auto;
        @include scrollbar;
    }
    td {
        min-height: 43px !important;
        .cell {
            display: block;
        }
        .params-info {
            padding: 12px 0;
        }
        .params-info-item {
            display: flex;
            margin-bottom: 12px;
            .name {
                width: 113px;
                flex-shrink: 0;
                display: flex;
                color: #979ba5;
                .name-text {
                    display: inline-block;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
            }
            .value {
                flex: 1;
                margin-left: 15px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: normal;
                display: -webkit-box;
                -webkit-box-orient: vertical;
                -webkit-line-clamp: 3;
            }
            &:last-child {
                margin-bottom: 0;
            }
        }
        .expand {
            color: #3a84ff;
            cursor: pointer;
        }
    }
}
</style>
