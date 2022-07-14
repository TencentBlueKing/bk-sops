<template>
    <section class="info-section log-info" data-test-id="taskExecute_form_nodeLog">
        <h4 class="common-section-title">{{ $t('节点日志') }}</h4>
        <!-- 内置插件/第三方插件tab -->
        <bk-tab v-if="isThirdPartyNode" :active.sync="curPluginTab" type="unborder-card">
            <bk-tab-panel v-bind="{ name: 'build_in_plugin', label: $t('节点日志') }"></bk-tab-panel>
            <bk-tab-panel
                v-bind="{ name: 'third_party_plugin', label: $t('第三方节点日志') }">
            </bk-tab-panel>
        </bk-tab>
        <div class="perform-log" v-bkloading="{ isLoading: isLogLoading, opacity: 1, zIndex: 100 }">
            <full-code-editor
                v-if="curPluginTab === 'build_in_plugin' ? logInfo : thirdPartyNodeLog"
                class="scroll-editor"
                :key="curPluginTab"
                :value="curPluginTab === 'build_in_plugin' ? logInfo : thirdPartyNodeLog">
            </full-code-editor>
            <NoData v-else></NoData>
        </div>
    </section>
</template>

<script>
    import { mapActions } from 'vuex'
    import NoData from '@/components/common/base/NoData.vue'
    import FullCodeEditor from '../FullCodeEditor.vue'
    export default {
        name: 'NodeLog',
        components: {
            NoData,
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

        },
        methods: {
            ...mapActions('task/', [
                'getEngineVerNodeLog',
                'getNodeExecutionRecordLog'
            ]),
            ...mapActions('atomForm/', [
                'loadPluginServiceLog'
            ]),
            // 非admin 用户执行记录
            async getPerformLog (query) {
                try {
                    this.isLogLoading = true
                    let performLog = {}
                    // 不同引擎版本的任务调用不同的接口
                    if (this.engineVer === 1) {
                        performLog = await this.getNodeExecutionRecordLog(query)
                    } else if (this.engineVer === 2) {
                        performLog = await this.getEngineVerNodeLog(query)
                    }
                    this.logInfo = this.logInfo + (this.logInfo ? '\n' : '') + performLog.data
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

<style>

</style>
