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
    <div class="variable-preview-value" v-bkloading="{ isLoading: loading, zIndex: 100 }">
        <div class="content">{{ valueStr }}</div>
    </div>
</template>
<script>
    import { mapActions } from 'vuex'

    export default {
        name: 'VariablePreviewValue',
        props: {
            keyid: String,
            params: Object
        },
        data () {
            return {
                valueStr: '',
                loading: false
            }
        },
        created () {
            if (this.keyid) {
                this.getVaribleValue()
            }
        },
        methods: {
            ...mapActions('template', [
                'getConstantsPreviewResult'
            ]),
            async getVaribleValue () {
                try {
                    this.loading = true
                    const resp = await this.getConstantsPreviewResult(this.params)
                    if (resp.result) {
                        this.valueStr = resp.data[this.keyid]
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.loading = false
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

        &:after {
            content: '';
            position: absolute;
            top: -5px;
            right: 44px;
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
    }
</style>
