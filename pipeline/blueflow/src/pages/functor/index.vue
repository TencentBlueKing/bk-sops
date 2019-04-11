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
    <div class="functor-container">
        <div class="list-wrapper">
            <div class="operation-area clearfix">
                <bk-button :type="'primary'" @click="onNewTask">{{i18n.new}}</bk-button>
                <div class="functor-search">
                    <input class="search-input" :placeholder="i18n.placeholder" v-model="searchStr" @input="onSearchInput"/>
                    <i class="common-icon-search"></i>
                </div>
            </div>
            <div class="functor-table-content">
                <table v-bkloading="{isLoading: listLoading, opacity: 1}">
                    <thead>
                        <tr>
                            <th class="functor-id">ID</th>
                            <th class="functor-business">{{i18n.business}}</th>
                            <th class="functor-name">{{ i18n.name }}</th>
                            <th class="functor-time">{{ i18n.createdTime }}</th>
                            <th class="functor-time">{{ i18n.claimedTime }}</th>
                            <th class="functor-creator">{{ i18n.creator }}</th>
                            <th class="functor-claimant">{{ i18n.claimant }}</th>
                            <th class="functor-status">{{ i18n.status }}</th>
                            <th class="functor-operation">{{ i18n.operation }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in functorList" :key="item.id">
                            <td class="functor-id">{{item.id}}</td>
                            <td class="functor-business">{{item.task.business.cc_name}}</td>
                            <td class="functor-name">
                                <router-link
                                    :title="item.task.name"
                                    :to="`/taskflow/execute/${item.task.business.cc_id}/?instance_id=${item.task.id}`">
                                    {{item.task.name}}
                                </router-link>
                            </td>
                            <td class="functor-time">{{item.create_time}}</td>
                            <td class="functor-time">{{item.claim_time || '--'}}</td>
                            <td class="functor-creator">{{item.creator}}</td>
                            <td class="functor-claimant">{{item.claimant || '--'}}</td>
                            <td class="functor-status">
                                <span :class="statusClass(item.status)"></span>
                                {{statusMethod(item.status, item.status_name)}}
                            </td>
                            <td class="functor-operation">
                                <router-link v-if="item.status === 'submitted'"
                                    class="functor-operation-btn"
                                    :to="`/taskflow/execute/${item.task.business.cc_id}/?instance_id=${item.task.id}`">
                                    {{ i18n.claim }}
                                </router-link>
                                <router-link v-else
                                    class="functor-operation-btn"
                                    :to="`/taskflow/execute/${item.task.business.cc_id}/?instance_id=${item.task.id}`">
                                    {{ i18n.view }}
                                </router-link>
                            </td>
                        </tr>
                        <tr v-if="!functorList || !functorList.length" class="empty-tr">
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
            :is-show.sync="isShowNewTaskDialog"
            @confirm="onConfirmlNewTask"
            @cancel="onCancelNewTask"
            :has-header="true"
            :quick-close="false"
            :ext-cls="'common-dialog'"
            :close-icon="false"
            width="600"
            padding="30px"
            :title="i18n.new">
            <div slot="content">
                <div class="common-form-item">
                    <label>{{i18n.choiceBusiness}}</label>
                    <div class="common-form-content">
                        <bk-selector
                            :allow-clear="true"
                            :list="business.list"
                            :selected.sync="business.selected"
                            :setting-key="'cc_id'"
                            :display-key="'cc_name'"
                            :search-key="'cc_name'"
                            :is-loading="business.loading"
                            :searchable="business.searchable"
                            @item-selected="onSelectedBusiness"
                            @clear="onClearBusiness">
                        </bk-selector>
                        <span v-show="business.empty" class="common-error-tip error-msg">{{i18n.choiceBusiness}}</span>
                    </div>
                </div>
                <div class="common-form-item">
                    <label>{{i18n.choiceTemplate}}</label>
                    <div class="common-form-content">
                        <bk-selector
                            :allow-clear="true"
                            :list="template.list"
                            :selected.sync="template.selected"
                            :setting-key="'id'"
                            :display-key="'name'"
                            :has-children='true'
                            :is-loading="template.loading"
                            :searchable="template.searchable"
                            :disabled="template.disabled"
                            @item-selected="onSelectedTemplate"
                            @clear="onClearTemplate">
                        </bk-selector>
                        <bk-tooltip placement="left" width="400" class="template-tooltip">
                            <i class="bk-icon icon-info-circle"></i>
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
import { mapActions, mapMutations } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
import NoData from '@/components/common/base/NoData.vue'
import BaseSearch from '@/components/common/base/BaseSearch.vue'
import toolsUtils from '@/utils/tools.js'
export default {
    name: 'functorTaskHome',
    components: {
        CopyrightFooter,
        BaseSearch,
        NoData
    },
    props: ['cc_id', 'app_id'],
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
                total: gettext('共'),
                item: gettext('条记录'),
                comma: gettext('，'),
                currentPageTip: gettext('当前第'),
                page: gettext('页')
            },
            listLoading: true,
            currentPage: 1,
            totalPage: 1,
            countPerPage: 15,
            totalCount: 0,
            searchStr: '',
            isShowNewTaskDialog: false,
            functorList: [],
            business: {
                list: [],
                selected: 0,
                loading: false,
                id: null,
                searchable: true,
                empty: false
            },
            template: {
                list: [
                    {
                        name: gettext('业务流程'),
                        children: []
                    },
                    {
                        name: gettext('公共流程'),
                        children: []
                    }
                ],
                selected: 0,
                loading: false,
                searchable: true,
                id: null,
                empty: false,
                disabled: true
            },
            isCommonTemplate: false
        }
    },
    created () {
        this.loadFunctionTask()
        this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        this.getBusinessList()
    },
    methods: {
        ...mapActions('functionTask/', [
            'loadFunctionTaskList',
            'loadFunctionBusinessList',
            'loadFunctionTemplateList'
        ]),
        ...mapActions('templateList/',[
            'loadTemplateList'
        ]),
        ...mapMutations('atomForm/', [
            'clearAtomForm'
        ]),
        async loadFunctionTask () {
            this.listLoading = true
            try {
                const data = {
                    limit: this.countPerPage,
                    offset: (this.currentPage - 1) * this.countPerPage,
                    q: this.searchStr
                }
                const functorListData = await this.loadFunctionTaskList(data)
                const list = functorListData.objects
                this.functorList = list
                this.totalCount = functorListData.meta.total_count
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
        statusMethod (status, status_name) {
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
            let cls
            switch (status) {
                case 'submitted': // 未认领
                    cls = 'common-icon-flag-circle default'
                    break
                case 'claimed': // 已认领
                    cls = 'common-icon-flag-circle success'
                    break
                case 'executed': // 已执行
                    cls = 'common-icon-dark-circle-ellipsis primary'
                    break
                case 'rejected': // 已驳回
                    cls = 'common-icon-dark-circle-close'
                    break
                case 'finished': // 完成
                    cls = 'bk-icon icon-check-circle-shape default'
                    break
                default:
                    cls = ''
            }

            return cls
        },
        onNewTask () {
            this.isShowNewTaskDialog = true
        },
        async getBusinessList () {
            this.business.loading = true
            try {
                let businessData = await this.loadFunctionBusinessList()
                this.business.list = businessData.objects
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.business.loading = false
            }
        },
        async getTemplateList () {
            this.template.loading = true
            try {
                // 查询职能化数据及公共流程数据
                await Promise.all([this.loadFunctionTemplateList(this.business.id), this.loadTemplateList({common: 1})]).then(value =>{
                    if (value[0].objects.length === 0) {
                        this.template.list[0].children = [{'id': undefined, 'name': gettext('无数据')}]
                    } else {
                        this.template.list[0].children = value[0].objects
                    }
                    if (value[1].objects.length === 0) {
                        this.template.list[1].children = [{'id': undefined, 'name': gettext('无数据')}]
                    } else {
                        this.template.list[1].children = value[1].objects
                    }
                    this.clearAtomForm()
                    this.$nextTick(() => {
                        this.changeNoDataTextStyle()
                    })
                })
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.template.loading = false
            }
        },
        onSelectedBusiness (id, data) {
            this.business.id = id
            this.getTemplateList()
            this.business.empty = false
            this.template.disabled = false
        },
        onSelectedTemplate (id, data) {
            if (id === undefined) {
                return
            }
            this.isCommonTemplate = false
            // 通过resource_uri查找是否是公共流程
            if (data.resource_uri.search('common_template') !== -1) {
                this.isCommonTemplate = true
            }
            this.template.id = id
            this.template.empty = false
        },
        onConfirmlNewTask () {
            if (this.business.id === null) {
                this.business.empty = true
                return
            }
            if (this.template.id === null) {
                this.template.empty = true
                return
            }
            if (this.isCommonTemplate) {
                this.$router.push({path: `/template/newtask/${this.business.id}/selectnode/`, query: {template_id: this.template.id, common: 1}})
            } else {
                this.$router.push({path: `/template/newtask/${this.business.id}/selectnode/`, query: {template_id: this.template.id}})
            }
        },
        onCancelNewTask () {
            this.onClearTemplate()
            this.onClearBusiness()
            this.isShowNewTaskDialog = false
        },
        onClearTemplate () {
            this.template.id = null
            this.template.selected = 0
        },
        onClearBusiness () {
            this.template.disabled = true
            this.business.id = null
            this.business.selected = 0
        },
        // 无数据文本修改样式
        changeNoDataTextStyle () {
            const textList = document.querySelectorAll('.text')
            for (let item of textList) {
                if (item.textContent === gettext(' 无数据 ')) {
                    item.style['cursor'] = 'not-allowed'
                    item.style['background-color'] = '#FAFAFA'
                    item.style['color'] = '#AAAAAA'
                    item.parentElement.style["background-color"] = '#FAFAFA'
                }
            }
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
    color: $redDark;
    font-family: "SimSun";
}
.functor-container {
    padding-top: 20px;
    min-width: 1320px;
    min-height: calc(100% - 50px);
    background: $whiteNodeBg;
}
.list-wrapper {
    padding: 0 60px;
    min-height: calc(100vh - 240px);
}
.template-tooltip {
    position: absolute;
    right: 30px;
    top: 156px;
    &:hover {
        color: #FF9C01;
    }
}

.common-form-item {
    label {
        width: 60px;
        font-weight: normal;
    }
    .common-form-content {
        margin-left: 80px;
        margin-right: 30px;
    }
}
.operation-area {
    margin: 20px 0;
    .functor-search {
        float: right;
        position: relative;
    }
    .search-input {
        padding: 0 40px 0 10px;
        width: 360px;
        height: 32px;
        line-height: 32px;
        font-size: 12px;
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
        top: 8px;
        color: $commonBorderColor;
    }
}
.functor-table-content {
    table {
        width: 100%;
        border: 1px solid $commonBorderColor;
        border-collapse: collapse;
        font-size: 12px;
        background: $whiteDefault;
        table-layout: fixed;
        tr:not(.empty-tr):hover {
            background: $whiteNodeBg;
        }
        th,td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid $commonBorderColor;
        }
        th {
            background: $whiteNodeBg;
        }
        .functor-id {
            width: 80px;
        }
        .functor-name {
            text-align: left;
            a {
                display: block;
                width: 100%;
                color: $blueDefault;
                text-overflow: ellipsis;
                white-space: nowrap;
                word-break: break-all;
                overflow: hidden;
            }
        }
        .functor-type {
            width: 110px;
        }
        .functor-time {
            width: 215px;
        }
        .functor-creator {
            width: 110px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .functor-claimant {
            width: 110px;
            overflow:hidden;
            text-overflow:ellipsis;
            white-space: nowrap;
        }
        .functor-business {
            width: 130px;
            overflow:hidden;
            text-overflow:ellipsis;
            white-space: nowrap;
        }
        .functor-status {
            width: 110px;
        }
        .functor-operation {
            width: 110px;
        }
    }
    .btn-size-mini {
        height: 24px;
        line-height: 22px;
        padding: 0 11px;
        font-size: 12px;
    }
    .functor-operation-btn {
        color: #3c96ff;
    }
    .empty-data {
        padding: 120px 0;
    }
}
.panagation {
    padding: 10px 20px;
    text-align: right;
    border: 1px solid #dde4eb;
    border-top: none;
    background: #fafbfd;
    .page-info {
        float: left;
        line-height: 36px;
        font-size: 14px;
    }
    .bk-page {
        display: inline-block;
    }
}
.icon-check-circle-shape {
    color: $greenDefault;
}
.common-icon-dark-circle-close {
    color: $redDefault;
}
.default {
    color: #979ba5;
}
.primary {
    color: #3a84ff;
}
.success {
    color: #2dcb56;
}

</style>

