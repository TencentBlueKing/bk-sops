/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="home-page">
        <div v-bkloading="{ isLoading: loading, opacity: 1 }">
            <div class="summary-info">
                <HomeSummary
                    :cc_id="cc_id"
                    :summary-data="summaryData">
                </HomeSummary>
            </div>
            <div class="main-wrapper">
                <QuickCreateTask
                    v-if="!loading"
                    :cc_id="cc_id"
                    :quick-task-list="quickTaskList"
                    :template-classify="templateClassify"
                    :total-template="totalTemplate"
                    @updateQuickTaskList="updateQuickTaskList">
                </QuickCreateTask>
                <div class="column-panel clearfix">
                    <div class="col-item">
                        <TaskFeeds
                            v-if="!loading"
                            :top-three-task-feeds="topThreeTaskFeeds"
                            :cc_id="cc_id">
                        </TaskFeeds>
                    </div>
                    <div class="col-item">
                        <TaskPercentChart
                            v-if="!loading"
                            :task-count="taskCount"
                            :total-task="totalTask">
                        </TaskPercentChart>
                    </div>
                </div>
            </div>
            <CopyrightFooter></CopyrightFooter>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import { errorHandler } from '@/utils/errorHandler.js'
    import HomeSummary from './HomeSummary.vue'
    import QuickCreateTask from './QuickCreateTask.vue'
    import TaskFeeds from './TaskFeeds.vue'
    import TaskPercentChart from './TaskPercentChart.vue'

    export default {
        name: 'HomePage',
        components: {
            CopyrightFooter,
            HomeSummary,
            QuickCreateTask,
            TaskFeeds,
            TaskPercentChart
        },
        props: ['cc_id', 'template_id'],
        data () {
            return {
                loading: true,
                summaryData: {
                    executeStatus: {},
                    templateStatus: {},
                    appmakerStatus: {}
                },
                quickTaskList: [],
                topThreeTaskFeeds: [],
                taskCount: [],
                totalTask: 0,
                templateClassify: [],
                totalTemplate: 0
            }
        },
        watch: {
            'cc_id' (val) {
                this.getData()
            }
        },
        created () {
            this.getData()
        },
        methods: {
            ...mapActions('template/', [
                'loadTemplateSummary',
                'loadTemplateCollectList'
            ]),
            ...mapActions('appmaker/', [
                'loadAppmakerSummary'
            ]),
            ...mapActions('task/', [
                'loadTaskSummary',
                'loadTaskTop3Data',
                'loadTaskCount'
            ]),
            ...mapActions('taskList/', [
                'loadTaskList'
            ]),
            async getData () {
                this.loading = true
                Promise.all([
                    this.getAppmakerSummary(),
                    this.getTaskTop3Data(),
                    this.getTaskCountData(),
                    this.getTaskExecuteData(),
                    this.getTemplateCategorySummary(),
                    this.getTemplateCollectList()
                ]).then(values => {
                    this.handleHomeData(values)
                    this.loading = false
                }).catch(e => {
                    errorHandler(e, this)
                    this.loading = false
                })
            },
            async getAppmakerSummary () {
                const query = {
                    groupBy: 'category'
                }
                try {
                    const appmakerData = await this.loadAppmakerSummary(query)
                    return appmakerData.data
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            async getTaskTop3Data () {
                try {
                    const query = {
                        limit: 3
                    }
                    const taskTop3Data = await this.loadTaskList(query)
                    return taskTop3Data.objects
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            async getTaskCountData () {
                const query = {
                    group_by: 'category'
                }
                try {
                    const taskCountData = await this.loadTaskCount(query)
                    if (taskCountData.result) {
                        return taskCountData.data
                    } else {
                        errorHandler(taskCountData, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            async getTaskExecuteData () {
                const query = {
                    group_by: 'status'
                }
                try {
                    const taskCountData = await this.loadTaskCount(query)
                    if (taskCountData.result) {
                        return taskCountData.data
                    } else {
                        errorHandler(taskCountData, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            /**
             * 流程统计
             */
            async getTemplateCategorySummary () {
                const query = {
                    groupBy: 'category'
                }
                try {
                    const categoryData = await this.loadTemplateSummary(query)
                    if (categoryData.result) {
                        return categoryData.data
                    } else {
                        errorHandler(categoryData, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            /**
             * 用户收藏的模板
             */
            async getTemplateCollectList () {
                try {
                    const collectListData = await this.loadTemplateCollectList()
                    if (collectListData.result) {
                        return collectListData.data
                    } else {
                        errorHandler(collectListData, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            /**
             * 默认流程模板分类数据
             */
            getDefaultGroup (list) {
                const groupDefaultData = {}
                list.forEach(item => {
                    groupDefaultData[item.code] = {
                        name: gettext(item.name),
                        value: 0
                    }
                })
                return groupDefaultData
            },
            handleHomeData (data) {
                this.templateClassify = []
                this.quickTaskList = data[5]
                data[2].groups.forEach(item => {
                    item.name = gettext(item.name)
                    this.templateClassify.push({
                        code: item.code,
                        name: item.name
                    })
                })
                data[3].groups.forEach(item => {
                    item.name = gettext(item.name)
                })
                // 头部概览数据
                this.summaryData = {
                    executeStatus: {
                        total: data[3].total,
                        groups: data[3].groups
                    },
                    templateStatus: {
                        total: data[4].total,
                        groups: data[4].groups
                    },
                    appmakerStatus: {
                        total: data[0].total,
                        groups: data[0].groups
                    }
                }
                // 任务的数量
                this.totalTemplate = data[4].total
                // 任务记录
                this.topThreeTaskFeeds = data[1]
                this.taskCount = data[2].groups
                this.totalTask = data[2].total
            },
            updateQuickTaskList (data) {
                this.quickTaskList = data
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.summary-info {
    background: #2b74c6;
    background: linear-gradient(to bottom, #2b74ca, #289dce);
}
.main-wrapper {
    width: 1200px;
    margin: 0 auto;
}
.col-item {
    float: left;
    margin-right: 20px;
    width: 590px;
    height: 480px;
    border: 1px solid $commonBorderColor;
    border-radius: 2px;
    box-shadow: -1px 1px 8px rgba(180, 180, 180, .15), 1px -1px 8px rgba(180, 180, 180, .15);
    background: $whiteDefault;
    vertical-align: top;
    &:nth-child(2n) {
        margin-right: 0;
    }
}
</style>
