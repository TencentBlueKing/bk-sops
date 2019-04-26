<template>
    <div class="page-view">
        <!-- 任务信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">任务信息</h2>
            <div class="bk-text-list">
                <van-cell title="任务名称" value="new20190313145111" />
                <van-cell title="方案" value="方案一" />
            </div>
        </section>
        <!-- 参数信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">参数信息</h2>
            <div class="bk-text-list">
                <van-cell title="参数01" value="参数值" />
                <van-cell title="参数02" value="参数值" />
            </div>
        </section>
        <!-- 暂无数据 -->
        <section class="bk-block">
            <h2 class="bk-text-title">参数信息</h2>
            <div class="bk-text-list">
                <van-cell title="" value="暂无数据" />
            </div>
        </section>
    </div>
</template>
<script>
    import { mapActions } from 'vuex'

    export default {
        name: 'TaskDetail',
        data () {
            return {
                task: {}
            }
        },
        mounted () {
            this.loadData()
        },
        methods: {
            ...mapActions('task', [
                'getTask'
            ]),

            async loadData () {
                this.task = await this.getTask()
            }
        }
    }
</script>

<style lang="scss">
    @import '../../../static/style/app.scss';
</style>
