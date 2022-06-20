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
    <bk-sideslider
        :title="$t('基础信息')"
        :is-show="true"
        :width="800"
        :quick-close="true"
        :before-close="beforeClose">
        <div class="config-wrapper" slot="content">
            <bk-form
                ref="configForm"
                class="form-area"
                :model="formData"
                :label-width="140"
                :rules="rules">
                <section class="form-section">
                    <h4>{{ $t('基础') }}</h4>
                    <bk-form-item :property="'name'" :label="$t('流程名称')" :required="true" data-test-id="tabTemplateConfig_form_name">
                        <bk-input :readonly="isViewMode" ref="nameInput" v-model.trim="formData.name" :placeholder="$t('请输入流程模板名称')"></bk-input>
                    </bk-form-item>
                    <bk-form-item v-if="!common" :label="$t('标签')" data-test-id="tabTemplateConfig_form_label">
                        <bk-select
                            v-model="formData.labels"
                            ext-popover-cls="label-select"
                            :display-tag="true"
                            :multiple="true"
                            :disabled="isViewMode"
                            @toggle="onSelectLabel">
                            <bk-option
                                v-for="(item, index) in templateLabels"
                                :key="index"
                                :id="item.id"
                                :name="item.name">
                                <div class="label-select-option">
                                    <span
                                        class="label-select-color"
                                        :style="{ background: item.color }">
                                    </span>
                                    <span>{{item.name}}</span>
                                    <i class="bk-option-icon bk-icon icon-check-1"></i>
                                </div>
                            </bk-option>
                            <div slot="extension" @click="onEditLabel" class="label-select-extension" data-test-id="tabTemplateConfig_form_editLabel">
                                <i class="common-icon-edit"></i>
                                <span>{{ $t('编辑标签') }}</span>
                            </div>
                        </bk-select>
                    </bk-form-item>
                    <bk-form-item property="category" :label="$t('分类')" data-test-id="tabTemplateConfig_form_category">
                        <bk-select
                            v-model="formData.category"
                            class="category-select"
                            :clearable="false"
                            :disabled="isViewMode"
                            @toggle="onSelectCategory">
                            <bk-option
                                v-for="(item, index) in taskCategories"
                                :key="index"
                                :id="item.id"
                                :data-test-id="`tabTemplateConfig_form_category${item.id}`"
                                :name="item.name">
                            </bk-option>
                        </bk-select>
                        <i
                            v-if="!common"
                            class="common-icon-info category-tips"
                            v-bk-tooltips="{
                                content: $t('模板分类即将下线，建议使用标签'),
                                placement: 'bottom',
                                theme: 'light',
                                showOnInit: true
                            }">
                        </i>
                    </bk-form-item>
                </section>
                <section class="form-section">
                    <h4>
                        <span>{{ $t('通知') }}</span>
                        <span class="tip-desc">{{ $t('选择通知方式后，将默认通知到任务执行人；可选择同时通知其他分组人员') }}</span>
                    </h4>
                    <NotifyTypeConfig
                        :label-width="140"
                        :notify-type="formData.notifyType"
                        :notify-type-list="[{ text: $t('任务状态') }]"
                        :receiver-group="formData.receiverGroup"
                        :common="common"
                        :is-view-mode="isViewMode"
                        @change="onSelectNotifyConfig">
                    </NotifyTypeConfig>
                </section>
                <section class="form-section">
                    <h4>{{ $t('其他') }}</h4>
                    <bk-form-item v-if="!common" :label="$t('执行代理人')" data-test-id="tabTemplateConfig_form_executorProxy">
                        <member-select
                            :multiple="false"
                            :disabled="isViewMode"
                            :value="formData.executorProxy"
                            @change="formData.executorProxy = $event">
                        </member-select>
                        <div class="executor-proxy-desc">
                            <div>
                                {{ $t('仅支持本流程的执行代理，可在项目配置中') }}
                                <span
                                    :class="{ 'project-management': authActions && authActions.length, 'disabled': isViewMode }"
                                    @click="jumpProjectManagement">
                                    {{ $t('设置项目执行代理人') }}
                                </span>。
                            </div>
                            {{ $t('模板级别的执行代理人会覆盖业务级别的执行代理人配置，') + $t('若模板配置了执行代理人，业务的执行代理人白名单不会生效。') }}
                        </div>
                    </bk-form-item>
                    <bk-form-item property="notifyType" :label="$t('备注')" data-test-id="tabTemplateConfig_form_notifyType">
                        <bk-input type="textarea" :readonly="isViewMode" v-model.trim="formData.description" :rows="5" :placeholder="$t('请输入流程模板备注信息')"></bk-input>
                    </bk-form-item>
                    <bk-form-item property="defaultFlowType" :label="$t('任务类型偏好')" data-test-id="tabTemplateConfig_form_defaultFlowType">
                        <bk-select v-model="formData.defaultFlowType" :clearable="false" :disabled="isViewMode">
                            <bk-option id="common" :name="$t('默认任务')"></bk-option>
                            <bk-option id="common_func" :name="$t('职能化任务')"></bk-option>
                        </bk-select>
                    </bk-form-item>
                </section>
            </bk-form>
            <div class="btn-wrap">
                <bk-button v-if="!isViewMode" class="save-btn" theme="primary" data-test-id="tabTemplateConfig_form_saveBtn" @click="onSaveConfig">{{ $t('保存') }}</bk-button>
                <bk-button theme="default" data-test-id="tabTemplateConfig_form_cancelBtn" @click="closeTab">{{ isViewMode ? $t('关闭') : $t('取消') }}</bk-button>
            </div>
            <bk-dialog
                width="400"
                ext-cls="common-dialog"
                :theme="'primary'"
                :mask-close="false"
                :show-footer="false"
                :value="isSaveConfirmDialogShow"
                data-test-id="tabTemplateConfig_dialog_confirmDialog"
                @cancel="isSaveConfirmDialogShow = false">
                <div class="template-config-dialog-content">
                    <div class="leave-tips">{{ $t('保存已修改的配置信息吗？') }}</div>
                    <div class="action-wrapper">
                        <bk-button theme="primary" data-test-id="tabTemplateConfig_form_saveBtn" @click="onConfirmClick">{{ $t('保存') }}</bk-button>
                        <bk-button theme="default" data-test-id="tabTemplateConfig_form_cancelBtn" @click="closeTab">{{ $t('不保存') }}</bk-button>
                    </div>
                </div>
            </bk-dialog>
        </div>
    </bk-sideslider>
</template>

<script>
    import { mapState, mapMutations } from 'vuex'
    import MemberSelect from '@/components/common/Individualization/MemberSelect.vue'
    import tools from '@/utils/tools.js'
    import { NAME_REG, STRING_LENGTH, TASK_CATEGORIES } from '@/constants/index.js'
    import i18n from '@/config/i18n/index.js'
    import NotifyTypeConfig from './NotifyTypeConfig.vue'

    export default {
        name: 'TabTemplateConfig',
        components: {
            MemberSelect,
            NotifyTypeConfig
        },
        props: {
            projectInfoLoading: Boolean,
            templateLabelLoading: Boolean,
            templateLabels: Array,
            isShow: Boolean,
            common: [String, Number],
            isViewMode: Boolean
        },
        data () {
            const {
                name, category, notify_type, notify_receivers, description,
                executor_proxy, template_labels, default_flow_type
            } = this.$store.state.template

            return {
                formData: {
                    name,
                    category,
                    description,
                    executorProxy: executor_proxy ? [executor_proxy] : [],
                    receiverGroup: notify_receivers.receiver_group.slice(0),
                    notifyType: [notify_type.success.slice(0), notify_type.fail.slice(0)],
                    labels: template_labels,
                    defaultFlowType: default_flow_type
                },
                isSaveConfirmDialogShow: false,
                rules: {
                    name: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH,
                            message: i18n.t('流程名称长度不能超过') + STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        },
                        {
                            regex: NAME_REG,
                            message: i18n.t('流程名称不能包含') + '\'‘"”$&<>' + i18n.t('非法字符'),
                            trigger: 'blur'
                        }
                    ]
                },
                taskCategories: TASK_CATEGORIES
            }
        },
        computed: {
            ...mapState({
                'timeout': state => state.template.time_out
            }),
            ...mapState('project', {
                'authActions': state => state.authActions
            })
        },
        mounted () {
            this.$refs.nameInput.focus()
        },
        methods: {
            ...mapMutations('template/', [
                'setTplConfig'
            ]),
            onSelectCategory (val) {
                if (val) {
                    window.reportInfo({
                        page: 'templateEdit',
                        zone: 'selectCategory',
                        event: 'click'
                    })
                }
            },
            onSelectLabel (val) {
                if (val) {
                    window.reportInfo({
                        page: 'templateEdit',
                        zone: 'selectLabel',
                        event: 'click'
                    })
                }
            },
            onEditLabel () {
                const { href } = this.$router.resolve({ name: 'projectConfig', params: { id: this.$route.params.project_id } })
                window.open(href, '_blank')
            },
            getTemplateConfig () {
                const { name, category, description, executorProxy, receiverGroup, notifyType, labels, defaultFlowType } = this.formData
                return {
                    name,
                    category,
                    description,
                    template_labels: labels,
                    executor_proxy: executorProxy.length === 1 ? executorProxy[0] : '',
                    receiver_group: receiverGroup,
                    notify_type: { success: notifyType[0], fail: notifyType[1] },
                    default_flow_type: defaultFlowType
                }
            },
            jumpProjectManagement () {
                if (this.isViewMode) return
                if (this.authActions.includes('project_edit')) {
                    this.$router.push({ name: 'projectConfig', params: { id: this.$route.params.project_id } })
                }
            },
            onSelectNotifyConfig (formData) {
                const { notifyType, receiverGroup } = formData
                this.formData.notifyType = notifyType
                this.formData.receiverGroup = receiverGroup
            },
            onSaveConfig () {
                this.$refs.configForm.validate().then(result => {
                    if (!result) {
                        return
                    }

                    const data = this.getTemplateConfig()
                    this.setTplConfig(data)
                    this.closeTab()
                    this.$emit('templateDataChanged')
                })
            },
            onConfirmClick () {
                this.isSaveConfirmDialogShow = false
                this.onSaveConfig()
            },
            beforeClose () {
                if (this.isViewMode) {
                    this.closeTab()
                    return true
                }
                const { name, category, description, template_labels, executor_proxy, notify_receivers, notify_type, default_flow_type } = this.$store.state.template
                const originData = {
                    name,
                    category,
                    description,
                    template_labels,
                    executor_proxy,
                    receiver_group: notify_receivers.receiver_group,
                    notify_type,
                    default_flow_type
                }
                const editingData = this.getTemplateConfig()
                if (tools.isDataEqual(originData, editingData)) {
                    this.closeTab()
                    return true
                } else {
                    this.isSaveConfirmDialogShow = true
                    return false
                }
            },
            closeTab () {
                this.$emit('closeTab')
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.config-wrapper {
    height: calc(100vh - 60px);
    background: none;
    border: none;
    .form-area {
        padding: 30px 30px 0;
        height: calc(100% - 49px);
        overflow-y: auto;
        @include scrollbar;
    }
    .form-section {
        margin-bottom: 30px;
        & > h4 {
            margin: 0 0 24px 0;
            padding-bottom: 10px;
            color: #313238;
            font-weight: bold;
            font-size: 14px;
            border-bottom: 1px solid #cacedb;
        }
        .tip-desc {
            font-size: 12px;
            font-weight: normal;
            margin-left: 20px;
            color: #979ba5;
        }
    }
    .btn-wrap {
        padding: 8px 30px;
        border-top: 1px solid #cacedb;
        .bk-button {
            margin-right: 10px;
            padding: 0 25px;
        }
    }
    /deep/ .bk-label {
        font-size: 12px;
    }
    .user-selector {
        display: block;
    }
    .category-tips {
        position: absolute;
        right: -20px;
        top: 10px;
        font-size: 16px;
        color: #c4c6cc;
        cursor: pointer;
        &:hover {
            color: #f4aa1a;
        }
    }
}
/deep/ .template-config-dialog-content {
    padding: 40px 0;
    text-align: center;
    .leave-tips {
        font-size: 24px;
        margin-bottom: 20px;
    }
    .action-wrapper .bk-button {
        margin-right: 6px;
    }
}
.executor-proxy-desc {
    font-size: 12px;
    line-height: 16px;
    margin-top: 5px;
    color: #b8b8b8;
    .project-management {
        color: #3a84ff;
        cursor: pointer;
    }
    .disabled {
        color: #dcdee5;
        cursor: not-allowed;
    }
    .bloack {
        display: block;
    }
}
</style>
