/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="home-page" v-bkloading="{isLoading: loading, opacity: 1}">
        <div v-if="!loading">
            <div class="summary-info">
                <HomeSummary
                    :cc_id="cc_id"
                    :summaryData="summaryData">
                </HomeSummary>
            </div>
            <div class="main-wrapper">
                <QuickCreateTask
                    :cc_id="cc_id"
                    :templateList="templateList"
                    :quickTaskList="quickTaskList"
                    :templateGrouped="templateGrouped"
                    @updateQuickTaskList="updateQuickTaskList">
                </QuickCreateTask>
                <div class="column-panel clearfix">
                    <div class="col-item">
                        <TaskFeeds
                            :top3TaskFeeds="top3TaskFeeds"
                            :cc_id="cc_id">
                        </TaskFeeds>
                    </div>
                    <div class="col-item">
                        <TaskPercentChart :taskCount="taskCount" :totalTask="totalTask"></TaskPercentChart>
                    </div>
                </div>
            </div>
            <CopyrightFooter></CopyrightFooter>
        </div>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapStates, mapMutations, mapActions } from 'vuex'
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
            templateList: [],
            summaryData: {
                executeStatus: {},
                templateStatus: {},
                appmakerStatus: {}
            },
            quickTaskList: [],
            top3TaskFeeds: [],
            taskCount: [],
            totalTask: 0,
            templateClassify: []
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
        ...mapActions('templateList/', [
            'loadTemplateList'
        ]),
        ...mapActions('task/', [
            'loadTaskSummary',
            'loadTaskTop3Data',
            'loadTaskCount'
        ]),
        ...mapActions('taskList/', [
            'loadTaskList'
        ]),
        ...mapMutations('templateList/', [
            'setTemplateListData'
        ]),
        async getData () {
            this.loading = true
            Promise.all([
                this.getTemplateList(),
                this.getTaskTop3Data(),
                this.getTaskCountData(),
                this.getTaskExecuteData()
            ]).then(values => {
                this.handleHomeData(values)
                this.loading = false
            }).catch(e => {
                errorHandler(e, this)
                this.loading = false
            })
        },
        async getTemplateList () {
            try {
                const templateListData = await this.loadTemplateList()
                return templateListData.objects
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
            this.quickTaskList = []
            this.templateList = data[0]
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
            const templateGroup = this.getDefaultGroup(data[2].groups)
            // 收藏常用任务
            data[0].forEach(item => {
                if (item.is_add) {
                    this.quickTaskList.push(item)
                }
                templateGroup[item.category].value += 1
            })
            // 头部概览数据
            this.summaryData = {
                executeStatus: {
                    total: data[3].total,
                    groups: data[3].groups
                },
                templateStatus: {
                    total: data[0].length,
                    groups: data[2].groups.map(item => templateGroup[item.code])
                },
                appmakerStatus: {
                    total: 0,
                    groups: null
                }
            }
            // 任务记录
            this.top3TaskFeeds = data[1]
            this.taskCount = data[2].groups
            this.totalTask = data[2].total
            this.templateGrouped = this.getGroupData(this.templateList, this.templateClassify)
        },
        getGroupData (list, classify) {
            const groupData = []
            classify.forEach(item => {
                groupData.push({
                    code: item.code,
                    name: item.name,
                    list: []
                })
            })
            list.forEach(item => {
                let index
                classify.some((cls, i) => {
                    if (item.category === cls.code) {
                        index = i
                        return true
                    }
                })
                groupData[index].list.push(item)
            })
            return groupData
        },
        updateQuickTaskList (data) {
            this.quickTaskList = data
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.home-page {
    min-width: 1200px;
    min-height: calc(100% -60px);
    background: $whiteMainBg;
}
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


