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
        :title="i18n.title"
        width="400"
        padding="30px"
        :is-show="isRevokeDialogShow"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div slot="content">
            <div>{{ i18n.revoke }}</div>
        </div>
    </bk-dialog>
</template>

<script>
import '@/utils/i18n.js'
export default {
    name: 'revokeDialog',
    props: ['isRevokeDialogShow'],
    data () {
        return {
            i18n: {
                revoke: gettext('是否撤销该任务？'),
                title: gettext('任务撤销')
            }
        }
    },
    methods: {
        onConfirm () {
            this.$emit('onConfirmRevokeTask')
        },
        onCancel () {
            this.$emit('onCancelRevokeTask')
        }
    }
}
</script>
