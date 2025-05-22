/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="user-selector-wrap">
        <BKMultiTenantUserSelector
            v-if="isMultiTenantMode"
            v-model="setValue"
            :api-base-url="apiBaseUrl"
            :tenant-id="tenantId"
            :current-user-id="username"
            exact-search-key="bk_username"
            :placeholder="placeholder"
            :disabled="disabled"
            :multiple="multiple">
        </BKMultiTenantUserSelector>
        <BkUserSelector
            v-else
            v-model="setValue"
            :api="api"
            :placeholder="placeholder"
            :disabled="disabled"
            :search-limit="maxResult"
            :multiple="multiple"
            :tag-clearable="hasDeleteIcon"
            :fixed-height="fixedHeight"
            @change="change"
            @select-user="select"
            @remove-selected="remove">
        </BkUserSelector>
    </div>
</template>
<script>
    import BkUserSelector from '@blueking/user-selector'
    import BKMultiTenantUserSelector from '@blueking/bk-user-selector/vue2'
    import '@blueking/bk-user-selector/vue2/vue2.css'
    import { mapState } from 'vuex'
    export default {
        name: 'MemberSelect',
        components: {
            BkUserSelector,
            BKMultiTenantUserSelector
        },
        model: {
            prop: 'value',
            event: 'change'
        },
        props: {
            value: {
                type: [Array, String],
                default: ''
            },
            placeholder: String,
            disabled: {
                type: Boolean,
                default: false
            },
            hasDeleteIcon: {
                type: Boolean,
                default: true
            },
            multiple: {
                type: Boolean,
                default: false
            },
            maxData: {
                type: Number,
                default: -1
            },
            maxResult: {
                type: Number,
                default: 5
            }
        },
        data () {
            return {
                fixedHeight: false,
                api: `${window.MEMBER_SELECTOR_DATA_HOST}/api/c/compapi/v2/usermanage/fs_list_users/`,
                tenantId: window.TENANT_ID,
                apiBaseUrl: window.BK_USER_WEB_APIGW_URL
            }
        },
        computed: {
            ...mapState({
                isMultiTenantMode: state => state.isMultiTenantMode,
                username: state => state.username
            }),
            setValue: {
                get () {
                    if (this.isMultiTenantMode) {
                        return this.value
                    }
                    return Array.isArray(this.value) ? this.value : this.value ? [this.value] : []
                },
                set (val) {
                    if (this.isMultiTenantMode) {
                        this.$emit('change', val)
                        return
                    }
                    if (Array.isArray(val) && !Array.isArray(this.value)) {
                        this.$emit('change', val[0])
                    } else {
                        this.$emit('change', val)
                    }
                }
            }
        },
        methods: {
            change (tags) {
                this.$emit('change', tags)
            },
            select (tag) {
                this.$emit('select', tag)
            },
            remove (tag) {
                this.$emit('remove', tag)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .user-selector-wrap {
        width: 100%;
        .user-selector {
            width: 100%;
        }
    }
    .tag-member-selector-wrap {
        .user-selector {
            width: 100%;
        }
    }
</style>
