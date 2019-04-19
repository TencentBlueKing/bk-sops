<template>
    <div class="page-view">
        <div class="task-status warning" v-if="taskState === 'RUNNING'">
            执行中
        </div>
        <div class="task-status danger" v-else-if="taskState === 'FAILED'">
            失败
        </div>
        <!--演示试用 start-->
        <div class="canvas-demo" v-if="taskState === 'FAILED'">
            <div class="container">
                <div class="box" @click="testShow = true">演示点我</div>
                <div class="tips-bar" v-if="testShow">
                    <van-button type="default" class="" @click="onNodeExecuteClick">执行详情</van-button>
                    <van-button type="default" class="" @click="onRetryClick">重试</van-button>
                    <van-button type="default" class="">跳过</van-button>
                </div>
            </div>
        </div>
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
    import { mapActions, mapState } from 'vuex'

    export default {
        name: '',
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
    /*以下为演示试用可删除*/
    .canvas-demo{
        align-items: center;
        display: flex;
        justify-content: center;
        height: calc(100% - 90px);
        .container{
            width: 100%;
            text-align: center;
            position: relative;
            .box{
                width: 120px;
                height: 60px;
                line-height: 60px;
                border:1px solid #EA3636;
                background: #fff;
                margin: auto;
                font-size: 14px;
            }
            .tips-bar{
                position: absolute;
                width: 100%;
                top: -60px;
            }
        }
    }
</style>
