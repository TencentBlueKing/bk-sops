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
            width="600"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :header-position="'left'"
            :title="i18n.edit"
            :value="isShow"
            @confirm="onConfirm"
            @cancel="onCancel">
            <div class="variable-params-content">
                <RenderForm
                    ref="renderForm"
                    :scheme="renderConfig"
                    :form-option="renderOption"
                    v-model="formData"
                    @change="onDataChange">
                </RenderForm>
                <div class="error-tips" v-if="formError">
                    <span class="common-error-tip error-info">{{i18n.checkData}}</span>
                </div>
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
                formData: tools.deepClone(this.renderData),
                formError: false,
                i18n: {
                    edit: gettext('编辑变量'),
                    checkData: gettext('变量的参数值不合法')
                }
            }
        },
        methods: {
            onConfirm () {
                let formValid = true
                if (this.$refs.renderForm) {
                    formValid = this.$refs.renderForm.validate()
                }
                if (!formValid) {
                    this.formError = true
                    return
                }
                this.$emit('onConfirmDialogEdit', this.formData)
            },
            onCancel () {
                this.$emit('onCancelDialogEdit')
            },
            onDataChange () {
                this.formError = false
            }
        }
    }
</script>
<style lang="scss" scoped>
.edit-dialog-wrapper {
    position: relative;
    /deep/ .tag-form {
        margin-left: 0;
    }
    /deep/ .bk-dialog-body {
        max-height: 360px;
        overflow-y: auto;
    }
    .error-tips {
        position: absolute;
        bottom: 18px;
        right: 230px;
        font-size: 12px;
    }
}
</style>
