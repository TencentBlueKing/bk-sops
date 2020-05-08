/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="page-view">
        <!-- 搜索 -->
        <van-search
            background="false"
            :placeholder="i18n.placeholder"
            v-model="value"
            class="bk-search"
            @change="search()"
            @clear="search()"
            @search="search()">
        </van-search>
        <!-- 列表 -->
        <section class="bk-block">
            <van-list
                v-model="loading"
                :finished="finished"
                :finished-text="i18n.finishedText"
                :error.sync="error"
                :error-text="i18n.errorText"
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
                            {{ item.create_time }} {{ i18n.to }}
                            <template v-if="item.finish_time">
                                <p>{{ item.finish_time }}</p>
                            </template>
                            <template v-else>
                                --
                            </template>
                        </div>
                    </template>
                    <StatusIcon :status="item['status']"></StatusIcon>
                </van-cell>
            </van-list>
        </section>
    </div>
</template>

<script>
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import StatusIcon from '@/components/MobileStatusIcon/index.vue'

    export default {
        name: 'TaskList',
        components: {
            StatusIcon
        },
        data () {
            return {
                taskList: [],
                originalTaskList: [],
                taskStatus: '',
                loading: false,
                finished: false,
                error: false,
                offset: 0,
                currPage: 1,
                limit: 10,
                total: 0,
                value: '',
                i18n: {
                    placeholder: window.gettext('搜索任务名称'),
                    errorText: window.gettext('请求失败，点击重新加载'),
                    finishedText: window.gettext('没有更多了'),
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
                try {
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
                    this.fillTaskStatus()
                } catch (e) {
                    this.error = true
                    errorHandler(e, this)
                } finally {
                    this.loading = false
                }
            },

            async fillTaskStatus () {
                for (const task of this.taskList) {
                    if (task['is_started'] && !task['is_finished']) {
                        try {
                            const response = await this.getTaskStatus({ id: task.id })
                            this.$set(task, 'status', response.state)
                        } catch (e) {
                            errorHandler(e, this)
                        }
                    } else {
                        if (task['is_finished']) {
                            task['status'] = 'FINISHED'
                        } else {
                            task['status'] = 'CREATED'
                        }
                    }
                }
            },

            search () {
                console.log(this.originalTaskList)
                this.taskList = this.originalTaskList.filter(item => item.name.includes(this.value))
            },

            onClickTask (taskId) {
                this.$store.commit('setTaskId', taskId)
                this.$router.push({ path: `/task/canvas?taskId=${taskId}` })
            }
        }
    }
</script>
