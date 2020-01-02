/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="appmaker-page">
        <div class="page-content">
            <div class="appmaker-table-content">
                <BaseTitle :title="i18n.title"></BaseTitle>
                <div class="operation-wrapper">
                    <bk-button theme="primary" @click="onCreateApp">{{i18n.addApp}}</bk-button>
                    <AdvanceSearch
                        v-model="searchStr"
                        :input-placeholader="i18n.placeholder"
                        @onShow="onAdvanceShow"
                        @input="onSearchInput">
                    </AdvanceSearch>
                </div>
            </div>
            <div class="app-search" v-show="isAdvancedSerachShow">
                <fieldset class="appmaker-fieldset">
                    <div class="advanced-query-content">
                        <div class="query-content">
                            <span class="query-span">{{i18n.editor}}</span>
                            <bk-input
                                v-model="editor"
                                class="bk-input-inline"
                                :clearable="true"
                                :placeholder="i18n.editorPlaceholder">
                            </bk-input>
                        </div>
                        <div class="query-content">
                            <span class="query-span">{{i18n.editTime}}</span>
                            <bk-date-picker
                                :placeholder="i18n.dateRange"
                                :type="'daterange'"
                                v-model="selectedTime"
                                @change="onChangeEditTime">
                            </bk-date-picker>
                        </div>
                        <div class="query-button">
                            <div class="query-button">
                                <bk-button class="query-primary" theme="primary" @click="loadData">{{i18n.query}}</bk-button>
                                <bk-button class="query-cancel" @click="onResetForm">{{i18n.reset}}</bk-button>
                            </div>
                        </div>
                    </div>
                </fieldset>
            </div>
            <div v-bkloading="{ isLoading: loading, opacity: 1 }">
                <div v-if="appList.length" class="app-list clearfix">
                    <AppCard
                        v-for="item in appList"
                        :key="item.id"
                        :app-data="item"
                        :cc_id="cc_id"
                        @onCardEdit="onCardEdit"
                        @onCardDelete="onCardDelete"
                        @onOpenPermissions="onOpenPermissions" />
                </div>
                <div v-else class="empty-app-list">
                    <NoData>
                        <p>{{emptyTips}}</p>
                    </NoData>
                </div>
            </div>
        </div>
        <AppEditDialog
            :is-edit-dialog-show="isEditDialogShow"
            :is-create-new-app="isCreateNewApp"
            :cc_id="cc_id"
            :current-app-data="currentAppData"
            @onEditConfirm="onEditConfirm"
            @onEditCancel="onEditCancel">
        </AppEditDialog>
        <bk-dialog
            width="400"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :header-position="'left'"
            :title="i18n.delete"
            :value="isDeleteDialogShow"
            @confirm="onDeleteConfirm"
            @cancel="onDeleteCancel">
            <div class="delete-tips-dialog" v-bkloading="{ isLoading: pending.delete, opacity: 1 }">
                {{i18n.deleteTips}}
            </div>
        </bk-dialog>
        <bk-dialog
            width="800"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :header-position="'left'"
            :title="i18n.jurisdiction"
            :value="isPermissionsDialog"
            @cancel="onCloseWindows">
            <div class="permission-content-dialog" v-bkloading="{ isLoading: loadingAuthority, opacity: 1 }">
                <p class="jurisdiction-hint">{{i18n.jurisdictionHint}}</p>
                <div class="permission-item">
                    <span class="addJurisdiction">{{i18n.addJurisdiction }}:</span>
                    <span>{{createdTaskPerList || '--'}}</span>
                </div>
                <div class="permission-item">
                    <span class="getJurisdiction">{{i18n.getJurisdiction}}:</span>
                    <span>{{modifyParamsPerList || '--'}}</span>
                </div>
                <div class="permission-item">
                    <span class="executeJurisdiction">{{i18n.executeJurisdiction}}:</span>
                    <span>{{executeTaskPerList || '--'}}</span>
                </div>
            </div>
            <div slot="footer" class="exit-btn">
                <bk-button
                    theme="default"
                    @click="onCloseWindows">
                    {{i18n.close}}
                </bk-button>
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions, mapState } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import toolsUtils from '@/utils/tools.js'
    import NoData from '@/components/common/base/NoData.vue'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import AppCard from './AppCard.vue'
    import AppEditDialog from './AppEditDialog.vue'
    import AdvanceSearch from '@/components/common/base/AdvanceSearch.vue'
    // moment用于时区使用
    import moment from 'moment-timezone'
    export default {
        name: 'AppMaker',
        components: {
            BaseTitle,
            AppCard,
            NoData,
            AppEditDialog,
            AdvanceSearch
        },
        props: ['cc_id', 'common'],
        data () {
            return {
                loading: true,
                loadingAuthority: false,
                list: [],
                searchMode: false,
                searchList: [],
                searchStr: '',
                currentAppData: undefined,
                isCreateNewApp: false,
                isEditDialogShow: false,
                isDeleteDialogShow: false,
                isAdvancedSerachShow: false,
                editor: undefined,
                selectedTime: [],
                editStartTime: undefined,
                editEndTime: undefined,
                isPermissionsDialog: false,
                createdTaskPerList: undefined,
                modifyParamsPerList: undefined,
                executeTaskPerList: undefined,
                pending: {
                    edit: false,
                    delete: false
                },
                i18n: {
                    title: gettext('轻应用'),
                    addApp: gettext('新建'),
                    placeholder: gettext('请输入轻应用名称'),
                    jurisdiction: gettext('使用权限'),
                    jurisdictionHint: gettext('轻应用的使用权限与其引用的流程模版使用权限一致。调整其对应流程模版的使用权限，会自动在轻应用上生效。'),
                    addJurisdiction: gettext('新建任务权限'),
                    getJurisdiction: gettext('认领任务权限'),
                    executeJurisdiction: gettext('执行任务权限'),
                    delete: gettext('删除'),
                    deleteTips: gettext('确认删除轻应用？'),
                    close: gettext('关闭'),
                    editor: gettext('更新人'),
                    editorPlaceholder: gettext('请输入更新人'),
                    editTime: gettext('更新时间'),
                    query: gettext('搜索'),
                    reset: gettext('清空'),
                    dateRange: gettext('选择日期时间范围')
                }
            }
        },
        computed: {
            ...mapState({
                'businessTimezone': state => state.businessTimezone
            }),
            appList () {
                return this.searchMode ? this.searchList : this.list
            },
            emptyTips () {
                return this.searchMode ? gettext('未找到相关轻应用') : gettext('暂未添加轻应用')
            }
        },
        created () {
            this.loadData()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions('appmaker', [
                'loadAppmaker',
                'appmakerEdit',
                'appmakerDelete'
            ]),
            ...mapActions('templateList/', [
                'getTemplatePersons'
            ]),
            async loadData () {
                this.loading = true
                if (this.editStartTime === '') {
                    this.editStartTime = undefined
                }
                try {
                    const data = {
                        editor: this.editor || undefined
                    }
                    if (this.editEndTime) {
                        data['edit_time__gte'] = moment.tz(this.editStartTime, this.businessTimezone).format('YYYY-MM-DD')
                        data['edit_time__lte'] = moment.tz(this.editEndTime, this.businessTimezone).add('1', 'd').format('YYYY-MM-DD')
                    }
                    const resp = await this.loadAppmaker(data)
                    this.list = resp.objects
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.loading = false
                }
            },
            searchInputhandler () {
                if (this.searchStr.length) {
                    this.searchMode = true
                    const reg = new RegExp(this.searchStr, 'i')
                    this.searchList = this.list.filter(item => {
                        return reg.test(item.name)
                    })
                } else {
                    this.searchMode = false
                    this.searchList = []
                }
            },
            onCreateApp () {
                this.isEditDialogShow = true
                this.isCreateNewApp = true
                this.currentAppData = undefined
            },
            onCardEdit (app) {
                this.isEditDialogShow = true
                this.isCreateNewApp = false
                this.currentAppData = app
            },
            onOpenPermissions (app) {
                this.isPermissionsDialog = true
                this.loadTemplatePersons(app.template_id)
            },
            async loadTemplatePersons (id) {
                this.loadingAuthority = true
                try {
                    const data = {
                        templateId: id
                    }
                    const res = await this.getTemplatePersons(data)
                    if (res.result) {
                        this.createdTaskPerList = res.data.create_task.map(item => item.show_name).join('、')
                        this.modifyParamsPerList = res.data.fill_params.map(item => item.show_name).join('、')
                        this.executeTaskPerList = res.data.execute_task.map(item => item.show_name).join('、')
                        this.loadingAuthority = false
                    } else {
                        errorHandler(res, this)
                        return []
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            onCardDelete (app) {
                this.isDeleteDialogShow = true
                this.currentAppData = app
            },
            async onDeleteConfirm () {
                if (this.pending.delete) return
                this.pending.delete = true
                this.isDeleteDialogShow = false
                try {
                    await this.appmakerDelete(this.currentAppData.id)
                    this.loadData()
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.pending.delete = false
                }
            },
            onDeleteCancel () {
                this.isDeleteDialogShow = false
            },
            onCloseWindows () {
                this.isPermissionsDialog = false
            },
            async onEditConfirm (app) {
                if (this.pending.edit) return
                this.pending.edit = true
                const id = this.isCreateNewApp ? '0' : this.currentAppData.id
                try {
                    const formData = new FormData()
                    formData.append('id', id)
                    formData.append('template_id', app.appTemplate)
                    formData.append('name', app.appName)
                    formData.append('template_scheme_id', app.appScheme)
                    formData.append('desc', app.appDesc)
                    formData.append('logo', app.appLogo)
                    const resp = await this.appmakerEdit(formData)
                    if (resp.result) {
                        this.isEditDialogShow = false
                        this.loadData()
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.pending.edit = false
                }
            },
            onEditCancel () {
                this.isEditDialogShow = false
                this.currentAppData = {
                    template_id: '',
                    name: '',
                    template_scheme_id: '',
                    desc: '',
                    logo_url: undefined
                }
            },
            onAdvanceShow () {
                this.isAdvancedSerachShow = !this.isAdvancedSerachShow
            },
            onChangeEditTime (value) {
                this.editStartTime = value[0]
                this.editEndTime = value[1]
            },
            onResetForm () {
                this.editor = undefined
                this.selectedTime = []
                this.editStartTime = undefined
                this.editEndTime = undefined
                this.loadData()
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.bk-select-inline,.bk-input-inline {
    display: inline-block;
    width: 260px;
}
.appmaker-page {
    .page-content {
        padding: 0 60px 40px 60px;
    }
    @media screen and (max-width: 1560px) {
        .card-wrapper {
            width: 32.5%;
        }
        .card-particular .app-synopsis {
            width: 67%;
        }
        .card-wrapper:nth-child(3n) {
            margin-right: 0;
        }
    }
    @media screen and (min-width: 1561px) and (max-width: 1919px) {
        .card-wrapper {
            width: 24.265%;
        }
        .card-wrapper:nth-child(4n) {
            margin-right: 0;
        }
    }
    @media screen and (min-width: 1920px) {
        .app-list {
            max-width: 2150px;
        }
        .card-wrapper {
            width: 19.3%;
        }
        .card-wrapper:nth-child(5n) {
            margin-right: 0;
        }
    }
    .operation-wrapper {
        margin: 18px 0 20px;
        .bk-button {
            width: 120px;
            height: 32px;
            line-height: 32px;
        }
        .app-search {
            float: right;
            position: relative;
        }
        .search-input {
            width: 300px;
            height: 36px;
            padding: 0 40px 0 10px;
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
    .appmaker-fieldset {
        width: 100%;
        margin: 0;
        padding: 8px;
        border: 1px solid $commonBorderColor;
        background: $whiteDefault;
        margin-bottom: 15px;
        .advanced-query-content {
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
                    color: #dddddd;
                }
                .search-input.placeholder {
                    color: $formBorderColor;
                }
            }
        }
        .query-button {
            padding: 5px;
            min-width: 440px;
            @media screen and (max-width: 1420px) {
                min-width: 380px;
            }
            text-align: center;
            .query-cancel {
                margin-left: 5px;
            }
        }
    }
    .card-wrapper {
        float: left;
        margin: 0 14px 20px 0;
    }
    .empty-app-list {
        padding: 200px 0;
        background: $whiteDefault;
        border: 1px solid $commonBorderColor;
    }
    .exit-btn {
        float:right;
        .bk-button {
            width: 100px;
            height: 32px;
            line-height: 30px;
            margin-right: 24px;
            margin-bottom: 4px;
        }
    }
    .addJurisdiction, .getJurisdiction, .executeJurisdiction {
        margin-right: 10px;
    }
    .advanced-search {
        margin: 0px;
    }
}
.delete-tips-dialog {
    padding: 30px;
}
.permission-content-dialog {
    padding: 24px;
    .jurisdiction-hint {
        padding: 0 10PX;
        line-height: 32px;
        background: #f0f1f5;
        border-radius: 2px;
        font-size: 12px;
    }
    .permission-item {
        margin: 20px 0px;
    }
}
</style>
