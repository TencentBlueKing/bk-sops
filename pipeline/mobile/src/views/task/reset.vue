<template>
    <div class="page-view">
        <!-- 任务信息 -->
        <section class="bk-block">
            <div class="bk-text-list">
                <van-field label="参数01" placeholder="输入参数值" />
                <van-field label="参数02" placeholder="输入参数值" />
            </div>
        </section>
        <div class="btn-group">
            <van-button size="large" type="default" @click="onClick">取消</van-button>
            <van-button size="large" type="info" @click="onClick">确定</van-button>
        </div>
    </div>
</template>
<script>
    import store from '@/store'
    import { mapActions, mapState } from 'vuex'

    export default {
        name: 'TaskReset',
        data () {
            return {
                templateData: {
                    name: '',
                    creator_name: '',
                    create_time: ''
                },
                templateConstants: {},
                i18n: {
                    btnCreate: window.gettext('执行任务')
                }
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
            ...mapActions('template', [
                'getTemplate',
                'getTemplateConstants'
            ]),
            async loadData () {
                // TODO: 重试需要填写原子的参数，原子的表单参数在mobile端需要重新开发
            },
            onClick () {
                this.$router.push({ path: '/task/canvas', query: { taskId: store.state.task.id } })
            }
        }
    }
</script>

<style lang="scss">
    @import '../../../static/style/app.scss';
</style>
