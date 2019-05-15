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
            <h2 class="bk-text-title">{{ i18n.executeInfo }}</h2>
            <div class="bk-text-list">
                <van-cell :title="i18n.startTime" :value="nodeDetail.start_time" />
                <van-cell :title="i18n.endTime" :value="nodeDetail.finish_time" />
                <van-cell :title="i18n.costTime" :value="nodeDetail.elapsed_time" />
                <van-cell :title="i18n.skipped" :value="nodeDetail.skip ? i18n.yes : i18n.no" />
                <van-cell :title="i18n.ignore" :value="nodeDetail.error_ignorable ? i18n.yes : i18n.no" />
                <van-cell :title="i18n.retryTimes" :value="nodeDetail.retry" />
            </div>
        </section>
        <!-- 输入参数 -->
        <section class="bk-block">
            <h2 class="bk-text-title">{{ i18n.inputParameter }}</h2>
            <VueJsonPretty
                class="parameter-info"
                :data="nodeDetail.inputs">
            </VueJsonPretty>
            <van-button type="default" class="view-btn" @click="showParameters">{{ i18n.showTotal }}</van-button>
        </section>
        <!-- 输出参数 -->
        <section class="bk-block">
            <h2 class="bk-text-title">{{ i18n.outputParameter }}</h2>
            <div class="bk-text-list">
                <van-cell
                    v-for="item in nodeDetail.outputs"
                    :key="item.index"
                    :title="item.name"
                    :value="item.value === '' ? '--' : str(item.value)" />
            </div>
        </section>
        <!-- 异常信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">{{ i18n.errorInfo }}</h2>
            <div class="bk-text-list">
                <van-cell :value="nodeDetail.ex_data" />
            </div>
        </section>
        <!-- 执行记录 -->
        <section
            class="bk-block"
            v-for="history in nodeDetail.histories"
            :key="history.index">
            <h2 class="bk-text-title">{{ i18n.executeHistory }}</h2>
            <div class="bk-text-list">
                <van-cell :title="i18n.startTime" :value="history.start_time" />
                <van-cell :title="i18n.endTime" :value="history.finish_time" />
                <van-cell :title="i18n.costTime" :value="history.elapsed_time" />
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
                nodeDetail: {},
                i18n: {
                    loading: window.gettext('加载中...'),
                    executeInfo: window.gettext('执行信息'),
                    startTime: window.gettext('开始时间'),
                    endTime: window.gettext('结束时间'),
                    costTime: window.gettext('耗时(S)'),
                    skipped: window.gettext('失败后跳过'),
                    yes: window.gettext('是'),
                    no: window.gettext('否'),
                    ignore: window.gettext('失败后自动忽略'),
                    retryTimes: window.gettext('重试次数'),
                    inputParameter: window.gettext('输入参数'),
                    outputParameter: window.gettext('输出参数'),
                    showTotal: window.gettext('查看全部'),
                    errorInfo: window.gettext('异常信息'),
                    executeHistory: window.gettext('执行记录')

                }
            }
        },
        mounted () {
            this.loadData()
        },
        methods: {
            ...mapActions('task', [
                'getTask',
                'getNodeDetail'
            ]),

            async loadData () {
                this.$toast.loading({ mask: true, message: this.i18n.loading })
                const node = this.$route.params.node
                const taskId = this.$store.state.taskId
                const params = {
                    taskId: taskId,
                    nodeId: node.id,
                    componentCode: ''
                }
                const response = await this.getNodeDetail(params)
                const task = await this.getTask({ id: taskId })
                if (response.result) {
                    this.nodeDetail = response.data
                    this.nodeDetail.name = task.name
                }
                this.$toast.clear()
            },

            showParameters () {
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
