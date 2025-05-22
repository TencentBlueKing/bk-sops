<template>
    <bk-sideslider
        :is-show="true"
        :width="800"
        ext-cls="operate-flow"
        :title="$t('操作记录')"
        :quick-close="true"
        :before-close="closeTab">
        <template slot="content">
            <bk-table
                ext-cls="operate-flow-table"
                :data="operateFlowData">
                <bk-table-column show-overflow-tooltip :render-header="renderTableHeader" min-width="130" :label="$t('操作时间')" prop="operate_date"></bk-table-column>
                <bk-table-column show-overflow-tooltip :render-header="renderTableHeader" :label="$t('操作名称')" :prop="$store.state.lang === 'en' ? 'operate_type' : 'operate_type_name'"></bk-table-column>
                <bk-table-column show-overflow-tooltip :render-header="renderTableHeader" :label="$t('操作来源')" prop="operate_source_name"></bk-table-column>
                <bk-table-column show-overflow-tooltip :render-header="renderTableHeader" :label="$t('操作人')" prop="operator"></bk-table-column>
                <div class="static-ip-empty" slot="empty">
                    <NoData></NoData>
                </div>
            </bk-table>
        </template>
    </bk-sideslider>
</template>

<script>
    import { mapActions } from 'vuex'
    import moment from 'moment'
    import NoData from '@/components/common/base/NoData.vue'
    export default {
        components: {
            NoData
        },
        data () {
            return {
                operateFlowData: []
            }
        },
        mounted () {
            this.getOperationTemplateData()
        },
        methods: {
            ...mapActions('task/', [
                'getOperationRecordTemplate'
            ]),
            async getOperationTemplateData () {
                const { params, query } = this.$route
                try {
                    if (!query.template_id) return
                    const resp = await this.getOperationRecordTemplate({
                        project_id: params.project_id,
                        instance_id: query.template_id
                    })
                    this.operateFlowData = resp.data.map(item => {
                        item.operate_date = moment(item.operate_date).format('YYYY-MM-DD HH:mm:ss')
                        return item
                    })
                } catch (error) {
                    console.warn(error)
                }
            },
            renderTableHeader (h, { column, $index }) {
                return h('p', {
                    class: 'label-text',
                    directives: [{
                        name: 'bk-overflow-tips'
                    }]
                }, [
                    column.label
                ])
            },
            closeTab () {
                this.$emit('closeTab')
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
.operate-flow {
    ::v-deep .bk-sideslider-content {
        padding: 20px 30px;
    }
    ::v-deep .operate-flow-table {
        .bk-table-body-wrapper {
            max-height: calc(100vh - 145px);
            color: #63656e;
            overflow-y: auto;
            @include scrollbar;
        }
    }
}
</style>
