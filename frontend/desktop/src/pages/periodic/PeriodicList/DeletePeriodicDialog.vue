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
        width="400"
        :ext-cls="'common-dialog'"
        :theme="'primary'"
        :mask-close="false"
        :header-position="'left'"
        :title="i18n.deleteTips"
        :value="isDeleteDialogShow"
        :draggable="true"
        @confirm="onDeletePeriodicConfrim"
        @cancel="onDeletePeriodicCancel">
        <div v-bkloading="{ isLoading: deleting, opacity: 1 }">
            <div class="information-tips">{{deleteInfo}}</div>
        </div>
    </bk-dialog>
</template>
<script>
    import '@/utils/i18n.js'
    export default {
        name: 'DeletePeriodicDialog',
        props: ['isDeleteDialogShow', 'templateName', 'deleting'],
        data () {
            return {
                i18n: {
                    deleteTips: gettext('确认删除')
                }
            }
        },
        computed: {
            deleteInfo () {
                return this.i18n.deleteTips + '"' + this.templateName + '"' + gettext('？')
            }
        },
        methods: {
            onDeletePeriodicCancel () {
                this.$emit('onDeletePeriodicCancel')
            },
            onDeletePeriodicConfrim () {
                this.$emit('onDeletePeriodicConfirm')
            }
        }
    }
</script>

<style lang="scss" scoped>
    .information-tips {
        word-break: break-all;
    }
</style>
