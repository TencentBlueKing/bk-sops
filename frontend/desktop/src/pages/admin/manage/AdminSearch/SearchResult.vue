/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="search-result" data-test-id="adminMessage_form_searchResult">
        <div class="search-input">
            <bk-input v-model.trim="searchStr" right-icon="bk-icon icon-search" @enter="onSearch"></bk-input>
        </div>
        <div class="result-wrapper" v-bkloading="{ isLoading: searchLoading, opacity: 1, zIndex: 100 }">
            <div class="result-title">
                <h3>{{ $t('搜索结果') }}</h3>
                <span>{{ $t('找到') }}</span>{{ searchResultTotal }}<span>{{ $t('条结果') }}</span>
            </div>
            <template v-if="matchedList.length">
                <div class="list-table template-list-table" v-if="tplDataLoading || tplData.length">
                    <bk-table
                        v-bkloading="{ isLoading: tplDataLoading, opacity: 1, zIndex: 100 }"
                        :data="tplData"
                        :pagination="tplPagination"
                        @page-change="handlePageChange($event, 'tpl')"
                        @page-limit-change="handlePageLimitChange($event, 'tpl')">
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
                                        v-if="!hasPermission(['flow_view'], props.row.auth_actions)"
                                        v-cursor="{ active: true }"
                                        class="text-permission-disable"
                                        @click="onApplyPerm(['flow_view'], props.row, 'tpl')">
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
                                    <span>{{ props.row.is_deleted ? $t('是') : $t('否') }}</span>
                                </template>
                                <template v-else-if="col.prop === 'operation'">
                                    <span
                                        v-if="props.row.is_deleted"
                                        :class="['table-link', { 'text-permission-disable': !hasEditPerm }]"
                                        v-cursor="{ active: !hasEditPerm }"
                                        @click="onRestoreTemplate(props.row)">
                                        {{ $t('恢复模板') }}
                                    </span>
                                    <template v-else>
                                        <span
                                            v-if="!hasPermission(['flow_edit'], props.row.auth_actions)"
                                            v-cursor="{ active: true }"
                                            class="text-permission-disable"
                                            @click="onApplyPerm(['flow_edit'], props.row, 'tpl')">
                                            {{$t('编辑')}}
                                        </span>
                                        <a
                                            v-else
                                            class="table-link"
                                            target="_blank"
                                            :href="`${site_url}template/edit/${props.row.project.id}/?template_id=${props.row.id}`">
                                            {{ $t('编辑') }}
                                        </a>
                                    </template>
                                </template>
                                <template v-else :title="props.row[col.prop]">{{ props.row[col.prop] }}</template>
                            </template>
                        </bk-table-column>
                        <div slot="empty"><no-data></no-data></div>
                    </bk-table>
                </div>
                <div class="list-table task-list-table" v-if="taskDataLoading || taskData.length">
                    <bk-table
                        v-bkloading="{ isLoading: taskDataLoading, opacity: 1, zIndex: 100 }"
                        :data="taskData"
                        :pagination="taskPagination"
                        @page-change="handlePageChange($event, 'task')"
                        @page-limit-change="handlePageLimitChange($event, 'task')">
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
                                        v-if="!hasPermission(['task_view'], props.row.auth_actions, taskOperations)"
                                        v-cursor="{ active: true }"
                                        class="text-permission-disable"
                                        @click="onApplyPerm(['task_view'], props.row, 'task')">
                                        {{props.row.name}}
                                    </span>
                                    <a
                                        v-else
                                        class="table-link"
                                        target="_blank"
                                        :title="props.row.name"
                                        :href="`${site_url}taskflow/execute/${props.row.project.id}/?instance_id=${props.row.id}&is_admin=true`">
                                        {{props.row.name}}
                                    </a>
                                </template>
                                <template v-else-if="col.prop === 'projectName'">
                                    <span :title="props.row[col.prop]">{{ props.row.project.name }}</span>
                                </template>
                                <template v-else-if="['start_time', 'finish_time', 'executor_name'].includes(col.prop)">
                                    <span :title="props.row[col.prop]">{{ props.row[col.prop] || '--' }}</span>
                                </template>
                                <template v-else-if="col.prop === 'create_method'">
                                    <span>{{ methodList[props.row.create_method] || props.row.create_method }}</span>
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
                        <div slot="empty"><no-data></no-data></div>
                    </bk-table>
                </div>
            </template>
            <div v-else class="no-data-matched" slot="empty"><no-data :message="$t('没有找到相关内容')"></no-data></div>
        </div>
        <bk-dialog
            width="400"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :header-position="'left'"
            :title="$t('恢复模板')"
            :value="isRestoreDialogShow"
            :loading="restorePending"
            @confirm="onRestoreConfirm"
            @cancel="isRestoreDialogShow = false">
            <div class="dialog-content">
                {{$t('确认恢复') + '"' + restoreData.name + '"?'}}
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapState } from 'vuex'
    import permission from '@/mixins/permission.js'
    import NoData from '@/components/common/base/NoData.vue'

    const TEMPLATE_TABLE_COLUMN = [
        {
            label: i18n.t('ID'),
            prop: 'id',
            width: 100
        },
        {
            label: i18n.t('流程名称'),
            prop: 'name'
        },
        {
            label: i18n.t('项目'),
            prop: 'projectName',
            width: 200
        },
        {
            label: i18n.t('更新时间'),
            prop: 'edit_time',
            width: 200
        },
        {
            label: i18n.t('创建时间'),
            prop: 'create_time',
            width: 200
        },
        {
            label: i18n.t('是否已删除'),
            prop: 'is_deleted',
            width: 100
        },
        {
            label: i18n.t('操作'),
            prop: 'operation',
            width: 100
        }
    ]

    const TASK_TABLE_COLUMN = [
        {
            label: i18n.t('ID'),
            prop: 'id',
            width: 90
        },
        {
            label: i18n.t('任务名称'),
            prop: 'name'
        },
        {
            label: i18n.t('项目'),
            prop: 'projectName'
        },
        {
            label: i18n.t('执行开始'),
            prop: 'start_time',
            width: 200
        },
        {
            label: i18n.t('执行结束'),
            prop: 'finish_time',
            width: 200
        },
        {
            label: i18n.t('创建时间'),
            prop: 'create_time',
            width: 200
        },
        {
            label: i18n.t('创建人'),
            prop: 'creator_name',
            width: 100
        },
        {
            label: i18n.t('执行人'),
            prop: 'executor_name',
            width: 100
        },
        {
            label: i18n.t('创建方式'),
            prop: 'create_method',
            width: 100
        },
        {
            label: i18n.t('状态'),
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
            keyword: String,
            hasEditPerm: Boolean,
            editPermLoading: Boolean
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
                methodList: {},
                templateResultTotal: 0,
                taskResultTotal: 0,
                tplFilter: {},
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
                    'limit-list': [15, 30, 50, 100],
                    limit: 15
                },
                taskPagination: {
                    current: 1,
                    count: 0,
                    'limit-list': [15, 30, 50, 100],
                    limit: 15
                }
            }
        },
        computed: {
            ...mapState({
                site_url: state => state.site_url
            }),
            searchResultTotal () {
                return this.templateResultTotal + this.taskResultTotal
            }
        },
        created () {
            this.getSearchResult()
        },
        methods: {
            ...mapActions('task/', [
                'getTaskStatus',
                'loadCreateMethod'
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
                    this.templateResultTotal = 0
                    this.taskResultTotal = 0
                    const res = await this.search({ keyword: this.searchStr })
                    if (res.result) {
                        this.matchedList = res.data.matched
                        this.tplFilter = this.matchedList.find(item => item.type === 'flow')
                        this.taskFilter = this.matchedList.find(item => item.type === 'task')
                        if (this.tplFilter) {
                            this.getAdminTemplate()
                        }
                        if (this.taskFilter) {
                            this.getAdminTask()
                            this.getCreateMethod()
                        }
                    }
                } catch (e) {
                    console.log(e)
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
                    this.tplData = res.results
                    this.templateResultTotal = res.count
                    this.tplPagination.count = res.count
                } catch (e) {
                    console.log(e)
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
                    this.taskData = res.results
                    this.taskResultTotal = res.count
                    this.taskOperations = res.auth_operations
                    this.taskResource = res.auth_resource
                    this.taskPagination.count = res.count
                    this.executeStatus = res.results.map((item, index) => {
                        const status = {}
                        
                        if (item.is_finished) {
                            status.cls = 'finished bk-icon icon-check-circle-shape'
                            status.text = i18n.t('完成')
                        } else if (item.is_revoked) {
                            status.cls = 'revoke common-icon-dark-circle-shape'
                            status.text = i18n.t('撤销')
                        } else if (item.is_started) {
                            status.cls = 'loading common-icon-loading'
                            this.getExecuteDetail(item, index)
                        } else {
                            status.cls = 'created common-icon-dark-circle-shape'
                            status.text = i18n.t('未执行')
                        }
                        return status
                    })
                } catch (e) {
                    console.log(e)
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
                    const detailInfo = await this.getTaskStatus(data)
                    if (detailInfo.result) {
                        const state = detailInfo.data.state
                        const status = {}
                        switch (state) {
                            case 'RUNNING':
                            case 'BLOCKED':
                                status.cls = 'running common-icon-dark-circle-ellipsis'
                                status.text = i18n.t('执行中')
                                break
                            case 'READY':
                                status.cls = 'running common-icon-dark-circle-ellipsis'
                                status.text = i18n.t('排队中')
                                break
                            case 'SUSPENDED':
                                status.cls = 'execute common-icon-dark-circle-pause'
                                status.text = i18n.t('暂停')
                                break
                            case 'NODE_SUSPENDED':
                                status.cls = 'execute common-icon-dark-circle-pause'
                                status.text = i18n.t('节点暂停')
                                break
                            case 'FAILED':
                                status.cls = 'failed common-icon-dark-circle-close'
                                status.text = i18n.t('失败')
                                break
                            default:
                                status.text = i18n.t('未知')
                        }
                        this.executeStatus.splice(index, 1, status)
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            async getCreateMethod () {
                try {
                    const methodList = {}
                    const resp = await this.loadCreateMethod()
                    if (resp.result) {
                        resp.data.forEach(item => {
                            methodList[item.value] = item.name
                        })
                        this.methodList = methodList
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            onSearch () {
                this.getSearchResult()
            },
            onApplyPerm (required, data, type) {
                const resourceData = {
                    project: [{
                        id: data.project.id,
                        name: data.project.name
                    }]
                }
                const reItem = { id: data.id, name: data.name }
                if (type === 'tpl') {
                    resourceData.flow = [reItem]
                } else {
                    resourceData.task = [reItem]
                }
                this.applyForPermission(required, data.auth_actions, resourceData)
            },
            onRestoreTemplate (tpl) {
                if (this.editPermLoading) {
                    return
                }
                if (!this.hasEditPerm) {
                    this.applyForPermission(['admin_edit'])
                } else {
                    this.isRestoreDialogShow = true
                    this.restoreData = tpl
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
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.restorePending = false
                }
            },
            handlePageChange (val, type) {
                if (type === 'tpl') {
                    this.tplPagination.current = val
                    this.getAdminTemplate()
                } else {
                    this.taskPagination.current = val
                    this.getAdminTask()
                }
            },
            handlePageLimitChange (val, type) {
                if (type === 'tpl') {
                    this.tplPagination.limit = val
                    this.tplPagination.current = 1
                    this.getAdminTemplate()
                } else {
                    this.taskPagination.limit = val
                    this.taskPagination.current = 1
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
                color: #3a84ff;
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
