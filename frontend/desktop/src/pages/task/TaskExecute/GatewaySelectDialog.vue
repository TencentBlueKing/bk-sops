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
    <bk-dialog
        width="600"
        :mask-close="false"
        :header-position="'left'"
        :ext-cls="'common-dialog'"
        :title="i18n.selectBranch"
        :value="isGatewaySelectDialogShow"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div class="dialog-content">
            <div class="common-form-item">
                <label>{{ i18n.branches }}</label>
                <div class="common-form-content">
                    <bk-select
                        v-model="selectedBranch"
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
    import '@/utils/i18n.js'
    export default {
        name: 'GatewaySelectDialog',
        props: [
            'isGatewaySelectDialogShow',
            'gatewayBranches'
        ],
        data () {
            return {
                i18n: {
                    selectBranch: gettext('请选择执行分支'),
                    branches: gettext('可选执行分支')
                },
                selectedBranch: this.gatewayBranches.length ? this.gatewayBranches[0].id : ''
            }
        },
        watch: {
            gatewayBranches (val) {
                this.selectedBranch = val.length ? val[0].id : ''
            }
        },
        methods: {
            onConfirm () {
                const selected = this.gatewayBranches.filter(item => {
                    return item.id === this.selectedBranch
                })[0]
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
    }
</style>
