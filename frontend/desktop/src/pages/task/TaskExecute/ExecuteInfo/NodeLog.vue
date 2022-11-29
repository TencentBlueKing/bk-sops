<template>
    <section class="info-section log-section" data-test-id="taskExecute_form_nodeLog">
        <div class="log-wrap">
            <!-- 内置插件/第三方插件tab -->
            <bk-tab
                v-if="isThirdPartyNode"
                :active-bar="{
                    position: 'top',
                    height: '2px'
                }"
                :active.sync="curPluginTab"
                type="unborder-card">
                <bk-tab-panel v-bind="{ name: 'build_in_plugin', label: $t('节点日志') }"></bk-tab-panel>
                <bk-tab-panel
                    v-bind="{ name: 'third_party_plugin', label: $t('第三方节点日志') }">
                </bk-tab-panel>
            </bk-tab>
            <div class="perform-log" v-bkloading="{ isLoading: isLogLoading, opacity: 1, zIndex: 100 }">
                <full-code-editor
                    class="scroll-editor"
                    :key="curPluginTab"
                    :value="curPluginTab === 'build_in_plugin' ? logInfo : thirdPartyNodeLog">
                </full-code-editor>
            </div>
        </div>
    </section>
</template>

<script>
    import { mapActions } from 'vuex'
    import FullCodeEditor from '@/components/common/FullCodeEditor.vue'
    export default {
        name: 'NodeLog',
        components: {
            FullCodeEditor
        },
        props: {
            nodeDetailConfig: {
                type: Object,
                default: () => ({})
            },
            executeInfo: {
                type: Object,
                default: () => ({})
            },
            thirdPartyNodeCode: {
                type: String,
                default: ''
            },
            adminView: {
                type: Boolean,
                default: false
            },
            engineVer: {
                type: Number,
                required: true
            }
        },
        data () {
            return {
                curPluginTab: 'build_in_plugin',
                isLogLoading: false,
                logInfo: '',
                thirdPartyNodeLog: '',
                scrollId: '',
                observer: null,
                editScrollDom: null,
                nodeLogPageInfo: null
            }
        },
        computed: {
            isThirdPartyNode () {
                const compCode = this.nodeDetailConfig.component_code
                return compCode && compCode === 'remote_plugin'
            }
        },
        watch: {
            curPluginTab (val) {
                this.editScrollDom = null
                if (val === 'third_party_plugin' || this.nodeLogPageInfo) {
                    this.watchEditorScroll()
                }
            },
            executeInfo: {
                handler (val) {
                    this.initLog()
                },
                deep: true
            }
        },
        beforeDestroy () {
            if (this.observer) {
                this.observer.disconnect()
                this.observer.takeRecords()
                this.observer = null
            }
        },
        mounted () {
            this.initLog()
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
                'taskflowHistroyLog'
            ]),
            initLog () {
                const { state, history_id, version, outputs } = this.executeInfo
                // 获取节点日志
                if (state && !['READY', 'CREATED'].includes(state)) {
                    const query = Object.assign({}, this.nodeDetailConfig, {
                        history_id: history_id,
                        version: version
                    })
                    this.getPerformLog(query)
                    // 获取第三方插件节点日志
                    if (this.isThirdPartyNode) {
                        const traceId = outputs.length && outputs[0].value
                        this.handleTabChange(traceId)
                    }
                }
            },
            // 非admin 用户执行记录
            async getPerformLog (query) {
                try {
                    this.isLogLoading = true
                    let performLog = {}
                    if (this.adminView) { // 管理端日志
                        performLog = await this.taskflowHistroyLog(query)
                    } else if (this.engineVer === 1) { // 不同引擎版本的任务调用不同的接口
                        performLog = await this.getNodeExecutionRecordLog(query)
                    } else if (this.engineVer === 2) {
                        performLog = await this.getEngineVerNodeLog(query)
                    }
                    this.logInfo = this.logInfo + (this.logInfo ? '\n' : '') + (this.adminView ? performLog.data.log : performLog.data)
                    this.nodeLogPageInfo = performLog.page
                    if (this.nodeLogPageInfo && !this.editScrollDom) {
                        this.watchEditorScroll()
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.isLogLoading = false
                }
            },
            watchEditorScroll () {
                // 第三方日志滚动加载
                this.$nextTick(() => {
                    // 滚动dom
                    const editScrollDom = document.querySelector('.scroll-editor .code-editor .vertical .slider')
                    if (!editScrollDom) return
                    // 编辑器dom
                    const editDom = document.querySelector('.scroll-editor .monaco-editor')
                    const MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver

                    // 监听滚动dom
                    this.observer = new MutationObserver(mutation => {
                        const { height } = editScrollDom.getBoundingClientRect()
                        const { height: editHeight } = editDom && editDom.getBoundingClientRect()
                        const top = editScrollDom.offsetTop
                        const offsetBottom = editHeight > 300 ? 180 : 80
                        if (this.curPluginTab === 'third_party_plugin') {
                            if (editHeight - height - top < offsetBottom && !this.isLogLoading && this.scrollId) {
                                const { outputs } = this.executeInfo
                                const traceId = outputs.length && outputs[0].value
                                this.handleTabChange(traceId)
                            }
                        } else if (this.nodeLogPageInfo) {
                            const { page, total, page_size } = this.nodeLogPageInfo
                            if (editHeight - height - top < offsetBottom && !this.isLogLoading && page < Math.ceil(total / page_size)) {
                                const { history_id, version } = this.executeInfo
                                const query = Object.assign({}, this.nodeDetailConfig, {
                                    page: page + 1,
                                    history_id,
                                    version
                                })
                                this.getPerformLog(query)
                            }
                        }
                    })
                    this.observer.observe(editScrollDom, {
                        childList: true,
                        attributes: true,
                        characterData: true,
                        subtree: true
                    })
                    this.editScrollDom = editScrollDom
                })
            },
            async handleTabChange (traceId) {
                try {
                    this.isLogLoading = true
                    const resp = await this.loadPluginServiceLog({
                        plugin_code: this.thirdPartyNodeCode,
                        trace_id: traceId,
                        scroll_id: this.scrollId || undefined
                    })
                    if (!resp.result) {
                        this.scrollId = ''
                        return
                    }
                    const { logs, scroll_id } = resp.data
                    const thirdPartyLogs = this.thirdPartyNodeLog || ''
                    this.thirdPartyNodeLog = thirdPartyLogs + logs
                    this.scrollId = logs && scroll_id ? scroll_id : ''
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isLogLoading = false
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    .log-section {
        height: 100%;
        .log-wrap {
            height: calc(100% - 10px);
            display: flex;
            flex-direction: column;
            position: relative;
            /deep/.bk-tab {
                position: absolute;
                z-index: 2;
                height: 40px;
                .bk-tab-header,
                .bk-tab-label-list {
                    height: 40px !important;
                }
                .bk-tab-label-item {
                    line-height: 40px !important;
                    &.active {
                        color: #fff;
                    }
                }
                .bk-tab-section {
                    padding: 0;
                }
            }
            .full-code-editor {
                margin: 0 !important;
                /deep/.tool-area {
                    height: 40px;
                    line-height: 40px;
                    background: #2e2e2e;
                    .bk-icon {
                        color: #979ba5;
                    }
                }
            }
        }
        .perform-log {
            height: 100%;
        }
    }
</style>
