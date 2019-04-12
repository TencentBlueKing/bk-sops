<template>
    <div class="page-view">
        <!-- 搜索 -->
        <van-search
            :placeholder="i18n.placeholder"
            v-model="value"
            class="bk-search"
            @search="search()">
        </van-search>
        <!-- 列表 -->
        <section class="bk-block">
            <van-cell
                clickable
                v-for="item in taskList"
                :key="item.id"
                :to="`/task/detail?taskId=${item.id}`">
                <template slot="title">
                    <div class="bk-text">{{ item.name }}</div>
                    <div class="bk-name">{{ item.creator_name }}</div>
                    <div class="bk-time">{{ item.create_time }} 至 {{ item.finish_time || '--' }}</div>
                </template>
                <van-icon slot="right-icon" name="more" :class="item.status_class" />
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
                taskList: [],
                taskStatus: '',
                i18n: {
                    placeholder: window.gettext('搜索任务名称')
                }
            }
        },
        mounted () {
            this.loadData()
        },
        methods: {
            ...mapActions('taskList', [
                'getTaskList'
            ]),
            async loadData () {
                this.taskList = await this.getTaskList()
            },
            search () {
                const arr = []
                for (let i = 0; i < this.taskList.length; i++) {
                    if (this.taskList[i].name.includes(this.value)) {
                        arr.push(this.taskList[i])
                    }
                }
                this.taskList = arr
            }
        }
    }
</script>

<style lang="scss">
    @import '../../../static/style/app.scss';
</style>
