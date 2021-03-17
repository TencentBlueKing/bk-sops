/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="page-view">
        <!-- 任务信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">{{ i18n.taskInfo }}</h2>
            <div class="bk-text-list">
                <van-cell :title="i18n.taskName" :value="task.name" />
            </div>
        </section>
        <!-- 参数信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">{{ i18n.paramInfo }}</h2>
            <div class="bk-text-list">
                <template v-if="Object.keys(constants).length">
                    <template v-for="item in constants">
                        <van-cell
                            :key="item.id"
                            :title="item.name"
                            :value="item.value">
                            {{ item.value }}
                        </van-cell>
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
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'TaskDetail',
        data () {
            return {
                task: {},
                constants: {},
                i18n: {
                    noData: window.gettext('暂无数据'),
                    taskInfo: window.gettext('任务信息'),
                    taskName: window.gettext('任务名称'),
                    paramInfo: window.gettext('参数信息'),
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
                try {
                    this.task = await this.getTask({ id: this.$route.query.taskId })
                    const pipelineTree = JSON.parse(this.task.pipeline_tree)
                    this.constants = pipelineTree.constants
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.$toast.clear()
                }
            }
        }
    }
</script>
