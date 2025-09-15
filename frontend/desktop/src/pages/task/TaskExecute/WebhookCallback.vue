<template>
    <div class="wehhook-callback">
        <bk-table
            ext-cls="wehhook-callback-table"
            :data="webhookHistory">
            <bk-table-column width="200" show-overflow-tooltip :label="$t('回调时间')" prop="created_at"></bk-table-column>
            <bk-table-column width="160" show-overflow-tooltip :label="$t('回调事件类型')" prop="event_code"></bk-table-column>
            <bk-table-column width="160" show-overflow-tooltip :label="$t('回调结果')" prop="is_success">
                <template slot-scope="props">
                    <bk-icon :type="statusInfo[props.row.is_success].icon"
                        :class="`${props.row.is_success}-icon`" />
                    <span class="task-status-text">{{$t(statusInfo[props.row.is_success].text)}}</span>
                </template>
            </bk-table-column>
            <bk-table-column width="160" show-overflow-tooltip :label="$t('请求状态码')" prop="status_code"></bk-table-column>
            <bk-table-column show-overflow-tooltip :label="$t('请求返回message')" prop="response"></bk-table-column>
            <div class="empty-data" slot="empty">
                <NoData></NoData>
            </div>
        </bk-table>
    </div>
</template>

<script>
    import { mapActions } from 'vuex'
    import NoData from '@/components/common/base/NoData.vue'
    export default {
        components: {
            NoData
        },
        props: {
            webhookHistory: Array
        },
        data () {
            return {
                callbackData: [
                    {
                        callback_time: '2020-01-01 00:00:00',
                        callback_type: 'callback',
                        callback_result: 'success',
                        callback_code: 200,
                        callback_message: 'success'
                    },
                    {
                        callback_time: '2020-01-01 00:00:00',
                        callback_type: 'callback',
                        callback_result: 'error',
                        callback_code: 500,
                        callback_message: 'error'
                    }
                ],
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
    .success-icon{
        color: #2dcb56,
    }
    .false-icon{
        color: #ea3636,
    }
}
</style>
