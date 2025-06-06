/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <bk-dialog
        class="import-dialog"
        width="739"
        :header-position="'left'"
        :mask-close="false"
        :ext-cls="'common-dialog'"
        :title="$t('导入') + 'DAT'"
        :value="isImportDialogShow"
        @cancel="onCancel">
        <div class="import-container" v-bkloading="{ isLoading: pending.submit, opacity: 1, zIndex: 100 }">
            <!-- 上传区域 -->
            <div v-if="!file" class="upload-file-area">
                <bk-upload
                    accept=".dat"
                    url=""
                    :limit="1"
                    :size="2048"
                    :tip="$t('支持DAT类型文件，文件小于2G')"
                    :custom-request="handleUpload">
                </bk-upload>
            </div>
            <div v-else class="import-wrapper">
                <div class="common-form-item">
                    <bk-alert :type="checkResult ? 'success' : 'error'">
                        <div slot="title">
                            {{ file.name }}
                            {{ checkResult ? $t('文件合法性检查通过。') : $t('文件不合法，请') }}
                            <label
                                :for="pending.upload ? '' : 'template-file'"
                                :class="['upload-tpl-btn', { 'is-disabled': pending.upload }]">
                                {{ $t('重新上传文件') }}
                            </label>
                            <input
                                ref="templateFile"
                                id="template-file"
                                type="file"
                                accept=".dat"
                                style="display: none;"
                                @change="onFileChange" />

                        </div>
                    </bk-alert>
                </div>
                <div class="common-form-item">
                    <label>{{ $t('导入列表') }}</label>
                    <div class="common-form-content">
                        <div class="template-head">
                            <span class="template-span">ID</span>
                            <span class="template-process-name">{{ $t('流程名称') }}</span>
                        </div>
                        <div class="template-fileList">
                            <table class="template-table">
                                <tbody>
                                    <template v-for="item in exportList">
                                        <tr
                                            v-if="!isChecked || overrideList.find(file => file.id === item.id )"
                                            :key="item.id"
                                            :class="{ 'template-table-conflict': overrideList.find(file => file.id === item.id ) }">
                                            <td class="conflict-id" :title="item.id">
                                                {{item.id}}
                                            </td>
                                            <td class="conflict-name">
                                                <span :title="item.name">{{item.name}}</span>
                                            </td>
                                        </tr>
                                    </template>
                                    <template v-if="isEmpty">
                                        <tr>
                                            <td colspan="2" class="p0">
                                                <NoData v-if="!pending.upload"></NoData>
                                                <div v-else class="uploading-tip">
                                                    <i class="common-icon-loading"></i>
                                                </div>
                                            </td>
                                        </tr>
                                    </template>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                <div class="common-content" v-show="dataConflict">
                    <div class="common-list-label">
                        <label class="common-list">{{$t('上传了')}}{{exportList.length}}{{$t('条流程')}}</label>
                        <label class="common-item" v-if="overrideList.length">{{$t('其中')}}{{overrideList.length}}{{$t('条流程与项目已有流程ID存在冲突')}}</label>
                    </div>
                    <div class="common-checkbox" @click="onShowConflicts">
                        <span :class="['checkbox', { checked: isChecked }]"></span>
                        <span>{{ $t('只显示冲突项') }}</span>
                    </div>
                </div>
                <div class="check-msg-title" id="checkMsgTitle">{{ $t('合法性检测结果') }}</div>
                <div class="check-msg">
                    <template v-if="!templateFileEmpty && !templateFileError && !templateFileErrorExt">{{ $t('合法性检查通过。') }}</template>
                    <template v-else>
                        <span
                            v-show="templateFileEmpty"
                            class="common-error-tip error-msg">
                            {{$t('模板文件上传为空')}}
                        </span>
                        <span
                            v-bk-tooltips.top="commonErrorMsg"
                            v-show="templateFileError"
                            class="common-error-tip error-msg multi-character-limit">
                            {{ commonErrorMsg }}
                        </span>
                        <span
                            v-show="templateFileErrorExt"
                            class="common-error-tip error-msg">
                            {{$t('该文件后缀不为.dat')}}
                        </span>
                    </template>
                </div>
            </div>
        </div>
        <div slot="footer" class="common-wrapper-btn">
            <div class="button-group">
                <bk-button v-if="file" theme="primary" :disabled="pending.submit" @click="onConfirm(true)">{{exportConflict}}</bk-button>
                <bk-button
                    v-if="file"
                    theme="default"
                    @click="onConfirm(false)"
                    :disabled="pending.submit"
                    v-cursor="{ active: common ? !hasCreateCommonTplPerm : !hasPermission(['flow_create'], authActions) }"
                    :class="{ 'btn-permission-disable': common ? !hasCreateCommonTplPerm : !hasPermission(['flow_create'], authActions) }">
                    {{overrideConflict}}
                </bk-button>
                <bk-button theme="default" @click="onCancel"> {{ $t('取消') }} </bk-button>
            </div>
        </div>
    </bk-dialog>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapState } from 'vuex'
    import NoData from '@/components/common/base/NoData.vue'
    import permission from '@/mixins/permission.js'

    export default {
        name: 'ImportDatTplDialog',
        components: {
            NoData
        },
        mixins: [permission],
        props: ['isImportDialogShow', 'common', 'authActions', 'hasCreateCommonTplPerm'],
        data () {
            return {
                active: true,
                file: null,
                filename: '',
                checkResult: true,
                exportList: [],
                overrideList: [],
                isChecked: false,
                overrideFormDisabled: true,
                uploaded: false,
                pending: {
                    upload: false,
                    submit: false
                },
                templateFileEmpty: false,
                templateFileError: false,
                templateFileErrorExt: false,
                dataConflict: false,
                commonErrorMsg: ''
            }
        },
        computed: {
            ...mapState({
                'site_url': state => state.site_url
            }),
            ...mapState('project', {
                'project_id': state => state.project_id,
                'projectName': state => state.projectName
            }),
            exportConflict () {
                return this.overrideList.length ? i18n.t('覆盖冲突项, 并提交') : i18n.t('覆盖ID相同的流程')
            },
            overrideConflict () {
                return this.overrideList.length ? i18n.t('保留两者, 并提交') : i18n.t('创建新流程')
            },
            isEmpty () {
                return !this.exportList.length || (this.isChecked && !this.overrideList.length)
            },
            uploadText () {
                return this.uploaded ? i18n.t('重新上传') : i18n.t('点击上传')
            }
        },
        methods: {
            ...mapActions('templateList/', [
                'templateUploadCheck',
                'templateImport'
            ]),
            async handleUpload (file) {
                this.resetErrorTips()
                if (this.pending.upload) {
                    return
                }
                const fileInfo = file.fileObj.origin
                if (fileInfo) {
                    this.file = fileInfo
                    this.uploaded = true
                    this.uploadCheck()
                }
            },
            async uploadCheck () {
                this.pending.upload = true
                this.dataConflict = true
                this.exportList = []
                this.overrideList = []
                this.overrideFormDisabled = true
                this.templateFileError = false
                try {
                    const data = {
                        formData: new FormData(),
                        common: this.common || undefined
                    }
                    data.formData.append('data_file', this.file)
                    const resp = await this.templateUploadCheck(data)
                    this.checkResult = resp.result
                    if (resp.result) {
                        const checkResult = resp.data
                        this.exportList = checkResult.new_template
                        this.overrideList = checkResult.override_template
                        this.templateFileError = false
                    } else {
                        this.commonErrorMsg = resp.message
                        this.templateFileError = true
                        this.pending.upload = false
                        this.dataConflict = false
                    }
                } catch (e) {
                    console.log(e)
                    this.templateFileError = true
                } finally {
                    this.pending.upload = false
                }
            },
            async importTemplate (isOverride) {
                this.pending.submit = true
                const formData = new FormData()
                formData.append('data_file', this.file)
                formData.append('override', isOverride)
                const data = {
                    formData: formData,
                    common: this.common || undefined
                }
                try {
                    const resp = await this.templateImport(data)
                    if (resp.result) {
                        this.$emit('onImportConfirm')
                        this.resetData()
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.submit = false
                }
            },
            onFileChange (e) {
                this.resetErrorTips()
                if (this.pending.upload) {
                    return
                }
                const file = e.target.files[0]
                if (file) {
                    if (file.size > 2 * 1024 * 1024 * 1024) {
                        this.$bkMessage({ message: i18n.t('上传失败，DAT类型文件最大为2G'), theme: 'error', delay: 10000 })
                        return
                    }
                    const filename = file.name
                    const ext = filename.substr(filename.lastIndexOf('.') + 1)
                    if (ext !== 'dat') {
                        this.templateFileErrorExt = true
                        this.file = null
                        return
                    }
                    this.file = file
                    this.uploaded = true
                    this.uploadCheck()
                }
            },
            onConfirm (isOverride) {
                if (this.pending.submit || this.pending.upload) {
                    return
                }
                if (!this.file) {
                    this.templateFileEmpty = true
                    // 防止错误重叠
                    this.templateFileError = false
                    this.templateFileErrorExt = false
                    return
                }
                if (!isOverride) {
                    const hasCreatePerm = this.common ? this.hasCreateCommonTplPerm : this.hasPermission(['flow_create'], this.authActions)
                    if (!hasCreatePerm) {
                        if (this.common) {
                            this.applyForPermission(['common_flow_create'])
                        } else {
                            const resourceData = {
                                project: [{
                                    id: this.project_id,
                                    name: this.projectName
                                }]
                            }
                            this.applyForPermission(['flow_create'], this.authActions, resourceData)
                        }
                        return
                    }
                }
                if (!this.templateFileErrorExt && !this.templateFileEmpty) {
                    this.importTemplate(isOverride)
                }
            },
            onShowConflicts () {
                this.isChecked = !this.isChecked
            },
            onCancel () {
                this.resetErrorTips()
                this.resetData()
                this.$emit('onImportCancel')
            },
            resetErrorTips () {
                this.templateFileEmpty = false
                this.templateFileErrorExt = false
                this.templateFileError = false
            },
            resetData () {
                this.file = null
                this.filename = ''
                this.exportList = []
                this.overrideList = []
                this.isChecked = false
                this.uploaded = false
                this.overrideFormDisabled = true
                this.templateFileEmpty = false
                this.templateFileError = false
                this.templateFileErrorExt = false
                this.dataConflict = false
                if (this.$refs.templateFile) {
                    this.$refs.templateFile.value = ''
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
@import "@/scss/config.scss";
@import "@/scss/mixins/scrollbar.scss";
.import-container {
    padding: 20px;
    .upload-file-area {
        width: 530px;
        margin: 120px auto 100px;
        ::v-deep .file-wrapper {
            background: #fafbfd;
        }
    }
    .common-form-item {
        margin-bottom: 15px;
        & > label {
            width: 80px;
            font-weight: normal;
        }
        .common-form-label {
            width: 180px;
            margin-left: 30px;
        }
        .common-form-content {
            margin-left: 120px;
            margin-right: 20px;
            .bk-button.bk-primary {
                width: 120px;
            }
            .multi-character-limit {
                max-width: 300px;
                overflow: hidden;
                text-overflow:ellipsis;
                white-space: nowrap;
                cursor: default;
            }
        }
    }
    .common-content {
        margin-left: 118px;
        .common-list-label {
            display: inline-block;
            width: 353px;
        }
        .common-item {
            color: #ff5656;
        }
        .common-checkbox {
            position: relative;
            right: 20px;
            float: right;
            cursor: pointer;
            .checkbox {
                display: inline-block;
                position: relative;
                width: 14px;
                height: 14px;
                color: $whiteDefault;
                border: 1px solid $formBorderColor;
                border-radius: 2px;
                text-align: center;
                vertical-align: -2px;
                &:hover {
                    border-color: $greyDark;
                }
                &.checked {
                    background: $blueDefault;
                    border-color: $blueDefault;
                    &::after {
                        content: "";
                        position: absolute;
                        left: 2px;
                        top: 2px;
                        height: 4px;
                        width: 8px;
                        border-left: 1px solid;
                        border-bottom: 1px solid;
                        border-color: $whiteDefault;
                        transform: rotate(-45deg);
                    }
                }
            }
        }
    }
    #template-file {
        display: none;
    }
    .file-name {
        margin: 10px 0;
    }
    .template-head {
        height: 42px;
        line-height: 42px;
        font-size: 0;
        border-top: 1px solid #c3cdd7;
        border-right: 1px solid #c3cdd7;
        .template-span {
            display: inline-block;
            width: 80px;
            height: 42px;
            color: #333333;
            font-size: 14px;
            font-weight: 600;
            border-left: 1px solid $formBorderColor;
        }
        .template-process-name {
            text-align: left;
            padding-left: 16px;
            font-size: 14px;
        }
        span {
            display: inline-block;
            width: 230px;
            height: 42px;
            line-height: 42px;
            text-align: center;
            color: #333333;
            font-weight: 600;
            border-left: 1px solid $formBorderColor;
        }
    }
    .template-fileList {
        height: 282px;
        border: 1px solid #c3cdd7;
        overflow-x: hidden;
        overflow-y: auto;
        @include scrollbar;
        .template-table {
            width: 100%;
            color: #e4e5e7;
            border-collapse: collapse;
            th,td {
                padding: 10px 10px;
                height: 42px;
                text-align: left;
                color: #313238;
            }
            .conflict-id {
                width: 79px;
                height: 42px;
                text-align: center;
                border-bottom: 1px solid #c3cdd7;
                border-right: 1px solid #c3cdd7;
                text-overflow: ellipsis;
                white-space: nowrap;
                overflow: hidden;
            }
            .conflict-name {
                max-width: 470px;
                text-overflow: ellipsis;
                white-space: nowrap;
                overflow: hidden;
                border-bottom: 1px solid #c3cdd7;
            }
            .template-table-conflict {
                .conflict-id {
                    color: #ff5656;
                }
            }
            .uploading-tip {
                margin-top: 105px;
                text-align: center;
                .common-icon-loading {
                    display: inline-block;
                    animation: bk-button-loading 1.4s infinite linear;
                }
                @keyframes bk-button-loading {
                    from {
                        -webkit-transform: rotate(0);
                        transform: rotate(0);
                    }
                    to {
                        -webkit-transform: rotate(360deg);
                        transform: rotate(360deg);
                    }
                }
            }
        }
    }
    .view-result-btn, .upload-tpl-btn {
        color: #3a84ff;
        cursor: pointer;
        font-size: 12px;
    }
    .check-msg-title {
        margin-top: 26px;
        font-size: 14px;
        color: #313237;
    }
    .check-msg {
        padding: 10px 0 10px;
        font-size: 12px;
        color: #696a72;
    }
}
.common-wrapper-btn {
    .bk-button {
        margin-left: 7px;
    }
}
</style>
