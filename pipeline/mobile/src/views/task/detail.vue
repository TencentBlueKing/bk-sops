<template>
    <div class="page-view">
        <!-- 任务信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">任务信息</h2>
            <div class="bk-text-list">
                <van-cell title="任务名称" :value="task.name" />
            </div>
        </section>
        <!-- 参数信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">参数信息</h2>
            <div class="bk-text-list">
                <template v-if="Object.keys(constants).length">
                    <template v-for="item in constants">
                        <van-cell
                            :key="item.id"
                            :title="item.name"
                            :value="item.value" />

                    </template>
                </template>
                <template v-else>
                    <van-cell title="" :value="i18n.noData" />
                </template>
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
                task: {},
                constants: {},
                i18n: {
                    noData: window.gettext('暂无数据'),
                    loading: window.gettext('加载中')
                }
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
                this.$toast.loading({ mask: true, message: this.i18n.loading })
                this.task = await this.getTask({ id: this.$route.query.taskId })
                const pipelineTree = JSON.parse(this.task.pipeline_tree)
                this.constants = pipelineTree.constants
                this.$toast.clear()
            }
        }
    }
</script>

<style lang="scss">
    @import '../../../static/style/app.scss';
</style>
