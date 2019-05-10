<template>
    <div class="page-view">
        <!-- 搜索 -->
        <van-search
            background="false"
            :placeholder="i18n.placeholder"
            v-model="value"
            class="bk-search"
            @search="search()">
        </van-search>
        <!-- 列表 -->
        <section class="bk-block">
            <van-list
                v-model="loading"
                :finished="finished"
                :finished-text="i18n.finished_text"
                @load="loadData">
                <van-cell
                    clickable
                    v-for="item in taskList"
                    :key="item.id"
                    @click="onClickTask(item.id)">
                    <template slot="title">
                        <div class="bk-text">{{ item.name }}</div>
                        <div class="bk-name">{{ item.creator_name }}</div>
                        <div class="bk-time">
                            {{ item.create_time }}
                            <template v-if="item.finish_time">
                                {{ i18n.to }} <p>{{ item.finish_time || '--' }}</p>
                            </template>
                        </div>
                    </template>
                    <van-icon
                        slot="right-icon"
                        :name="item['status_icon_name']"
                        :class="['task-icon', item['status_class']]" />
                </van-cell>
            </van-list>
        </section>
    </div>
</template>

<script>
    import { mapActions } from 'vuex'
    // { 任务状态 : [图标名称, css名称] }
    const STATUS_CLASS = {
        'CREATED': ['circle', 'circle'],
        'FINISHED': ['checked', 'checked'],
        'FAILED': ['close', 'clear'],
        'SUSPENDED': ['pause', 'pause-circle'],
        'REVOKED': ['close', 'clear'],
        'RUNNING': ['more', 'more']
    }

    export default {
        name: 'TaskList',
        data () {
            return {
                taskList: [],
                originalTaskList: [],
                taskStatus: '',
                loading: false,
                finished: false,
                offset: 0,
                currPage: 1,
                limit: 10,
                total: 0,
                value: '',
                i18n: {
                    placeholder: window.gettext('搜索任务名称'),
                    finished_text: window.gettext('没有更多了'),
                    to: window.gettext('至')
                }
            }
        },
        methods: {
            ...mapActions('taskList', [
                'getTaskList',
                'getTaskStatus'
            ]),
            async loadData () {
                const response = await this.getTaskList({ offset: this.offset, limit: this.limit })
                this.total = response.meta.total_count
                const totalPage = Math.ceil(this.total / this.limit)
                if (this.currPage >= totalPage) {
                    this.finished = true
                } else {
                    this.offset = this.currPage * this.limit
                    this.currPage += 1
                }
                this.taskList = [...this.originalTaskList, ...response.objects]
                this.originalTaskList = this.taskList
                await this.fillTaskStatus()
                this.loading = false
            },

            async fillTaskStatus () {
                this.taskList.forEach((task) => {
                    // 任务未开始
                    if (task.is_started) {
                        const promise = this.getTaskStatus({ id: task.id })
                        promise.then(response => {
                            this.$set(task, 'status_class', STATUS_CLASS[response.state][0])
                            this.$set(task, 'status_icon_name', STATUS_CLASS[response.state][1])
                        })
                    } else {
                        [task['status_class'], task['status_icon_name']] = STATUS_CLASS['CREATED']
                    }
                })
            },

            search () {
                this.taskList = this.originalTaskList.filter(item => item.name.includes(this.value))
            },

            onClickTask (taskId) {
                this.$store.commit('setTaskId', taskId)
                this.$router.push({ path: `/task/canvas?taskId=${taskId}` })
            }
        }
    }
</script>

<style lang="scss">
    @import '../../../static/style/app.scss';
</style>
