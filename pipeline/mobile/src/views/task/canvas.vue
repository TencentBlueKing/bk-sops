<template>
    <div class="page-view">
        <div :class="[taskStateClass, taskStateColor]">{{ taskStateName }}</div>
        <JsFlowIndex :task="currTask"></JsFlowIndex>
        <van-tabbar>
            <van-tabbar-item>
                <van-icon slot="icon" class-prefix="icon" name="pause" v-if="taskState === 'RUNNING'" />
                <van-icon slot="icon" class-prefix="icon" name="pause" v-else class="disabled" disabled />
            </van-tabbar-item>
            <van-tabbar-item>
                <van-icon
                    v-if="taskState === 'RUNNING'"
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
                    disabled
                    @click="onBackClick" />
            </van-tabbar-item>
            <van-tabbar-item>
                <van-icon
                    slot="icon"
                    class-prefix="icon"
                    name="file"
                    @click="onDetailClick" />
            </van-tabbar-item>
        </van-tabbar>
        <template>
            <van-dialog v-model="revokeConfirmShow" title="标题" show-cancel-button />
        </template>
    </div>
</template>
<script>
    import JsFlowIndex from '../jsflow/index.vue'
    import { mapActions, mapState } from 'vuex'

    const TASK_STATE = {
        'CREATED': [window.gettext('未执行'), 'info'],
        'RUNNING': [window.gettext('执行中'), 'info'],
        'SUSPENDED': [window.gettext('暂停'), 'warning'],
        'NODE_SUSPENDED': [window.gettext('节点暂停'), 'warning'],
        'FAILED': [window.gettext('失败'), 'danger'],
        'FINISHED': [window.gettext('完成'), 'danger'],
        'REVOKED': [window.gettext('撤销'), 'danger']
    }

    export default {
        name: '',
        components: {
            JsFlowIndex
        },
        props: { taskId: String },
        data () {
            return {
                // 演示用flag，当做画布的某个原子
                testShow: false,
                revokeConfirmShow: false,
                taskStateClass: '',
                taskStateName: '',
                taskStateColor: ''
            }
        },
        computed: {
            ...mapState({
                currTask: state => state.task,
                currTaskState: state => state.taskState
            })
        },
        mounted () {
            this.loadData()
        },
        methods: {
            ...mapActions('task', [
                'getTask',
                'getTaskState'
            ]),
            async loadData () {
                const taskId = this.$route.query.taskId
                const task = await this.getTask(taskId)
                const taskState = await this.getTaskState(taskId);
                ([this.taskStateClass, this.taskStateName, this.taskStateColor] = ['task-status', ...TASK_STATE[taskState]])
                this.$store.commit('setTaskState', taskState)
                this.$store.commit('setTask', task)
            },
            onNodeExecuteClick () {
                this.$router.push({ path: '/task/nodes', query: { taskId: this.task.id } })
            },
            onRetryClick () {
                this.$router.push({ path: '/task/reset', query: { taskId: this.task.id } })
            },
            onDetailClick () {
                this.$router.push({ path: '/task/detail', query: { taskId: this.task.id } })
            },
            onBackClick () {
                this.$router.push({ path: '/task/list', query: { taskId: this.task.id } })
            },
            onRevokeConfirm () {
                this.$dialog.confirm({
                    message: '撤销任务?'
                }).then(() => {
                    this.revokeConfirmShow = false
                    this.$router.push({ path: '/task/list' })
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
