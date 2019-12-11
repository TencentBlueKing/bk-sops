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
    <div class="file-upload">
        <slot>
            <div class="upload-wrapper">
                <span class="drag-upload">{{i18n.dragUpload}}</span>
                <span class="click-upload">{{i18n.clickUpload}}</span>
            </div>
        </slot>
        <input type="file" accept=".js" @change="handleFileUpload" />
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    export default {
        name: 'UploadReadFile',
        data () {
            return {
                i18n: {
                    dragUpload: gettext('拖拽到此处上传或'),
                    clickUpload: gettext('点击上传')
                }
            }
        },
        methods: {
            handleFileUpload (e) {
                this.$emit('uploaded', e)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .file-upload {
        position: relative;
        .upload-wrapper {
            width: 100%;
            height: 70px;
            line-height: 70px;
            font-size: 14px;
            border-radius: 2px;
            border: 1px dashed #c3cdd7;
            text-align: center;
            .drag-upload {
                color: #c4c6cc;
            }
            .click-upload {
                color: #3a84ff;
            }
        }
        & > input[type=file]{
            width: 100%;
            height: 100%;
            position: absolute;
            left: 0;
            top: 0;
            z-index: 10;
            cursor: pointer;
            opacity: 0;
        }
    }
</style>
