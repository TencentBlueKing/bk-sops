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
        :title="i18n.title"
        :auto-close="false"
        :value="isEditDialogShow"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div class="app-edit-content" v-bkloading="{ isLoading: templateLoading, opacity: 1 }">
            <div class="common-form-item">
                <label class="required">{{i18n.template}}</label>
                <div class="common-form-content">
                    <bk-select
                        v-model="appData.appTemplate"
                        class="bk-select-inline"
                        :searchable="true"
                        :placeholder="i18n.statusPlaceholder"
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
                    <span v-show="appTemplateEmpty" class="common-error-tip error-msg">{{i18n.templateTips}}</span>
                </div>
            </div>
            <div class="common-form-item">
                <label class="required">{{i18n.appName}}</label>
                <div class="common-form-content">
                    <bk-input
                        v-model="appData.appName"
                        v-validate.disable="appNameRule"
                        name="appName"
                        class="bk-input-inline"
                        :clearable="true">
                    </bk-input>
                    <span v-show="errors.has('appName')" class="common-error-tip error-msg">{{ errors.first('appName') }}</span>
                </div>
            </div>
            <div class="common-form-item">
                <label>{{i18n.scheme}}</label>
                <div class="common-form-content">
                    <bk-select
                        v-model="appData.appScheme"
                        class="bk-select-inline"
                        :searchable="true"
                        :placeholder="i18n.statusPlaceholder"
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
                            content: i18n.schemeTips,
                            placements: ['left'],
                            customClass: 'offset-left-tooltip',
                            width: 400,
                            zIndex: 1501 }">
                    </i>
                </div>
            </div>
            <div class="common-form-item">
                <label>{{i18n.appDesc}}</label>
                <div class="common-form-content">
                    <textarea
                        class="app-desc"
                        name="appDesc"
                        v-model="appData.appDesc"
                        v-validate="appDescRule">
                    </textarea>
                    <span v-show="errors.has('appDesc')" class="common-error-tip error-msg">{{ errors.first('appDesc') }}</span>
                </div>
            </div>
            <div class="common-form-item">
                <label>{{i18n.appLogo}}</label>
                <div class="common-form-content">
                    <label v-if="isLogoEmpty" for="app-logo" class="upload-btn-wrapper">
                        <i class="common-icon-add"></i>
                    </label>
                    <label v-else class="logo-wrapper" for="app-logo">
                        <span class="change-tips">{{i18n.change}}</span>
                        <div v-if="isShowDefaultLogo" class="default-logo">
                            <i class="common-icon-blueking"></i>
                        </div>
                        <div v-else>
                            <img class="logo-pic" :src="logoUrl" @error="useDefaultLogo" />
                        </div>
                    </label>
                    <div class="upload-tip">{{i18n.uploadTips}}</div>
                    <input ref="appLogo" type="file" id="app-logo" accept=".jpg, .jpeg, .png" @change="onLogoChange" />
                </div>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    export default {
        name: 'AppEditDialog',
        props: {
            'cc_id': String,
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
                        logo_url: undefined
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
                appData: {
                    appTemplate: '',
                    appName: '',
                    appScheme: '',
                    appDesc: '',
                    appLogo: undefined
                },
                logoUrl: '',
                isShowDefaultLogo: false,
                isLogoEmpty: !!this.isCreateNewApp,
                appNameRule: {
                    required: true,
                    max: STRING_LENGTH.APP_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                appDescRule: {
                    max: STRING_LENGTH.APP_DESCRIPTION_MAX_LENGTH
                },
                i18n: {
                    title: this.isCreateNewApp ? gettext('新建轻应用') : gettext('修改轻应用'),
                    template: gettext('流程模板'),
                    templateTips: gettext('流程模板不能为空'),
                    appName: gettext('应用名称'),
                    scheme: gettext('执行方案'),
                    schemeTips: gettext('当流程模板包含可选节点时，用户可以在新建任务时添加执行方案。这里选择执行方案后，创建的轻应用只能按照固定执行方案新建任务。'),
                    appDesc: gettext('应用简介'),
                    appLogo: gettext('应用LOGO'),
                    change: gettext('点击更换'),
                    uploadTips: gettext('只能上传JPG/PNG类型文件，建议大小为100px*100px，不能超过 100K')
                }
            }
        },
        watch: {
            currentAppData (val) {
                const { template_id, name, template_scheme_id, desc, logo_url } = val
                this.appData = {
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
                this.isShowDefaultLogo = true
            },
            async getTemplateList () {
                this.templateLoading = true
                try {
                    const templateListData = await this.loadTemplateList()
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
                        cc_id: this.cc_id,
                        template_id: this.appData.appTemplate
                    }
                    this.schemeList = await this.loadTaskScheme(data)
                    this.schemeLoading = false
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            onSelectTemplate (id) {
                this.appData.appTemplate = id
                this.appData.appName = this.templateList.find(item => item.id === id).name
                this.appTemplateEmpty = false
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
                    e.target.value = ''
                    this.appData.appLogo = []
                    this.$bkMessage({
                        message: gettext('图片大小不能超过 100K'),
                        theme: 'warning'
                    })
                } else {
                    this.isLogoEmpty = false
                    this.isShowDefaultLogo = false
                    this.logoUrl = window.URL.createObjectURL(pic)
                    this.appData.appLogo = pic
                }
            },
            onConfirm () {
                if (!this.appData.appTemplate) {
                    this.appTemplateEmpty = true
                    return
                }
                this.appData.appName = this.appData.appName.trim()
                this.$validator.validateAll().then((result) => {
                    if (!result) return
                    this.$emit('onEditConfirm', this.appData)
                })
            },
            onCancel () {
                this.$emit('onEditCancel')
                this.errors.clear()
                this.appTemplateEmpty = false
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.app-edit-content {
    padding: 30px;
    .common-form-content {
        position: relative;
        margin-right: 30px;
    }
    .scheme-tooltip {
        position: absolute;
        right: -20px;
        top: 10px;
        color: #c4c6cc;
        &:hover {
            color: #f4aa1a;
        }
    }
    .app-desc {
        width: 100%;
        height: 80px;
        border: 1px solid $commonBorderColor;
        outline: none;
        resize: none;
        &:hover {
            border-color: #c0c4cc;
        }
        &:focus {
            border-color: #3c96ff;
        }
    }
    .upload-btn-wrapper {
        display: block;
        width: 60px;
        height: 60px;
        line-height: 60px;
        color: $commonBorderColor;
        background: $whiteDefault;
        border: 2px dashed $commonBorderColor;
        text-align: center;
        cursor: pointer;
        &:hover {
            color: #3c96ff;
            border-color: #3c96ff;
        }
        .common-icon-add {
            font-size: 38px;
            vertical-align: -10px;
        }
    }
    .logo-wrapper {
        display: block;
        position: relative;
        width: 60px;
        height: 60px;
        border: 1px solid $commonBorderColor;
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
        .logo-pic {
            width: 60px;
            height: 60px;
            border-radius: 6px;
        }
    }
    .default-logo {
        width: 59px;
        height: 59px;
        text-align: center;
        border: 1px dashed #1b7cef;
        border-radius: 6px;
        .common-icon-blueking {
            display: inline-block;
            margin-top: 10px;
            color: #1b7cef;
            font-size: 40px;
        }
    }
    .upload-tip {
        margin-top: 10px;
        font-size: 12px;
    }
    #app-logo {
        visibility: hidden;
    }
}
</style>
