<template>
    <div class="node-operate-flow">
        <bk-table
            ext-cls="node-operate-flow-table"
            :data="operateFlowData"
            v-bkloading="{ isLoading: isFlowLoading }">
            <bk-table-column width="220" :label="$t('操作时间')" prop="operate_date"></bk-table-column>
            <bk-table-column width="140" :label="$t('操作类型')" :prop="$store.state.lang === 'en' ? 'operate_type' : 'operate_type_name'"></bk-table-column>
            <bk-table-column width="160" :label="$t('操作来源')" :prop="$store.state.lang === 'en' ? 'operate_source' : 'operate_source_name'"></bk-table-column>
            <bk-table-column width="150" :label="$t('操作人')" prop="operator">
                <template slot-scope="props">
                    <UserDisplayName :name="props.row.operator" />
                </template>
            </bk-table-column>
            <div class="empty-data" slot="empty">
                <NoData></NoData>
            </div>
        </bk-table>
    </div>
</template>

<script>
    import { mapActions } from 'vuex'
    import moment from 'moment'
    import NoData from '@/components/common/base/NoData.vue'
    import UserDisplayName from '@/components/common/Individualization/UserDisplayName.vue'
    export default {
        components: {
            UserDisplayName,
            NoData
        },
        props: {
            nodeId: {
                type: String,
                default: ''
            },
            notPerformedSubNode: {
                type: Boolean,
                default: false
            },
            subProcessTaskId: {
                type: [String, Number]
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
                    if (this.notPerformedSubNode) return
                    this.isFlowLoading = true
                    if (!this.nodeId) { // 未执行的任务节点操作历史为空
                        this.operateFlowData = []
                        return
                    }
                    const resp = await this.getOperationRecordTask({
                        project_id: params.project_id,
                        instance_id: this.subProcessTaskId || query.instance_id,
                        node_id: this.nodeId || undefined
                    })
                    this.operateFlowData = resp.data.map(item => {
                        item.operate_date = moment(item.operate_date).format('YYYY-MM-DD HH:mm:ss')
                        return item
                    }) || []
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isFlowLoading = false
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
/deep/ .node-operate-flow-table {
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
    }
}
</style>
