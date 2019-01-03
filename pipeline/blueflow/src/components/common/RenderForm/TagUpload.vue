/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="tag-form tag-upload" v-show="showForm">
        <div v-if="editable">
            <el-upload
                :action="url"
                :multiple="multiple"
                :limit="limit"
                :auto-upload="auto_upload"
                :headers="headers"
                :on-preview="handlePreview"
                :on-remove="_handleRemove"
                :on-success="_handleSuccess"
                :on-error="handleError"
                :on-progress="handleProgress"
                :on-change="handleChange"
                :on-exceed="handleExceed"
                :before-upload="beforeUpload"
                :before-remove="beforeRemove"
                :file-list="value">
                <el-button size="small" type="primary">{{ text }}</el-button>
                <div slot="tip" class="el-upload__tip">{{ placeholder }}</div>
            </el-upload>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validate.message}}</span>
        </div>
        <span v-else class="view-value">{{(value === 'undefined' || value === '') ? '--' : value}}</span>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { getAtomFormMixins, getInitialProps } from './atomFormMixins.js'
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
        desc: "upload url"
    },
    multiple: {
        type: Boolean,
        required: false,
        default () {
            return false
        },
        desc: "set multiple selected files when upload"
    },
    headers: {
        type: Object,
        required: false,
        default () {
            return {}
        },
        desc: "upload headers, you should add X-CSRFToken when project has CsrfViewMiddleware"
    },
    auto_upload: {
        type: Boolean,
        required: false,
        default () {
            return false
        },
        desc: "auto upload after selecting file"
    },
    limit: {
        type: Number,
        required: false,
        default () {
            return 100
        },
        desc: "max of files"
    },
    placeholder: {
        type: String,
        required: false,
        default () {
            return ""
        },
        desc: "placeholder"
    },
    text: {
        type: String,
        required: false,
        default () {
            return gettext("点击上传")
        },
        desc: "tips on upload button"
    }
}
export default {
    name: 'TagUpload',
    mixins: [getAtomFormMixins(uploadAttrs)],
    props: getInitialProps(uploadAttrs),
    methods: {
        // 点击已上传的文件链接时的钩子, 可以通过 file.response 拿到服务端返回数据
        handlePreview: function (file) {},
        // 文件列表移除文件时的钩子
        handleRemove: function (file, fileList) {
            return true
        },
        _handleRemove: function (file, fileList) {
            if (this.handleRemove(file, fileList)){
                this.value = fileList
            }
        },
        // 文件上传成功时的钩子
        handleSuccess: function (response, file, fileList){
            return true
        },
        _handleSuccess: function (response, file, fileList) {
            if (this.handleSuccess(response, file, fileList)){
                this.value = fileList
            }
        },
        // 文件上传失败时的钩子
        handleError: function (err, file, fileList) {},
        // 文件上传时的钩子
        handleProgress: function (file, fileList) {},
        // 文件状态改变时的钩子，添加文件、上传成功和上传失败时都会被调用
        handleChange: function (file, fileList) {},
        // 文件超出个数限制时的钩子
        handleExceed: function (file, fileList) {},
        // 上传文件之前的钩子，参数为上传的文件，若返回 false 或者返回 Promise 且被 reject，则停止上传
        beforeUpload: function (file, fileList) {},
        // 删除文件之前的钩子，参数为上传的文件和文件列表，若返回 false 或者返回 Promise 且被 reject，则停止上传
        beforeRemove: function (file, fileList) {}
    }
}
</script>
