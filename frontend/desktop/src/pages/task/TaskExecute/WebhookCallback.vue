<template>
    <div class="wehhook-callback">
        <bk-table
            ext-cls="wehhook-callback-table"
            :data="webhookHistory">
            <bk-table-column width="200" show-overflow-tooltip :label="$t('回调时间')" prop="created_at">
                <template slot-scope="props">
                    <span v-if="props.row.created_at">{{ props.row.created_at }}</span>
                    <span v-else>--</span>
                </template>
            </bk-table-column>
            <bk-table-column width="160" show-overflow-tooltip :label="$t('回调事件类型')" prop="event_code">
                <template slot-scope="props">
                    <span v-if="props.row.event_code">{{ props.row.event_code }}</span>
                    <span v-else>--</span>
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
                    <span v-if="props.row.status_code">{{ props.row.status_code }}</span>
                    <span v-else>--</span>
                </template>
            </bk-table-column>
            <bk-table-column show-overflow-tooltip :label="$t('请求返回message')" prop="response">
                <template slot-scope="props">
                    <span v-if="props.row.response">{{ props.row.response }}</span>
                    <span v-else>--</span>
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
