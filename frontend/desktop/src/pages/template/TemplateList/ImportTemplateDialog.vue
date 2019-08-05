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
    <bk-dialog
        class="import-dialog"
        width="739"
        :header-position="'left'"
        :mask-close="false"
        :ext-cls="'common-dialog'"
        :title="i18n.title"
        :value="isImportDialogShow"
        @cancel="onCancel">
        <div class="import-container" v-bkloading="{ isLoading: pending.submit, opacity: 1 }">
            <div class="import-wrapper">
                <div class="common-form-item">
                    <label class="required">{{ i18n.files }}</label>
                    <div class="common-form-content">
                        <label
                            :for="pending.upload ? '' : 'template-file'"
                            :class="['bk-button', 'bk-primary', { 'is-disabled': pending.upload }]">
                            {{ uploadText }}
                        </label>
                        <h4 class="file-name">{{file && file.name}}</h4>
                        <input
                            ref="templateFile"
                            id="template-file"
                            type="file"
                            accept=".dat"
                            @change="onFileChange" />
                        <span
                            v-show="templateFileEmpty"
                            class="common-error-tip error-msg">
                            {{i18n.templateFileEmpty}}
                        </span>
                        <span
                            v-show="templateFileError"
                            class="common-error-tip error-msg">
                            {{i18n.templateFileError}}
                        </span>
                        <span
                            v-show="templateFileErrorExt"
                            class="common-error-tip error-msg">
                            {{i18n.templateFileErrorExt}}
                        </span>
                    </div>
                </div>
                <div class="common-form-item">
                    <label>{{ i18n.list }}</label>
                    <div class="common-form-content">
                        <div class="template-head">
                            <span class="template-span">ID</span>
                            <span class="template-process-name">{{ i18n.name }}</span>
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
                                            <td colspan="2">
                                                <NoData v-if="!pending.upload">
                                                    <div>{{ i18n.noData }}</div>
                                                </NoData>
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
                        <label class="common-list">{{i18n.uploadProcess}}{{exportList.length}}{{i18n.process}}</label>
                        <label class="common-item" v-if="overrideList.length">{{i18n.amongThem}}{{overrideList.length}}{{i18n.conflictList}}</label>
                    </div>
                    <div class="common-checkbox" @click="onShowConflicts">
                        <span :class="['checkbox', { checked: isChecked }]"></span>
                        <span>{{ i18n.showConflicts }}</span>
                    </div>
                </div>
            </div>
        </div>
        <div slot="footer" class="common-wrapper-btn">
            <bk-button theme="primary" @click="exportSubmit(true)">{{exportConflict}}</bk-button>
            <bk-button theme="default" @click="exportSubmit(false)"> {{overrideConflict}} </bk-button>
            <bk-button theme="default" @click="onCancel"> {{ i18n.cancel}} </bk-button>
        </div>
    </bk-dialog>
</template>

<script>
    import '@/utils/i18n.js'
    import { mapActions, mapState } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'ImportTemplateDialog',
        components: {
            NoData
        },
        props: ['isImportDialogShow', 'common'],
        data () {
            return {
                file: null,
                filename: '',
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
                i18n: {
                    files: gettext('上传文件'),
                    upload: gettext('点击上传'),
                    reupload: gettext('重新上传'),
                    title: gettext('导入流程'),
                    list: gettext('导入列表'),
                    name: gettext('流程名称'),
                    noData: gettext('无数据'),
                    cover: gettext('是否覆盖'),
                    yes: gettext('是'),
                    no: gettext('否'),
                    uploadProcess: gettext('上传了'),
                    process: gettext('条流程'),
                    showConflicts: gettext('只显示冲突项'),
                    override: gettext('导入的流程会沿用文件中的流程ID，当前业务下具有相同ID的流程将会被覆盖（若任一具有相同ID的流程不在当前业务下，则无法进行覆盖操作）'),
                    createNew: gettext('导入的流程会使用新的流程ID，不会对现有的流程造成影响'),
                    templateFileEmpty: gettext('模板文件上传为空'),
                    templateFileError: gettext('模板上传内容不合法，请重新选择文件'),
                    templateFileErrorExt: gettext('该文件后缀不为.dat'),
                    amongThem: gettext('其中'),
                    replaceWithoutConflict: gettext('保留ID，并提交'),
                    reservedWithoutConflict: gettext('使用新ID, 并提交'),
                    replaceSubmit: gettext('覆盖冲突项, 并提交'),
                    reservedSubmit: gettext('保留两者, 并提交'),
                    cancel: gettext('取消'),
                    conflictList: gettext('条流程与系统已有流程存在冲突')
                }
            }
        },
        computed: {
            ...mapState({
                'site_url': state => state.site_url,
                'cc_id': state => state.cc_id
            }),
            exportConflict () {
                return this.overrideList.length ? this.i18n.replaceSubmit : this.i18n.replaceWithoutConflict
            },
            overrideConflict () {
                return this.overrideList.length ? this.i18n.reservedSubmit : this.i18n.reservedWithoutConflict
            },
            isEmpty () {
                return !this.exportList.length || (this.isChecked && !this.overrideList.length)
            },
            uploadText () {
                return this.uploaded ? this.i18n.reupload : this.i18n.upload
            }
        },
        methods: {
            ...mapActions('templateList/', [
                'templateUploadCheck',
                'templateImport'
            ]),
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
                        common: this.common
                    }
                    data.formData.append('data_file', this.file)
                    const resp = await this.templateUploadCheck(data)
                    if (resp.result) {
                        const checkResult = resp.data
                        this.exportList = checkResult.new_template
                        this.overrideList = checkResult.override_template
                        this.templateFileError = false
                    } else {
                        this.templateFileError = true
                        this.pending.upload = false
                        this.dataConflict = false
                    }
                } catch (e) {
                    errorHandler(e, this)
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
                    common: this.common
                }
                try {
                    const resp = await this.templateImport(data)
                    if (resp.result) {
                        this.$emit('onImportConfirm')
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
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
                if (!this.templateFileErrorExt && !this.templateFileEmpty && !this.templateFileError) {
                    this.importTemplate(isOverride)
                    this.resetData()
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
            exportSubmit (isOverride) {
                this.onConfirm(isOverride)
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
            }
        }
    }
</script>
<style lang="scss" scoped>
@import "@/scss/config.scss";
@import "@/scss/mixins/scrollbar.scss";
.import-container {
    padding: 20px;
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
        padding: 4px 0px 0px 0px;
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
        height: 252px;
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
            /deep/ .no-data-wrapper {
                margin-top: 90px;
                .common-icon-no-data {
                    font-size: 32px;
                }
                .no-data-wording {
                    margin: 0;
                    font-size: 12px;
                }
            }
            .template-table-conflict {
                td {
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
    .common-wrapper-btn {
        float: right;
        margin-top: 28px;
        .bk-button {
            margin: 5px;
        }
    }
}
/deep/ .bk-dialog-footer .bk-dialog-outer {
    display: none;
}
</style>
