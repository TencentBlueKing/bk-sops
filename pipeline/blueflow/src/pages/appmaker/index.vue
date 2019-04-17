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
    <div class="appmaker-page" v-bkloading="{isLoading: false, opacity: 1}">
        <div class="page-content" v-if="!loading">
            <BaseTitle :title="i18n.title"></BaseTitle>
            <div class="operation-wrapper">
                <bk-button type="primary" @click="onCreateApp">{{i18n.addApp}}</bk-button>
                <div class="app-search">
                    <input class="search-input" :placeholder="i18n.placeholder" v-model="searchStr" @input="onSearchInput"/>
                    <i class="common-icon-search"></i>
                </div>
            </div>
            <div v-if="appList.length" class="app-list clearfix">
                <AppCard
                    v-for="item in appList"
                    :key="item.id"
                    :appData="item"
                    :cc_id="cc_id"
                    @onCardEdit="onCardEdit"
                    @onCardDelete="onCardDelete"
                    @onJurisdiction="onJurisdiction"/>
            </div>
            <div v-else class="empty-app-list">
                <NoData>
                    <p>{{emptyTips}}</p>
                </NoData>
            </div>
        </div>
        <!-- 编辑 -->
        <AppEditDialog
            v-if="isEditDialogShow"
            :isEditDialogShow="isEditDialogShow"
            :isCreateNewApp="isCreateNewApp"
            :cc_id="cc_id"
            :currentAppData="currentAppData"
            @onEditConfirm="onEditConfirm"
            @onEditCancel="onEditCancel">
        </AppEditDialog>
        <!-- 删除 -->
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
            <div slot="content" class="delete-tips" v-bkloading="{isLoading: pending.delete, opacity: 1}">
                {{i18n.deleteTips}}
            </div>
        </bk-dialog>
        <!-- 权限查看 -->
        <bk-dialog
            :quick-close="false"
            :ext-cls="'common-dialog'"
            :title="i18n.jurisdiction"
            width="800"
            padding="30px"
            :is-show.sync="isjurisdictionUser"
            @cancel="onSurveyCancel">
            <div slot="content" v-bkloading="{isLoading: loadingAauthority,opacity: 1}">
                <p class="jurisdictionHint">{{i18n.jurisdictionHint}}</p>
                <div class="box">
                    <span class="addJurisdiction">{{i18n.addJurisdiction}}{{':'}}</span>
                    <span>{{createdTaskPerList|| '--'}}</span>
                </div>
                <div class="box">
                    <span class="getJurisdiction">{{i18n.getJurisdiction}}{{':'}}</span>
                    <span>{{modifyParamsPerList|| '--'}}</span>
                </div>
                <div>
                    <span class="executeJurisdiction">{{i18n.executeJurisdiction}}{{':'}}</span>
                    <span>{{executeTaskPerList|| '--'}}</span>
                </div>
                <div class="exit-btn">
                    <div class="btn" @click ="onExit">{{i18n.close}}</div>
                </div>
            </div>
        </bk-dialog>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapActions } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import toolsUtils from '@/utils/tools.js'
import NoData from '@/components/common/base/NoData.vue'
import BaseTitle from '@/components/common/base/BaseTitle.vue'
import AppCard from './AppCard.vue'
import AppEditDialog from './AppEditDialog.vue'
export default {
    name: 'AppMaker',
    components: {
        BaseTitle,
        AppCard,
        NoData,
        AppEditDialog
    },
    props: ['cc_id'],
    data () {
        return {
            loading: true,
            loadingAauthority: false,
            list: [],
            searchMode: false,
            searchList: [],
            searchStr: '',
            currentAppData: undefined,
            isCreateNewApp: false,
            isEditDialogShow: false,
            isDeleteDialogShow: false,
            isjurisdictionUser: false,
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
                jurisdictionHint: gettext('“轻应用”的使用权限与其引用的“流程模版”使用权限一致。调整“轻应用”使用权限，可以调整其对应的“流程模版”使用权限。'),
                addJurisdiction: gettext('新建任务权限'),
                getJurisdiction: gettext('领取任务权限'),
                executeJurisdiction: gettext('执行任务权限'),
                delete: gettext('删除'),
                deleteTips: gettext('确认删除轻应用？'),
                close: gettext('关闭')
            }
        }
    },
    computed: {
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
            'getBizPerson',
            'getTemplatePersons'
        ]),
        async loadData () {
            this.loading = true
            try {
                const data = await this.loadAppmaker()
                this.list = data.objects
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
        // 卡牌创建
        onCreateApp () {
            this.isEditDialogShow = true
            this.isCreateNewApp = true
            this.currentAppData = undefined
        },
        // 卡牌编辑
        onCardEdit (app) {
            this.isEditDialogShow = true
            this.isCreateNewApp = false
            this.currentAppData = app
        },
        // 卡牌权限
        onJurisdiction (app) {
            this.isjurisdictionUser = true
            this.loadTemplatePersons(app.template_id)
        },
        async loadTemplatePersons (id) {
            this.loadingAauthority = true
            try {
                const data = {
                    templateId: id
                }
                const res = await this.getTemplatePersons(data)
                if (res.result) {
                    this.createdTaskPerList = res.data.create_task.map(item => item.show_name).join('、')
                    this.modifyParamsPerList = res.data.fill_params.map(item => item.show_name).join('、')
                    this.executeTaskPerList = res.data.execute_task.map(item => item.show_name).join('、')
                    this.loadingAauthority = false
                } else {
                    errorHandler(res, this)
                    return []
                }
            } catch (e) {
                errorHandler(e, this)
            }
        },
        // 卡牌删除
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
        onSurveyCancel () {
            this.isjurisdictionUser = false
        },
        onExit () {
            this.isjurisdictionUser = false
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
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.appmaker-page {
    min-width: 1320px;
    min-height: calc(100% - 50px);
    background: #f4f7fa;
    .page-content {
        width: 1200px;
        padding-bottom: 40px;
        overflow: hidden;
        margin: 0 auto;
    }
    @media screen and (max-width: 1505px) {
        .page-content {
            width: 1200px;
        }
        .card-wrapper:nth-child(3n) {
            margin-right: 0;
        }
    }
    @media screen and (min-width: 1506px) and (max-width: 1810px) {
        .page-content {
            width: 1505px;
        }
        .card-wrapper:nth-child(4n) {
            margin-right: 0;
        }
    }
    @media screen and (min-width: 1811px) {
        .page-content {
            width: 1810px;
        }
        .card-wrapper:nth-child(5n) {
            margin-right: 0;
        }
    }
    .operation-wrapper {
        margin: 18px 0 20px;
        .bk-button {
            width:120px;
            height:32px;
            line-height: 32px;
        }
        .app-search {
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
    .card-wrapper {
        float: left;
        margin: 0 20px 20px 0;
        // &:hover {
        //     box-shadow: -1px 1px 8px rgba(100, 100, 100, .15), 1px -1px 8px rgba(100, 100, 100, .15);
        // }
    }
    .empty-app-list {
        padding: 200px 0;
        background: $whiteDefault;
        border: 1px solid $commonBorderColor;
    }
    .jurisdictionHint {
        padding: 0 10PX;
        line-height: 32px;
        background:rgba(240,241,245,1);
        border-radius:2px;
        font-size:12px;
    }
    .box{
        margin: 20px 0px;
    }
    .exit-btn{
            width: 220px;
            height: 50px;
            top: 191px;
            left: 550px;
            position: absolute;
            background: #fafafa;
            .btn{
                float: right;
                margin: 8px 24px 0 0;
                width:100px;
                height:32px;
                font-size:14px;
                line-height: 32px;
                text-align: center;
                cursor: pointer;
                border-radius:2px;
                border:1px solid rgba(196,198,204,1);
            }
    }
    .addJurisdiction,.getJurisdiction,.executeJurisdiction{
        margin-right: 10px;
    }
}
</style>


