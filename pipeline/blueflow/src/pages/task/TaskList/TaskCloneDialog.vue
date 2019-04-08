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
        width="600"
        :is-show.sync="isTaskCloneDialogShow"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div slot="content">
            <div class="clone-wrapper" v-bkloading="{isLoading: pending, opacity: 1}">
                <div class="common-form-item">
                    <label>{{ i18n.template }}</label>
                    <div class="common-form-content">
                        <BaseInput
                            name="taskName"
                            v-model="name"
                            v-validate="taskNameRule">
                        </BaseInput>
                        <span v-if="errors.has('taskName')" class="common-error-tip error-msg">{{ errors.first('taskName') }}</span>
                    </div>
                </div>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
import '@/utils/i18n.js'
import BaseInput from '@/components/common/base/BaseInput.vue'
import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'

export default {
    name: 'TaskCloneDialog',
    components: {
        BaseInput
    },
    props: ['isTaskCloneDialogShow', 'taskName', 'pending'],
    data () {
        return {
            name: 'copy' + this.taskName.slice(0, STRING_LENGTH.TASK_NAME_MAX_LENGTH - 4),
            taskNameRule: {
                required: true,
                max: STRING_LENGTH.TASK_NAME_MAX_LENGTH,
                regex: NAME_REG
            },
            i18n: {
                title: gettext('任务克隆'),
                template: gettext('任务名称')
            }
        }
    },
    methods: {
        onConfirm () {
            this.$validator.validateAll().then(result => {
                if (!result) {
                    return
                }
                this.name = this.name.trim()
                this.$emit('confirm', this.name)
            })
        },
        onCancel () {
            this.$emit('cancel')
        }
    }
}
</script>
<style lang="scss" scoped>
    .clone-wrapper {
        padding: 10px 0;
        .common-form-item {
            label {
                font-weight: normal;
                 width:100px;
            }
            .common-form-content {
                margin: 0 30px 0 120px;
            }
        }
    }
</style>

