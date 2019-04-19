<template>
    <div class="page-view">
        <!-- 信息 -->
        <section class="bk-block">
            <van-cell>
                <template slot="title">
                    <div class="bk-text">{{ nodeDetail.name }}</div>
                </template>
                <div class="status">
                    <van-icon slot="right-icon" name="clear" class="task-icon close" />
                    <span class="text">失败</span>
                </div>
            </van-cell>
        </section>
        <!-- 执行信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">执行信息</h2>
            <div class="bk-text-list">
                <van-cell title="开始时间" :value="nodeDetail.start_time" />
                <van-cell title="结束时间" :value="nodeDetail.finish_time" />
                <van-cell title="耗时" :value="nodeDetail.elapsed_time" />
                <van-cell title="失败后跳过" :value="nodeDetail.skip ? '是' : '否'" />
                <van-cell title="失败后自动忽略" :value="nodeDetail.error_ignorable ? '是' : '否'" />
                <van-cell title="重试次数" :value="nodeDetail.retry" />
            </div>
        </section>
        <!-- 输入参数 -->
        <section class="bk-block">
            <h2 class="bk-text-title">输入参数</h2>
            <VueJsonPretty
                class="parameter-info"
                :data="nodeDetail.inputs">
            </VueJsonPretty>
            <van-button type="default" class="view-btn" @click="showParameters">查看全部</van-button>
        </section>
        <!-- 输出参数 -->
        <section class="bk-block">
            <h2 class="bk-text-title">输出参数</h2>
            <div class="bk-text-list">
                <van-cell
                    v-for="item in nodeDetail.outputs"
                    :key="item.index"
                    :title="item.name"
                    :value="item.value === '' ? '--' : JSON.stringify(item.value)" />
            </div>
        </section>
        <!-- 异常信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">异常信息</h2>
            <div class="bk-text-list">
                <van-cell :value="nodeDetail.ex_data" />
            </div>
        </section>
        <!-- 执行记录 -->
        <section
            class="bk-block"
            v-for="history in nodeDetail.histories"
            :key="history.index">
            <h2 class="bk-text-title">执行记录01</h2>
            <div class="bk-text-list">
                <van-cell title="开始时间" :value="history.start_time" />
                <van-cell title="结束时间" :value="history.finish_time" />
                <van-cell title="耗时（s）" :value="history.elapsed_time" />
            </div>
        </section>
    </div>
</template>
<script>
    import VueJsonPretty from 'vue-json-pretty'
    import { mapActions } from 'vuex'

    export default {
        name: 'TaskNodes',
        components: {
            VueJsonPretty
        },
        data () {
            return {
                nodeDetail: {}
            }
        },
        mounted () {
            this.loadData()
        },
        methods: {
            ...mapActions('task', [
                'getNodeDetail'
            ]),

            async loadData () {
                this.nodeDetail = await this.getNodeDetail()
                console.log(this.nodeDetail)
            },

            showParameters () {
                // pass
                this.$router.push({ name: 'task_node_parameter', params: { parameters: JSON.stringify(this.nodeDetail.inputs) } })
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '../../../static/style/app.scss';
    .bk-block .status{
        .task-icon{
            vertical-align: middle;
        }
        .text{
            margin-left: 5px;
            font-size: $fs-12;
            color: $text-color-light;
        }
    }
    .parameter-info{
        background: #313238;
        max-height: 100px;
        color: $white;
        font-size: $fs-14;
        padding: 0 25px;
        overflow: hidden;
    }
    .view-btn{
        display: block;
        background: none;
        border-radius: 0;
        margin: 15px 25px 0 25px;
        width: calc(100% - 50px);
        font-size: $fs-14;
    }
</style>
