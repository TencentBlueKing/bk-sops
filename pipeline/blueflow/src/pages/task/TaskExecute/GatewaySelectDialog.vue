/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <bk-dialog
        :quick-close="false"
        :has-header="true"
        :ext-cls="'common-dialog'"
        :title="i18n.select_branch"
        width="600"
        padding="15px 40px 60px"
        :is-show.sync="isGatewaySelectDialogShow"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div slot="content">
            <div class="common-form-item">
                <label>{{ i18n.branches }}</label>
                <div class="common-form-content">
                    <bk-selector
                        :list="gatewayBranches"
                        :selected.sync="selectedBranch"
                        @item-selected="onSelectBranch">
                    </bk-selector>
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
                select_branch: gettext("请选择执行分支"),
                branches: gettext("可选执行分支")
            },
            selectedBranch: this.gatewayBranches.length ? this.gatewayBranches[0].id : ''
        }
    },
    methods: {
        onSelectBranch (id) {
            this.selectedBranch = id
        },
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
