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
        watch: {
            '$route': {
                handler () {
                    const query = this.$route.query
                    const params = this.$route.params
                    const context = Object.assign({}, query, params)
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
                if (operationName === 'checkScript') {
                    try {
                        const curPrompt = `使用脚本审计工具优化以下脚本\n检查代码如下:\n${data}`
                        const curCommond = tools.deepClone(shortcutsCommand.find(item => item.id === 'ai-scripting'))
                        curCommond.components[0].default = curPrompt
                        await this.$refs.aiBlueking.handleShow(undefined, { isTemporary: true })
                        this.$refs.aiBlueking.handleShortcutClick({ shortcut: curCommond, source: 'popup' }, true)
                    } catch (error) {
                        console.error(error)
                    }
                }
            }

        }
    }
</script>
<style lang="scss" scoped>
</style>
