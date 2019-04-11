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
    <div class="template-container">
        <div class="list-wrapper">
            <BaseTitle :title="common ? i18n.commonFlow : i18n.businessFlow"></BaseTitle>
            <div class="template-table-content">
                <div class="operation-area clearfix">
                    <router-link
                        class="bk-button bk-primary create-template"
                        v-show="!isNewTaskCommonTemplate"
                        :to="getNewTemplateUrl()">
                        {{i18n.new}}
                    </router-link>
                    <bk-button
                        type="default"
                        class="template-btn"
                        size="small"
                        v-show="!isNewTaskCommonTemplate"
                        @click="onExportTemplate">
                        {{i18n.export}}
                    </bk-button>
                    <bk-button
                        type="default"
                        class="template-btn"
                        size="small"
                        v-show="!isNewTaskCommonTemplate"
                        @click="onImportTemplate">
                        {{ i18n.import }}
                    </bk-button>
                    <div class="template-advanced-search">
                        <BaseSearch
                            class="base-search"
                            v-model="flowName"
                            :inputPlaceholader="i18n.templateNamePlaceholder"
                            @onShow="onAdvanceShow"
                            @input="onSearchInput">
                        </BaseSearch>
                    </div>
                </div>
            </div>
            <div class="template-search" v-show="isAdvancedSerachShow">
                <fieldset class="template-fieldset">
                    <div class="template-query-content">
                        <div class="query-content">
                            <span class="query-span">{{i18n.type}}</span>
                            <bk-selector
                                :placeholder="i18n.templateCategoryPlaceholder"
                                :is-loading="categoryLoading"
                                :list="templateCategoryList"
                                :selected.sync="templateCategorySync"
                                :setting-key="'value'"
                                :display-key="'name'"
                                :allow-clear="true"
                                :searchable="true"
                                @clear="onClearCategory"
                                @item-selected="onSelectedCategory">
                            </bk-selector>
                        </div>
                        <div class="query-content">
                            <span class="query-span">{{i18n.updateTime}}</span>
                            <bk-date-range
                                ref="bkRanger"
                                :range-separator="'-'"
                                :quick-select="false"
                                :start-date.sync="editStartTime"
                                :end-date.sync="editEndTime"
                                @change="onChangeEditTime">
                            </bk-date-range>
                        </div>
                        <div class="query-content" v-if="!common_template">
                            <span class="query-span">{{i18n.subflowUpdate}}</span>
                            <bk-selector
                                :placeholder="i18n.select"
                                :list="selectSubprocessUpdateList"
                                :selected.sync="subprocessUpdateSync"
                                :allow-clear="true"
                                @clear="onClearSubprocessUpdate"
                                @item-selected="onSelectedSubprocessUpdate">
                            </bk-selector>
                        </div>
                        <div class="query-content">
                            <span class="query-span">{{i18n.creator}}</span>
                            <input class="search-input" v-model="creator" :placeholder="i18n.creatorPlaceholder"/>
                        </div>
                        <div class="query-button">
                            <bk-button class="query-primary" type="primary" @click="getTemplateList">{{i18n.query}}</bk-button>
                            <bk-button class="query-cancel" @click="onResetForm">{{i18n.reset}}</bk-button>
                        </div>
                    </div>
                </fieldset>
            </div>
            <div class="template-table-content" v-bkloading="{isLoading: listLoading, opacity: 1}">
                <table>
                    <thead>
                        <tr>
                            <th class="template-id">ID</th>
                            <th class="template-name">{{ i18n.name }}</th>
                            <th class="template-type">{{ i18n.type }}</th>
                            <th class="update-time">{{ i18n.updateTime }}</th>
                            <th v-if="!common_template" class="subflow-update">{{ i18n.subflowUpdate }}</th>
                            <th class="template-creator">{{ i18n.creator }}</th>
                            <th class="template-operation">{{ i18n.operation }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in templateList" :key="item.id">
                            <td class="template-id">{{item.id}}</td>
                            <td class="template-name">
                                <router-link
                                    v-if="!common || !common_template"
                                    :title="item.name"
                                    :to="getEditTemplateUrl(item.id)">
                                    {{item.name}}
                                </router-link>
                                <p v-else>{{item.name}}</p>
                            </td>
                            <td class="template-type">{{item.category_name}}</td>
                            <td class="update-time">{{item.edit_time}}</td>
                            <td v-if="!common_template" :class="['subflow-update', {'subflow-has-update': item.subprocess_has_update}]">
                                {{getSubflowContent(item)}}
                            </td>
                            <td class="template-creator">{{item.creator_name}}</td>
                            <td class="template-operation" v-if="!common && !common_template">
                                <!-- 业务流程按钮 -->
                                <router-link
                                    class="create-template-btn"
                                    :to="getNewTaskUrl(item.id)">
                                    {{ i18n.newTemplate }}
                                </router-link>
                                <router-link
                                    class="create-template-btn"
                                    :to="getEditTemplateUrl(item.id)">
                                    {{ i18n.edit }}
                               </router-link>
                               <bk-dropdown-menu>
                                <i slot="dropdown-trigger" class="bk-icon icon-more drop-icon-ellipsis"></i>
                                   <ul class="bk-dropdown-list" slot="dropdown-content">
                                        <li>
                                            <router-link :to="getCloneUrl(item.id)">{{ i18n.clone }}</router-link>
                                        </li>
                                        <li>
                                            <a href="javascript:void(0);" @click="onManageAuthority(item.id)">{{ i18n.authority }}</a>
                                        </li>
                                        <li>
                                            <router-link :to="getExecuteHistoryUrl(item.id)">{{ i18n.executeHistory }}</router-link>
                                        </li>
                                        <li>
                                            <a href="javascript:void(0);" @click="onDeleteTemplate(item.id, item.name)">{{ i18n.delete }}</a>
                                        </li>
                                   </ul>
                               </bk-dropdown-menu>
                            </td>
                            <td class="template-operation" v-else-if="common_template || !common">
                                <!-- 嵌套在业务流程页面中的公共流程，通过查询条件切换 -->
                                <router-link
                                    class="create-template-btn"
                                    :to="getNewTaskUrl(item.id)">
                                    {{ i18n.newTemplate }}
                                </router-link>
                               <bk-dropdown-menu>
                                   <i slot="dropdown-trigger" class="bk-icon icon-more drop-icon-ellipsis"></i>
                                    <ul class="bk-dropdown-list" slot="dropdown-content">
                                        <li>
                                            <a href="javascript:void(0);" @click="onManageAuthority(item.id)">{{ i18n.authority }}</a>
                                        </li>
                                        <li>
                                            <router-link :to="getExecuteHistoryUrl(item.id)">{{ i18n.executeHistory }}</router-link>
                                        </li>
                                    </ul>
                               </bk-dropdown-menu>
                            </td>
                            <td class="template-operation" v-else-if="common">
                                <!-- 公共流程首页 -->
                                <router-link class="create-template-btn" :to="getEditTemplateUrl(item.id)">{{ i18n.edit}}</router-link>
                                <bk-dropdown-menu>
                                    <i slot="dropdown-trigger" class="bk-icon icon-more drop-icon-ellipsis"></i>
                                    <ul class="bk-dropdown-list" slot="dropdown-content">
                                        <li>
                                            <router-link :to="getCloneUrl(item.id)">{{ i18n.clone }}</router-link>
                                        </li>
                                        <li>
                                            <a href="javascript:void(0);" @click="onDeleteTemplate(item.id, item.name)">{{i18n.delete}}</a>
                                        </li>
                                    </ul>
                                </bk-dropdown-menu>
                            </td>
                        </tr>
                        <tr v-if="!templateList || !templateList.length" class="empty-tr">
                            <td colspan="7">
                                <div class="empty-data"><NoData :message="i18n.empty" /></div>
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
        <ImportTemplateDialog
            v-if="isImportDialogShow"
            :common="common"
            :isImportDialogShow="isImportDialogShow"
            @onImportConfirm="onImportConfirm"
            @onImportCancel="onImportCancel">
        </ImportTemplateDialog>
         <ExportTemplateDialog
            v-if="isExportDialogShow"
            :common="common"
            :isExportDialogShow="isExportDialogShow"
            :businessInfoLoading="businessInfoLoading"
            :exportPending="pending.export"
            @onExportConfirm="onExportConfirm"
            @onExportCancel="onExportCancel">
        </ExportTemplateDialog>
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
            <div slot="content" class="dialog-content" v-bkloading="{isLoading: pending.delete, opacity: 1}">
                {{i18n.deleleTip + '"' + deleteTemplateName + '"' + '?' }}
            </div>
        </bk-dialog>
        <AuthorityManageDialog
            v-if="isAuthorityDialogShow"
            :isAuthorityDialogShow="isAuthorityDialogShow"
            :templateId="theAuthorityManageId"
            :pending="pending.authority"
            :common="common_template"
            @onAuthorityConfirm="onAuthorityConfirm"
            @onAuthorityCancel="onAuthorityCancel">
        </AuthorityManageDialog>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapMutations, mapActions } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import toolsUtils from '@/utils/tools.js'
import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
import ImportTemplateDialog from './ImportTemplateDialog.vue'
import ExportTemplateDialog from './ExportTemplateDialog.vue'
import AuthorityManageDialog from './AuthorityManageDialog.vue'
import BaseTitle from '@/components/common/base/BaseTitle.vue'
import BaseSearch from '@/components/common/base/BaseSearch.vue'
import NoData from '@/components/common/base/NoData.vue'
// moment用于时区使用
import moment from 'moment-timezone'
export default {
    name: 'TemplateList',
    components: {
        CopyrightFooter,
        ImportTemplateDialog,
        ExportTemplateDialog,
        AuthorityManageDialog,
        BaseTitle,
        BaseSearch,
        NoData
    },
    props: ['cc_id', 'common', 'common_template'],
    data () {
        return {
            i18n: {
                placeholder: gettext("请输入ID或流程名称"),
                businessFlow: gettext("业务流程"),
                commonFlow: gettext('公共流程'),
                new: gettext("新建"),
                name: gettext("流程名称"),
                type: gettext("分类"),
                updateTime: gettext("更新时间"),
                subflowUpdate: gettext("子流程更新"),
                creator: gettext("创建人"),
                operation: gettext("操作"),
                newTemplate: gettext("新建任务"),
                edit: gettext("编辑"),
                clone: gettext("克隆"),
                authority: gettext("权限管理"),
                delete: gettext("删除"),
                executeHistory: gettext("执行历史"),
                deleleTip: gettext("确认删除"),
                import_v1_template: gettext("导入 V1 模板"),
                export: gettext("导出"),
                import: gettext("导入"),
                total: gettext("共"),
                item: gettext("条记录"),
                comma: gettext("，"),
                currentPageTip: gettext("当前第"),
                page: gettext("页"),
                yes: gettext("是"),
                no: gettext("否"),
                empty: gettext("无数据，若您不是运维人员，请尝试联系运维人员为您添加模板权限"),
                templateNamePlaceholder: gettext('请输入流程名称'),
                templateCategoryPlaceholder: gettext('请选择分类'),
                subprocessUpdatePlaceholder: gettext('请选择子流程更新'),
                creatorPlaceholder: gettext('请输入创建人'),
                templateType: gettext('来源'),
                templateTypePlaceholder: gettext('请选择来源'),
                select: gettext('请选择'),
                query: gettext('搜索'),
                reset: gettext('清空'),
                templateName: gettext('名称'),
                advanceSearch: gettext('高级搜索'),
                searchName: gettext('搜索流程名称')
            },
            listLoading: true,
            businessInfoLoading: true, // 模板分类信息 loading
            searchStr: '',
            currentPage: 1,
            totalPage: 1,
            countPerPage: 15,
            totalCount: 0,
            isDeleteDialogShow: false,
            isImportDialogShow: false,
            isExportDialogShow: false,
            isAuthorityDialogShow: false,
            theDeleteTemplateId: undefined,
            theAuthorityManageId: undefined,
            isAdvancedSerachShow: false,
            pending: {
                export: false, // 导出
                delete: false, // 删除
                authority: false // 权限管理
            },
            flowName: undefined,
            templateCategorySync: -1,
            templateCategoryList: [],
            subprocessUpdateSync: '',
            category: undefined,
            editStartTime: undefined,
            editEndTime: undefined,
            selectSubprocessUpdateList: [
                {'id': 0, name: gettext('是'), value: true},
                {'id': 1, name: gettext('否'), value: false},
                {'id': 2, name: gettext('无子流程'), value: 'no'}
            ],
            subprocessUpdateList: [
                {'id': 1, 'name': gettext('是')},
                {'id': 0, 'name': gettext('否')}
            ],
            isSubprocessUpdated: undefined,
            isHasSubprocess: undefined,
            creator: undefined,
            templateType: this.common_template,
            deleteTemplateName: ''
        }
    },
    computed: {
        ...mapState({
            'site_url': state => state.site_url,
            'templateList': state => state.templateList.templateListData,
            'businessBaseInfo': state => state.template.businessBaseInfo,
            'v1_import_flag': state => state.v1_import_flag,
            'businessTimezone': state => state.businessTimezone
        })
    },
    created () {
        this.getTemplateList()
        this.getBusinessBaseInfo()
        this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
    },
    methods: {
        ...mapActions('template/', [
            'loadBusinessBaseInfo'
        ]),
        ...mapActions('templateList/', [
            'loadTemplateList',
            'deleteTemplate',
            'saveTemplatePersons',
            'templateImport',
            'templateExport'
        ]),
        ...mapMutations('template/', [
            'setBusinessBaseInfo'
        ]),
        ...mapMutations('templateList/', [
            'setTemplateListData'
        ]),
        async getTemplateList () {
            if (this.editStartTime === '') {
                this.editStartTime = undefined
            }
            this.listLoading = true
            try {
                const data = {
                    limit: this.countPerPage,
                    offset: (this.currentPage - 1) * this.countPerPage,
                    common: this.common,
                    pipeline_template__name__contains: this.flowName,
                    pipeline_template__creator__contains: this.creator,
                    category: this.category,
                    subprocess_has_update: this.isSubprocessUpdated,
                    has_subprocess: this.isHasSubprocess
                }
                if (this.templateType === 'common') {
                    // 公共流程
                    data['common'] = 1
                    this.isNewTaskCommonTemplate = true
                } else {
                    // 业务流程
                    this.isNewTaskCommonTemplate = false
                }
                if (this.editEndTime) {
                    if (this.isNewTaskCommonTemplate) {
                        data['pipeline_template__edit_time__gte'] = moment(this.editStartTime).format('YYYY-MM-DD')
                        data['pipeline_template__edit_time__lte'] = moment(this.editEndTime).add('1','d').format('YYYY-MM-DD')
                        // 无时区的公共流程使用本地的时间
                    } else {
                        data['pipeline_template__edit_time__gte'] = moment.tz(this.editStartTime, this.businessTimezone).format('YYYY-MM-DD')
                        data['pipeline_template__edit_time__lte'] = moment.tz(this.editEndTime, this.businessTimezone).add('1','d').format('YYYY-MM-DD')
                    }
                }
                const templateListData = await this.loadTemplateList(data)
                const list = templateListData.objects
                this.setTemplateListData(list)
                this.totalCount = templateListData.meta.total_count
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
        async getBusinessBaseInfo () {
            this.businessInfoLoading = true
            this.categoryLoading = true
            try {
                const data = await this.loadBusinessBaseInfo()
                this.setBusinessBaseInfo(data)
                this.templateCategoryList = data.task_categories
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.businessInfoLoading = false
                this.categoryLoading = false
            }
        },
        searchInputhandler () {
            this.currentPage = 1
            this.getTemplateList()
        },
        onImportTemplate () {
            this.isImportDialogShow = true
        },
        onImportConfirm () {
            this.isImportDialogShow = false
            this.getTemplateList()
        },
        onImportCancel () {
            this.isImportDialogShow = false
        },
        onExportTemplate () {
            this.isExportDialogShow = true
        },
        async onExportConfirm (list) {
            if (this.pending.export) return
            this.pending.export = true
            try {
                const data = {
                    common: this.common,
                    list: JSON.stringify(list)
                }
                const resp = await this.templateExport(data)
                if (resp.result) {
                    this.isExportDialogShow = false
                } else {
                    errorHandler(resp, this)
                }
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.pending.export = false
            }
        },
        onExportCancel () {
            this.isExportDialogShow = false
        },
        onDeleteTemplate (id, name) {
            this.theDeleteTemplateId = id
            this.deleteTemplateName = name
            this.isDeleteDialogShow = true
        },
        onPageChange (page) {
            this.currentPage = page
            this.getTemplateList()
        },
        onManageAuthority (id) {
            this.isAuthorityDialogShow = true
            this.theAuthorityManageId = id
        },
        async onDeleteConfirm () {
            if (this.pending.delete) return
            this.pending.delete = true
            try {
                const data = {
                    templateId: this.theDeleteTemplateId,
                    common: this.common
                }
                await this.deleteTemplate(data)
                this.theDeleteTemplateId = undefined
                this.isDeleteDialogShow = false
                // 最后一页最后一条删除后，往前翻一页
                if (
                    this.currentPage > 1 &&
                    this.totalPage === this.currentPage &&
                    this.totalCount - (this.totalPage - 1) * this.countPerPage === 1
                ) {
                    this.currentPage -= 1
                }
                this.getTemplateList()
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.pending.delete = false
            }
        },
        onDeleteCancel () {
            this.theDeleteTemplateId = undefined
            this.isDeleteDialogShow = false
        },
        async onAuthorityConfirm (data) {
            if (this.pending.authority) return
            this.pending.authority = true
            try {
                await this.saveTemplatePersons(data)
                this.isAuthorityDialogShow = false
                this.theAuthorityManageId = undefined
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.pending.authority = false
            }
        },
        onAuthorityCancel () {
            this.isAuthorityDialogShow = false
            this.theAuthorityManageId = undefined
        },
        // 获取编辑按钮的跳转链接
        getEditTemplateUrl (id) {
            let url = `/template/edit/${this.cc_id}/?template_id=${id}`
            if (this.common) {
                url += '&common=1'
            }
            return url
        },
        // 获取新建模板的跳转链接
        getNewTemplateUrl () {
            let url = `/template/new/${this.cc_id}`
            if (this.common) {
                url += '/?&common=1'
            }
            return url
        },
        // 获取新建任务的跳转链接
        getNewTaskUrl (id) {
            let url = `/template/newtask/${this.cc_id}/selectnode/?template_id=${id}`
            if (this.common || this.common_template) {
                url += '&common=1'
            }
            return url
        },
        getExecuteHistoryUrl (id) {
            let url = `/taskflow/home/${this.cc_id}/?template_id=${id}`
            if (this.common || this.common_template) {
                url += '&common=1'
            }
            return url
        },
        getCloneUrl (id) {
            let url = `/template/clone/${this.cc_id}/?template_id=${id}`
            if (this.common || this.common_template) {
                url += '&common=1'
            }
            return url
        },
        // 清除查询的分类选择
        onClearCategory () {
            this.templateCategorySync = -1
            this.category = undefined
        },
        // 选择查询的分类
        onSelectedCategory (name, value) {
            this.category = name
        },
        onClearSubprocessUpdate () {
            this.isSubprocessUpdated = undefined
            this.isHasSubprocess = undefined
        },
        onSelectedSubprocessUpdate (id, data) {
            if (data.value === 'no') {
                this.isHasSubprocess = false
                this.isSubprocessUpdated = undefined
            } else {
                this.isHasSubprocess = true
                this.isSubprocessUpdated = data.value
            }
        },
        onChangeEditTime (oldValue, newValue) {
            const dateArray = newValue.split(' - ')
            this.editStartTime = dateArray[0]
            this.editEndTime = dateArray[1]
        },
        // 重置查询表单
        onResetForm () {
            this.$refs.bkRanger.clear()
            this.isSubprocessUpdated = undefined
            this.isHasSubprocess = undefined
            this.templateCategorySync = -1
            this.category = undefined
            this.flowName = undefined
            this.creator = undefined
            this.editStartTime = undefined
            this.editEndTime = undefined
            this.isHasSubprocess = undefined
            this.isSubprocessUpdated = undefined
            this.subprocessUpdateSync = ''
        },
        // 获得子流程展示内容
        getSubflowContent (item) {
            if (!item.has_subprocess) {
                return '--'
            }
            return item.subprocess_has_update ? this.i18n.yes : this.i18n.no
        },
        onAdvanceShow () {
            this.isAdvancedSerachShow = !this.isAdvancedSerachShow
        }
    }
}
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
.template-container {
    min-width: 1320px;
    min-height: calc(100% - 50px);
    background: $whiteNodeBg;
    .dialog-content {
        word-break: break-all;
    }
    .bk-selector-icon.clear-icon {
        top: 6px;
    }
}
.list-wrapper {
    padding: 0 60px;
    min-height: calc(100vh - 240px);
}
.template-fieldset {
    width: 100%;
    margin: 0;
    border: 1px solid $commonBorderColor;
    background: $whiteDefault;
    margin-bottom: 15px;
    .template-query-content {
        display: flex;
        flex-wrap: wrap;
        .query-content {
            min-width: 420px;
            @media screen and (max-width: 1420px){
                min-width: 380px;
            }
            padding: 10px;
            .query-span {
                float: left;
                min-width: 130px;
                margin-right: 12px;
                height: 32px;
                line-height: 32px;
                font-size: 14px;
                @media screen and (max-width: 1420px){
                    min-width: 100px;
                }
                text-align: right;
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
            input, .bk-selector, .bk-date-range {
                min-width: 260px;
            }
            .bk-selector-search-item > input {
                min-width: 249px;
            }
            .bk-date-range {
                display: inline-block;
                width: 260px;
                height: 32px;
                line-height: 32px;
            }
            /deep/ .bk-date-range input {
                height: 32px;
                line-height: 32px;
            }
            .search-input {
                width: 260px;
                height: 32px;
                padding: 0 10px 0 10px;
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
                }
            }
            .ommon-icon-search {
                position: relative;
                right: 15px;
                top: 11px;
                color:#dddddd;
            }
            .search-input.placeholder {
                color: $formBorderColor;
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
        .query-cancel {
            margin-left: 5px;
        }
    }
    .bk-button {
        height: 32px;
        line-height: 32px;
    }
}

.operation-area {
    margin: 20px 0;
    .create-template {
        height: 32px;
        line-height: 29px;
        font-size: 14px;
    }
    .template-btn {
        margin-left: 5px;
        color:#313238;
    }
    .template-search {
        height: 156px;
        background: #fff;
    }
    .common-icon-search {
        position: absolute;
        right: 15px;
        top: 8px;
        color: $commonBorderColor;
    }
    .template-advanced-search {
        float: right;
        .base-search {
            margin: 0px;
        }
    }
}
.template-table-content {
    table {
        width: 100%;
        border: 1px solid #dde4eb;
        border-collapse: collapse;
        font-size: 12px;
        background: $whiteDefault;
        table-layout: fixed;
        tr:not(.empty-tr):hover {
            background: $whiteNodeBg;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid $commonBorderColor;
        }
        th {
            background: $whiteNodeBg;
        }
        .template-id {
            width: 80px;
        }
        .template-name {
            text-align: left;
            a, p{
                display: block;
                width: 100%;
                text-overflow: ellipsis;
                white-space: nowrap;
                word-break: break-all;
                overflow: hidden;
            }
            a {
                color: $blueDefault;
            }
        }
        .template-type {
            width: 122px;
        }
        .update-time {
            width: 220px;
        }
        .subflow-update {
            width: 100px;
        }
        .subflow-has-update {
            color: $redDefault;
        }
        .template-creator {
            width: 110px;
        }
        .template-operation {
            width: 260px;
        }
    }
    .btn-size-mini {
        height: 24px;
        line-height: 22px;
        padding: 0 11px;
        font-size: 12px;
    }
    .create-template-btn {
        padding: 5px;
        color: #3c96ff;
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
    .empty-data {
        padding: 120px 0;
    }
}
.template-content-from {
    height: 156px;
    background: $whiteDefault;
    border-radius:2px;
    border: 1px solid #dde4eb;
}
.panagation {
    padding: 10px 20px;
    text-align: right;
    border: 1px solid #dde4eb;
    border-top: none;
    background: #ffff;
    .page-info {
        float: left;
        line-height: 36px;
        font-size: 12px;
    }
    .bk-page {
        display: inline-block;
    }
}
.bk-dropdown-menu .bk-dropdown-list > li > a {
    font-size: 12px;
}
 /deep/ .bk-selector-wrapper .bk-selector-input {
        height: 32px;
        line-height: 32px;
    }
.bk-page .page-item.disabled .page-button {
     color: #737987;
     &:hover {
          color: #737987;
     }
}
</style>

