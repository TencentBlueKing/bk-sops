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
    <div class="tag-int">
        <div v-if="formMode">
            <el-input
                type="number"
                :disabled="!editable"
                :placeholder="placeholder"
                v-model="intValue">
            </el-input>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="rf-view-value">{{(value === 'undefined' || value === '') ? '--' : value}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { getFormMixins } from '../formMixins.js'

    const intAttrs = {
        placeholder: {
            type: String,
            required: false,
            default: '',
            desc: 'placeholder'
        },
        value: {
            type: [Number, String],
            required: false,
            default: 0
        }
    }
    export default {
        name: 'TagInt',
        mixins: [getFormMixins(intAttrs)],
        computed: {
            intValue: {
                get () {
                    return Number(this.value)
                },
                set (val) {
                    val = parseInt(val)
                    this.updateForm(val)
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
.tag-input {
    /deep/ .el-input__inner {
        height: 36px;
        line-height: 36px;
    }
}
</style>
