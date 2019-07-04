/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="appmaker-container">
        <div class="list-wrapper">
            <div class="operation-area clearfix">
                <div class="appmaker-search">
                    <input class="search-input" :placeholder="i18n.placeholder" v-model="searchStr" @input="onSearchInput"/>
                    <i class="common-icon-search"></i>
                </div>
            </div>
            <div class="appmaker-table-content" v-bkloading="{isLoading: listLoading, opacity: 1}">
                <table>
                    <thead>
                        <tr>
                            <th class="appmaker-id">ID</th>
                            <th class="appmaker-name">{{ i18n.name }}</th>
                            <th class="appmaker-time">{{ i18n.startedTime }}</th>
                            <th class="appmaker-time">{{ i18n.finishedTime }}</th>
                            <th class="appmaker-category">{{ i18n.category }}</th>
                            <th class="appmaker-creator">{{ i18n.creator }}</th>
                            <th class="appmaker-operator">{{ i18n.operator }}</th>
                            <th class="appmaker-status">{{ i18n.status }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in appmakerList" :key="item.id">
                            <td class="appmaker-id">{{item.id}}</td>
                            <td class="appmaker-name">
                                <router-link
                                    :to="`/appmaker/${item.create_info}/execute/${item.business.cc_id}/?instance_id=${item.id}`">
                                    {{item.name}}
                                </router-link>
                            </td>
                            <td class="appmaker-time">{{formatter(item.start_time)}}</td>
                            <td class="appmaker-time">{{formatter(item.finish_time)}}</td>
                            <td class="appmaker-category">{{item.category_name}}</td>
                            <td class="appmaker-creator">{{item.creator_name}}</td>
                            <td class="appmaker-operator">{{formatter(item.executor_name)}}</td>
                            <td class="appmaker-status" :class="statusClass(item.is_started, item.is_finished)">{{statusMethod(item.is_started, item.is_finished)}}</td>
                        </tr>
                        <tr v-if="!appmakerList || !appmakerList.length" class="empty-tr">
                            <td colspan="8">
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
    name: 'appmakerTaskHome',
    components: {
        CopyrightFooter,
        NoData
    },
    props: ['cc_id','app_id'],
    data () {
        return {
            i18n: {
                placeholder: gettext('请输入ID或流程名称'),
                startedTime: gettext('执行开始'),
                finishedTime: gettext('执行结束'),
                name: gettext('任务名称'),
                category: gettext('任务类型'),
                creator: gettext('创建人'),
                operator: gettext('执行人'),
                status: gettext('状态'),
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
            isDeleteDialogShow: false,
            theDeleteTemplateId: undefined,
            pending: {
                delete: false,
                authority: false
            },
            searchStr: '',
            appmakerList: []
        }
    },
    computed: {
    },
    created () {
        this.getAppmakerList()
        this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
    },
    methods: {
        ...mapActions('taskList/', [
            'loadTaskList'
        ]),
        async getAppmakerList () {
            this.listLoading = true
            try {
                const data = {
                    limit: this.countPerPage,
                    offset: (this.currentPage - 1) * this.countPerPage,
                    create_method: 'app_maker',
                    create_info: this.app_id,
                    q: this.searchStr
                }
                const appmakerListData = await this.loadTaskList(data)
                const list = appmakerListData.objects
                this.appmakerList = list
                this.totalCount = appmakerListData.meta.total_count
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
            this.getAppmakerList()
        },
        searchInputhandler () {
            this.currentPage = 1
            this.getAppmakerList()
        },
        statusMethod (is_started, is_finished) {
            var status = ''
            if (is_finished) {
                status = gettext('完成')
            }
            else if (is_started) {
                status = gettext('执行中')
            }
            else {
                status = gettext('未执行')
            }
            return status
        },
        statusClass (is_started, is_finished) {
            var statusClass = ''
            if (is_finished) {
                statusClass = {success: true}
            }
            else if (is_started) {
                statusClass = {warning: true}
            }
            else {
                statusClass = {primary: true}
            }
            return statusClass
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
.appmaker-container {
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
    .appmaker-search {
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
.appmaker-table-content {
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
        .appmaker-id {
            width: 80px;
        }
        .appmaker-name {
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
        .appmaker-type {
            width: 110px;
        }
        .appmaker-time {
            width: 220px;
        }
        .appmaker-creator {
            width: 110px;
        }
        .appmaker-operator {
            width: 110px;
        }
        .appmaker-category {
            width: 110px;
        }
        .appmaker-status {
            width: 110px;
        }
        .appmaker-name {
            width: 220px;
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
.warning {
    color: #f8b53f;
}
.primary {
    color: #4a9bff;
}
</style>

