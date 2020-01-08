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
    <div class="tag-datetime">
        <div v-if="formMode">
            <el-date-picker
                v-model="dateValue"
                type="datetime"
                format="yyyy-MM-dd HH:mm:ss"
                value-format="yyyy-MM-dd HH:mm:ss"
                :disabled="!editable"
                :placeholder="placeholder">
            </el-date-picker>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="rf-view-value">{{(value === 'undefined' || value === '') ? '--' : value}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { getFormMixins } from '../formMixins.js'

    const datetimeAttrs = {
        placeholder: {
            type: String,
            required: false,
            default: gettext('请选择日期时间'),
            desc: 'placeholder'
        },
        value: {
            type: String,
            required: false,
            default: ''
        }
    }
    export default {
        name: 'TagDatetime',
        mixins: [getFormMixins(datetimeAttrs)],
        computed: {
            dateValue: {
                get () {
                    return this.value
                },
                set (val) {
                    this.updateForm(val)
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
.tag-datetime {
    /deep/ .el-date-editor {
        width: 100%;
        &.el-input {
            .el-input__inner {
                padding: 0 30px;
            }
        }
    }
}
</style>
