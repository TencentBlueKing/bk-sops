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
    <div class="tag-member-selector">
        <div v-if="formMode" class="tag-member-selector-wrap">
            <bk-member-selector
                v-model="memberValue"
                :type="'all'">
            </bk-member-selector>
        </div>
        <span v-else class="rf-view-value">{{viewValue}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { getFormMixins } from '../formMixins.js'

    const intAttrs = {
        value: {
            type: Array,
            required: false,
            default () {
                return []
            }
        }
    }
    export default {
        name: 'TagMember_selector',
        mixins: [getFormMixins(intAttrs)],
        computed: {
            memberValue: {
                get () {
                    return this.value.slice(0)
                },
                set (val) {
                    this.updateForm(val)
                }
            }
        }
    }
</script>
