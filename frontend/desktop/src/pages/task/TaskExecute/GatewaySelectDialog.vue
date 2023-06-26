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
    <bk-dialog
        width="600"
        :mask-close="false"
        :header-position="'left'"
        :ext-cls="'common-dialog'"
        :title="$t('请选择执行分支')"
        :value="isGatewaySelectDialogShow"
        data-test-id="taskExcute_form_gatewaySelectDialog"
        :cancel-text="$t('取消')"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div class="dialog-content" v-if="isGatewaySelectDialogShow">
            <div class="common-form-item">
                <label>{{ $t('可选执行分支') }}</label>
                <div class="common-form-content">
                    <bk-select
                        v-model="selectedBranch"
                        :multiple="isCondParallelGw"
                        :display-tag="isCondParallelGw"
                        :clearable="false">
                        <bk-option
                            v-for="item in gatewayBranches"
                            :key="item.id"
                            :id="item.id"
                            :name="item.name">
                        </bk-option>
                    </bk-select>
                </div>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
    export default {
        name: 'GatewaySelectDialog',
        props: [
            'isGatewaySelectDialogShow',
            'isCondParallelGw',
            'gatewayBranches'
        ],
        data () {
            return {
                selectedBranch: null
            }
        },
        watch: {
            gatewayBranches (val) {
                if (this.isCondParallelGw) {
                    this.selectedBranch = val.length ? [val[0].id] : []
                } else {
                    this.selectedBranch = val.length ? val[0].id : ''
                }
            }
        },
        methods: {
            onConfirm () {
                const selected = this.gatewayBranches.filter(item => {
                    if (this.isCondParallelGw) {
                        return this.selectedBranch.includes(item.id)
                    }
                    return item.id === this.selectedBranch
                })
                this.$emit('onConfirm', selected)
            },
            onCancel () {
                this.$emit('onCancel')
            }
        }
    }
</script>
<style lang="scss" scoped>
    .dialog-content {
        padding: 30px 40px;
        .common-form-item > label {
            font-weight: normal;
        }
        /deep/.bk-select .bk-select-tag-container {
            padding-top: 0 !important;
        }
    }
</style>
