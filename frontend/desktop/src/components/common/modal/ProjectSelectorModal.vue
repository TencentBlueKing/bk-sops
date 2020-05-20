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
        :title="title"
        :value="isModalShow"
        :header-position="'left'"
        :ext-cls="'common-dialog'"
        :has-header="false"
        :mask-close="false">
        <div class="select-wrapper">
            <div class="common-form-item">
                <label class="required">{{ $t('选择项目') }}</label>
                <div class="common-form-content">
                    <project-selector
                        :show="true"
                        :redirect="false"
                        @loading="onLoading">
                    </project-selector>
                </div>
                <span v-if="!Number(project_id)" class="common-error-tip error-msg">{{ $t('请选择项目') }}</span>
            </div>
        </div>
        <div slot="footer" class="common-wrapper-btn">
            <div class="bk-button-group">
                <bk-button
                    :loading="isLoading"
                    style="margin-right:10px" theme="primary"
                    @click="onCreateTask">
                    {{ confirm }}
                </bk-button>
                <bk-button theme="default" @click="cancel"> {{ $t('取消') }} </bk-button>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import ProjectSelector from '@/components/layout/ProjectSelector.vue'
    import { mapState } from 'vuex'
    export default {
        name: 'ProjectSelectorModal',
        components: {
            ProjectSelector
        },
        props: {
            // 是否新建任务
            isNewTask: {
                type: Boolean,
                default: true
            }
        },
        data () {
            return {
                isModalShow: false,
                isLoading: false,
                templateId: '',
                title: this.isNewTask ? i18n.t('新建任务') : i18n.t('选择项目'),
                confirm: this.isNewTask ? i18n.t('去新建') : i18n.t('确定')
            }
        },
        computed: {
            ...mapState('project', {
                project_id: state => state.project_id
            })
        },
        methods: {
            show (templateId) {
                this.isModalShow = true
                this.templateId = templateId
            },
            onCreateTask () {
                if (isNaN(Number(this.project_id))) {
                    return
                }
                this.$emit('confirm', this.project_id, this.templateId)
                this.isModalShow = false
            },
            cancel () {
                this.templateId = ''
                this.isModalShow = false
            },
            onLoading (val) {
                this.isLoading = val
            }
        }
    }
</script>
<style lang="scss" scoped>
@import "@/scss/config.scss";
.select-wrapper {
    padding: 30px;
    overflow: hidden;
    .error-msg {
        margin-left: 120px;
    }
    /deep/ {
        .project-wrapper {
           margin-top: 0;
           width: 320px;
        }
        .project-select {
            border-color: #c4c6cc;
            color: #63656e;
        }
    }
}
</style>
