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
                <base-title :title="$t('轻应用')"></base-title>
                <div class="operation-wrapper">
                    <advance-search-form
                        :search-form="searchForm"
                        @onSearchInput="onSearchInput"
                        @submit="onSearchFormSubmit">
                        <template v-slot:operation>
                            <bk-button theme="primary" @click="onCreateApp">{{$t('新建')}}</bk-button>
                        </template>
                    </advance-search-form>
                </div>
            </div>
            <div v-bkloading="{ isLoading: loading, opacity: 1 }">
                <div v-if="appList.length" class="app-list clearfix">
                    <app-card
                        v-for="item in appList"
                        :key="item.id"
                        :app-data="item"
                        :app-resource="appResource"
                        :app-operations="appOperations"
                        :project_id="project_id"
                        :collected-loading="collectedLoading"
                        :collected-list="collectedList"
                        @onCardEdit="onCardEdit"
                        @onCardDelete="onCardDelete"
                        @getCollectList="getCollectList">
                    </app-card>
                </div>
                <div v-else-if="searchMode" class="empty-app-list">
                    <NoData>
                        <p>{{$t('未找到相关轻应用')}}</p>
                    </NoData>
                </div>
                <div v-else class="empty-app-content">
                    <div class="appmaker-info">
                        <h2 class="appmaker-info-title">{{$t('什么是轻应用？')}}</h2>
                        <p class="appmaker-info-text">{{$t('业务运维人员将日常工作标准化后，以标准运维中一个模板的形式提供给业务非技术人员使用，为了降低使用者的操作风险和使用成本，将该模板以独立SaaS应用的方式指定给授权者使用，这种不需要开发、零成本快速生成的SaaS应用称为“轻应用”。')}}</p>
                        <div class="appmaker-default-icons">
                            <img
                                v-for="item in 6"
                                :key="item"
                                :src="require(`@/assets/images/appmaker-default-icon-${item}.png`)"
                                class="default-icon-item"
                                alt="appmaker-default-icons">
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <AppEditDialog
            :is-edit-dialog-show="isEditDialogShow"
            :is-create-new-app="isCreateNewApp"
            :project_id="project_id"
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
            :title="$t('删除')"
            :value="isDeleteDialogShow"
            @confirm="onDeleteConfirm"
            @cancel="onDeleteCancel">
            <div class="delete-tips-dialog" v-bkloading="{ isLoading: pending.delete, opacity: 1 }">
                {{$t('确认删除轻应用？')}}
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapState } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import toolsUtils from '@/utils/tools.js'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    import AppCard from './AppCard.vue'
    import AppEditDialog from './AppEditDialog.vue'
    import NoData from '@/components/common/base/NoData.vue'
    // moment用于时区使用
    import moment from 'moment-timezone'
    const searchForm = [
        {
            type: 'input',
            key: 'editor',
            label: i18n.t('更新人'),
            placeholder: i18n.t('请输入更新人'),
            value: ''
        },
        {
            type: 'dateRange',
            key: 'updateTime',
            placeholder: i18n.t('选择日期时间范围'),
            label: i18n.t('更新时间'),
            value: []
        }
    ]
    export default {
        name: 'AppMaker',
        components: {
            NoData,
            BaseTitle,
            AppCard,
            AppEditDialog,
            AdvanceSearchForm
        },
        props: ['project_id', 'common'],
        data () {
            return {
                loading: true,
                collectedLoading: false,
                list: [],
                collectedList: [],
                searchMode: false,
                searchList: [],
                currentAppData: undefined,
                isCreateNewApp: false,
                isEditDialogShow: false,
                isDeleteDialogShow: false,
                pending: {
                    edit: false,
                    delete: false
                },
                appOperations: [],
                appResource: {},
                searchForm: searchForm,
                requestData: {
                    updateTime: [],
                    editor: '',
                    flowName: ''
                }
            }
        },
        computed: {
            ...mapState('project', {
                'timeZone': state => state.timezone
            }),
            appList () {
                return this.searchMode ? this.searchList : this.list
            }
        },
        created () {
            this.loadData()
            this.getCollectList()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions([
                'loadCollectList'
            ]),
            ...mapActions('appmaker', [
                'loadAppmaker',
                'appmakerEdit',
                'appmakerDelete'
            ]),
            async loadData () {
                this.loading = true
                try {
                    const { updateTime, editor } = this.requestData
                    const data = {
                        editor: editor || undefined,
                        project__id: this.project_id
                    }
                    if (updateTime[0] && updateTime[1]) {
                        data['edit_time__gte'] = moment.tz(updateTime[0], this.timeZone).format('YYYY-MM-DD')
                        data['edit_time__lte'] = moment.tz(updateTime[1], this.timeZone).add('1', 'd').format('YYYY-MM-DD')
                    }
                    const resp = await this.loadAppmaker(data)
                    this.list = resp.objects
                    this.appOperations = resp.meta.auth_operations
                    this.appResource = resp.meta.auth_resource
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.loading = false
                }
            },
            async getCollectList () {
                try {
                    this.collectedLoading = true
                    const res = await this.loadCollectList()
                    this.collectedList = res.objects
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.collectedLoading = false
                }
            },
            searchInputhandler (data) {
                this.requestData.flowName = data
                if (data.length) {
                    this.searchMode = true
                    const reg = new RegExp(this.requestData.flowName, 'i')
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
            async onEditConfirm (app, callback) {
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
                        typeof callback === 'function' && callback()
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
            onSearchFormSubmit (data) {
                this.requestData = data
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
        margin: 20px 0px;
        .bk-button {
            width: 120px;
            height: 32px;
            line-height: 32px;
        }
        .app-search {
            float: right;
            position: relative;
        }
    }
    .card-wrapper {
        float: left;
        margin: 0 14px 20px 0;
    }
    .add-appmaker-btn {
        margin: 20px 0;
        width: 120px;
    }
    .empty-app-list {
        padding: 200px 0;
        background: $whiteDefault;
        border: 1px solid $commonBorderColor;
    }
    .empty-app-content {
        padding: 160px 0;
        .appmaker-info {
            margin: 0 auto;
            width: 680px;
            .appmaker-info-title {
                margin-bottom: 30px;
                color: #63656e;
                font-size: 24px;
                font-weight: normal;;
                text-align: center;
            }
            .appmaker-info-text {
                padding-bottom: 30px;
                margin-bottom: 30px;
                line-height: 20px;
                color: #979ba5;
                font-size: 12px;
                border-bottom: 1px solid #dfe6ec;
            }
            .appmaker-default-icons {
                display: flex;
                align-items: center;
                justify-content: space-between;
                .default-icon-item {
                    max-height: 55px;
                }
            }
        }
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
