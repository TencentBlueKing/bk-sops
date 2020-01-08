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
    <div class="tag-textarea">
        <el-input
            type="textarea"
            v-model="textareaValue"
            :class="{ 'rf-view-textarea-value': !formMode, 'rf-view-textarea': !editable }"
            :disabled="!editable || !formMode"
            :autosize="formMode ? { minRows: 2 } : true"
            resize="none"
            :placeholder="placeholder">
        </el-input>
        <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { getFormMixins } from '../formMixins.js'

    const textareaAttrs = {
        value: {
            type: String,
            required: false,
            default: ''
        },
        placeholder: {
            type: String,
            required: false,
            default: '',
            desc: 'placeholder'
        }
    }
    export default {
        name: 'TagTextarea',
        mixins: [getFormMixins(textareaAttrs)],
        computed: {
            textareaValue: {
                get () {
                    if (!this.formMode && !this.value) {
                        return '--'
                    }
                    return this.value
                },
                set (val) {
                    this.updateForm(val)
                }
            }
        }
    }
</script>
<style lang="scss">
@import '@/scss/mixins/scrollbar.scss';
.rf-view-textarea-value {
    .el-textarea__inner {
        padding: 6px 0;
        border: none;
        resize: none;
        &[disabled = "disabled"] {
            background: inherit;
            color: inherit;
            cursor: text;
        }
    }
}
.el-textarea {
    /deep/ .el-textarea__inner {
        padding-left: 10px;
        padding-right: 10px;
        word-break: break-all;
        @include scrollbar;
    }
}
.rf-view-textarea-value {
    /deep/ .el-textarea__inner {
        padding: 6px 0 0;
        line-height: 24px;
    }
}
</style>
