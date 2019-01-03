/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="template-container">
        <div class="list-wrapper">
            <div class="template-table-content">
                <div class="operation-area clearfix">
                    <router-link class="bk-button bk-primary create-template" :to="`/template/new/${cc_id}`">{{ i18n.new }}</router-link>
                    <div class="template-search">
                        <input class="search-input" :placeholder="i18n.placeholder" v-model="searchStr" @input="onSearchInput"/>
                        <i class="common-icon-search"></i>
                    </div>
                </div>
            </div>
            <div class="template-table-content" v-bkloading="{isLoading: listLoading, opacity: 1}">
                <table>
                    <thead>
                        <tr>
                            <th class="template-id">ID</th>
                            <th class="template-name">{{ i18n.name }}</th>
                            <th class="template-type">{{ i18n.type }}</th>
                            <th class="update-time">{{ i18n.update_time }}</th>
                            <th class="template-creator">{{ i18n.creator }}</th>
                            <th class="template-operation">{{ i18n.operation }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in templateList" :key="item.id">
                            <td class="template-id">{{item.id}}</td>
                            <td class="template-name">
                                <router-link
                                    :title="item.name"
                                    :to="`/template/edit/${cc_id}/?template_id=${item.id}`">
                                    {{item.name}}
                                </router-link>
                            </td>
                            <td class="template-type">{{item.category_name}}</td>
                            <td class="update-time">{{item.edit_time}}</td>
                            <td class="template-creator">{{item.creator_name}}</td>
                            <td class="template-operation">
                                <router-link
                                    class="bk-button bk-primary btn-size-mini"
                                    :to="`/template/newtask/${cc_id}/selectnode/?template_id=${item.id}`">
                                    {{ i18n.new_task }}
                                </router-link>
                                <router-link
                                    class="bk-button bk-warning btn-size-mini"
                                    :to="`/template/edit/${cc_id}/?template_id=${item.id}`">
                                    {{ i18n.edit }}
                                </router-link>
                                <router-link
                                    class="bk-button bk-default btn-size-mini"
                                    :to="`/template/clone/${cc_id}/?template_id=${item.id}`">
                                    {{ i18n.clone }}
                                </router-link>
                                <bk-button size="mini" @click="onManageAuthority(item.id)">{{ i18n.authority }}</bk-button>
                                <bk-button type="danger" size="mini" @click="onDeleteTemplate(item.id)">{{ i18n.delete }}</bk-button>
                                <router-link
                                    class="bk-button bk-default btn-size-mini"
                                    :to="`/taskflow/home/${cc_id}/?template_id=${item.id}`">
                                    {{ i18n.executeHistory }}
                                </router-link>
                            </td>
                        </tr>
                        <tr v-if="!templateList || !templateList.length" class="empty-tr">
                            <td colspan="7">
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
        <ImportTemplateDialog
            v-if="isImportDialogShow"
            :isImportDialogShow="isImportDialogShow"
            @onImportConfirm="onImportConfirm"
            @onImportCancel="onImportCancel">
        </ImportTemplateDialog>
        <ExportTemplateDialog
            v-if="isExportDialogShow"
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
            <div slot="content">{{i18n.deleleTip}}</div>
        </bk-dialog>
        <AuthorityManageDialog
            v-if="isAuthorityDialogShow"
            :isAuthorityDialogShow="isAuthorityDialogShow"
            :templateId="theAuthorityManageId"
            :pending="pending.authority"
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
import NoData from '@/components/common/base/NoData.vue'
export default {
    name: 'TemplateList',
    components: {
        CopyrightFooter,
        ImportTemplateDialog,
        ExportTemplateDialog,
        AuthorityManageDialog,
        NoData
    },
    props: ['cc_id'],
    data () {
        return {
            i18n: {
                placeholder: gettext("请输入ID或流程名称"),
                flows: gettext("流程模板"),
                new: gettext("新建流程"),
                name: gettext("流程名称"),
                type: gettext("分类"),
                update_time: gettext("更新时间"),
                creator: gettext("创建人"),
                operation: gettext("操作"),
                new_task: gettext("新建任务"),
                edit: gettext("编辑"),
                clone: gettext("克隆"),
                authority: gettext("权限管理"),
                delete: gettext("删除"),
                executeHistory: gettext("执行历史"),
                deleleTip: gettext("确认删除该模板流程？"),
                import_v1_template: gettext("导入 V1 模板"),
                export: gettext("导出流程"),
                import: gettext("导入流程"),
                total: gettext("共"),
                item: gettext("条记录"),
                comma: gettext("，"),
                currentPageTip: gettext("当前第"),
                page: gettext("页")
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
            pending: {
                export: false, // 导出
                delete: false, // 删除
                authority: false // 权限管理
            }
        }
    },
    computed: {
        ...mapState({
            'site_url': state => state.site_url,
            'templateList': state => state.templateList.templateListData,
            'businessBaseInfo': state => state.template.businessBaseInfo,
            'v1_import_flag': state => state.v1_import_flag
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
            this.listLoading = true
            try {
                const data = {
                    limit: this.countPerPage,
                    offset: (this.currentPage - 1) * this.countPerPage,
                    q: this.searchStr
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
            try {
                const data = await this.loadBusinessBaseInfo()
                this.setBusinessBaseInfo(data)
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.businessInfoLoading = false
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
                const resp = await this.templateExport(JSON.stringify(list))
                if (resp.result) {
                    this.isExportDialogShow = false
                    this.getTemplateList()
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
        onDeleteTemplate (id) {
            this.theDeleteTemplateId = id
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
                await this.deleteTemplate(this.theDeleteTemplateId)
                this.theDeleteTemplateId = undefined
                this.isDeleteDialogShow = false
                await this.getTemplateList()
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
        }
    }
}
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
.template-container {
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
    .create-template {
        height: 32px;
        line-height: 32px;
    }
    .template-search {
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
.template-table-content {
    table {
        width: 100%;
        border: 1px solid $commonBorderColor;
        border-collapse: collapse;
        font-size: 14px;
        background: $whiteDefault;
        table-layout: fixed;
        tr:not(.empty-tr):hover {
            background: $whiteNodeBg;
        }
        th,td {
            padding: 10px;
            text-align: center;
            border: 1px solid $commonBorderColor;
        }
        th {
            background: $whiteNodeBg;
        }
        .template-id {
            width: 80px;
        }
        .template-name {
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
        .template-type {
            width: 110px;
        }
        .update-time {
            width: 220px;
        }
        .template-creator {
            width: 110px;
        }
        .template-operation {
            width: 460px;
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
</style>

