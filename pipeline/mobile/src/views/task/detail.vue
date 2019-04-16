<template>
    <div class="page-view">
        <!-- 信息 -->
        <section class="bk-block">
            <van-cell>
                <template slot="title">
                    <div class="bk-text">Troytu的测试流程模版任务</div>
                    <div class="bk-name">Troytu</div>
                    <div class="bk-time">2019-03-10 13:49:20</div>
                </template>
                <van-icon slot="right-icon" name="star" class="star-icon collection" clickable />
            </van-cell>
        </section>
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
