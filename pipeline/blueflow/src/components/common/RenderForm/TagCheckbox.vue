/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="tag-form tag-checkbox" v-show="showForm">
        <div v-if="editable">
            <div>
                <div class="checkbox-item" v-for="item in items" :key="item.name">
                    <el-checkbox
                        v-model="value"
                        :label="item.value"
                        @change="onChange">
                        {{item.name}}
                    </el-checkbox>
                </div>
            </div>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="view-value">{{(value === 'undefined' || value === '') ? '--' : value}}</span>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { getAtomFormMixins, getInitialProps } from './atomFormMixins.js'
import BaseCheckbox from '../base/BaseCheckbox.vue'
const checkboxAttrs = {
    items: {
        type: Array,
        required: true,
        desc: "array like [{name: '', value: ''}, {name: '', value: ''}]"
    },
    value: {
        type: Array,
        required: false,
        default () {
            return []
        }
    }
}
export default {
    name: 'TagCheckBox',
    components: {
        BaseCheckbox
    },
    mixins: [getAtomFormMixins(checkboxAttrs, this)],
    props: getInitialProps(checkboxAttrs)
}
</script>
<style lang="scss" scoped>
    .checkbox-item {
        display: inline-block;
        min-width: 100px;
        height: 36px;
        line-height: 36px;
        /deep/ .el-checkbox__input.is-checked + .el-checkbox__label {
            color: #606266;
        }
    }
</style>
