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
    <div class="template-header-wrapper">
        <base-title class="template-title" :title="title"></base-title>
        <div class="template-name-input">
            <bk-input :value="name"></bk-input>
        </div>
        <div class="button-area">
            <bk-button theme="primary">{{i18n.save}}</bk-button>
            <bk-button theme="primary">{{i18n.saveAndCreateTask}}</bk-button>
            <bk-button theme="default">{{i18n.back}}</bk-button>
        </div>
    </div>
</template>
<script>
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    export default {
        name: 'TemplateHeader',
        components: {
            BaseTitle
        },
        props: {
            type: {
                type: String,
                default: 'edit'
            },
            name: {
                type: String,
                default: ''
            },
            cc_id: {
                type: [String, Number],
                default: ''
            },
            common: {
                type: String,
                default: ''
            },
            templateSaving: {
                type: Boolean,
                default: false
            },
            createTaskSaving: {
                type: Boolean,
                default: false
            },
            isTemplateDataChanged: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                i18n: {
                    create: gettext('新建流程'),
                    edit: gettext('编辑流程'),
                    save: gettext('保存'),
                    createTask: gettext('新建任务'),
                    saveAndCreateTask: gettext('保存并新建任务'),
                    back: gettext('返回列表')
                }
            }
        },
        computed: {
            title () {
                return this.type === 'edit' ? this.i18n.edit : this.i18n.create
            }
        },
        methods: {

        }
    }
</script>
<style lang="scss" scoped>
    .template-header-wrapper {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px;
        height: 59px;
        line-height: 59px;
        background: #f4f7fa;
        border: 1px solid #cacedb;
        .template-name-input {
            width: 430px;
        }
    }
</style>
