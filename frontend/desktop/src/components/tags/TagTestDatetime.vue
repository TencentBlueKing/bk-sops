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
    <div class="tag-form tag-testdatetime" v-show="showForm">
        <div v-if="editable">
            <el-date-picker
                v-model="value"
                type="datetime"
                format="yyyy-MM-dd hh:mm:ss"
                value-format="yyyy-MM-dd hh:mm:ss"
                :placeholder="placeholder">
            </el-date-picker>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="view-value">{{value || '--'}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { getFormMixins } from '@/components/common/RenderForm/formMixins.js'
    const datetimeAttrs = {
        placeholder: {
            type: String,
            required: false,
            default () {
                return gettext('请选择日期时间')
            },
            desc: 'placeholder'
        },
        value: {
            type: String,
            required: false,
            default () {
                return ''
            }
        }
    }
    export default {
        name: 'TagTestDatetime',
        mixins: [getFormMixins(datetimeAttrs)]
    }
</script>
<style lang="scss" scoped>
.tag-testdatetime {
    /deep/ .el-date-editor {
        width: 100%;
    }
}
</style>
