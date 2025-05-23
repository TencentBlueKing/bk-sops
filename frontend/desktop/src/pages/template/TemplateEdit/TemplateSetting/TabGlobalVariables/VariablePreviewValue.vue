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
    <div class="variable-preview-value" v-bkloading="{ isLoading: loading, zIndex: 100 }">
        <div class="content" v-if="valueStr">{{ valueStr }}</div>
        <bk-alert v-else-if="!loading" type="warning" :title="$t('暂无数据')"></bk-alert>
    </div>
</template>
<script>
    import { mapActions } from 'vuex'

    export default {
        name: 'VariablePreviewValue',
        props: {
            params: Object,
            variableData: Object
        },
        data () {
            return {
                valueStr: '',
                loading: false
            }
        },
        created () {
            if (this.variableData.key) {
                this.getVariableValue()
            }
        },
        methods: {
            ...mapActions('template', [
                'getConstantsPreviewResult'
            ]),
            async getVariableValue () {
                try {
                    this.loading = true
                    const { key, custom_type, value } = this.variableData

                    if (window.ENABLE_MULTI_TENANT_MODE && custom_type === 'bk_user_selector') {
                        await this.fetchUserDisplayInfo(value)
                        return
                    }

                    const resp = await this.getConstantsPreviewResult(this.params)
                    if (resp.result) {
                        this.valueStr = resp.data[key]
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.loading = false
                }
            },
            async fetchUserDisplayInfo (value) {
                if (!value) return

                try {
                    const resp = await fetch(`${window.BK_USER_WEB_APIGW_URL}/api/v3/open-web/tenant/users/-/display_info/?bk_usernames=${value}`, {
                        headers: {
                            'x-bk-tenant-id': window.TENANT_ID
                        },
                        credentials: 'include'
                    })
                    if (!resp.ok) return
        
                    const data = await resp.json()
                    this.valueStr = data.data.map(item => item.display_name).join(',')
                } catch (e) {
                    console.error(e)
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .variable-preview-value {
        position: relative;
        margin: 10px 30px;
        background: #f0f1f5;
        border: 1px solid #dcdee5;
        border-radius: 2px;
        min-height: 50px;

        &:after {
            content: '';
            position: absolute;
            top: -5px;
            right: 260px;
            width: 8px;
            height: 8px;
            background: #f0f1f5;
            border-style: solid;
            border-width: 1px 1px 0 0;
            border-color: #dcdee5 #dcdee5 transparent transparent;
            transform: rotate(-45deg);
            border-radius: 1px;
        }
        .content {
            padding: 16px;
            max-height: 200px;
            word-break: break-all;
            overflow: auto;
        }
        .bk-alert-warning {
            margin: 8px;
        }
    }
</style>
