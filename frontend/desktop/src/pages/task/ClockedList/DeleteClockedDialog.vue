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
        width="400"
        :ext-cls="'common-dialog'"
        :theme="'primary'"
        :mask-close="false"
        :header-position="'left'"
        :title="$t('确认删除')"
        :value="isDeleteDialogShow"
        :draggable="true"
        data-test-id="clockedList_dialog_deleteClockedDialog"
        @confirm="onDeleteClockedConfirm"
        @cancel="onDeleteClockedCancel">
        <div class="dialog-content" v-bkloading="{ isLoading: deleting, opacity: 1, zIndex: 100 }">
            <div class="information-tips">{{deleteInfo}}</div>
        </div>
    </bk-dialog>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    export default {
        name: 'DeleteClockedDialog',
        props: ['isDeleteDialogShow', 'templateName', 'deleting'],
        computed: {
            deleteInfo () {
                return i18n.t('确认删除') + '"' + this.templateName + '"' + i18n.t('？')
            }
        },
        methods: {
            onDeleteClockedCancel () {
                this.$emit('onDeleteClockedCancel')
            },
            onDeleteClockedConfirm () {
                this.$emit('onDeleteClockedConfirm')
            }
        }
    }
</script>

<style lang="scss" scoped>
    .dialog-content {
        padding: 30px;
    }
    .information-tips {
        word-break: break-all;
    }
</style>
