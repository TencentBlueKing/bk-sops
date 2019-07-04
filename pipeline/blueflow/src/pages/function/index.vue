/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="function-container">
        <div class="list-wrapper">
            <div class="operation-area clearfix">
                <div class="function-search">
                    <input class="search-input" :placeholder="i18n.placeholder" v-model="searchStr" @input="onSearchInput"/>
                    <i class="common-icon-search"></i>
                </div>
                <bk-button :type="'primary'" @click="clickDialog">{{i18n.new}}</bk-button>
            </div>
            <div class="function-table-content" v-bkloading="{isLoading: listLoading, opacity: 1}">
                <table>
                    <thead>
                        <tr>
                            <th class="function-id">ID</th>
                            <th class="function-business">{{i18n.business}}</th>
                            <th class="function-name">{{ i18n.name }}</th>
                            <th class="function-time">{{ i18n.createdTime }}</th>
                            <th class="function-time">{{ i18n.claimedTime }}</th>
                            <th class="function-creator">{{ i18n.creator }}</th>
                            <th class="function-claimant">{{ i18n.claimant }}</th>
                            <th class="function-status">{{ i18n.status }}</th>
                            <th class="function-operation">{{ i18n.operation }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in functionList" :key="item.id">
                            <td class="function-id">{{item.id}}</td>
                            <td class="function-business">{{item.task.business.cc_name}}</td>
                            <td class="function-name">
                                <router-link :to="`/taskflow/execute/${item.task.business.cc_id}/?instance_id=${item.task.id}`">{{item.task.name}}</router-link>
                            </td>
                            <td class="function-time">{{item.create_time}}</td>
                            <td class="function-time">{{formatter(item.claim_time)}}</td>
                            <td class="function-creator">{{item.creator}}</td>
                            <td class="function-claimant">{{formatter(item.claimant)}}</td>
                            <td class="function-status" :class="statusClass(item.status)">{{statusMethod(item.status, item.status_name)}}</td>
                            <td class="function-operation">
                                <router-link v-if="item.status === 'submitted'"
                                    class="bk-button bk-primary btn-size-mini"
                                    :to="`/taskflow/execute/${item.task.business.cc_id}/?instance_id=${item.task.id}`">
                                    {{ i18n.claim }}
                                </router-link>
                                <router-link v-else
                                    class="bk-button bk-primary btn-size-mini"
                                    :to="`/taskflow/execute/${item.task.business.cc_id}/?instance_id=${item.task.id}`">
                                    {{ i18n.view }}
                                </router-link>
                            </td>
                        </tr>
                        <tr v-if="!functionList || !functionList.length" class="empty-tr">
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
        :is-show.sync="dialog.isShow"
            @confirm="confirm" @cancel="cancel"
            :has-header="true"
            :quick-close="false"
            :ext-cls="'common-dialog'"
            :close-icon="false"
            width="600"
            padding="30px"
            :title="i18n.new">
            <div slot="content">
                <div class="common-form-item">
                    <label class="required">{{i18n.choiceBusiness}}</label>
                    <div class="common-form-content">
                        <bk-selector
                            :allow-clear="true"
                            :list="business.list"
                            :selected.sync="business.selected"
                            :setting-key="'cc_id'"
                            :display-key="'cc_name'"
                            :search-key="'cc_name'"
                            @item-selected="businessSelectedMethod"
                            :is-loading="business.loading"
                            :searchable="business.searchable"
                            @clear="businessClear">
                        </bk-selector>
                        <span v-show="business.empty" class="common-error-tip error-msg">{{i18n.choiceBusiness}}</span>
                    </div>
                </div>
                <div class="common-form-item">
                    <label class="required">{{i18n.choiceTemplate}}</label>
                    <div class="common-form-content">
                        <bk-selector
                            :allow-clear="true"
                            :list="template.list"
                            :selected.sync="template.selected"
                            :setting-key="'id'"
                            :display-key="'name'"
                            @item-selected="templateSelectedMethod"
                            :is-loading="template.loading"
                            :searchable="template.searchable"
                            @clear="templateClear">
                        </bk-selector>
                        <bk-tooltip placement="left" width="400" class="template-tooltip">
                            <i class="common-icon-warning"></i>
                            <div slot="content" style="white-space: normal;">
                                <div class="">{{i18n.tips}}</div>
                            </div>
                        </bk-tooltip>
                        <span v-show="template.empty" class="common-error-tip error-msg">{{i18n.choiceTemplate}}</span>
                    </div>
                </div>
            </div>
        </bk-dialog>
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
    name: 'functionTaskHome',
    components: {
        CopyrightFooter,
        NoData
    },
    props: ['cc_id','app_id'],
    data () {
        return {
            i18n: {
                placeholder: gettext('请输入ID或流程名称'),
                business: gettext('所属业务'),
                createdTime: gettext('提单时间'),
                claimedTime: gettext('认领时间'),
                name: gettext('任务名称'),
                creator: gettext('提单人'),
                claimant: gettext('认领人'),
                status: gettext('状态'),
                operation: gettext('操作'),
                claim: gettext('认领'),
                view: gettext('查看'),
                new: gettext('新建任务'),
                choiceBusiness: gettext('选择业务'),
                choiceTemplate: gettext('选择模板'),
                tips: gettext('如果未找到模板，请联系业务运维在流程模板的权限管理中对你或所有职能化人员授予“新建任务权限”'),
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
            dialog: {
                isShow: false
            },
            functionList: [],
            business: {
                list: [],
                selected: 0,
                loading: false,
                id: null,
                searchable: true,
                empty: false
            },
            template: {
                list: [],
                selected: 0,
                loading: false,
                searchable: true,
                id: null,
                empty: false
            }
        }
    },
    computed: {
    },
    created () {
        this.loadFunctionTask()
        this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        this.business.loading = true
        this.getBusinessList()
    },
    methods: {
        ...mapActions('functionTask/', [
            'loadFunctionTaskList',
            'loadFunctionBusinessList',
            'loadFunctionTemplateList'
        ]),
        async loadFunctionTask () {
            this.listLoading = true
            try {
                const data = {
                    limit: this.countPerPage,
                    offset: (this.currentPage - 1) * this.countPerPage,
                    q: this.searchStr
                }
                const functionListData = await this.loadFunctionTaskList(data)
                const list = functionListData.objects
                this.functionList = list
                this.totalCount = functionListData.meta.total_count
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
        statusMethod (status,status_name) {
            if (status === 'finished') {
                return gettext('完成')
            }
            else if (status === 'submitted'){
                return gettext('未认领')
            }
            else if (status === 'rejected') {
                return gettext('已驳回')
            }
            return status_name
        },
        statusClass (status) {
            if (status === 'finished') {
                return {success: true}
            }
            else if (status === 'submitted'){
                return {danger: true}
            }
            else if (status === 'rejected') {
                return {primary: true}
            }
            return {warning: true}
        },
        formatter (value) {
            if (value === '' || value === null) {
                return '--'
            }
            return value
        },
        clickDialog () {
            this.dialog.isShow = true
        },
        async getBusinessList () {
            let businessData = await this.loadFunctionBusinessList()
            this.business.list = businessData.objects
            this.business.loading = false
        },
        async getTemplateList () {
            this.template.list = []
            let templateData = await this.loadFunctionTemplateList(this.business.id)
            this.template.list = templateData.objects
            this.template.loading = false
        },
        businessSelectedMethod (id, data) {
            this.template.loading = true
            this.business.id = id
            this.getTemplateList()
            this.business.empty = false
        },
        templateSelectedMethod (id, data) {
            this.template.id = id
            this.template.empty = false
        },
        confirm () {
            if (this.business.id === null) {
                this.business.empty = true
                return
            }
            if (this.template.id === null) {
                this.template.empty = true
                return
            }
            var path = this.$store.state.site_url + 'template/newtask/' + this.business.id + '/selectnode/?template_id=' + this.template.id
            window.location.href = window.location.protocol + "//" + window.location.host + path
        },
        cancel (done) {
            this.templateClear()
            this.businessClear()
            done()
        },
        templateClear () {
            this.template.id = null
            this.template.selected = 0
        },
        businessClear () {
            this.business.id = null
            this.business.selected = 0
        }
    }
}
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
label.required:after {
    content: '*';
    position: absolute;
    top: 0px;
    right: -10px;
    color: #ff2602;
    font-family: "SimSun";
}
.function-container {
    padding-top: 20px;
    min-width: 1320px;
    min-height: calc(100% - 60px);
    background: #fafafa;
}
.list-wrapper {
    padding: 0 60px;
}
.template-tooltip {
    position: absolute;
    right: 8px;
    top: 165px;
    .common-icon-warning {
        color: #cac8c8;
        cursor: pointer;
    }
}

.common-form-item {
    label {
        font-weight: normal;
    }
}
.operation-area {
    margin: 20px 0;
    .function-search {
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
.function-table-content {
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
        .function-id {
            width: 80px;
        }
        .function-name {
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
        .function-type {
            width: 110px;
        }
        .function-time {
            width: 210px;
        }
        .function-creator {
            width: 130px;
            overflow:hidden;
            text-overflow:ellipsis;
            white-space: nowrap;
        }
        .function-claimant {
            width: 130px;
            overflow:hidden;
            text-overflow:ellipsis;
            white-space: nowrap;
        }
        .function-business {
            width: 130px;
            overflow:hidden;
            text-overflow:ellipsis;
            white-space: nowrap;
        }
        .function-status {
            width: 110px;
        }
        .function-operation {
            width: 110px;
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
.danger {
    color: #ff5757;
}
.primary {
    color: #4a9bff;
}
.warning {
    color: #f8b53f;
}
</style>

