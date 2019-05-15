<template>
    <tippy
        v-if="show"
        :to="'tip_' + node.id"
        placement="bottom"
        arrow="true"
        theme="dark"
        interactive="true"
        :ref="'tooltip_' + node.id"
        watch-props="true">
        <div v-if="node.type === 'tasknode'" class="tooltip">
            <div class="tooltip-btn" @click="onNodeExecuteDetail">{{ i18n.detail }}</div>
            <template v-if="node.status === 'FAILED'">
                <!--<div class="tooltip-btn" @click="onRetry">{{ i18n.retry }}</div>-->
                <div class="tooltip-btn" @click="onSkip">{{ i18n.skip }}</div>
            </template>
        </div>
        <div v-else-if="node.type === 'subflow'" class="tooltip-btn">{{ i18n.sub }}</div>
    </tippy>
</template>

<script>

    import { mapActions, mapState } from 'vuex'

    export default {
        name: 'Tooltips',
        props: {
            node: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        inject: ['refreshTaskStatus'],
        data () {
            return {
                i18n: {
                    i18n: window.gettext('加载中'),
                    detail: window.gettext('执行详情'),
                    retry: window.gettext('重试'),
                    skip: window.gettext('跳过'),
                    sub: window.gettext('查看子流程')
                },
                show: true,
                moveFlag: false
            }
        },
        computed: {
            ...mapState({
                taskId: state => state.taskId
            })
        },
        methods: {
            ...mapActions('task', [
                'getTask',
                'instanceNodeSkip',
                'getNodeRetryData'
            ]),
            onNodeExecuteDetail () {
                this.show = false
                this.$router.push({ name: 'task_nodes', params: { node: this.node } })
            },
            async onRetry () {
                this.show = false
                this.$toast.loading({ mask: true, message: this.i18n.loading })
                const task = await this.getTask({ id: this.taskId })
                const pipelineTree = JSON.parse(task.pipeline_tree)
                const taskId = this.taskId
                const params = {
                    taskId: taskId,
                    nodeId: this.node.id,
                    componentCode: pipelineTree.activities[this.node.id]
                }
                const response = await this.getNodeRetryData(params)
                this.$toast.clear()
                this.$router.push({ name: 'task_reset', params: { inputs: response.data.inputs } })
            },
            async onSkip () {
                try {
                    this.show = false
                    this.$toast.loading({ mask: true, message: this.i18n.loading })
                    const response = await this.instanceNodeSkip({ id: this.taskId, nodeId: this.node.id })
                    if (response.result) {
                        setTimeout(() => {
                            this.refreshTaskStatus()
                        }, 1000)
                    } else {
                        console.error(response, this)
                    }
                } catch (e) {
                    console.error(e, this)
                } finally {
                    this.$toast.clear()
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '../../../static/style/app.scss';
    .tooltip {
        text-align: center;
        display: table;
        .tooltip-btn {
            display: table-cell;
            font-size: $fs-14;
            vertical-align: middle;
            + .tooltip-btn:before {
                content: "|";
                display: inline-block;
                color: rgba(255, 255, 255, 0.6);
            }
        }
    }
</style>
