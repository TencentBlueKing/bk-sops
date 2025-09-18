<template>
    <div class="wehhook-callback">
        <bk-table
            ext-cls="wehhook-callback-table"
            :data="webhookHistory">
            <bk-table-column width="200" show-overflow-tooltip :label="$t('回调时间')" prop="created_at">
                <template slot-scope="props">
                    <span>{{ props.row?.created_at || '--' }}</span>
                </template>
            </bk-table-column>
            <bk-table-column width="160" show-overflow-tooltip :label="$t('回调事件类型')" prop="event_code_name">
                <template slot-scope="props">
                    <span>{{ props.row?.event_code_name || '--'}}</span>
                </template>
            </bk-table-column>
            <bk-table-column width="160" show-overflow-tooltip :label="$t('回调结果')" prop="is_success">
                <template slot-scope="props">
                    <span v-if="props.row.is_success !== undefined">
                        <bk-icon :type="statusInfo[props.row.is_success].icon"
                            :class="`${props.row.is_success}-icon`" />
                        <span class="task-status-text">{{$t(statusInfo[props.row.is_success].text)}}</span>
                    </span>
                    <span v-else>--</span>
                </template>
            </bk-table-column>
            <bk-table-column width="160" show-overflow-tooltip :label="$t('请求状态码')" prop="status_code">
                <template slot-scope="props">
                    <span>{{ props.row?.status_code || '--' }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t('请求返回message')" prop="response">
                <template slot-scope="props">
                    <span v-bk-tooltips="{
                        width: 240,
                        placement: 'top',
                        extCls: JSON.stringify(JSON.parse(props.row.response)).length <= 14 ? 'hidden-tips' : '',
                        content: JSON.stringify(JSON.parse(props.row?.response)) }">
                        {{JSON.parse(props.row?.response) || '--'}}
                    </span>
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
    import NoData from '@/components/common/base/NoData.vue'
    import Vue from 'vue'
    import { bkTooltips } from 'bk-magic-vue'
    Vue.use(bkTooltips)
    export default {
        components: {
            NoData
        },
        props: {
            webhookHistory: Array
        },
        data () {
            return {
                statusInfo: {
                    'true': {
                        text: '成功',
                        icon: 'check-circle-shape'
                    },
                    'false': {
                        text: '失败',
                        icon: 'close-circle-shape'
                    }
                }
            }
        },
        methods: {
            ...mapActions('task/', [
                'getOperationRecordTask'
            ])
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
::v-deep .wehhook-callback-table {
    .bk-table-body-wrapper {
        max-height: calc(100vh - 145px);
        color: #63656e;
        overflow-y: auto;
        @include scrollbar;
    }
    .true-icon{
        color: #2dcb56,
    }
    .false-icon{
        color: #ea3636,
    }
}
</style>

<style lang="scss">
    .hidden-tips{
        display: none !important;
    }
</style>
