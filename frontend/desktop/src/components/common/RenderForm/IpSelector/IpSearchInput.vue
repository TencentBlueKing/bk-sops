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
    <div :class="['ip-search-input', { 'disabled': !editable }]">
        <bk-input
            class="search-input"
            right-icon="bk-icon icon-search"
            font-size="large"
            :placeholder="placeholder"
            :disabled="!editable"
            :clearable="true"
            v-model="keyword"
            @input="onInputChange">
        </bk-input>
    </div>
</template>
<script>
    import '@/utils/i18n.js' // ip选择器兼容标准运维国际化

    const i18n = {
        placeholder: gettext('搜索IP，多个以逗号隔开')
    }

    export default {
        name: 'IpSearchInput',
        props: {
            placeholder: {
                type: String,
                default: i18n.placeholder
            },
            editable: {
                type: Boolean,
                default: true
            }
        },
        data () {
            return {
                keyword: '',
                delay: 500,
                timer: null
            }
        },
        methods: {
            onInputChange () {
                clearTimeout(this.timer)
                this.timer = setTimeout(() => {
                    this.$emit('search', this.keyword)
                }, this.delay)
            }
        }
    }
</script>
<style lang="scss" scoped>
.search-input {
    font-size: 14px;
}
</style>
