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
    <div class="search-result">
        <div class="search-input">
            <bk-input v-model="searchStr" right-icon="bk-icon icon-search" @enter="onSearch"></bk-input>
        </div>
        <div class="result-wrapper" v-bkloading="{ isLoading: searchLoading, opacity: 1 }">
            <div class="result-title">
                <h3>{{ i18n.resultTitle }}</h3>
                <span>{{ i18n.find }}</span>{{ matchedList.length }}<span>{{ i18n.result }}</span>
            </div>
            <template v-if="matchedList.length">
                <div class="list-table template-list-table">
                    <bk-table
                        v-bkloading="{ isLoading: tplDataLoading, opacity: 1 }"
                        :data="tplData"
                        :pagination="tplPagination"
                        @sort-change="handleSortChange($event, 'tpl')"
                        @page-change="handlePageChange($event, 'tpl')">
                        <bk-table-column
                            v-for="col in tplListColumn"
                            :key="col.props"
                            :label="col.label"
                            :prop="col.prop"
                            :width="col.hasOwnProperty('width') ? col.width : 'auto'"
                            :sortable="col.sortable">
                            <template slot-scope="props">
                                <template v-if="col.prop === 'name'">
                                    <span
                                        v-if="!hasPermission(['view'], props.row.auth_actions, tplOperations)"
                                        v-cursor="{ active: true }"
                                        class="text-permission-disable"
                                        @click="onApplyPerm(['view'], props.row, 'tpl')">
                                        {{props.row.name}}
                                    </span>
                                    <a
                                        v-else
                                        class="table-link"
                                        target="_blank"
                                        :title="props.row.name"
                                        :href="`${site_url}template/edit/${props.row.project.id}/?template_id=${props.row.id}`">
                                        {{props.row.name}}
                                    </a>
                                </template>
                                <template v-else-if="col.prop === 'projectName'">
                                    <span :title="props.row[col.prop]">{{ props.row.project.name }}</span>
                                </template>
                                <template v-else-if="col.prop === 'is_deleted'">
                                    <span>{{ props.row.is_deleted ? i18n.yes : i18n.no }}</span>
                                </template>
                                <template v-else-if="col.prop === 'operation'">
                                    <span
                                        v-if="props.row.is_deleted"
                                        v-cursor="{ active: !hasPermission(['delete'], props.row.auth_actions, tplOperations) }"
                                        :class="['table-link', {
                                            'text-permission-disable': !hasPermission(['delete'], props.row.auth_actions, tplOperations)
                                        }]"
                                        @click="onRestoreTemplate(props.row)">
                                        {{ i18n.restore }}
                                    </span>
                                    <template v-else>
                                        <span
                                            v-if="!hasPermission(['edit'], props.row.auth_actions, tplOperations)"
                                            v-cursor="{ active: true }"
                                            class="text-permission-disable"
                                            @click="onApplyPerm(['edit'], props.row, 'tpl')">
                                            {{i18n.edit}}
                                        </span>
                                        <a
                                            v-else
                                            class="table-link"
                                            target="_blank"
                                            :href="`${site_url}template/edit/${props.row.project.id}/?template_id=${props.row.id}`">
                                            {{ i18n.edit }}
                                        </a>
                                    </template>
                                </template>
                                <template v-else :title="props.row[col.prop]">{{ props.row[col.prop] }}</template>
                            </template>
                        </bk-table-column>
                    </bk-table>
                </div>
                <div class="list-table task-list-table">
                    <bk-table
                        v-bkloading="{ isLoading: taskDataLoading, opacity: 1 }"
                        :data="taskData"
                        :pagination="taskPagination"
                        @sort-change="handleSortChange($event, 'task')"
                        @page-change="handlePageChange($event, 'task')">
                        <bk-table-column
                            v-for="col in taskListColumn"
                            :key="col.props"
                            :label="col.label"
                            :prop="col.prop"
                            :width="col.hasOwnProperty('width') ? col.width : 'auto'"
                            :sortable="col.sortable">
                            <template slot-scope="props">
                                <template v-if="col.prop === 'name'">
                                    <span
                                        v-if="!hasPermission(['view'], props.row.auth_actions, taskOperations)"
                                        v-cursor="{ active: true }"
                                        class="text-permission-disable"
                                        @click="onApplyPerm(['view'], props.row, 'task')">
                                        {{props.row.name}}
                                    </span>
                                    <a
                                        v-else
                                        class="table-link"
                                        target="_blank"
                                        :title="props.row.name"
                                        :href="`${site_url}taskflow/execute/${props.row.project.id}/?instance_id=${props.row.id}`">
                                        {{props.row.name}}
                                    </a>
                                </template>
                                <template v-else-if="col.prop === 'projectName'">
                                    <span :title="props.row[col.prop]">{{ props.row.project.name }}</span>
                                </template>
                                <template v-else-if="['start_time', 'finish_time', 'executor_name'].includes(col.prop)">
                                    <span :title="props.row[col.prop]">{{ props.row[col.prop] || '--' }}</span>
                                </template>
                                <template v-else-if="col.prop === 'status'">
                                    <div class="task-status">
                                        <span :class="executeStatus[props.$index] && executeStatus[props.$index].cls"></span>
                                        <span v-if="executeStatus[props.$index]" class="task-status-text">{{executeStatus[props.$index].text}}</span>
                                    </div>
                                </template>
                                <template v-else :title="props.row[col.prop]">{{ props.row[col.prop] }}</template>
                            </template>
                        </bk-table-column>
                    </bk-table>
                </div>
            </template>
            <div v-else class="no-data-matched" slot="empty"><NoData :message="i18n.empty" /></div>
        </div>
        <bk-dialog
            width="400"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :header-position="'left'"
            :title="i18n.restore"
            :value="isRestoreDialogShow"
            :loading="restorePending"
            @confirm="onRestoreConfirm"
            @cancel="isRestoreDialogShow = false">
            <div class="dialog-content">
                {{i18n.restoreTip + '"' + restoreData.name + '"?'}}
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import { mapActions, mapState } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import permission from '@/mixins/permission.js'
    import NoData from '@/components/common/base/NoData.vue'

    const TEMPLATE_TABLE_COLUMN = [
        {
            label: gettext('ID'),
            prop: 'id',
            sortable: true,
            width: 100
        },
        {
            label: gettext('流程名称'),
            prop: 'name'
        },
        {
            label: gettext('项目'),
            prop: 'projectName',
            width: 200
        },
        {
            label: gettext('更新时间'),
            prop: 'edit_time',
            width: 200
        },
        {
            label: gettext('是否已删除'),
            prop: 'is_deleted',
            width: 100
        },
        {
            label: gettext('操作'),
            prop: 'operation',
            width: 100
        }
    ]

    const TASK_TABLE_COLUMN = [
        {
            label: gettext('ID'),
            prop: 'id',
            sortable: true,
            width: 90
        },
        {
            label: gettext('任务名称'),
            prop: 'name'
        },
        {
            label: gettext('项目'),
            prop: 'projectName'
        },
        {
            label: gettext('执行开始'),
            prop: 'start_time',
            width: 200
        },
        {
            label: gettext('执行结束'),
            prop: 'finish_time',
            width: 200
        },
        {
            label: gettext('创建人'),
            prop: 'creator_name',
            width: 100
        },
        {
            label: gettext('执行人'),
            prop: 'executor_name',
            width: 100
        },
        {
            label: gettext('创建方式'),
            prop: 'create_method',
            width: 100
        },
        {
            label: gettext('状态'),
            prop: 'status',
            width: 100
        }
    ]

    export default {
        name: 'SearchResult',
        components: {
            NoData
        },
        mixins: [permission],
        props: {
            keyword: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                searchStr: this.keyword,
                searchLoading: true,
                tplListColumn: TEMPLATE_TABLE_COLUMN,
                taskListColumn: TASK_TABLE_COLUMN,
                tplDataLoading: false,
                taskDataLoading: false,
                matchedList: [],
                tplFilter: {},
                tplOperations: [],
                tplResource: {},
                taskFilter: {},
                tplData: [],
                taskData: [],
                executeStatus: [],
                taskOperations: [],
                taskResource: {},
                isRestoreDialogShow: false,
                restoreData: {},
                restorePending: false,
                tplPagination: {
                    current: 1,
                    count: 0,
                    'limit-list': [15],
                    'show-limit': false,
                    limit: 15
                },
                taskPagination: {
                    current: 1,
                    count: 0,
                    'limit-list': [15],
                    'show-limit': false,
                    limit: 15
                },
                i18n: {
                    resultTitle: gettext('搜索结果'),
                    find: gettext('找到'),
                    result: gettext('条结果'),
                    empty: gettext('没有找到相关内容'),
                    yes: gettext('是'),
                    no: gettext('否'),
                    restore: gettext('恢复模板'),
                    edit: gettext('编辑'),
                    restoreTip: gettext('确认恢复')
                }
            }
        },
        computed: {
            ...mapState({
                site_url: state => state.site_url
            })
        },
        created () {
            this.getSearchResult()
        },
        methods: {
            ...mapActions('task/', [
                'getInstanceStatus'
            ]),
            ...mapActions('admin/', [
                'search',
                'template',
                'templateRestore',
                'taskflow'
            ]),
            async getSearchResult () {
                try {
                    this.searchLoading = true
                    const res = await this.search({ keyword: this.searchStr })
                    if (res.result) {
                        this.matchedList = res.data.matched
                        this.tplFilter = this.matchedList.find(item => item => item.type === 'flow')
                        this.taskFilter = this.matchedList.find(item => item => item.type === 'taskflow')
                        if (this.tplFilter) {
                            this.getAdminTemplate()
                        }
                        if (this.taskFilter) {
                            this.getAdminTask()
                        }
                    } else {
                        errorHandler(res, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.searchLoading = false
                }
            },
            async getAdminTemplate () {
                try {
                    this.tplDataLoading = true
                    const params = {
                        limit: this.tplPagination.limit,
                        offset: (this.tplPagination.current - 1) * this.tplPagination.limit,
                        ...this.tplFilter.filter
                    }
                    const res = await this.template(params)
                    this.tplData = res.objects
                    this.tplOperations = res.meta.auth_operations
                    this.tplResource = res.meta.auth_resource
                    this.tplPagination.count = res.meta.total_count
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.tplDataLoading = false
                }
            },
            async getAdminTask () {
                try {
                    this.taskDataLoading = true
                    const params = {
                        limit: this.taskPagination.limit,
                        offset: (this.taskPagination.current - 1) * this.taskPagination.limit,
                        ...this.taskFilter.filter
                    }
                    const res = await this.taskflow(params)
                    this.taskData = res.objects
                    this.taskOperations = res.meta.auth_operations
                    this.taskResource = res.meta.auth_resource
                    this.taskPagination.count = res.meta.total_count
                    this.executeStatus = res.objects.map((item, index) => {
                        const status = {}
                        
                        if (item.is_finished) {
                            status.cls = 'finished bk-icon icon-check-circle-shape'
                            status.text = gettext('完成')
                        } else if (item.is_revoked) {
                            status.cls = 'revoke common-icon-dark-circle-shape'
                            status.text = gettext('撤销')
                        } else if (item.is_started) {
                            status.cls = 'loading common-icon-loading'
                            this.getExecuteDetail(item, index)
                        } else {
                            status.cls = 'created common-icon-dark-circle-shape'
                            status.text = gettext('未执行')
                        }
                        return status
                    })
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.taskDataLoading = false
                }
            },
            async getExecuteDetail (task, index) {
                const data = {
                    instance_id: task.id,
                    project_id: task.project.id
                }
                try {
                    const detailInfo = await this.getInstanceStatus(data)
                    if (detailInfo.result) {
                        const state = detailInfo.data.state
                        const status = {}
                        switch (state) {
                            case 'RUNNING':
                            case 'BLOCKED':
                                status.cls = 'running common-icon-dark-circle-ellipsis'
                                status.text = gettext('执行中')
                                break
                            case 'SUSPENDED':
                                status.cls = 'execute common-icon-dark-circle-pause'
                                status.text = gettext('暂停')
                                break
                            case 'NODE_SUSPENDED':
                                status.cls = 'execute common-icon-dark-circle-pause'
                                status.text = gettext('节点暂停')
                                break
                            case 'FAILED':
                                status.cls = 'failed common-icon-dark-circle-close'
                                status.text = gettext('失败')
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
            onSearch () {
                this.getSearchResult()
            },
            onApplyPerm (required, data, type) {
                const operations = type === 'tpl' ? this.tplOperations : this.taskOperations
                const resource = type === 'tpl' ? this.tplResource : this.taskResource
                this.applyForPermission(required, data, operations, resource)
            },
            onRestoreTemplate (tpl) {
                if (this.hasPermission(['delete'], tpl.auth_actions, this.tplOperations)) {
                    this.isRestoreDialogShow = true
                    this.restoreData = tpl
                } else {
                    this.onApplyPerm(['delete'], tpl, 'tpl')
                }
            },
            async onRestoreConfirm () {
                if (this.restorePending) {
                    return
                }
                try {
                    this.restorePending = true
                    const data = { template_id: this.restoreData.id }
                    const resp = await this.templateRestore(data)
                    if (resp.result) {
                        this.isRestoreDialogShow = false
                        this.getAdminTemplate()
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.restorePending = false
                }
            },
            handleSortChange () {},
            handlePageChange (val, type) {
                if (type === 'tpl') {
                    this.tplPagination.current = val
                    this.getAdminTemplate()
                } else {
                    this.taskPagination.current = val
                    this.getAdminTask()
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/config.scss';

    .search-result {
        margin: 0 60px;
        padding: 20px 0 40px;
    }
    .search-input {
        margin-bottom: 20px;
        width: 360px;
        color: #313238;
    }
    .result-title {
        font-size: 14px;
        color: #c4c6cc;
        & > h3 {
            margin: 0 12px 0 0;
            display: inline-block;
            color: #313238;
            font-size: 14px;
        }
    }
    .list-table {
        margin-top: 20px;
        background: #ffffff;
        .table-link {
            color: #3a84ff;
            cursor: pointer;
        }
        .task-status {
            width: 105px;
            text-align: left;
            .common-icon-dark-circle-shape {
                display: inline-block;
                font-size: 14px;
                color: #979BA5;
                vertical-align: middle;
            }
            .common-icon-dark-circle-ellipsis {
                color: #3c96ff;
                font-size: 14px;
                vertical-align: middle;
            }
            .icon-check-circle-shape {
                font-size: 14px;
                color: $greenDefault;
                vertical-align: middle;
            }
            .common-icon-dark-circle-close {
                color: $redDefault;
                font-size: 14px;
                vertical-align: middle;
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
            .task-status-text {
                display: inline-block;
                vertical-align: middle;
            }
        }
    }
    .no-data-matched {
        padding: 30px 0;
        .no-data-wrapper {
            padding: 50px 0;
        }
    }
    .dialog-content {
        padding: 30px;
        word-break: break-all;
    }
</style>
