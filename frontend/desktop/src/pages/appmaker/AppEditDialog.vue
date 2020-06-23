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
    <bk-dialog
        width="800"
        ext-cls="common-dialog"
        :theme="'primary'"
        :mask-close="false"
        :header-position="'left'"
        :title="dialogTitle"
        :auto-close="false"
        :value="isEditDialogShow"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div class="app-edit-content" v-bkloading="{ isLoading: templateLoading, opacity: 1 }">
            <div class="common-form-item">
                <label class="required">{{$t('流程模板')}}</label>
                <div class="common-form-content">
                    <bk-select
                        v-model="appData.appTemplate"
                        class="ui-form-item"
                        :searchable="true"
                        :placeholder="$t('请选择')"
                        :clearable="true"
                        :disabled="!isCreateNewApp"
                        @selected="onSelectTemplate">
                        <bk-option
                            v-for="(option, index) in templateList"
                            :key="index"
                            :id="option.id"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                    <span v-show="appTemplateEmpty" class="common-error-tip error-msg">{{$t('流程模板不能为空')}}</span>
                </div>
            </div>
            <div class="common-form-item">
                <label class="required">{{$t('应用名称')}}</label>
                <div class="common-form-content">
                    <bk-input
                        v-model="appData.appName"
                        v-validate.disable="appNameRule"
                        name="appName"
                        class="ui-form-item"
                        :clearable="true">
                    </bk-input>
                    <span v-show="errors.has('appName')" class="common-error-tip error-msg">{{ errors.first('appName') }}</span>
                </div>
            </div>
            <div class="common-form-item">
                <label>{{$t('执行方案')}}</label>
                <div class="common-form-content">
                    <bk-select
                        v-model="appData.appScheme"
                        class="ui-form-item"
                        :searchable="true"
                        :placeholder="$t('请选择')"
                        :clearable="true"
                        :is-loading="schemeLoading"
                        @selected="onSelectScheme">
                        <bk-option
                            v-for="(option, index) in schemeList"
                            :key="index"
                            :id="option.id"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                    <i
                        class="common-icon-info scheme-tooltip"
                        v-bk-tooltips="{
                            content: $t('当流程模板包含可选节点时，用户可以在新建任务时添加执行方案。这里选择执行方案后，创建的轻应用只能按照固定执行方案新建任务。'),
                            placements: ['left'],
                            customClass: 'offset-left-tooltip',
                            width: 400,
                            zIndex: 1501 }">
                    </i>
                </div>
            </div>
            <div class="common-form-item">
                <label>{{$t('应用LOGO')}}</label>
                <div class="common-form-content">
                    <div class="app-logo-content">
                        <div class="logo-body">
                            <span class="logo-wrapper">
                                <span
                                    class="change-tips"
                                    @click="onLogoClick">{{ $t('更改') }}</span>
                                <div>
                                    <img class="logo-pic" :src="logoUrl" @error="useDefaultLogo" />
                                </div>
                            </span>
                        </div>
                        <!-- 选择图标面板 -->
                        <div v-if="isChooseLogoPanelShow" class="choose-icon-panel">
                            <i
                                class="bk-icon icon-close-circle-shape"
                                @click="isChooseLogoPanelShow = false">
                            </i>
                            <div class="icon-panel-tab">
                                <span
                                    :class="['tab-item', { 'active': logoPanelActiveTab === 0 }]"
                                    @click="logoPanelActiveTab = 0">{{ $t('默认图标') }}</span>
                                <span
                                    :class="['tab-item', { 'active': logoPanelActiveTab === 1 }]"
                                    @click="logoPanelActiveTab = 1">{{ $t('自定义') }}</span>
                            </div>
                            <!-- 默认 -->
                            <div v-if="logoPanelActiveTab === 0" class="panel-content-default">
                                <ul class="default-icon-list">
                                    <li class="default-icon-item"
                                        v-for="item in 6"
                                        :key="item"
                                        :class="{ 'active': selectedLogoIndex === item }"
                                        @click="onChooseDefaultLogo(item)">
                                        <img
                                            :src="require(`@/assets/images/appmaker-default-icon-${item}.png`)"
                                            class="default-icon-img"
                                            alt="appmaker-default-icons" />
                                    </li>
                                </ul>
                            </div>
                            <!-- 自定义 -->
                            <div v-if="logoPanelActiveTab === 1" class="panel-content-customize">
                                <label v-if="isLogoEmpty" for="app-logo" class="upload-btn-wrapper">
                                    <i class="common-icon-add"></i>
                                </label>
                                <div v-else>
                                    <div class="upload-logo">
                                        <img class="logo-img" :src="logoUrl" @error="useDefaultLogo" />
                                        <label class="reload-btn" for="app-logo">{{ $t('重新上传') }}</label>
                                    </div>
                                </div>
                                <input ref="appLogo" type="file" id="app-logo" accept=".jpg, .jpeg, .png" @change="onLogoChange" />
                            </div>
                        </div>
                    </div>
                    <div class="upload-tip">{{$t('只能上传JPG/PNG类型文件，建议大小为100px*100px，不能超过 100K')}}</div>
                </div>
            </div>
            <div class="common-form-item">
                <label>{{$t('应用简介')}}</label>
                <div class="common-form-content">
                    <bk-input
                        class="app-desc"
                        name="appDesc"
                        type="textarea"
                        v-model="appData.appDesc"
                        v-validate="appDescRule">
                    </bk-input>
                    <span v-show="errors.has('appDesc')" class="common-error-tip error-msg">{{ errors.first('appDesc') }}</span>
                </div>
            </div>
        </div>
        <div slot="footer" class="dialog-footer">
            <div class="button-group">
                <bk-button
                    theme="primary"
                    :class="{
                        'btn-permission-disable': !hasConfirmPerm
                    }"
                    v-cursor="{ active: appData.appTemplate && !hasConfirmPerm }"
                    @click="onConfirm">
                    {{$t('确认')}}
                </bk-button>
                <bk-button type="default" @click="onCancel">{{$t('取消')}}</bk-button>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions } from 'vuex'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import permission from '@/mixins/permission.js'
    export default {
        name: 'AppEditDialog',
        mixins: [permission],
        props: {
            'project_id': [String, Number],
            'isCreateNewApp': Boolean,
            'isEditDialogShow': Boolean,
            'currentAppData': {
                type: Object,
                default () {
                    return {
                        template_id: '',
                        name: '',
                        template_scheme_id: '',
                        desc: '',
                        logo_url: undefined,
                        appActions: []
                    }
                }
            }
        },
        data () {
            return {
                templateLoading: true,
                schemeLoading: false,
                templateList: [],
                schemeList: [],
                appTemplateEmpty: false,
                isChooseLogoPanelShow: false,
                logoPanelActiveTab: 0,
                selectedLogoIndex: null, // 已选默认图标下标
                appData: {
                    appTemplate: '',
                    appName: '',
                    appScheme: '',
                    appDesc: '',
                    appActions: this.currentAppData ? this.currentAppData.auth_actions : [],
                    appLogo: undefined
                },
                logoUrl: '',
                isLogoLoadingError: false,
                isLogoEmpty: !!this.isCreateNewApp,
                appNameRule: {
                    required: true,
                    max: STRING_LENGTH.APP_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                appDescRule: {
                    max: STRING_LENGTH.APP_DESCRIPTION_MAX_LENGTH
                }
            }
        },
        computed: {
            dialogTitle () {
                return this.isCreateNewApp ? i18n.t('新建轻应用') : i18n.t('编辑轻应用')
            },
            btnPermission () {
                return this.isCreateNewApp ? ['flow_create_mini_app'] : ['mini_app_edit']
            },
            hasConfirmPerm () {
                return this.hasPermission(this.btnPermission, this.appData.appActions)
            },
            isShowDefaultLogo () {
                return this.isLogoLoadingError || !this.logoUrl
            }
        },
        watch: {
            isEditDialogShow () {
                this.isLogoEmpty = !!this.isCreateNewApp
                this.logoPanelActiveTab = 0
                this.selectedLogoIndex = null
                this.isChooseLogoPanelShow = false
            },
            isShowDefaultLogo: {
                handler (val) {
                    if (val) {
                        // 自动选择默认图标
                        this.onChooseDefaultLogo(1, false)
                    }
                },
                immediate: true
            },
            currentAppData: {
                handler (val) {
                    const { template_id, name, template_scheme_id, desc, logo_url, auth_actions } = val
                    this.appData = {
                        appActions: auth_actions,
                        appTemplate: template_id ? Number(template_id) : '',
                        appName: name,
                        appScheme: template_scheme_id ? Number(template_scheme_id) : '',
                        appDesc: desc,
                        appLogo: undefined
                    }
                    this.logoUrl = logo_url
                    if (template_id !== '') {
                        this.getTemplateScheme()
                    }
                },
                deep: true
            }
        },
        created () {
            this.getTemplateList()
        },
        methods: {
            ...mapActions('templateList', [
                'loadTemplateList'
            ]),
            ...mapActions('task/', [
                'loadTaskScheme'
            ]),
            useDefaultLogo () {
                this.isLogoLoadingError = true
            },
            async getTemplateList () {
                this.templateLoading = true
                try {
                    const templateListData = await this.loadTemplateList({ project__id: this.project_id })
                    this.templateList = templateListData.objects
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.templateLoading = false
                }
            },
            async getTemplateScheme () {
                this.schemeLoading = true
                try {
                    const data = {
                        project__id: this.project_id,
                        template_id: this.appData.appTemplate
                    }
                    this.schemeList = await this.loadTaskScheme(data)
                    this.schemeLoading = false
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            onSelectTemplate (id) {
                const template = this.templateList.find(item => item.id === id)
                this.appData.appTemplate = id
                this.appData.appName = template.name
                this.appTemplateEmpty = false
                this.appData.appScheme = ''
                this.appData.appActions = template.auth_actions
                this.getTemplateScheme()
            },
            onSelectScheme (id) {
                this.appData.appScheme = Number(id)
            },
            // logo 上传
            onLogoChange (e) {
                const pic = e.target.files[0]
                const size = pic.size
                if (size > 1024000) {
                    this.appData.appLogo = []
                    this.$bkMessage({
                        message: i18n.t('图片大小不能超过 100K'),
                        theme: 'warning'
                    })
                } else {
                    this.isLogoEmpty = false
                    this.isLogoLoadingError = false
                    this.logoUrl = window.URL.createObjectURL(pic)
                    this.appData.appLogo = pic
                }
                e.target.value = ''
            },
            onConfirm () {
                if (!this.appData.appTemplate) {
                    this.appTemplateEmpty = true
                    return
                }
                if (!this.hasConfirmPerm) {
                    let resourceData = {}
                    if (this.isCreateNewApp) {
                        const templateName = this.templateList.find(item => item.id === this.appData.appTemplate).name
                        resourceData = [{
                            flow: [{
                                id: this.appData.appTemplate,
                                name: templateName
                            }]
                        }]
                    } else {
                        resourceData = {
                            mini_app: [{
                                id: this.currentAppData.id,
                                name: this.currentAppData.name
                            }]
                        }
                    }
                    this.applyForPermission(this.btnPermission, this.appData.appActions, resourceData)
                    return
                }
                
                this.appData.appName = this.appData.appName.trim()
                this.$validator.validateAll().then((result) => {
                    if (!result) return
                    this.$emit('onEditConfirm', this.appData, this.resetAppData)
                })
            },
            onCancel () {
                this.$emit('onEditCancel')
                this.errors.clear()
                this.appTemplateEmpty = false
            },
            resetAppData () {
                this.appData = {
                    appTemplate: '',
                    appName: '',
                    appScheme: '',
                    appDesc: '',
                    appActions: [],
                    appLogo: undefined
                }
            },
            // 将base64转换为blob
            dataURLtoBlob (dataURI) {
                const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0]
                const byteString = atob(dataURI.split(',')[1])
                const arrayBuffer = new ArrayBuffer(byteString.length)
                const intArray = new Uint8Array(arrayBuffer)

                for (let i = 0; i < byteString.length; i++) {
                    intArray[i] = byteString.charCodeAt(i)
                }
                return new Blob([intArray], { type: mimeString })
            },
            // 将blob转换为file
            blobToFile (theBlob, fileName) {
                theBlob.lastModifiedDate = new Date()
                theBlob.name = fileName
                return theBlob
            },
            // 打开选择图标面板
            onLogoClick () {
                this.isChooseLogoPanelShow = !this.isChooseLogoPanelShow
                this.logoPanelActiveTab = this.isCreateNewApp ? 0 : 1
            },
            onChooseDefaultLogo (index, isSlected = true) {
                if (isSlected) {
                    this.selectedLogoIndex = index
                }
                const url = require(`@/assets/images/appmaker-default-icon-${index}.png`)
                const blob = this.dataURLtoBlob(url)
                const file = this.blobToFile(blob)
                file.name = `appmaker-default-icon-${index}`
                this.logoUrl = url
                this.appData.appLogo = file
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.common-error-tip {
    position: absolute;
    left: 0;
    bottom: -14px;
}
.common-form-item > label {
    font-weight: normal;
}
.app-edit-content {
    padding: 30px;
    .common-form-content {
        position: relative;
        margin-right: 30px;
    }
    .scheme-tooltip {
        position: absolute;
        right: -24px;
        top: 10px;
        color: #c4c6cc;
        &:hover {
            color: #f4aa1a;
        }
    }
    .app-desc {
        width: 100%;
        height: 80px;
        font-size: 12px;
    }
    .upload-btn-wrapper {
        display: block;
        width: 60px;
        height: 60px;
        line-height: 60px;
        color: $commonBorderColor;
        background: #dcdee5;
        text-align: center;
        cursor: pointer;
        &:hover {
            background: #c4c6cc;
        }
        .common-icon-add {
            font-size: 38px;
            vertical-align: -5px;
            color: #ffffff;
        }
    }
    .app-logo-content {
        position: relative;
        .logo-body {
            .logo-wrapper {
                display: block;
                position: relative;
                width: 60px;
                height: 60px;
                border-radius: 6px;
                &:hover {
                    .change-tips {
                        display: inline-block;
                    }
                }
                .change-tips {
                    display: none;
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 60px;
                    height: 60px;
                    line-height: 60px;
                    font-size: 12px;
                    color: $whiteDefault;
                    background: rgba(10, 10, 10, .85);
                    text-align: center;
                    border-radius: 6px;
                    cursor: pointer;
                }
            }
        }
        .choose-icon-panel {
            position: absolute;
            left: -7px;
            top: 80px;
            padding: 10px 20px;
            z-index: 1;
            width: 310px;
            height: 208px;
            background: #ffffff;
            border: 2px solid #c4c6cc;
            border-radius: 2px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, .15);
            .icon-close-circle-shape {
                position: absolute;
                right: 6px;
                top: 6px;
                width: 12px;
                height: 12px;
                text-align: center;
                line-height: 12px;
                color: #cecece;
                cursor: pointer;
                &:hover {
                    color: #979ba5;
                }
            }
            .icon-panel-tab {
                .tab-item {
                    display: inline-block;
                    padding: 6px 0;
                    font-size: 14px;
                    color: #63656e;
                    cursor: pointer;
                    &:not(:first-child) {
                        margin-left: 20px;
                    }
                    &.active {
                        color: #3a84ff;
                        border-bottom: 2px solid #3a84ff;
                    }
                }
            }
            .panel-content-default {
                .default-icon-list {
                    .default-icon-item {
                        float: left;
                        margin-top: 10px;
                        padding: 10px 7px;
                        width: 60px;
                        height: 60px;
                        border-radius: 2px;
                        cursor: pointer;
                        &:not(:nth-child(4n + 1)) {
                            margin-left: 8px;
                        }
                        &:hover {
                            border: 1px solid #e1ecff;
                        }
                        &.active {
                            border: 2px solid #3a84ff;
                        }
                        .default-icon-img {
                            width: 100%;
                            height: 100%;
                        }
                    }
                }
            }
            .panel-content-customize {
                .upload-logo {
                    position: relative;
                    margin-top: 10px;
                    padding: 10px 7px;
                    width: 62px;
                    height: 62px;
                    border-radius: 2px;
                    border: 2px solid #3a84ff;
                    .logo-img {
                        width: 100%;
                        height: 100%;
                    }
                    .reload-btn {
                        display: inline-block;
                        position: absolute;
                        left: -2px;
                        bottom: -26px;
                        width: 62px;
                        height: 16px;
                        line-height: 16px;
                        text-align: center;
                        font-size: 12px;
                        color: #ffffff;
                        background: #000000;
                        cursor: pointer;
                        opacity: 0.6;
                        &:hover {
                            opacity: 1;
                        }
                    }
                }
            }
        }
    }
    .default-logo {
        width: 59px;
        height: 59px;
        text-align: center;
        .default-icon {
            width: 100%;
            height: 100%;
        }
    }
    .logo-pic {
        width: 60px;
        height: 60px;
        border-radius: 6px;
    }
    .upload-tip {
        margin-top: 10px;
        font-size: 12px;
    }
    #app-logo {
        visibility: hidden;
    }
}
.dialog-footer {
    .bk-button {
        margin-left: 7px;
        min-width: 90px;
    }
}
</style>
