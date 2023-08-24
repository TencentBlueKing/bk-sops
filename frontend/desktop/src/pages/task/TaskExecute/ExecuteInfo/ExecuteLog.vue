<template>
    <section class="info-section" data-test-id="taskExecute_form_executeLog">
        <h4 class="common-section-title">{{ $t('节点执行详情') }}</h4>
        <div class="excute-time" v-if="loop && loop > 1">
            <span>{{$t('第')}}</span>
            <bk-select
                :clearable="false"
                :value="theExecuteTime"
                @selected="onSelectExecuteTime">
                <bk-option
                    v-for="index in loopTimes"
                    :key="index"
                    :id="index"
                    :name="index">
                </bk-option>
            </bk-select>
            <span>{{$t('次循环')}}</span>
        </div>
        <bk-table
            ref="recordTable"
            class="record-table"
            :data="historyList"
            row-key="history_id"
            @expand-change="onHistoryExpand">
            <bk-table-column type="expand" :width="30">
                <div class="record-wrap" slot-scope="{ row }">
                    <section class="info-section abnormal-section" data-test-id="taskExcute_form_exceptionInfo" v-if="row.ex_data">
                        <h4 class="abnormal-label">{{ $t('异常信息') }}</h4>
                        <div v-html="row.failInfo"></div>
                    </section>
                    <InputParams
                        :inputs="row.inputs"
                        :render-config="row.renderConfig"
                        :constants="row.constants"
                        :admin-view="adminView"
                        :render-data="row.renderData">
                    </InputParams>
                    <OutputParams
                        :outputs="row.outputsInfo"
                        :admin-view="adminView"
                        :node-detail-config="nodeDetailConfig">
                    </OutputParams>
                    <NodeLog
                        ref="nodeLog"
                        :node-detail-config="nodeDetailConfig"
                        :execute-info="row"
                        :third-party-node-code="thirdPartyNodeCode"
                        :admin-view="adminView"
                        :engine-ver="engineVer">
                    </NodeLog>
                </div>
            </bk-table-column>
            <bk-table-column :label="$t('任务名')" :width="80" v-if="isSubProcessNode">
                <div slot-scope="{ row }" v-bk-overflow-tips>
                    {{ getTaskName(row.outputs) }}
                </div>
            </bk-table-column>
            <bk-table-column :label="$t('开始时间')" :width="200" prop="start_time">
                <div slot-scope="{ row }" v-bk-overflow-tips>  {{ row.start_time }} </div>
            </bk-table-column>
            <bk-table-column :label="$t('结束时间')" :width="200" prop="finish_time">
                <div slot-scope="{ row }" v-bk-overflow-tips> {{ row.finish_time }} </div>
            </bk-table-column>
            <bk-table-column :label="$t('耗时')" :width="60">
                <div slot-scope="{ row }" v-bk-overflow-tips>
                    {{ getLastTime(row.elapsed_time) }}
                </div>
            </bk-table-column>
            <bk-table-column v-if="isSubProcessNode" :label="$t('操作')" :width="60">
                <template slot-scope="{ row }">
                    <bk-button v-if="hasTaskNodeUrl(row.outputs)" text title="primary" @click="onSkipSubProcess(row)">{{ $t('详情') }}</bk-button>
                </template>
            </bk-table-column>
        </bk-table>
    </section>
</template>

<script>
    import { mapState, mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import InputParams from './InputParams.vue'
    import OutputParams from './OutputParams.vue'
    import NodeLog from './NodeLog.vue'

    export default {
        components: {
            InputParams,
            OutputParams,
            NodeLog
        },
        props: {
            isReadyStatus: {
                type: Boolean,
                default: false
            },
            loop: {
                type: Number,
                default: 1
            },
            theExecuteTime: {
                type: Number,
                default: 1
            },
            historyInfo: {
                type: Array,
                default: () => ([])
            },
            isThirdPartyNode: {
                type: Boolean,
                default: false
            },
            isSubProcessNode: {
                type: Boolean,
                default: false
            },
            thirdPartyNodeCode: {
                type: String,
                default: ''
            },
            nodeDetailConfig: {
                type: Object,
                default: () => ({})
            },
            engineVer: {
                type: Number,
                required: true
            },
            adminView: {
                type: Boolean,
                required: false
            }
        },
        data () {
            return {
                historyList: []
            }
        },
        computed: {
            ...mapState({
                'atomFormConfig': state => state.atomForm.config,
                'atomOutputConfig': state => state.atomForm.outputConfig
            }),
            loopTimes () {
                const times = []
                for (let i = 0; i < this.loop; i++) {
                    times.push(this.loop - i)
                }

                return times
            }
        },
        watch: {
            historyInfo: {
                handler (val) {
                    this.historyList = [...val]
                    this.$nextTick(() => {
                        const dom = this.$refs.recordTable
                        const recordData = val[0]
                        if (dom && recordData) {
                            dom.toggleRowExpansion(recordData, true)
                        }
                    })
                },
                immediate: true,
                deep: true
            }
        },
        methods: {
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadPluginServiceDetail'
            ]),
            getTaskName (outputs) {
                if (Array.isArray(outputs)) {
                    const taskNameInfo = outputs.find(item => item.key === 'task_name')
                    return taskNameInfo ? taskNameInfo.value : ''
                } else {
                    return outputs.task_name
                }
            },
            hasTaskNodeUrl (outputs) {
                if (Array.isArray(outputs)) {
                    const taskUrlInfo = outputs.find(item => item.key === 'task_url')
                    return taskUrlInfo ? taskUrlInfo.value : ''
                } else {
                    return outputs.task_url
                }
            },
            getLastTime (time) {
                return tools.timeTransform(time)
            },
            onSelectExecuteTime (val) {
                this.$emit('onSelectExecuteTime', val)
            },
            onSkipSubProcess (row) {
                const taskInfo = row.outputsInfo.find(item => item.key === 'task_url')
                if (taskInfo) {
                    window.open(taskInfo.value, '_blank')
                }
            },
            async onHistoryExpand (record) {
                if ('isExpand' in record) return
                this.$parent.setFillRecordField(record)
            }
        }
    }
</script>

<style lang="scss" scoped>
    .excute-time {
        margin-top: 16px;
        display: flex;
        justify-content: flex-start;
        align-items: center;
        font-size: 14px;
        &>span {
            font-size: 14px;
            font-weight: 600;
        }
        /deep/.bk-select {
            margin: 0 8px;
            width: 88px;
            height: 24px;
            line-height: 22px;
            .icon-angle-down {
                top: 0;
            }
        }
    }
    .record-table {
        font-size: 12px;
        margin-top: 16px;
        .common-form-item {
            & > label {
                margin-top: 0;
                width: 60px;
                font-size: 12px;
            }
            .commont-form-content {
                margin-left: 100px;
                font-size: 12px;
            }
        }
        .executeLog {
            /deep/.bk-tab {
                position: relative;
                top: -16px;
                margin-left: 120px;
                .bk-tab-section {
                    padding: 0;
                }
            }
            .perform-log {
                margin-left: 120px;
                .no-data-wrapper {
                    margin: 20px 0;
                }
            }
        }
    }
    /deep/.bk-table .bk-table-body td.bk-table-expanded-cell {
        background: #f5f7fa;
        padding: 16px 24px 22px 32px;
        .info-section:not(:last-child) {
            margin-bottom: 16px;
        }
        .abnormal-section {
            display: flex;
            line-height: 16px;
            > div {
                margin-left: 24px;
            }
        }
        .abnormal-label,
        .inputs-label,
        .outputs-label,
        .log-label {
            flex-shrink: 0;
            color: #313238;
            font-size: 12px;
            line-height: 20px;
            font-weight: 600;
            margin: 0;
        }
        .origin-value {
            position: absolute;
            top: 0;
            right: 0;
            display: flex;
            font-weight: normal;
            .bk-switcher {
                margin-right: 5px;
            }
        }
        .full-code-editor {
            flex: 1;
            margin: 20px 0 0 48px;
        }
        .no-data-wrapper {
            background: #f5f7fa;
            .no-data-wording {
                font-size: 12px;
                color: #63656e;
            }
        }
        .ex-data-wrap {
            /deep/ pre {
                white-space: pre-wrap;
            }
        }
        .perform-log {
            width: 100%;
        }
        .code-block-wrap {
            margin-left: 24px;
        }
    }
</style>
