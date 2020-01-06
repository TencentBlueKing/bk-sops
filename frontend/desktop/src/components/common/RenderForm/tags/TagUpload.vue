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
    <div class="tag-upload">
        <div v-if="formMode">
            <el-upload
                ref="upload"
                :action="url"
                :multiple="multiple"
                :limit="limit"
                :auto-upload="auto_upload"
                :headers="headers"
                :disabled="!editable || disabled"
                :on-success="handleSuccess.bind(this)"
                :on-remove="handleRemove.bind(this)"
                :on-error="handleError.bind(this)"
                :on-change="handleChange.bind(this)"
                :before-upload="handleBeforeUpload.bind(this)"
                :before-remove="handleBeforeRemove.bind(this)"
                :file-list="fileValue">
                <bk-button size="small" theme="primary">{{ uploadText }}</bk-button>
                <div slot="tip" class="el-upload__tip">{{ placeholder }}</div>
            </el-upload>
            <bk-button v-if="!auto_upload" size="small" type="success" @click="onSubmit">{{ i18n.submit }}</bk-button>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="rf-view-value">{{viewValue}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { getFormMixins } from '../formMixins.js'

    const uploadAttrs = {
        value: {
            type: Array,
            required: false,
            default () {
                return []
            }
        },
        url: {
            type: String,
            required: true,
            default: '',
            desc: 'upload url'
        },
        multiple: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'set multiple selected files when upload'
        },
        headers: {
            type: Object,
            required: false,
            default () {
                return {}
            },
            desc: 'upload headers, you should add X-CSRFToken when project has CsrfViewMiddleware'
        },
        auto_upload: {
            type: Boolean,
            required: false,
            default: true,
            desc: 'auto upload after selecting file'
        },
        limit: {
            type: Number,
            required: false,
            default: 100,
            desc: 'max of files'
        },
        disabled: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'disable upload'
        },
        placeholder: {
            type: String,
            required: false,
            default: '',
            desc: 'placeholder'
        },
        text: {
            type: String,
            required: false,
            default: '',
            desc: 'tips on upload button'
        },
        submit: {
            type: Function,
            default: null
        },
        beforeUpload: {
            type: Function,
            default: null
        },
        beforeRemove: {
            type: Function,
            default: null
        },
        onSuccess: {
            type: Function,
            default: null
        },
        onRemove: {
            type: Function,
            default: null
        },
        fileChange: {
            type: Function,
            default: null
        },
        onError: {
            type: Function,
            default: null
        }
    }
    export default {
        name: 'TagUpload',
        mixins: [getFormMixins(uploadAttrs)],
        data () {
            return {
                i18n: {
                    submit: gettext('提交'),
                    upload: gettext('点击上传'),
                    select: gettext('选择文件')
                }
            }
        },
        computed: {
            fileValue: {
                get () {
                    return this.value
                },
                set (val) {
                    this.updateForm(val)
                }
            },
            viewValue () {
                if (this.fileValue === 'undefined' || !this.fileValue.length) {
                    return '--'
                }
                return this.fileValue.join(',')
            },
            uploadText () {
                return this.text || (this.auto_upload ? this.i18n.upload : this.i18n.select)
            }
        },
        methods: {
            // 手动提交
            onSubmit () {
                if (typeof this.submit === 'function') {
                    this.submit()
                } else {
                    this.$refs.upload.submit()
                }
            },
            handleBeforeUpload (file, fileList) {
                if (typeof this.beforeUpload === 'function') {
                    return this.beforeUpload(file)
                }
                return true
            },
            handleSuccess (response, file, fileList) {
                this.updateForm(fileList)
                if (typeof this.onSuccess === 'function') {
                    this.onSuccess(response, file, fileList)
                }
            },
            handleBeforeRemove (file, fileList) {
                if (typeof this.beforeRemove === 'function') {
                    return this.beforeRemove(file, fileList)
                }
                return true
            },
            handleRemove (file, fileList) {
                this.updateForm(fileList)
                if (typeof this.onRemove === 'function') {
                    this.onRemove(file, fileList)
                }
            },
            handleChange (file, fileList) {
                if (typeof this.fileChange === 'function') {
                    this.fileChange(file, fileList)
                }
            },
            handleError (err, file, fileList) {
                if (typeof this.onError === 'function') {
                    this.onError(file, fileList)
                }
                console.log(err)
            }
        }
    }
</script>
