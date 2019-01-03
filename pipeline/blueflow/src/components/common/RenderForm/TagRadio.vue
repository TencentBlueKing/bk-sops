/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="tag-form tag-radio" v-show="showForm">
        <div v-if="editable">
            <div>
                <div class="radio-item" v-for="item in items" :key="item.name">
                    <el-radio
                        v-model="value"
                        :label="item.value"
                        @change="onChange">
                        {{item.name}}
                    </el-radio>
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
const radioAttrs = {
    items: {
        type: Array,
        required: true,
        desc: "array like [{name: '', value: ''}, {name: '', value: ''}]"
    },
    value: {
        required: false,
        default () {
            return ''
        }
    }
}
export default {
    name: 'TagRadio',
    mixins: [getAtomFormMixins(radioAttrs, this)],
    props: getInitialProps(radioAttrs)
}
</script>
<style lang="scss" scoped>
    .radio-item {
        display: inline-block;
        /deep/ .el-radio__label {
            display: inline-block;
            padding-right: 10px;
            min-width: 80px;
        }
        .el-radio {
            height: 36px;
            line-height: 36px;
        }
    }
</style>
