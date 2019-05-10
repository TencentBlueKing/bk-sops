<template>
    <div class="tooltip" style="display: none">
        <div v-if="node.type === 'tasknode'">
            <div class="tooltip-arrow"></div>
            <div class="tooltip-inner">
                <div class="tooltip-btn" @click="onNodeExecuteDetail">{{ i18n.detail }}</div>
                <template v-if="node.status === 'FAILED'">
                    <div class="tooltip-btn" @click="onRetry">{{ i18n.retry }}</div>
                    <div class="tooltip-btn" @click="onSkip">{{ i18n.skip }}</div>
                </template>
            </div>
        </div>
        <div v-if="node.type === 'subflow'">
            <div class="tooltip-arrow"></div>
            <div class="tooltip-inner">
                <div class="tooltip-btn">{{ i18n.sub }}</div>
            </div>
        </div>
    </div>
</template>

<script>

    import { mapActions } from 'vuex'

    export default {
        name: 'Tooltips',
        props: {
            node: {
                type: Object,
                default () {
                    return {}
                }
            },
            task: {
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
                    detail: window.gettext('执行详情'),
                    retry: window.gettext('重试'),
                    skip: window.gettext('跳过'),
                    sub: window.gettext('查看子流程')
                },
                moveFlag: false
            }
        },
        mounted () {

        },
        methods: {
            ...mapActions('task', [
                'instanceNodeSkip'
            ]),
            onNodeExecuteDetail () {
                this.$router.push({ name: 'task_nodes', params: { node: this.node, task: this.task } })
            },
            async onRetry () {
            },
            async onSkip () {
                try {
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
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '../../../static/style/app.scss';
    .tooltip{
        position: absolute;
        margin-top: 10px;
        &-arrow{
             position: absolute;
             margin: 6px 0 0 -3px;
             width: 0;
             height: 0;
             border-style: solid;
             border-color: #333;
             border-width: 0 6px 6px 6px;
             border-left-color: transparent;
             border-right-color: transparent;
             border-top-color: transparent;
             top: -12px;
             left: 50%;
         }
        .tooltip-inner {
            color: #ffffff;
            border-radius: 10px;
            text-align: center;
            background: #29292a;
            padding: 8px 15px;
            white-space: nowrap;
            display: table;
            .tooltip-btn{
                display: table-cell;
                font-size: $fs-14;
                vertical-align: middle;
                + .tooltip-btn:before{
                    content: "|";
                    display: inline-block;
                    padding: 0 10px;
                    color: rgba(255,255,255,0.6);
                }
            }
        }
    }
</style>
