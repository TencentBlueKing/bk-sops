<template>
    <section class="info-section" data-test-id="taskExecute_form_excuteInfo">
        <h4 class="common-section-title">{{ $t('执行信息') }}</h4>
        <table class="operation-table" v-if="executeCols && isReadyStatus">
            <tr v-for="col in executeCols" :key="col.id">
                <th>{{ col.title }}</th>
                <td>
                    <template v-if="typeof executeInfo[col.id] === 'boolean'">
                        {{ executeInfo[col.id] ? $t('是') : $t('否') }}
                    </template>
                    <template v-else-if="col.id === 'elapsed_time'">
                        {{ getLastTime(executeInfo.elapsed_time) }}
                    </template>
                    <template v-else-if="col.id === 'callback_data'">
                        <div class="code-block-wrap">
                            <VueJsonPretty :data="executeInfo.callback_data"></VueJsonPretty>
                        </div>
                    </template>
                    <template v-else>
                        {{ executeInfo[col.id] }}
                    </template>
                </td>
            </tr>
        </table>
        <NoData v-else></NoData>
    </section>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import VueJsonPretty from 'vue-json-pretty'
    import NoData from '@/components/common/base/NoData.vue'
    import tools from '@/utils/tools.js'

    const EXECUTE_INFO_COL = [
        {
            title: i18n.t('开始时间'),
            id: 'start_time'
        },
        {
            title: i18n.t('结束时间'),
            id: 'finish_time'
        },
        {
            title: i18n.t('耗时'),
            id: 'elapsed_time'
        },
        {
            title: i18n.t('失败后跳过'),
            id: 'skip'
        },
        {
            title: i18n.t('失败后自动忽略'),
            id: 'error_ignored'
        },
        {
            title: i18n.t('重试次数'),
            id: 'retry'
        },
        {
            title: i18n.t('插件版本'),
            id: 'plugin_version'
        },
        {
            title: i18n.t('插件名称'),
            id: 'plugin_name'
        },
        {
            title: i18n.t('节点ID'),
            id: 'id'
        }
    ]

    const ADMIN_EXECUTE_INFO_COL = [
        {
            title: i18n.t('开始时间'),
            id: 'start_time'
        },
        {
            title: i18n.t('结束时间'),
            id: 'archive_time'
        },
        {
            title: i18n.t('耗时'),
            id: 'elapsed_time'
        },
        {
            title: i18n.t('失败后跳过'),
            id: 'skip'
        },
        {
            title: i18n.t('失败后自动忽略'),
            id: 'error_ignored'
        },
        {
            title: i18n.t('重试次数'),
            id: 'retry_times'
        },
        {
            title: i18n.t('ID'),
            id: 'id'
        },
        {
            title: i18n.t('状态'),
            id: 'state'
        },
        {
            title: i18n.t('循环次数'),
            id: 'loop'
        },
        {
            title: i18n.t('创建时间'),
            id: 'create_time'
        },
        {
            title: i18n.t('调度ID'),
            id: 'schedule_id'
        },
        {
            title: i18n.t('正在被调度'),
            id: 'is_scheduling'
        },
        {
            title: i18n.t('调度次数'),
            id: 'schedule_times'
        },
        {
            title: i18n.t('等待回调'),
            id: 'wait_callback'
        },
        {
            title: i18n.t('完成调度'),
            id: 'is_finished'
        },
        {
            title: i18n.t('调度节点版本'),
            id: 'schedule_version'
        },
        {
            title: i18n.t('执行版本'),
            id: 'version'
        },
        {
            title: i18n.t('回调数据'),
            id: 'callback_data'
        },
        {
            title: i18n.t('插件版本'),
            id: 'plugin_version'
        },
        {
            title: i18n.t('插件名称'),
            id: 'plugin_name'
        },
        {
            title: i18n.t('节点ID'),
            id: 'id'
        }
    ]
    export default {
        components: {
            VueJsonPretty,
            NoData
        },
        props: {
            adminView: {
                type: Boolean,
                default: false
            },
            isReadyStatus: {
                type: Boolean,
                default: false
            },
            executeInfo: {
                type: Object,
                default: () => ({})
            }
        },
        data () {
            return {
                
            }
        },
        computed: {
            executeCols () {
                return this.adminView ? ADMIN_EXECUTE_INFO_COL : EXECUTE_INFO_COL
            }
        },
        methods: {
            getLastTime (time) {
                return tools.timeTransform(time)
            }
        }
    }
</script>

<style>
</style>
