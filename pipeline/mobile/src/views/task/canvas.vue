<template>
    <div class="page-view">
        <div class="task-status warning" v-if="taskState === 'RUNNING'">
            执行中
        </div>
        <div class="task-status danger" v-else-if="taskState === 'FAILED'">
            失败
        </div>
        <!--演示试用 start-->

        <JsFlowIndex v-bind:task="task"></JsFlowIndex>
        <!--演示试用 end-->
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
                    @click="onBackClick"
                    disabled />
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
    import store from '@/store'
    import JsFlowIndex from '../jsflow/index.vue'
    import { mapActions, mapState } from 'vuex'

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
                taskState: ''
            }
        },
        computed: {
            ...mapState({
                task: state => state.task
            })
        },
        mounted () {
            this.loadData()
        },
        methods: {
            ...mapActions('task', [
                'getTask'
            ]),
            async loadData () {
                const taskInfo = await this.getTask(this.$route.query.taskId)
                console.log('==============')
                console.log(taskInfo[0])
                console.log(taskInfo[1])
                this.taskState = taskInfo[1]
                store.commit('setTask', taskInfo[0])
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
                    // on confirm
                    console.log('on confirm')
                    this.revokeConfirmShow = false
                    this.$router.push({ path: '/task/list' })
                }).catch(() => {
                    // on cancel
                    console.log('on cancel')
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
