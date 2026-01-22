<template>
    <div>
        <AIBlueking
            ref="aiBlueking"
            :url="aiAgentUrl"
            :request-options="requestOptions" />
    </div>
</template>
<script>
    import AIBlueking from '@blueking/ai-blueking/vue2'
    import '@blueking/ai-blueking/dist/vue2/style.css'
    import tools from '@/utils/tools.js'
    import { mapState } from 'vuex'

    export default {
        name: 'aiBulekingComp',
        components: {
            AIBlueking
        },
        data () {
            return {
                aiAgentUrl: window.AI_SOPS_AGENT_URL,
                requestOptions: null
            }
        },
        computed: {
            ...mapState({
                'bizId': state => state.project.bizId
            })
        },
        watch: {
            '$route': {
                handler () {
                    const { instance_id: instanceId } = this.$route.query
                    const params = this.$route.params
                    const context = Object.assign({ bk_biz_id: this.bizId, task_id: instanceId }, this.$route.query, params)
                    this.requestOptions = { context }
                },
                immediate: true,
                deep: true
            }
        },
        methods: {
            showAi () {
                this.$refs.aiBlueking.handleShow()
            },
            async sendDefaultcommand ({ data, operationName }) {
                const shortcutsCommand = this.$refs.aiBlueking.agentInfo?.conversationSettings?.commands
                try {
                    let curCommond = null
                    if (operationName === 'checkScript') {
                        const curPrompt = `使用脚本审计工具优化以下脚本\n检查代码如下:\n${data}`
                        curCommond = tools.deepClone(shortcutsCommand.find(item => item.id === 'ai-scripting'))
                        curCommond.components[0].default = curPrompt
                    }
                    if (operationName === 'checkExecutedFailed') {
                        curCommond = tools.deepClone(shortcutsCommand.find(item => item.id === 'analyze_task_error'))
                        const { instance_id: instanceId, bk_biz_id: bkBizId } = this.requestOptions.context
                        curCommond.components.forEach(item => {
                            if (item.key === 'task_id') {
                                item.default = instanceId
                            }
                            if (item.key === 'bk_biz_id') {
                                item.default = bkBizId
                            }
                        })
                    }
                    await this.$refs.aiBlueking.handleShow(undefined, { isTemporary: true })
                    this.$refs.aiBlueking.handleShortcutClick({ shortcut: curCommond, source: 'popup' }, true)
                } catch (error) {
                    console.error(error)
                }
            }

        }
    }
</script>
<style lang="scss" scoped>
</style>
