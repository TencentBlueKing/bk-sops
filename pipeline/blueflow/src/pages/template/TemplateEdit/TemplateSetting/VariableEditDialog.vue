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
    <div class="edit-dialog-wrapper">
        <bk-dialog
            :quick-close="false"
            :ext-cls="'common-dialog'"
            :title="i18n.edit"
            width="600"
            :is-show.sync="isShow"
            @confirm="onConfirm"
            @cancel="onCancel">
            <div slot="content">
                <RenderForm
                    ref="renderForm"
                    :scheme="renderConfig"
                    :formOption="renderOption"
                    v-model="formData">
                </RenderForm>
            </div>
        </bk-dialog>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import tools from '@/utils/tools.js'
import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
export default {
    name: 'VariableEditDialog',
    components: {
        RenderForm
    },
    props: ['isShow', 'renderConfig', 'renderData', 'renderOption'],
    data () {
        return {
            i18n: {
                edit: gettext("编辑变量")
            },
            formData: tools.deepClone(this.renderData)
        }
    },
    methods: {
        onConfirm () {
            let formValid = true
            if (this.$refs.renderForm) {
                formValid = this.$refs.renderForm.validate()
            }
            if (!formValid) return
            this.$emit('onConfirmDialogEdit', this.formData)
        },
        onCancel () {
            this.$emit('onCancelDialogEdit')
        }
    }
}
</script>
<style lang="scss" scoped>
.edit-dialog-wrapper {
    /deep/ .tag-form {
        margin-left: 0;
    }
    /deep/ .bk-dialog-body {
        max-height: 360px;
        overflow-y: auto;
    }
}
</style>


