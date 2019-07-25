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
            <BaseTitle :title="i18n.functorList"></BaseTitle>
            <div class="operation-area clearfix">
                <bk-button theme="primary" class="task-create-btn" @click="onCreateTask">{{i18n.new}}</bk-button>
                <BaseSearch
                    v-model="searchStr"
                    :input-placeholader="i18n.placeholder"
                    @onShow="onAdvanceShow"
                    @input="onSearchInput">
                </BaseSearch>
            </div>
            <div class="functor-search" v-show="isAdvancedSerachShow">
                <fieldset class="functor-fieldset">
                    <div class="functor-query-content">
                        <div class="query-content">
                            <span class="query-span">{{i18n.ownBusiness}}</span>
                            <bk-select
                                v-model="selectedCcId"
                                class="bk-select-inline"
                                :popover-width="260"
                                :searchable="true"
                                :placeholder="i18n.choice"
                                :clearable="true"
                                @selected="onSelectedBizCcId">
                                <bk-option
                                    v-for="(option, index) in business.list"
                                    :key="index"
                                    :id="option.cc_id"
                                    :name="option.cc_name">
                                </bk-option>
                            </bk-select>
                        </div>
                        <div class="query-content">
                            <span class="query-span">{{i18n.billTime}}</span>
                            <bk-date-picker
                                ref="bkRanger"
                                :placeholder="i18n.dateRange"
                                :type="'daterange'"
                                @change="onChangeExecuteTime">
                            </bk-date-picker>
                        </div>
                        <div class="query-content">
                            <span class="query-span">{{i18n.creator}}</span>
                            <bk-input
                                v-model="creator"
                                class="bk-input-inline"
                                :clearable="true"
                                :placeholder="i18n.creatorPlaceholder">
                            </bk-input>
                        </div>
                        <div class="query-content">
                            <span class="query-span">{{i18n.status}}</span>
                            <bk-select
                                v-model="statusSync"
                                class="bk-select-inline"
                                :popover-width="260"
                                :searchable="true"
                                :placeholder="i18n.statusPlaceholder"
                                :clearable="true"
                                @clear="onClearStatus"
                                @selected="onSelectedStatus">
                                <bk-option
                                    v-for="(option, index) in statusList"
                                    :key="index"
                                    :id="option.id"
                                    :name="option.name">
                                </bk-option>
                            </bk-select>
                        </div>
                        <div class="query-button">
                            <bk-button class="query-primary" theme="primary" @click="searchInputhandler">{{i18n.query}}</bk-button>
                            <bk-button class="query-cancel" @click="onResetForm">{{i18n.reset}}</bk-button>
                        </div>
                    </div>
                </fieldset>
            </div>
            <div class="functor-table-content">
                <table v-bkloading="{ isLoading: listLoading, opacity: 1 }">
                    <thead>
                        <tr>
                            <th class="functor-business">{{i18n.business}}</th>
                            <th class="functor-id">{{i18n.taskId}}</th>
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
                            <td class="functor-business">{{item.task.business.cc_name}}</td>
                            <td class="functor-id">{{item.task.id}}</td>
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
                                <div class="empty-data"><NoData /></div>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <div class="panagation" v-if="totalPage > 1">
                    <div class="page-info">
                        <span> {{i18n.total}} {{totalCount}} {{i18n.item}}{{i18n.comma}} {{i18n.currentPageTip}} {{currentPage}} {{i18n.page}}</span>
                    </div>
                    <bk-pagination
                        :current.sync="currentPage"
                        :count="totalCount"
                        :limit="countPerPage"
                        :limit-list="[15,20,30]"
                        :show-limit="false"
                        @change="onPageChange">
                    </bk-pagination>
                </div>
            </div>
        </div>
        <CopyrightFooter></CopyrightFooter>
        <bk-dialog
            width="600"
            ext-cls="common-dialog"
            padding="30px"
            :theme="'primary'"
            :mask-close="false"
            :header-position="'left'"
            :title="i18n.new"
            :value="isShowNewTaskDialog"
            @confirm="onConfirmlNewTask"
            @cancel="onCancelNewTask">
            <div>
                <div class="common-form-item">
                    <label>{{i18n.choiceBusiness}}</label>
                    <div class="common-form-content">
                        <bk-select
                            v-model="business.id"
                            class="bk-select-inline"
                            :popover-width="260"
                            :searchable="true"
                            :is-loading="business.loading"
                            :placeholder="i18n.statusPlaceholder"
                            :clearable="true"
                            @clear="onClearBusiness"
                            @selected="onSelectedBusiness">
                            <bk-option
                                v-for="(option, index) in business.list"
                                :key="index"
                                :id="option.cc_id"
                                :name="option.cc_name">
                            </bk-option>
                        </bk-select>
                        <span v-show="business.empty" class="common-error-tip error-msg">{{i18n.choiceBusiness}}</span>
                    </div>
                </div>
                <div class="common-form-item">
                    <label>{{i18n.choiceTemplate}}</label>
                    <div class="common-form-content">
                        <bk-select
                            v-model="template.id"
                            style="width: 260px;"
                            :popover-width="260"
                            :is-loading="business.loading"
                            :searchable="template.searchable"
                            :placeholder="i18n.statusPlaceholder"
                            :clearable="true"
                            :disabled="template.disabled"
                            @selected="onSelectedTemplate"
                            @clear="onClearTemplate">
                            <bk-option-group
                                v-for="(group, index) in template.list"
                                :name="group.name"
                                :key="index">
                                <bk-option v-for="(childOption, childIndex) in group.children"
                                    :key="childIndex"
                                    :id="childOption.id"
                                    :name="childOption.name">
                                </bk-option>
                            </bk-option-group>
                        </bk-select>
                        <i class="bk-icon icon-info-circle template-selector-tips"
                            v-bk-tooltips="{
                                width: 400,
                                placement: 'top',
                                content: i18n.tips }"></i>
                        <span v-show="template.empty" class="common-error-tip error-msg">{{i18n.choiceTemplate}}</span>
                    </div>
                </div>
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions, mapMutations, mapState } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import BaseSearch from '@/components/common/base/BaseSearch.vue'
    import toolsUtils from '@/utils/tools.js'
    import moment from 'moment-timezone'

    export default {
        name: 'functorTaskHome',
        components: {
            CopyrightFooter,
            BaseSearch,
            BaseTitle,
            NoData
        },
        props: ['cc_id', 'app_id'],
        data () {
            return {
                i18n: {
                    functorList: gettext('职能化中心'),
                    placeholder: gettext('请输入ID或流程名称'),
                    business: gettext('所属业务'),
                    taskId: gettext('任务ID'),
                    createdTime: gettext('提单时间'),
                    claimedTime: gettext('认领时间'),
                    ownBusiness: gettext('所属业务'),
                    finishedTime: gettext('执行结束'),
                    name: gettext('任务名称'),
                    billTime: gettext('提单时间'),
                    billTimePlaceholder: gettext('请选择时间'),
                    creator: gettext('提单人'),
                    claimant: gettext('认领人'),
                    status: gettext('状态'),
                    operation: gettext('操作'),
                    claim: gettext('认领'),
                    view: gettext('查看'),
                    new: gettext('新建'),
                    choiceBusiness: gettext('选择业务'),
                    choiceTemplate: gettext('选择模板'),
                    tips: gettext('如果未找到模板，请联系业务运维在流程模板的使用权限中对你或所有职能化人员授予“新建任务权限”'),
                    total: gettext('共'),
                    item: gettext('条记录'),
                    comma: gettext('，'),
                    choice: gettext('请选择'),
                    currentPageTip: gettext('当前第'),
                    page: gettext('页'),
                    functorType: gettext('任务分类'),
                    functorTypePlaceholder: gettext('请选择分类'),
                    creatorPlaceholder: gettext('请输入提单人'),
                    query: gettext('搜索'),
                    reset: gettext('清空'),
                    dateRange: gettext('选择日期时间范围')
                },
                listLoading: true,
                selectedCcId: '',
                currentPage: 1,
                totalPage: 1,
                countPerPage: 15,
                totalCount: 0,
                functorSync: 0,
                statusSync: '',
                searchStr: undefined,
                isShowNewTaskDialog: false,
                functorBasicInfoLoading: true,
                functorList: [],
                business: {
                    list: [],
                    loading: false,
                    id: '',
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
                    loading: false,
                    searchable: true,
                    id: '',
                    empty: false,
                    disabled: false
                },
                bizCcId: undefined,
                billTime: undefined,
                creator: undefined,
                executeStartTime: undefined,
                executeEndTime: undefined,
                isStarted: undefined,
                isFinished: undefined,
                isCommonTemplate: false,
                isAdvancedSerachShow: false,
                status: undefined,
                functorCategory: [],
                statusList: [
                    { 'id': 'submitted', 'name': gettext('未认领') },
                    { 'id': 'claimed', 'name': gettext('已认领') },
                    { 'id': 'executed', 'name': gettext('已执行') },
                    { 'id': 'finished', 'name': gettext('完成') }
                ]
            }
        },
        computed: {
            ...mapState({
                bizList: state => state.bizList,
                categorys: state => state.categorys
            })
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
            ...mapActions('templateList/', [
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
                        task__pipeline_instance__name__contains: this.searchStr,
                        creator: this.creator || undefined,
                        pipeline_instance__is_started: this.isStarted,
                        pipeline_instance__is_finished: this.isFinished,
                        task__business__cc_id: this.bizCcId,
                        status: this.status
                    }
                    if (this.executeEndTime) {
                        if (this.common) {
                            data['pipeline_template__start_time__gte'] = moment(this.executeStartTime).format('YYYY-MM-DD')
                            data['pipeline_template__start_time__lte'] = moment(this.executeEndTime).add('1', 'd').format('YYYY-MM-DD')
                        } else {
                            data['create_time__gte'] = moment.tz(this.executeStartTime, this.businessTimezone).format('YYYY-MM-DD')
                            data['create_time__lte'] = moment.tz(this.executeEndTime, this.businessTimezone).add('1', 'd').format('YYYY-MM-DD')
                        }
                    }
                    const functorListData = await this.loadFunctionTaskList(data)
                    const list = functorListData.objects
                    this.functorList = list
                    this.totalCount = functorListData.meta.total_count
                    const totalPage = Math.ceil(this.totalCount / this.countPerPage)
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
                } else if (status === 'submitted') {
                    return gettext('未认领')
                } else if (status === 'rejected') {
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
            onCreateTask () {
                this.isShowNewTaskDialog = true
            },
            async getBusinessList () {
                this.business.loading = true
                try {
                    const businessData = await this.loadFunctionBusinessList()
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
                    await Promise.all([
                        this.loadFunctionTemplateList(this.business.id),
                        this.loadTemplateList({ common: 1 })
                    ]).then(value => {
                        if (value[0].objects.length === 0) {
                            this.template.list[0].children = [{ 'id': undefined, 'name': gettext('无数据'), disabled: true }]
                        } else {
                            this.template.list[0].children = value[0].objects
                        }
                        if (value[1].objects.length === 0) {
                            this.template.list[1].children = [{ 'id': undefined, 'name': gettext('无数据') }]
                        } else {
                            this.template.list[1].children = value[1].objects
                        }
                        this.clearAtomForm()
                    })
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.template.loading = false
                }
            },
            onSelectedBizCcId (value) {
                if (this.bizCcId === value) {
                    return
                }
                this.bizCcId = value
            },
            onSelectedBusiness (id, data) {
                this.business.id = id
                this.getTemplateList()
                this.business.empty = false
                this.template.disabled = false
                this.template.id = ''
            },
            onSelectedTemplate (id) {
                const templateList = this.template.list
                let resource_uri = ''
                if (id === undefined) {
                    return
                }
                // 查找id对应的resource_uri
                for (const gloup in templateList) {
                    const childrens = templateList[gloup].children
                    for (const item in childrens) {
                        if (childrens[item].id === id) {
                            resource_uri = childrens[item].resource_uri
                            break
                        }
                    }
                    if (resource_uri !== '') break
                }
                this.isCommonTemplate = false
                // 通过resource_uri查找是否是公共流程
                if (resource_uri.search('common_template') !== -1) {
                    this.isCommonTemplate = true
                }
                this.template.id = id
                this.template.empty = false
            },
            onConfirmlNewTask () {
                if (this.business.id === '') {
                    this.business.empty = true
                    return
                }
                if (this.template.id === '') {
                    this.template.empty = true
                    return
                }
                if (this.isCommonTemplate) {
                    this.$router.push({ path: `/template/newtask/${this.business.id}/selectnode/`, query: { template_id: this.template.id, common: 1 } })
                } else {
                    this.$router.push({ path: `/template/newtask/${this.business.id}/selectnode/`, query: { template_id: this.template.id } })
                }
            },
            onCancelNewTask () {
                this.onClearTemplate()
                this.onClearBusiness()
                this.isShowNewTaskDialog = false
                this.business.empty = false
                this.template.empty = false
            },
            onClearTemplate () {
                this.template.id = ''
            },
            onClearBusiness () {
                this.business.id = ''
                this.template.id = ''
                this.template.disabled = true
            },
            onAdvanceShow () {
                this.isAdvancedSerachShow = !this.isAdvancedSerachShow
            },
            onChangeExecuteTime (Value) {
                this.executeStartTime = Value[0]
                this.executeEndTime = Value[1]
            },
            onClearStatus () {
                this.isStarted = undefined
                this.isFinished = undefined
            },
            onResetForm () {
                this.status = undefined
                this.creator = undefined
                this.statusSync = ''
                this.selectedCcId = 0
                this.funtorSync = 0
                this.executeStartTime = undefined
                this.executeEndTime = undefined
            },
            onSelectedStatus (id, name) {
                this.status = id
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
.bk-select-inline,.bk-input-inline {
    display: inline-block;
    width: 260px;
}
label.required:after {
    content: '*';
    position: absolute;
    top: 0px;
    right: -10px;
    color: $redDark;
    font-family: "SimSun";
}
.functor-container {
    min-width: 1320px;
    min-height: calc(100% - 50px);
    background: #f4f7fa;
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
        position: relative;
        margin-left: 80px;
        margin-right: 30px;
        .template-selector-tips {
            position: absolute;
            left: 0;
            top: 0;
            margin-left: 264px;
            margin-top: 9px;
        }
    }
}
.operation-area {
    margin: 20px 0;
    .task-create-btn {
        min-width: 120px;
    }
}
.advanced-search {
    margin: 0;
}
.functor-fieldset {
    width: 100%;
    margin-bottom: 20px;
    padding: 8px;
    border: 1px solid $commonBorderColor;
    background: #fff;
    .functor-query-content {
        display: flex;
        flex-wrap: wrap;
        .query-content {
            min-width: 420px;
            padding: 10px;
            @media screen and (max-width: 1420px){
                min-width: 380px;
            }
            .query-span {
                float: left;
                min-width: 130px;
                margin-right: 12px;
                height: 32px;
                line-height: 32px;
                font-size: 14px;
                text-align: right;
                @media screen and (max-width: 1420px){
                    min-width: 100px;
                }
            }
            input {
                max-width: 260px;
                height: 32px;
                line-height: 32px;
            }
            .bk-date-range:after {
                height: 32px;
                line-height: 32px;
            }
            .bk-selector-icon.clear-icon {
                top:6px;
            }
            /deep/ .bk-selector {
                max-width: 260px;
                display: inline-block;
            }
            input::-webkit-input-placeholder{
                color: $formBorderColor;
            }
            input:-moz-placeholder {
                color: $formBorderColor;
            }
            input::-moz-placeholder {
                color: $formBorderColor;
            }
            input:-ms-input-placeholder {
                color: $formBorderColor;
            }
            input,.bk-selector,.bk-date-range {
                min-width: 260px;
            }
            .search-input {
                width: 260px;
                height: 32px;
                padding: 0 10px 0 10px;
                font-size: 14px;
                border: 1px solid $commonBorderColor;
                line-height: 32px;
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
            .bk-selector-search-item > input {
                min-width: 249px;
            }
            .bk-date-range {
                display: inline-block;
                width: 260px;
            }
        }
        .query-button {
            padding: 10px;
            min-width: 450px;
            @media screen and (max-width: 1420px) {
                min-width: 390px;
            }
            text-align: center;
            .query-cancel {
                margin-left: 5px;
            }
            .bk-button {
                height: 32px;
                line-height: 32px;
            }
        }
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
            padding: 11px;
            text-align: left;
            border-bottom: 1px solid $commonBorderColor;
        }
        td {
            color: #63656e
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
            padding-left: 20px;
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
