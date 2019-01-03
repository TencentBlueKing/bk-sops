/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="tag-form tag-textarea" v-show="showForm">
        <div v-if="editable">
            <el-input
                type="textarea"
                :rows="3"
                :placeholder="placeholder"
                v-model="value">
            </el-input>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="view-value">{{value || '--'}}</span>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { getAtomFormMixins, getInitialProps } from './atomFormMixins.js'
const textareaAttrs = {
    value: {
        type: String,
        required: false,
        default () {
            return ''
        }
    },
    placeholder: {
        type: String,
        required: false,
        default () {
            return ""
        },
        desc: "placeholder"
    }
}
export default {
    name: "TagTextarea",
    mixins: [getAtomFormMixins(textareaAttrs, this)],
    props: getInitialProps(textareaAttrs)
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
textarea {
    padding: 10px;
    width: 100%;
    height: 70px;
    border: 1px solid $formBorderColor;
    border-radius: 2px;
    outline: none;
    resize: none;
    &:focus {
        border-color: $blueDefault;
    }
    @include scrollbar;
}
</style>


