/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="task-container">
        <div class="list-wrapper">
            <div class="operation-area clearfix">
                <div class="task-category">
                    <span class="category-label">{{i18n.task_type}}:</span>
                    <div class="bk-button-group">
                        <bk-button
                            size="small"
                            :type="activeTaskCategory ? 'default' : 'primary'"
                            @click="onCategoryClick(undefined)">
                            {{i18n.allCategory}}
                        </bk-button>
                        <bk-button
                            size="small"
                            :type="item.value === activeTaskCategory ? 'primary' : 'default'"
                            v-for="item in taskCategory"
                            :key="item.value"
                            @click="onCategoryClick(item.value)">
                            {{item.name}}
                        </bk-button>
                    </div>
                </div>
                <div class="task-search">
                    <input class="search-input" :placeholder="i18n.placeholder" v-model="searchStr" @input="onSearchInput"/>
                    <i class="common-icon-search"></i>
                </div>
            </div>
            <div class="task-table-content">
                <table v-bkloading="{isLoading: listLoading, opacity: 1}">
                    <thead>
                        <tr>
                            <th class="task-id">ID</th>
                            <th class="task-name">{{ i18n.task_name }}</th>
                            <th class="task-time">{{ i18n.start_time }}</th>
                            <th class="task-time">{{ i18n.finish_time }}</th>
                            <th class="task-type">{{ i18n.task_type }}</th>
                            <th class="task-executor">{{ i18n.creator }}</th>
                            <th class="task-executor">{{ i18n.executor }}</th>
                            <th class="task-status">{{ i18n.status }}</th>
                            <th class="task-operation">{{ i18n.operation }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(item, index) in taskList" :key="item.id">
                            <td class="task-id">{{item.id}}</td>
                            <td class="task-name">
                                <router-link
                                    :title="item.name"
                                    :to="`/taskflow/execute/${cc_id}/?instance_id=${item.id}`">
                                    {{item.name}}
                                </router-link>
                            </td>
                            <td class="task-time">{{item.start_time || '--'}}</td>
                            <td class="task-time">{{item.finish_time || '--'}}</td>
                            <td class="task-type">{{item.category_name}}</td>
                            <td class="task-executor">{{item.creator_name}}</td>
                            <td class="task-executor">{{item.executor_name || '--'}}</td>
                            <td
                                :class="['task-status', executeStatus[index] && executeStatus[index].cls]">
                                <template v-if="executeStatus[index]">
                                    <template v-if="executeStatus[index].cls === 'loading'">
                                        <i class="common-icon-loading"></i>
                                    </template>
                                    <template v-else>{{executeStatus[index].text}}</template>
                                </template>
                            </td>
                            <td class="task-operation">
                                <bk-button type="primary" size="mini" @click="onCloneTask(item.id)">{{ i18n.clone }}</bk-button>
                                <bk-button type="danger" size="mini" @click="onDeleteTask(item.id)">{{ i18n.delete }}</bk-button>
                            </td>
                        </tr>
                        <tr v-if="!taskList || !taskList.length" class="empty-tr">
                            <td colspan="9">
                                <div class="empty-data"><NoData/></div>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <div class="panagation" v-if="totalPage > 1">
                    <div class="page-info">
                        <span> {{i18n.total}} {{totalCount}} {{i18n.item}}{{i18n.comma}} {{i18n.currentPageTip}} {{currentPage}} {{i18n.page}}</span>
                    </div>
                    <bk-paging
                        :cur-page.sync="currentPage"
                        :total-page="totalPage"
                        @page-change="onPageChange">
                    </bk-paging>
                </div>
            </div>
        </div>
        <CopyrightFooter></CopyrightFooter>
        <bk-dialog
            :quick-close="false"
            :has-header="true"
            :ext-cls="'common-dialog'"
            :title="i18n.delete"
            width="400"
            padding="30px"
            :is-show.sync="isDeleteDialogShow"
            @confirm="onDeleteConfirm"
            @cancel="onDeleteCancel">
            <div slot="content">{{i18n.deleleTip}}</div>
        </bk-dialog>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapMutations, mapActions } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import toolsUtils from '@/utils/tools.js'
import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
import NoData from '@/components/common/base/NoData.vue'

export default {
    name: 'TaskList',
    components: {
        CopyrightFooter,
        NoData
    },
    props: ['cc_id'],
    data () {
        return {
            i18n: {
                allCategory: gettext("全部"),
                placeholder: gettext("请输入ID或任务名称"),
                task_list: gettext("任务记录"),
                task_name: gettext("任务名称"),
                start_time: gettext("执行开始"),
                finish_time: gettext("执行结束"),
                task_type: gettext("任务分类"),
                creator: gettext("创建人"),
                executor: gettext("执行人"),
                status: gettext("状态"),
                operation: gettext("操作"),
                clone: gettext("克隆"),
                delete: gettext("删除"),
                deleleTip: gettext("确认删除该任务？"),
                total: gettext("共"),
                item: gettext("条记录"),
                comma: gettext("，"),
                currentPageTip: gettext("当前第"),
                page: gettext("页")
            },
            listLoading: true,
            templateId: this.$route.query.template_id,
            taskCategory: [],
            activeTaskCategory: undefined, // 任务类型筛选
            searchStr: '',
            executeStatus: [], // 任务执行状态
            currentPage: 1,
            totalPage: 1,
            countPerPage: 15,
            totalCount: 0,
            isDeleteDialogShow: false,
            theDeleteTaskId: undefined,
            pending: {
                delete: false
            }
        }
    },
    computed: {
        ...mapState({
            taskList: state => state.taskList.taskListData
        })
    },
    created () {
        this.getTaskList()
        this.getBizBaseInfo()
        this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
    },
    methods: {
        ...mapActions('template/', [
            'loadBusinessBaseInfo'
        ]),
        ...mapActions('task/', [
            'getInstanceStatus'
        ]),
        ...mapActions('taskList/', [
            'loadTaskList',
            'deleteTask',
            'cloneTask'
        ]),
        ...mapMutations('template/', [
            'setBusinessBaseInfo'
        ]),
        ...mapMutations('taskList/', [
            'setTaskListData'
        ]),
        async getTaskList () {
            this.listLoading = true
            this.executeStatus = []
            try {
                const data = {
                    limit: this.countPerPage,
                    offset: (this.currentPage - 1) * this.countPerPage,
                    category: this.activeTaskCategory,
                    template_id: this.templateId,
                    q: this.searchStr
                }
                const taskListData = await this.loadTaskList(data)
                const list = taskListData.objects
                this.totalCount = taskListData.meta.total_count
                const totalPage = Math.ceil( this.totalCount / this.countPerPage)
                if (!totalPage) {
                    this.totalPage = 1
                } else {
                    this.totalPage = totalPage
                }
                this.executeStatus = list.map((item, index) => {
                    const status = {}
                    if (item.is_finished) {
                        status.cls = 'finished'
                        status.text = gettext('完成')
                    } else if (item.is_started) {
                        status.cls = 'loading'
                        this.getExecuteDetail(item, index)
                    } else {
                        status.cls = 'created'
                        status.text = gettext('未执行')
                    }
                    return status
                })
                this.setTaskListData(list)
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.listLoading = false
            }
        },
        async getExecuteDetail (task, index) {
            try {
                const detailInfo = await this.getInstanceStatus(task.id)
                if (detailInfo.result) {
                    const state = detailInfo.data.state
                    const status = {}
                    switch (state) {
                        case 'RUNNING':
                        case 'BLOCKED':
                            status.cls = 'execute'
                            status.text = gettext('执行中')
                            break
                        case 'SUSPENDED':
                            status.cls = 'execute'
                            status.text = gettext('暂停')
                            break
                        case 'NODE_SUSPENDED':
                            status.cls = 'execute'
                            status.text = gettext('节点暂停')
                            break
                        case 'FAILED':
                            status.cls = 'failed'
                            status.text = gettext('失败')
                            break
                        case 'REVOKED':
                            status.cls = 'revoke'
                            status.text = gettext('撤销')
                            break
                        default:
                            status.text = gettext('未知')
                    }
                    this.executeStatus.splice(index, 1, status)
                } else {
                    errorHandler(detailInfo, this)
                }
            } catch (e) {
                errorHandler(e, this)
            }
        },
        async getBizBaseInfo () {
            try {
                const bizBasicInfo = await this.loadBusinessBaseInfo()
                this.taskCategory = bizBasicInfo.task_categories
                this.setBusinessBaseInfo(bizBasicInfo)
            } catch (e) {
                errorHandler(e, this)
            }
        },
        onCategoryClick (category) {
            this.activeTaskCategory = category
            this.currentPage = 1
            this.getTaskList()
        },
        searchInputhandler () {
            this.currentPage = 1
            this.getTaskList(this.searchStr)
        },
        onDeleteTask (id) {
            this.theDeleteTaskId = id
            this.isDeleteDialogShow = true
        },
        async onCloneTask (id) {
            try {
                const data = await this.cloneTask(id)
                this.$router.push({path: `/taskflow/execute/${this.cc_id}/`, query: {instance_id: data.data.new_instance_id}})
            } catch (e) {
                errorHandler(e, this)
            }
        },
        onPageChange (page) {
            this.currentPage = page
            this.getTaskList()
        },
        async onDeleteConfirm () {
            if (this.pending.delete) return
            this.pending.delete = true
            try {
                await this.deleteTask(this.theDeleteTaskId)
                this.theDeleteTaskId = undefined
                this.isDeleteDialogShow = false
                await this.getTaskList()
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.pending.delete = false
            }
        },
        onDeleteCancel () {
            this.theDeleteTaskId = undefined
            this.isDeleteDialogShow = false
        }
    }
}
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
.task-container {
    padding-top: 20px;
    min-width: 1320px;
    min-height: calc(100% - 60px);
    background: #fafafa;
}
.list-wrapper {
    padding: 0 60px;
}
.operation-area {
    margin: 20px 0;
    .task-category {
        float: left;
        font-size: 14px;
        vertical-align: middle;
        .category-label {
            float: left;
            margin-right: 8px;
            height: 32px;
            line-height: 32px;
        }
    }
    .create-task {
        float: right;
        margin-bottom: 20px;
    }
    .task-search {
        float: right;
        position: relative;
    }
    .search-input {
        padding: 0 40px 0 10px;
        width: 300px;
        height: 36px;
        line-height: 36px;
        font-size: 14px;
        background: $whiteDefault;
        border: 1px solid $commonBorderColor;
        border-radius: 4px;
        outline: none;
        &:hover {
            border-color: #c0c4cc;
        }
        &:focus {
            border-color: $blueDefault;
            & + i {
                color: $blueDefault;
            }
        }
    }
    .common-icon-search {
        position: absolute;
        right: 15px;
        top: 11px;
        color: $commonBorderColor;
    }
}
.task-table-content {
    table {
        width: 100%;
        border: 1px solid #ebebeb;
        border-collapse: collapse;
        font-size: 14px;
        background: $whiteDefault;
        table-layout: fixed;
        tr:not(.empty-tr):hover {
            background: #fafafa;
        }
        th,td {
            padding: 10px;
            text-align: center;
            border: 1px solid #ebebeb;
        }
        th {
            background: #fafafa;
        }
        .task-id {
            width: 80px;
        }
        .task-name {
            text-align: left;
            a {
                display: block;
                width: 100%;
                color: #3c96ff;
                text-overflow: ellipsis;
                white-space: nowrap;
                word-break: break-all;
                overflow: hidden;
            }
        }
        .task-time {
            width: 220px;
        }
        .task-type {
            width: 110px;
        }
        .task-executor {
            width: 110px;
        }
        .task-status {
            width: 84px;
            &.created {
                color: $blueDefault;
            }
            &.execute {
                color: $yellowDefault;
            }
            &.finished {
                color: $greenDefault;
            }
            &.failed {
                color: $redDefault;
            }
            &.revoke {
                color: $blueDisable;
            }
            .common-icon-loading {
                display: inline-block;
                animation: bk-button-loading 1.4s infinite linear;
            }
            @keyframes bk-button-loading {
                from {
                    -webkit-transform: rotate(0);
                    transform: rotate(0); }
                to {
                    -webkit-transform: rotate(360deg);
                    transform: rotate(360deg);
                }
            }
        }
        .task-operation {
            width: 150px;
        }
    }
    .empty-data {
        padding: 120px 0;
    }
}
.panagation {
    margin-top: 20px;
    text-align: right;
    .page-info {
        float: left;
        margin-top: 10px;
        font-size: 14px;
    }
}
</style>
