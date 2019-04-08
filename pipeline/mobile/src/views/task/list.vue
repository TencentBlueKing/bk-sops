<template>
    <div class="page-view">
        <!-- 搜索 -->
        <van-search :placeholder="i18n.placeholder"
            v-model="value"
            show-action
            class="bk-search"
            @search="search()">
            <div slot="action" @click="search">搜索</div>
        </van-search>
        <!-- 列表 -->
        <section class="bk-block">
            <van-cell clickable>
                <template slot="title">
                    <div class="bk-text">Troytu的测试流程模版任务</div>
                    <div class="bk-name">Troytu</div>
                    <div class="bk-time">2019-03-10 13:49:20 至 2019-03-10 15:01:20</div>
                </template>
                <van-icon slot="right-icon" name="clear" class="task-icon close" />
            </van-cell>
            <van-cell clickable>
                <template slot="title">
                    <div class="bk-text">Troytu的测试流程模版任务</div>
                    <div class="bk-name">Troytu</div>
                    <div class="bk-time">2019-03-10 13:49:20 至 2019-03-10 15:01:20</div>
                </template>
                <van-icon slot="right-icon" name="more" class="task-icon more" />
            </van-cell>
            <van-cell clickable>
                <template slot="title">
                    <div class="bk-text">Troytu的测试流程模版任务</div>
                    <div class="bk-name">Troytu</div>
                    <div class="bk-time">2019-03-10 13:49:20 至 2019-03-10 15:01:20</div>
                </template>
                <van-icon slot="right-icon" name="pause-circle" class="task-icon pause" />
            </van-cell>
            <van-cell clickable>
                <template slot="title">
                    <div class="bk-text">Troytu的测试流程模版任务</div>
                    <div class="bk-name">Troytu</div>
                    <div class="bk-time">2019-03-10 13:49:20 至 2019-03-10 15:01:20</div>
                </template>
                <van-icon slot="right-icon" name="" class="task-icon circle" />
            </van-cell>
        </section>
    </div>
</template>

<script>
    import { mapActions } from 'vuex'

    export default {
        name: 'TaskList',
        data () {
            return {
                i18n: {
                    placeholder: window.gettext('搜索任务名称')
                }
            }
        },
        mounted () {
            this.loadData()
        },
        methods: {
            ...mapActions('template', [
                'getTemplate',
                'getCollectTemplateList'
            ])
        }
    }
</script>

<style lang="scss">
    @import '../../../static/style/app.scss';
</style>
