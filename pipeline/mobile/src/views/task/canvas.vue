<template>
    <div class="page-view">
        <div :class="[taskStateClass, taskStateColor]">{{ taskStateName }}</div>
        <MobileCanvas v-if="!loading" :canvas-data="canvasData"></MobileCanvas>
        <van-tabbar>
            <van-tabbar-item>
                <van-icon
                    v-if="taskState === 'CREATED'"
                    slot="icon"
                    class-prefix="icon"
                    name="play"
                    @click="onExecute" />
                <van-icon
                    v-else-if="taskState === 'RUNNING'"
                    slot="icon"
                    class-prefix="icon"
                    name="pause"
                    @click="onPause" />
                <van-icon
                    v-else
                    slot="icon"
                    class-prefix="icon"
                    name="pause"
                    class="disabled"
                    disabled />
            </van-tabbar-item>
            <van-tabbar-item>
                <van-icon
                    v-if="taskState !== 'CREATED' && taskState !== 'REVOKED' && taskState !== 'FINISHED'"
                    slot="icon"
                    class-prefix="icon"
                    name="revoke"
                    @click="onRevokeConfirm" />
                <van-icon
                    v-else
                    slot="icon"
                    class-prefix="icon"
                    name="revoke"
                    class="disabled"
                    disabled />
            </van-tabbar-item>
            <van-tabbar-item>
                <van-icon
                    v-if="taskState !== 'CREATED'"
                    slot="icon"
                    class-prefix="icon"
                    name="file"
                    @click="onDetailClick" />
                <van-icon
                    v-else
                    class="disabled"
                    disabled
                    slot="icon"
                    class-prefix="icon"
                    name="file" />
            </van-tabbar-item>
        </van-tabbar>
        <template>
            <van-dialog v-model="revokeConfirmShow" :title="i18n.tip" show-cancel-button />
        </template>
    </div>
</template>
<script>
    import MobileCanvas from '@/components/MobileCanvas/index.vue'
    import { mapActions } from 'vuex'

    const TASK_STATE = {
        'CREATED': [window.gettext('未执行'), 'info'],
        'RUNNING': [window.gettext('执行中'), 'info'],
        'SUSPENDED': [window.gettext('暂停'), 'warning'],
        'NODE_SUSPENDED': [window.gettext('节点暂停'), 'warning'],
        'FAILED': [window.gettext('失败'), 'danger'],
        'FINISHED': [window.gettext('完成'), 'success'],
        'REVOKED': [window.gettext('撤销'), 'danger']
    }

    export default {
        name: '',
        components: {
            MobileCanvas
        },
        provide () {
            return {
                refreshTaskStatus: this.setTaskStatusTimer
            }
        },
        data () {
            return {
                // 演示用flag，当做画布的某个原子
                testShow: false,
                revokeConfirmShow: false,
                taskId: 0,
                task: {},
                taskState: '',
                taskStateClass: '',
                taskStateName: '',
                taskStateColor: '',
                timer: null,
                loading: true,
                i18n: {
                    tip: window.gettext('提示'),
                    loading: window.gettext('加载中...')
                }
            }
        },
        computed: {
            canvasData () {
                const pipelineTree = this.task ? this.task.pipeline_tree || {} : {}
                const { line = [], location = [] } = JSON.parse(pipelineTree)
                return { lines: line, nodes: location }
            }
        },
        created () {
            this.loadData()
        },
        methods: {
            ...mapActions('task', [
                'getTask',
                'getTaskStatus',
                'instanceStart',
                'instancePause',
                'instanceRevoke'
            ]),
            async loadData () {
                try {
                    this.$toast.loading({ mask: true, message: this.i18n.loading })
                    this.taskId = this.$route.query.taskId
                    this.task = await this.getTask({ id: this.taskId })
                    await this.loadTaskStatus()
                    if (this.$route.query.executeTask) {
                        this.onExecute()
                    }
                    this.$nextTick(() => {
                        this.loading = false
                        this.$toast.clear()
                    })
                } catch (err) {
                    console.error(err)
                }
            },
            updateTaskNodes (taskState) {
                if (taskState.state !== 'CREATED') {
                    this.canvasData.nodes.forEach((node) => {
                        const data = taskState.children[node.id]
                        // node = Object.assign(node, { 'data': data })
                        this.$set(node, 'data', data)
                        if (data) {
                            // Object.assign(node, { 'status': data.state })
                            this.$set(node, 'status', data.state)
                        }
                    })
                }
            },
            async loadTaskStatus () {
                try {
                    const taskState = await this.getTaskStatus({ id: this.taskId })
                    if (taskState.result) {
                        this.taskState = taskState.data.state
                        if (this.taskState === 'RUNNING') {
                            this.setTaskStatusTimer()
                        }
                        this.updateTaskNodes(taskState.data);
                        ([this.taskStateClass, this.taskStateName, this.taskStateColor] = ['task-status', ...TASK_STATE[this.taskState]])
                    } else {
                        this.cancelTaskStatusTimer()
                        console.error(taskState, this)
                    }
                } catch (e) {
                    this.cancelTaskStatusTimer()
                    console.error(e, this)
                }
            },

            setTaskStatusTimer () {
                this.cancelTaskStatusTimer()
                this.timer = setTimeout(() => {
                    this.loadTaskStatus()
                }, 2000)
            },
            cancelTaskStatusTimer () {
                if (this.timer) {
                    clearTimeout(this.timer)
                    this.timer = null
                }
            },
            async onExecute () {
                try {
                    const response = await this.instanceStart({ id: this.taskId })
                    if (response.result) {
                        this.setTaskStatusTimer()
                    } else {
                        console.error(response, this)
                    }
                } catch (e) {
                    console.error(e, this)
                }
            },
            async onRevoke () {
                try {
                    const response = await this.instanceRevoke({ id: this.taskId })
                    if (response.result) {
                        setTimeout(() => {
                            this.setTaskStatusTimer()
                        }, 1000)
                    } else {
                        console.error(response, this)
                    }
                } catch (e) {
                    console.error(e, this)
                }
            },
            onDetailClick () {
                this.$router.push({ path: '/task/detail', query: { taskId: String(this.taskId) } })
            },
            async onPause () {
                try {
                    const response = await this.instancePause({ id: this.taskId })
                    if (response.result) {
                        // TODO: 子流程暂停
                    } else {
                        console.error(response, this)
                    }
                } catch (e) {
                    console.error(e, this)
                }
            },
            onRevokeConfirm () {
                this.$dialog.confirm({
                    message: '撤销任务?'
                }).then(() => {
                    this.revokeConfirmShow = false
                    this.onRevoke()
                }).catch(() => {
                    this.revokeConfirmShow = false
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '../../../static/style/app.scss';
    .page-view{
        -webkit-overflow-scrolling: auto;
    }
</style>
