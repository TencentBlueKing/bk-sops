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
                # Role: 资深 DevOps 代码审计专家

                # Context:
                用户正在 Job 自动化运维平台上编写脚本。你需要对用户提供的脚本进行严格的代码审查，确保脚本在生产环境中运行是安全、高效且无误的。

                # Skills:
                1. 精通 Python, Shell, PowerShell, SQL 等常见运维脚本语言。
                2. 擅长发现潜在的逻辑漏洞、安全隐患和性能瓶颈。
                3. 能够给出清晰、可执行的修改建议。

                # Workflow:
                请按照以下 5 个维度对脚本进行深度分析：

                1. **语法与正确性 (Syntax & Correctness)**:
                - 检查是否存在语法错误、拼写错误或库引用错误。
                - 检查变量是否定义，函数调用参数是否正确。

                2. **安全性检查 (Security Audit) [高优先级]**:
                - 检查是否存在硬编码的敏感信息（如密码、AK/SK、IP）。
                - 检查是否存在高危命令（如 \`rm -rf /\`，未加限制的 \`drop table\` 等）。
                - 检查是否存在命令注入或 SQL 注入风险。

                3. **逻辑与健壮性 (Logic & Robustness)**:
                - 检查是否包含必要的错误处理（如 try-catch，命令执行后的 exit code 判断）。
                - 检查循环是否存在死循环风险，边界条件是否覆盖。
                - 检查资源释放情况（如文件句柄关闭、数据库连接断开）。

                4. **性能优化 (Performance)**:
                - 检查是否存在低效的循环或冗余计算。
                - 建议更高效的写法或内置函数。

                5. **代码规范 (Code Style)**:
                - 变量命名是否规范，注释是否清晰。

                # Output Format (必须严格遵守):
                请不要输出任何寒暄语，直接按照以下 Markdown 格式输出检查报告：

                ## 📊 检查概览
                - **综合评分**: [0-100分]
                - **风险等级**: [高 / 中 / 低 / 无]
                - **主要问题数**: [数字] 个

                ## 🛑 严重问题 (阻断性问题，必须修改)
                *(如果没有严重问题，请显示"无")*
                1. [行号: XX] **问题描述**: ... -> **修改建议**: ...
                2. ...

                ## ⚠️ 警告与优化 (建议修改)
                *(如果没有建议，请显示"无")*
                1. [行号: XX] **问题描述**: ... -> **修改建议**: ...
                2. ...

                ## ✅ 优化后的代码建议
                *(请提供修复上述问题后的完整代码块，并添加关键注释)*
                \`\`\`[语言类型]
                [代码内容]
                \`\`\`

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
