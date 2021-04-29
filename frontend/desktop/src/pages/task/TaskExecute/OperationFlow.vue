<template>
    <div class="operate-flow">
        <bk-table
            ext-cls="operate-flow-table"
            :data="operateFlowData">
            <bk-table-column :label="$t('操作时间')" prop="operate_date"></bk-table-column>
            <bk-table-column :label="$t('操作名称')" prop="operate_type_name"></bk-table-column>
            <bk-table-column :label="$t('节点名称')" prop="node_name"></bk-table-column>
            <bk-table-column :label="$t('操作来源')" prop="operate_source_name"></bk-table-column>
            <bk-table-column :label="$t('操作人')" prop="operator"></bk-table-column>
        </bk-table>
    </div>
</template>

<script>
    import { mapActions } from 'vuex'
    export default {
        props: {
            nodeId: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
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
                    const resp = await this.getOperationRecordTask({
                        project_id: params.project_id,
                        instance_id: query.instance_id,
                        node_id: this.nodeId || undefined
                    })
                    this.operateFlowData = resp.data || []
                } catch (error) {
                    console.warn(error)
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
}
</style>
