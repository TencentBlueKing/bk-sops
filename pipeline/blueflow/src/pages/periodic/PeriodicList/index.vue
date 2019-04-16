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
    <div class="periodic-container">
        <div class="list-wrapper">
            <BaseTitle :title="i18n.periodicTask"></BaseTitle>
            <BaseSearch
                v-model="periodicName"
                :inputPlaceholader="i18n.periodicNamePlaceholder"
                @onShow="onAdvanceShow"
                @input="onSearchInput">
            </BaseSearch>
            <div class="periodic-search" v-show="isAdvancedSerachShow">
                <fieldset class="periodic-fieldset">
                    <div class="periodic-query-content">
                        <div class="query-content">
                            <span class="query-span">{{i18n.creator}}</span>
                            <input class="search-input" v-model="creator" :placeholder="i18n.creatorPlaceholder"/>
                        </div>
                        <div class="query-content">
                            <span class="query-span">{{i18n.enabled}}</span>
                            <bk-selector
                                :placeholder="i18n.enabledPlaceholder"
                                :list="enabledList"
                                :selected.sync="enabledSync"
                                :searchable="true"
                                :allow-clear="true"
                                @clear="onClearSelectedEnabled"
                                @item-selected="onSelectEnabled">
                            </bk-selector>
                        </div>
                        <div class="query-button">
                            <bk-button class="query-primary" type="primary" @click="getPeriodicList">{{i18n.query}}</bk-button>
                            <bk-button class="query-cancel" @click="onResetForm">{{i18n.reset}}</bk-button>
                        </div>
                    </div>
                </fieldset>
            </div>
            <div class="periodic-table-content">
                <table v-bkloading="{isLoading: listLoading, opacity: 1}">
                    <thead>
                        <tr>
                            <th class="periodic-id">ID</th>
                            <th class="periodic-name">{{ i18n.periodicName }}</th>
                            <th class="periodic-name">{{ i18n.periodicTemplate }}</th>
                            <th class="periodic-cron">{{ i18n.periodicRule }}</th>
                            <th class="periodic-time">{{ i18n.lastRunAt }}</th>
                            <th class="periodic-creator">{{ i18n.creator }}</th>
                            <th class="periodic-total-run-count">{{ i18n.totalRunCount }}</th>
                            <th class="periodic-enabled">{{ i18n.enabled }}</th>
                            <th class="periodic-operation">{{ i18n.operation }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(item) in periodicList" :key="item.id">
                            <td class="periodic-id">{{item.id}}</td>
                            <td class="periodic-name" :title="item.name">{{item.name}}</td>
                            <td class="periodic-name" :title="item.name">
                                <router-link
                                    :title="item.task_template_name"
                                    :to="`/template/edit/${cc_id}/?template_id=${item.template_id}`">
                                    {{item.task_template_name}}
                                </router-link>
                            </td>
                            <td class="periodic-cron" :title="splitPeriodicCron(item.cron)">{{splitPeriodicCron(item.cron)}}</td>
                            <td class="periodic-time">{{item.last_run_at || '--'}}</td>
                            <td class="periodic-creator">{{item.creator}}</td>
                            <td class="periodic-total-run-count">{{ item.total_run_count }}</td>
                            <td class="periodic-status">
                               <span :class="item.enabled? 'bk-icon icon-check-circle-shape': 'common-icon-dark-circle-pause'"></span>
                                {{item.enabled? i18n.start: i18n.pause}}
                            </td>
                            <td class="periodic-operation">
                                <a
                                    href="javascript:void(0);"
                                    :class="['periodic-pause-btn', {'periodic-start-btn':!item.enabled}]"
                                    @click="onSetEnable(item)">
                                    {{!item.enabled? i18n.start: i18n.pause}}
                                </a>
                                <a
                                    href="javascript:void(0);"
                                    :class="['periodic-bk-btn', {'periodic-bk-disable': item.enabled}]"
                                    :title="item.enabled ? i18n.editTitle : ''"
                                    @click="onModifyCronPeriodic(item)">
                                    {{ i18n.edit }}
                                </a>
                                <bk-dropdown-menu>
                                    <i slot="dropdown-trigger" class="bk-icon icon-more drop-icon-ellipsis"></i>
                                    <ul class="bk-dropdown-list" slot="dropdown-content">
                                        <li>
                                            <a href="javascript:void(0);" @click="onDeletePeriodic(item.id, item.name)">{{ i18n.delete }}</a>
                                        </li>
                                        <li>
                                            <router-link :to="`/taskflow/home/${cc_id}/?template_id=${item.template_id}&create_method=periodic`">
                                                {{ i18n.executeHistory }}
                                            </router-link>
                                        </li>
                                    </ul>
                                </bk-dropdown-menu>
                            </td>
                        </tr>
                        <tr v-if="!periodicList || !periodicList.length" class="empty-tr">
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
        <ModifyPeriodicDialog
            v-if="isModifyDialogShow"
            :loading="modifyDialogLoading"
            :constants="constants"
            :cron="selectedCron"
            :taskId="selectedPeriodicId"
            :isModifyDialogShow="isModifyDialogShow"
            @onModifyPeriodicConfirm="onModifyPeriodicConfirm"
            @onModifyPeriodicCancel="onModifyPeriodicCancel">
        </ModifyPeriodicDialog>
        <DeletePeriodicDialog
            v-if="isDeleteDialogShow"
            :isDeleteDialogShow="isDeleteDialogShow"
            :templateName="selectedTemplateName"
            :deleting="deleting"
            @onDeletePeriodicConfirm="onDeletePeriodicConfirm"
            @onDeletePeriodicCancel="onDeletePeriodicCancel">
        </DeletePeriodicDialog>
    </div>
    
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapMutations, mapActions } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import { NAME_REG, TIMING_REG } from '@/constants/index.js'
import toolsUtils from '@/utils/tools.js'
import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
import BaseTitle from '@/components/common/base/BaseTitle.vue'
import BaseSearch from '@/components/common/base/BaseSearch.vue'
import NoData from '@/components/common/base/NoData.vue'
import BaseInput from '@/components/common/base/BaseInput.vue'
import ModifyPeriodicDialog from './ModifyPeriodicDialog.vue'
import DeletePeriodicDialog from './DeletePeriodicDialog.vue'
export default {
    name: 'PeriodicList',
    components: {
        CopyrightFooter,
        BaseTitle,
        BaseSearch,
        NoData,
        BaseInput,
        ModifyPeriodicDialog,
        DeletePeriodicDialog
    },
    props: ['cc_id'],
    data () {
        return {
            i18n: {
                lastRunAt: gettext("上次运行时间"),
                periodicRule: gettext("周期规则"),
                periodicTask: gettext('周期任务'),
                advanceSearch: gettext('高级搜索'),
                creator: gettext("创建人"),
                operation: gettext("操作"),
                start: gettext("启动"),
                delete: gettext("删除"),
                edit: gettext('编辑'),
                pause: gettext('暂停'),
                totalRunCount: gettext('运行次数'),
                total: gettext("共"),
                item: gettext("条记录"),
                comma: gettext("，"),
                currentPageTip: gettext("当前第"),
                page: gettext("页"),
                periodicNamePlaceholder: gettext('请输入任务名称'),
                creatorPlaceholder: gettext('请输入创建人'),
                statusPlaceholder: gettext('请选择状态'),
                enabled: gettext('状态'),
                periodicName: gettext('名称'),
                editTitle: gettext('请暂停任务后再执行编辑操作'),
                enabledPlaceholder: gettext('请选择状态'),
                periodicTemplate: gettext('流程模板'),
                executeHistory: gettext('执行历史'),
                query: gettext('搜索'),
                reset: gettext('清空')
            },
            listLoading: true,
            deleting: false,
            currentPage: 1,
            totalPage: 1,
            countPerPage: 15,
            totalCount: 0,
            isDeleteDialogShow: false,
            isAdvancedSerachShow: false,
            creator: undefined,
            enabled: undefined,
            enabledList: [
                {'id': 'true', 'name': gettext('启动')},
                {'id': 'false', 'name': gettext('暂停')}
            ],
            selectedPeriodicId: undefined,
            periodicList: [],
            isModifyDialogShow: false,
            selectedCron: undefined,
            constants: undefined,
            modifyDialogLoading: false,
            selectedTemplateName: undefined,
            periodicName: undefined,
            enabledSync: -1
        }
    },
    created () {
        this.getPeriodicList()
        this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
    },
    methods: {
        ...mapActions('periodic/', [
            'loadPeriodicList',
            'setPeriodicEnable',
            'getPeriodic',
            'deletePeriodic'
        ]),
        async getPeriodicList () {
            this.listLoading = true
            try {
                const data = {
                    limit: this.countPerPage,
                    offset: (this.currentPage - 1) * this.countPerPage,
                    task__name__contains: this.periodicName,
                    task__celery_task__enabled: this.enabled,
                    task__creator__contains: this.creator,
                    task__name__contains: this.periodicName
                }
                const periodicListData = await this.loadPeriodicList(data)
                const list = periodicListData.objects
                this.periodicList = list
                this.totalCount = periodicListData.meta.total_count
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
        searchInputhandler () {
            this.currentPage = 1
            this.getPeriodicList()
        },
        onDeletePeriodic (id, name) {
            this.isDeleteDialogShow = true
            this.selectedDeleteTaskId = id
            this.selectedTemplateName = name
        },
        onPageChange (page) {
            this.currentPage = page
            this.getPeriodicList()
        },
        onSelectEnabled (enabled) {
            this.enabled = enabled
        },
        async onSetEnable (item) {
            try {
                const data = {
                    'taskId': item.id,
                    'enabled': !item.enabled
                }
                const periodicData = await this.setPeriodicEnable(data)
                if (periodicData.result) {
                    const periodic = this.periodicList.find(periodic => periodic.id === item.id)
                    periodic.enabled = !periodic.enabled
                }
            } catch (e) {
                errorHandler(e, this)
            }
        },
        onModifyCronPeriodic (item) {
            const {enabled, id: taskId, cron} = item
            if (enabled) {
                return
            }
            const splitCron = this.splitPeriodicCron(cron)
            this.selectedCron = splitCron
            this.selectedPeriodicId = taskId
            this.getPeriodicConstant(taskId)
            this.isModifyDialogShow = true
        },
        onModifyPeriodicCancel () {
            this.isModifyDialogShow = false
        },
        onModifyPeriodicConfirm () {
            this.isModifyDialogShow = false
            this.getPeriodicList()
        },
        async getPeriodicConstant (taskId) {
            this.modifyDialogLoading = true
            const data = {
                'taskId': taskId
            }
            const periodic = await this.getPeriodic(data)
            this.constants = periodic.form
            this.modifyDialogLoading = false
        },
        onDeletePeriodicConfirm () {
            this.deleteSelecedPeriodic()
        },
        async deleteSelecedPeriodic () {
            if (this.deleting) {
                return
            }
            try {
                this.deleting = true
                await this.deletePeriodic(this.selectedDeleteTaskId)
                this.$bkMessage({
                    'message': gettext('删除周期任务成功'),
                    'theme': 'success'
                })
                this.isDeleteDialogShow = false
                // 最后一页最后一条删除后，往前翻一页
                if (
                    this.currentPage > 1 &&
                    this.totalPage === this.currentPage &&
                    this.totalCount - (this.totalPage - 1) * this.countPerPage === 1
                ) {
                    this.currentPage -= 1
                }
                this.getPeriodicList()
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.deleting = false
            }
        },
        onDeletePeriodicCancel () {
            this.isDeleteDialogShow = false
        },
        onClearSelectedEnabled () {
            this.enabled = undefined
        },
        splitPeriodicCron (cron) {
            return cron.split('(')[0].trim()
        },
        onResetForm () {
            this.periodicName = undefined
            this.creator = undefined
            this.enabled = undefined
            this.enabledSync = -1
        },
        onAdvanceShow () {
            this.isAdvancedSerachShow = !this.isAdvancedSerachShow
        }
    }
}
</script>
<style lang='scss'>
@import '@/scss/config.scss';
.periodic-container {
    min-width: 1320px;
    min-height: calc(100% - 50px);
    background: $whiteNodeBg;
}
.list-wrapper {
    padding: 0 60px;
    min-height: calc(100vh - 240px);
    .advanced-search {
        margin: 20px 0px;
    }
}
.periodic-fieldset {
    width: 100%;
    margin-bottom: 15px;
    border: 1px solid $commonBorderColor;
    background: #ffffff;
    .periodic-query-content {
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
            .bk-selector {
                display: inline-block;
                width: 260px;
            }
            // 浏览兼容样式
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
            .bk-selector-search-item > input {
                min-width: 249px;
            }
            .search-input {
                width: 260px;
                height: 32px;
                padding: 0 32px 0 10px;
                font-size: 14px;
                color: $greyDefault;
                border: 1px solid $formBorderColor;
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
            .search-input.placeholder {
                color: $formBorderColor;
            }
        }
    }
}
.query-button {
    padding: 10px;
    min-width: 450px;
    @media screen and (max-width: 1420px) {
        min-width: 390px;
    }
    text-align: center;
    .bk-button {
        height: 32px;
        line-height: 32px;
    }
    .query-cancel {
        margin-left: 5px;
    }
}
.periodic-table-content {
    margin-top: 25px;
    table {
        width: 100%;
        border: 1px solid #ebebeb;
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
        .periodic-id {
            width: 80px;
        }
        .periodic-name {
            text-align: left;
            text-overflow: ellipsis;
            white-space: nowrap;
            word-break: break-all;
            overflow: hidden;
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
        @media screen and (min-width: 1420px) {
            .periodic-time {
                width: 220px;
            }
        }
        @media screen and (max-width: 1420px) {
            .periodic-time {
                width: 130px;
            }
            td[class="periodic-time"] {
                height: 60px;
            }
        }
        .periodic-cron {
            width: 200px;
            text-overflow: ellipsis;
            white-space: nowrap;
            word-break: break-all;
            overflow: hidden;
        }
        .periodic-creator {
            width: 110px;
        }
        .periodic-total-run-count {
            width: 92px;
        }
        .periodic-enabled {
            width: 100px;
        }
        .periodic-status {
            width: 100px;
            .icon-check-circle-shape {
                color: $greenDefault;
            }
        }
        .common-icon-dark-circle-pause {
            color: #FF9C01;
            border-radius: 20px;
            font-size: 12px;
        }
        .periodic-operation {
            width: 180px;
            .periodic-bk-btn {
                color: #3C96FF;
                padding: 5px;
                font-size: 12px;
            }
            .periodic-pause-btn {
                padding: 5px;
                color: #3C96FF;
                font-size: 12px;
            }
            .periodic-start-btn {
                color: #3C96FF;
                font-size: 12px;
                padding: 5px;
            }
            .periodic-bk-disable {
                color:#cccccc;
                padding: 5px;
                cursor: not-allowed;
            }

        }
        .drop-icon-ellipsis {
            position: absolute;
            top: -13px;
            font-size: 18px;
            cursor: pointer;
            &:hover {
                color: #3c96ff;
            }
        }
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
.btn-size-mini {
    height: 24px;
    line-height: 22px;
    padding: 0 11px;
    font-size: 12px;
}
.bk-dropdown-menu .bk-dropdown-list > li > a {
    font-size: 12px;
}
</style>
