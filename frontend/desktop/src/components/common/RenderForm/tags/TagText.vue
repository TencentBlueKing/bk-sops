/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="tag-text">
        <pre v-if="raw" class="view-value-raw">{{ viewValue }}</pre>
        <span v-else class="rf-view-value">{{ viewValue }}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { getFormMixins } from '../formMixins.js'

    export const attrs = {
        raw: {
            type: Boolean,
            required: false,
            default: false
        },
        value: {
            type: String,
            required: false,
            default: ''
        }
    }
    export default {
        name: 'TagText',
        mixins: [getFormMixins(attrs)],
        computed: {
            viewValue () {
                return (this.value === 'undefined' || this.value === '') ? '--' : this.value
            }
        }
    }
</script>
<style lang="scss" scoped>
    .view-value-raw {
        margin: 0;
        word-break: break-word;
        white-space: pre-wrap;
        font-family: 'Microsoft YaHei','PingFang SC','Hiragino Sans GB','SimSun','sans-serif';;
    }
</style>
