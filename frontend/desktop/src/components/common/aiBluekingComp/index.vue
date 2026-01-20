<template>
    <AIBlueking
        ref="aiBlueking"
        :url="aiAgentUrl"
        :request-options="requestOptions"
        @stop="handleStop"
        @receive-end="handleStop" />
    <!-- :prompts="customPrompts"  -->
</template>
<script>
    import AIBlueking from '@blueking/ai-blueking/vue2'
    import '@blueking/ai-blueking/dist/vue2/style.css'

    export default {
        name: 'aiBulekingComp',
        components: {
            AIBlueking
        },
        data () {
            return {
                aiAgentUrl: window.AI_SOPS_AGENT_URL,
                requestOptions: null,
                scriptCode: ''
            }
        },
        computed: {
            customPrompts () {
                const prompt = `
                使用脚本审计工具优化以下脚本
                检查代码如下: ${this.scriptCode}`
                return [prompt]
            }
        },
        watch: {
            '$route': {
                handler (val, oldVal) {
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
            // ai小鲸会话响应结束or手动停止
            handleStop () {
                this.scriptCode = ''
            },
            showAi () {
                this.$refs.aiBlueking.handleShow()
            },
            sendDefaultcommand (data) {
                this.scriptCode = data
                this.$refs.aiBlueking.handleShow()
                this.$refs.aiBlueking.handleSendMessage(this.customPrompts[0])
            }

        }
    }
</script>
<style lang="scss" scoped>
</style>
