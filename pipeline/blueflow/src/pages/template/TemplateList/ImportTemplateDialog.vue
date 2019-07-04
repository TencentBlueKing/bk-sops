/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <bk-dialog
        :quick-close="false"
        :has-header="true"
        :ext-cls="'common-dialog'"
        :title="i18n.title"
        width="600"
        :is-show.sync="isImportDialogShow"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div slot="content" class="import-container" v-bkloading="{isLoading: pending.submit, opacity: 1}">
            <div class="common-form-item">
                <label>{{ i18n.files }}</label>
                <div class="common-form-content">
                    <label
                        :for="pending.upload ? '' : 'template-file'"
                        :class="['bk-button', 'bk-default', {'is-disabled': pending.upload}]">
                        {{ i18n.click }}
                    </label>
                    <h4>{{file && file.name}}</h4>
                    <input ref="templateFile" id="template-file" type="file" accept=".dat" @change="onFileChange"/>
                </div>
            </div>
            <template>
                <div class="common-form-item">
                    <label>{{ i18n.list }}</label>
                    <div class="common-form-content">
                        <table class="template-table">
                            <thead>
                                <th>ID</th>
                                <th>{{ i18n.name }}</th>
                            </thead>
                            <tbody>
                                <tr v-for="item in uploadedTemplate" :key="item.id">
                                    <td>{{item.id}}</td>
                                    <td>{{item.name}}</td>
                                </tr>
                                <tr v-if="!uploadedTemplate.length">
                                    <td colspan="2">
                                        <NoData v-if="!pending.upload"><div>{{ i18n.no_data }}</div></NoData>
                                        <div v-else class="uploading-tip"><i class="common-icon-loading"></i></div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="common-form-item">
                    <label>{{ i18n.cover }}</label>
                    <div class="common-form-content">
                        <span :class="['is-override-radio', 'radio-item', {'is-disabled': overrideFormDisabled}]">
                            <input
                                name="override-template"
                                type="radio"
                                id="override"
                                :disabled="overrideFormDisabled"
                                :checked="isOverride"
                                @change="onOverrideChange(true)"/>
                            <label
                                class="radio-input"
                                for="override"
                                v-bktooltips="{
                                    content: i18n.override,
                                    placement: 'top',
                                    width: 300
                                }">
                                <span class="radio-icon"></span>
                                <span class="radio-label">{{ i18n.yes }}</span>
                            </label>
                        </span>
                        <span :class="['is-override-radio', 'radio-item', {'is-disabled': overrideFormDisabled}]">
                            <input
                                name="override-template"
                                type="radio"
                                id="createNew"
                                :disabled="overrideFormDisabled"
                                :checked="!isOverride"
                                @change="onOverrideChange(false)"/>
                            <label class="radio-input" for="createNew" v-bktooltips.top="i18n.createNew">
                                <span class="radio-icon"></span>
                                <span class="radio-label">{{ i18n.no }}</span>
                            </label>
                        </span>
                    </div>
                </div>
                <div class="common-form-item" v-if="overrideTemplate.length && isOverride">
                    <label for="">{{ i18n.cover_list }}</label>
                    <div class="common-form-content">
                        <table class="template-table">
                            <thead>
                                <th>ID</th>
                                <th>{{ i18n.name }}</th>
                            </thead>
                            <tbody>
                                <tr v-for="item in overrideTemplate" :key="item.id">
                                    <td>{{item.id}}</td>
                                    <td>{{item.name}}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </template>
        </div>
    </bk-dialog>
</template>
<script>
import { mapActions, mapState } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import NoData from '@/components/common/base/NoData.vue'
export default {
    name: 'ImportTemplateDialog',
    components: {
        NoData
    },
    props: ['isImportDialogShow'],
    data () {
        return {
            file: null,
            filename: '',
            uploadedTemplate: [],
            overrideTemplate: [],
            isOverride: false,
            overrideFormDisabled: true,
            pending: {
                upload: false,
                submit: false
            },
            i18n: {
                files: gettext('上传文件'),
                click: gettext('点击上传'),
                title: gettext('导入流程'),
                list: gettext('导入列表'),
                name: gettext('流程名称'),
                no_data: gettext('无数据'),
                cover: gettext('是否覆盖'),
                yes: gettext('是'),
                no: gettext('否'),
                cover_list: gettext('覆盖列表'),
                override: gettext('导入的流程会沿用文件中的流程ID，当前业务下具有相同ID的流程将会被覆盖（若任一具有相同ID的流程不在当前业务下，则无法进行覆盖操作）'),
                createNew: gettext('导入的流程会使用新的流程ID，不会对现有的流程造成影响')
            }
        }
    },
    computed: {
        ...mapState({
            'site_url': state => state.site_url,
            'cc_id': state => state.cc_id
        })
    },
    methods: {
        ...mapActions('templateList/', [
            'templateUploadCheck',
            'templateImport'
        ]),
        async uploadCheck () {
            this.pending.upload = true
            this.uploadedTemplate = []
            this.overrideTemplate = []
            this.overrideFormDisabled = true
            try {
                const data = new FormData()
                data.append('data_file', this.file)
                const resp = await this.templateUploadCheck(data)
                if (resp.result) {
                    const checkResult = resp.data
                    this.uploadedTemplate = checkResult.new_template
                    this.overrideTemplate = checkResult.override_template
                    this.overrideFormDisabled = !checkResult.can_override
                } else {
                    errorHandler(resp, this)
                    this.pending.upload = false
                }
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.pending.upload = false
            }
        },
        async importTemplate () {
            this.pending.submit = true
            const formData = new FormData()
            formData.append('data_file', this.file)
            formData.append('override', this.isOverride)
            try {
                const resp = await this.templateImport(formData)
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
            if (this.pending.upload) {
                return
            }
            const file = e.target.files[0]
            if (file) {
                this.file = file
                this.uploadCheck()
            }
        },
        onOverrideChange (value) {
            this.isOverride = value
        },
        onConfirm () {
            if (this.pending.submit || this.pending.upload) {
                return
            }
            if (!this.file) {
                this.$bkMessage({
                    message: gettext('请选择包含导入流程的文件'),
                    theme: 'warning'
                })
                return
            }
            this.importTemplate()
        },
        onCancel () {
            this.$emit('onImportCancel')
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.import-container {
    padding: 30px 0;
    max-height: 420px;
    overflow-y: auto;
    @include scrollbar;
    .common-form-item {
        & > label {
            width: 80px;
            font-weight: normal;
        }
        .common-form-content {
            margin-left: 100px;
            margin-right: 20px;
        }
        .template-table {
            width: 450px;
            border: 1px solid $commonBorderColor;
            border-collapse: collapse;
            th,td {
                padding: 4px 10px;
                text-align: center;
                border: 1px solid $commonBorderColor;
            }
            th {
                background: $whiteNodeBg;
            }
            /deep/ .no-data {
                padding: 10px 0;
                .common-icon-no-data {
                    font-size: 32px;
                }
                .no-data-wording {
                    margin: 0;
                    font-size: 12px;
                }
            }
            .uploading-tip {
                padding: 10px;
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
        .is-override-radio {
            margin-right: 14px;
            height: 36px;
            line-height: 36px;
            font-size: 14px;
            .radio-icon {
                position: relative;
                display: inline-block;
                width: 14px;
                height: 14px;
                border: 1px solid $commonBorderColor;
                border-radius: 50%;
                cursor: pointer;
            }
            .radio-label {
                padding-left: 4px;
                line-height: 1;
                cursor: pointer;
            }
            input[type="radio"] {
                display: none;
            }
            input[type="radio"]:checked + label {
                & > .radio-icon {
                    background: $blueDefault;
                    border: 1px solid $blueDefault;
                    &:after {
                        content: "";
                        position: absolute;
                        top: 4px;
                        left: 4px;
                        width: 4px;
                        height: 4px;
                        background: $whiteDefault;
                        border-radius: 50%;
                    }
                }
            }
            &.is-disabled {
                .radio-label {
                    color: $greyDisable;
                    cursor: not-allowed;
                }
                .radio-icon {
                    border-color: $greyDisable;
                }
                input[type="radio"]:checked + label {
                    & > .radio-icon {
                        background: $whiteDefault;
                        border-color: $greyDisable;
                        &::after {
                            background: $greyDisable;
                        }
                    }
                }
            }
        }
    }
    #template-file {
        display: none;
    }
}
</style>
