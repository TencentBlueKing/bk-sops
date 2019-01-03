/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="audit-container">
        <div class="list-wrapper">
            <div class="operation-area clearfix">
                <div class="audit-search">
                    <input class="search-input" :placeholder="i18n.placeholder" v-model="searchStr" @input="onSearchInput"/>
                    <i class="common-icon-search"></i>
                </div>
            </div>
            <div class="audit-table-content" v-bkloading="{isLoading: listLoading, opacity: 1}">
                <table>
                    <thead>
                        <tr>
                            <th class="audit-id">ID</th>
                            <th class="audit-business">{{ i18n.business }}</th>
                            <th class="audit-name">{{ i18n.name }}</th>
                            <th class="audit-time">{{ i18n.startedTime }}</th>
                            <th class="audit-time">{{ i18n.finishedTime }}</th>
                            <th class="audit-category">{{ i18n.category }}</th>
                            <th class="audit-creator">{{ i18n.creator }}</th>
                            <th class="audit-executor">{{ i18n.operator }}</th>
                            <th class="audit-status">{{ i18n.status }}</th>
                            <th class="audit-operation">{{ i18n.operation }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in auditList" :key="item.id">
                            <td class="audit-id">{{item.id}}</td>
                            <td class="audit-business">{{item.business.cc_name}}</td>
                            <td class="audit-name">
                                <router-link :to="`/taskflow/execute/${item.business.cc_id}/?instance_id=${item.id}`">{{item.name}}</router-link>
                            </td>
                            <td class="audit-time">{{formatter(item.start_time)}}</td>
                            <td class="audit-time">{{formatter(item.finish_time)}}</td>
                            <td class="audit-category">{{item.category_name}}</td>
                            <td class="audit-creator">{{item.creator_name}}</td>
                            <td class="audit-executor">{{formatter(item.executor_name)}}</td>
                            <td class="audit-status" :class="statusClass(item.is_started, item.is_finished)">{{statusMethod(item.is_started,item.is_finished)}}</td>
                            <td class="audit-operation">
                                <router-link
                                    class="bk-button bk-primary btn-size-mini"
                                    :to="`/taskflow/execute/${item.business.cc_id}/?instance_id=${item.id}`">
                                    {{ i18n.view }}
                                </router-link>
                            </td>
                        </tr>
                        <tr v-if="!auditList || !auditList.length" class="empty-tr">
                            <td colspan="10">
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
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapActions } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
import NoData from '@/components/common/base/NoData.vue'
import toolsUtils from '@/utils/tools.js'
export default {
    name: 'auditTaskHome',
    components: {
        CopyrightFooter,
        NoData
    },
    data () {
        return {
            i18n: {
                placeholder: gettext('请输入ID或流程名称'),
                business: gettext('所属业务'),
                startedTime: gettext('执行开始'),
                finishedTime: gettext('执行结束'),
                name: gettext('任务名称'),
                category: gettext('任务类型'),
                creator: gettext('创建人'),
                operator: gettext('执行人'),
                status: gettext('状态'),
                operation: gettext('操作'),
                view: gettext('查看'),
                total: gettext("共"),
                item: gettext("条记录"),
                comma: gettext("，"),
                currentPageTip: gettext("当前第"),
                page: gettext("页")
            },
            listLoading: true,
            currentPage: 1,
            totalPage: 1,
            countPerPage: 15,
            totalCount: 0,
            searchStr: '',
            auditList: []
        }
    },
    computed: {
    },
    created () {
        this.loadFunctionTask()
        this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
    },
    methods: {
        ...mapActions('auditTask/', [
            'loadAuditTaskList'
        ]),
        async loadFunctionTask () {
            this.listLoading = true
            try {
                const data = {
                    limit: this.countPerPage,
                    offset: (this.currentPage - 1) * this.countPerPage,
                    q: this.searchStr
                }
                const auditListData = await this.loadAuditTaskList(data)
                const list = auditListData.objects
                this.auditList = list
                this.totalCount = auditListData.meta.total_count
                const totalPage = Math.ceil( this.totalCount / this.countPerPage)
                if (!totalPage) {
                    this.totalPage = 1
                } else {
                    this.totalPage = totalPage
                }
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.listLoading = false
            }
        },
        onPageChange (page) {
            this.currentPage = page
            this.loadFunctionTask()
        },
        searchInputhandler () {
            this.currentPage = 1
            this.loadFunctionTask()
        },
        statusMethod (is_started,is_finished) {
            if (is_finished) {
                return gettext('完成')
            }
            else if (is_started){
                return gettext('执行中')
            }
            return gettext('未执行')
        },
        statusClass (is_started,is_finished) {
            if (is_finished) {
                return {success: true}
            }
            else if (is_started){
                return {warning: true}
            }
            return {primary: true}
        },
        formatter (value) {
            if (value === '' || value === null) {
                return '--'
            }
            return value
        }
    }
}
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
.audit-container {
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
    .audit-search {
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
.audit-table-content {
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
        .audit-id {
            width: 80px;
        }
        .audit-name {
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
        .audit-type {
            width: 110px;
        }
        .audit-time {
            width: 210px;
        }
        .audit-creator {
            width: 130px;
            overflow:hidden;
            text-overflow:ellipsis;
            white-space: nowrap;
        }
        .audit-business {
            width: 130px;
            overflow:hidden;
            text-overflow:ellipsis;
            white-space: nowrap;
        }
        .audit-status {
            width: 110px;
        }
        .audit-operation {
            width: 110px;
        }
        .audit-category {
            width: 160px;
        }
        .audit-executor {
            width: 130px;
            overflow:hidden;
            text-overflow:ellipsis;
            white-space: nowrap;
        }
    }
    .btn-size-mini {
        height: 24px;
        line-height: 22px;
        padding: 0 11px;
        font-size: 12px;
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
.success {
    color:#30d878;
}
.primary {
    color: #4a9bff;
}
.warning {
    color: #f8b53f;
}
</style>

