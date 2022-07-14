<template>
    <section class="info-section" data-test-id="taskExecute_form_executeLog" v-if="historyList && historyList.length">
        <h4 class="common-section-title">{{ $t('执行记录') }}</h4>
        <bk-table
            class="retry-table"
            :data="historyList"
            @expand-change="onHistoryExpand">
            <bk-table-column type="expand" :width="30">
                <template slot-scope="props">
                    <div class="common-form-item">
                        <label>{{ $t('输入参数') }}</label>
                        <div class="common-form-content">
                            <div class="code-block-wrap">
                                <VueJsonPretty :data="props.row.inputs"></VueJsonPretty>
                            </div>
                        </div>
                    </div>
                    <div class="common-form-item">
                        <label>{{ $t('输出参数') }}</label>
                        <div class="common-form-content">
                            <div class="code-block-wrap">
                                <VueJsonPretty :data="props.row.outputs"></VueJsonPretty>
                            </div>
                        </div>
                    </div>
                    <div class="common-form-item" v-if="props.row.ex_data">
                        <label>{{ $t('异常信息') }}</label>
                        <div class="common-form-content">
                            <div v-html="props.row.ex_data"></div>
                        </div>
                    </div>
                    <div class="common-form-item executeLog">
                        <label>{{ $t('日志') }}</label>
                        <!-- 内置插件/第三方插件tab -->
                        <bk-tab
                            v-if="isThirdPartyNode"
                            :active.sync="props.row.historyLogTab"
                            type="unborder-card">
                            <bk-tab-panel v-bind="{ name: 'build_in_plugin', label: $t('节点日志') }"></bk-tab-panel>
                            <bk-tab-panel
                                v-bind="{ name: 'third_party_plugin', label: $t('第三方节点日志') }">
                            </bk-tab-panel>
                        </bk-tab>
                        <div class="perform-log" v-bkloading="{ isLoading: historyLogLoading[props.row.history_id], opacity: 1, zIndex: 100 }">
                            <div v-show="getHistoryLogData(props.row)">
                                <VueJsonPretty
                                    v-show="adminView"
                                    :data="getHistoryLogData(props.row)">
                                </VueJsonPretty>
                                <full-code-editor
                                    v-show="!adminView"
                                    :class="[
                                        `history-editor-${props.row.history_id}`
                                    ]"
                                    :value="getHistoryLogData(props.row)">
                                </full-code-editor>
                            </div>
                            <NoData v-show="!getHistoryLogData(props.row)"></NoData>
                        </div>

                    </div>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t('序号')" :width="60">
                <template slot-scope="props">
                    {{ props.$index + 1 }}
                </template>
            </bk-table-column>
            <bk-table-column :label="$t('执行次数')" :width="100" prop="loop"></bk-table-column>
            <bk-table-column
                v-for="col in historyCols"
                show-overflow-tooltip
                :key="col.id"
                :label="col.title"
                :prop="col.id">
            </bk-table-column>
        </bk-table>
    </section>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import VueJsonPretty from 'vue-json-pretty'
    import FullCodeEditor from '../FullCodeEditor.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import { mapActions } from 'vuex'

    const HISTORY_COLS = [
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
            id: 'last_time'
        }
    ]

    const ADMIN_HISTORY_COLS = [
        {
            title: i18n.t('开始时间'),
            id: 'started_time'
        },
        {
            title: i18n.t('结束时间'),
            id: 'finished_time'
        },
        {
            title: i18n.t('耗时'),
            id: 'elapsed_time'
        }
    ]

    export default {
        components: {
            NoData,
            VueJsonPretty,
            FullCodeEditor
        },
        props: {
            adminView: {
                type: Boolean,
                default: false
            },
            historyInfo: {
                type: Array,
                default: () => ([])
            },
            isThirdPartyNode: {
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
            }
        },
        data () {
            return {
                historyList: [],
                historyLog: {},
                thirdHistoryLog: {},
                historyLogLoading: {}
            }
        },
        computed: {
            historyCols () {
                return this.adminView ? ADMIN_HISTORY_COLS : HISTORY_COLS
            }
        },
        watch: {
            historyInfo: {
                handler (val) {
                    this.historyList = [...val]
                },
                immediate: true
            }
        },
        beforeDestroy () {
            if (this.historyList.length) {
                this.historyList.forEach(item => {
                    if (item.observe) {
                        item.observer.disconnect()
                        item.observer.takeRecords()
                        item.observer = null
                    }
                })
            }
        },
        methods: {
            ...mapActions('task/', [
                'getEngineVerNodeLog',
                'getNodeExecutionRecordLog'
            ]),
            ...mapActions('atomForm/', [
                'loadPluginServiceLog'
            ]),
            ...mapActions('admin/', [
                'taskflowNodeDetail',
                'taskflowHistroyLog'
            ]),
            async onHistoryExpand (row, expended) {
                const id = Number(row.history_id)
                if (expended && !this.historyLog.hasOwnProperty(id)) {
                    // 获取普通节点历史日志
                    await this.getHistoryLog(id, row)
                    // 获取第三方插件的执行历史日志
                    const traceId = row.outputs.trace_id
                    if (traceId) {
                        // 设置第三方节点历史日志
                        await this.setThirdHistoryLog(row)
                    } else {
                        this.$set(this.thirdHistoryLog, id, i18n.t('输出参数中不包含trace_id，无法查看第三方节点日志'))
                    }
                }
                if (row && !row.observer) {
                    this.$nextTick(() => {
                        // 给历史日志设置监听事件
                        this.setHistoryLogWatch(row)
                    })
                }
            },
            async getHistoryLog (id, row) {
                try {
                    this.$set(this.historyLogLoading, id, true)
                    const data = {
                        page: row.pageInfo ? (row.pageInfo.page + 1) : 1,
                        node_id: this.nodeDetailConfig.node_id,
                        history_id: id,
                        instance_id: this.nodeDetailConfig.instance_id,
                        version: row.version
                    }
                    let resp = null
                    if (this.adminView) {
                        resp = await this.taskflowHistroyLog(data)
                    } else if (this.engineVer === 1) {
                        resp = await this.getNodeExecutionRecordLog(data)
                    } else if (this.engineVer === 2) {
                        resp = await this.getEngineVerNodeLog(data)
                    }
                    if (resp.result) {
                        const respData = this.adminView ? resp.data.log : resp.data
                        row.pageInfo = this.adminView ? resp.data.page : resp.page
                        const curLog = this.historyLog[id] || ''
                        this.$set(this.historyLog, id, curLog + (curLog ? '\n' : '') + respData)
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.historyLogLoading[id] = false
                }
            },
            // 设置第三方节点历史日志
            setHistoryLogWatch (row) {
                try {
                    // 滚动dom
                    const editorDom = document.querySelector(`.history-editor-${row.history_id}`)
                    const scrollDom = editorDom && editorDom.querySelector('.code-editor .vertical .slider')
                    if (!scrollDom) return
                    // 编辑器dom
                    const editDom = editorDom && editorDom.querySelector('.monaco-editor')
                    const MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver
                    // 监听滚动dom
                    row.observer = new MutationObserver(async mutation => {
                        const { height } = scrollDom.getBoundingClientRect()
                        const { height: editHeight } = editDom && editDom.getBoundingClientRect()
                        const top = scrollDom.offsetTop
                        const offsetBottom = editHeight > 300 ? 180 : 100
                        if (row.historyLogTab === 'third_party_plugin') {
                            if (editHeight - height - top < offsetBottom && !this.historyLogLoading[row.history_id] && row.scrollId) {
                                this.historyLogLoading[row.history_id] = true
                                // 设置第三方节点历史日志
                                await this.setThirdHistoryLog(row)
                            }
                        } else if (row.nodeInfo) {
                            const { page, total, page_size } = row.nodeInfo
                            if (editHeight - height - top < offsetBottom && !this.this.historyLogLoading[row.history_id] && page < Math.ceil(total / page_size)) {
                                const id = Number(row.history_id)
                                this.getHistoryLog(id, row)
                            }
                        }
                    })
                    row.observer.observe(scrollDom, {
                        childList: true,
                        attributes: true,
                        characterData: true,
                        subtree: true
                    })
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.historyLogLoading[row.history_id] = false
                }
            },
            // 设置第三方节点历史日志
            async setThirdHistoryLog (row) {
                try {
                    const id = Number(row.history_id)
                    const traceId = row.outputs.trace_id
                    const thirdLogsResp = await this.loadPluginServiceLog({
                        plugin_code: this.thirdPartyNodeCode,
                        trace_id: traceId,
                        scroll_id: row.scrollId || undefined
                    })
                    if (thirdLogsResp.result) {
                        const { logs, scroll_id } = thirdLogsResp.data
                        const thirdPartyLogs = this.thirdHistoryLog[id] || ''
                        this.$set(this.thirdHistoryLog, id, thirdPartyLogs + logs)
                        row.scrollId = logs && scroll_id ? scroll_id : ''
                    } else {
                        row.scrollId = ''
                    }
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.historyLogLoading[row.history_id] = false
                }
            },
            getHistoryLogData (row) {
                return row.historyLogTab === 'build_in_plugin' ? this.historyLog[row.history_id] : this.thirdHistoryLog[row.history_id]
            }
        }
    }
</script>

<style lang="scss" scoped>
    .retry-table {
        font-size: 12px;
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
</style>
