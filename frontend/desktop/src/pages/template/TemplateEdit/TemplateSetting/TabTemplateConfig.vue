/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
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
                    <bk-form-item property="name" :label="$t('流程名称')" :required="true">
                        <bk-input ref="nameInput" v-model.trim="formData.name" :placeholder="$t('请输入流程模板名称')"></bk-input>
                    </bk-form-item>
                    <bk-form-item v-if="!common" :label="$t('标签')">
                        <bk-select
                            v-model="formData.labels"
                            ext-popover-cls="label-select"
                            :display-tag="true"
                            :multiple="true"
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
                            <div slot="extension" @click="onEditLabel" class="label-select-extension">
                                <i class="common-icon-edit"></i>
                                <span>{{ $t('编辑标签') }}</span>
                            </div>
                        </bk-select>
                    </bk-form-item>
                    <bk-form-item property="category" :label="$t('分类')">
                        <bk-select
                            v-model="formData.category"
                            class="category-select"
                            :clearable="false"
                            @toggle="onSelectCategory">
                            <bk-option
                                v-for="(item, index) in taskCategories"
                                :key="index"
                                :id="item.id"
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
                    <h4>{{ $t('通知') }}</h4>
                    <bk-form-item :label="$t('通知方式')">
                        <bk-table v-bkloading="{ isLoading: notifyTypeLoading }" class="notify-type-table" :data="formData.notifyType">
                            <bk-table-column v-for="(col, index) in notifyTypeList" :key="index" :render-header="getNotifyTypeHeader">
                                <template slot-scope="props">
                                    <bk-switcher
                                        v-if="col.type"
                                        size="small"
                                        theme="primary"
                                        :value="props.row.includes(col.type)"
                                        @change="onSelectNotifyType(props.$index, col.type, $event)">
                                    </bk-switcher>
                                    <span v-else>{{ props.$index === 0 ? $t('成功') : $t('失败') }}</span>
                                </template>
                            </bk-table-column>
                        </bk-table>
                    </bk-form-item>
                    <bk-form-item :label="$t('通知分组')">
                        <bk-checkbox-group v-model="formData.receiverGroup" v-bkloading="{ isLoading: notifyGroupLoading, opacity: 1, zIndex: 100 }">
                            <bk-checkbox
                                v-for="item in notifyGroup"
                                :key="item.id"
                                :value="item.id">
                                {{item.name}}
                            </bk-checkbox>
                        </bk-checkbox-group>
                    </bk-form-item>
                </section>
                <section class="form-section">
                    <h4>{{ $t('其他') }}</h4>
                    <bk-form-item v-if="!common" :label="$t('执行代理人')">
                        <member-select
                            :multiple="false"
                            :value="formData.executorProxy"
                            @change="formData.executorProxy = $event">
                        </member-select>
                        <div class="executor-proxy-desc">
                            <div>
                                {{ $t('仅支持本流程的执行代理，可在项目配置中') }}
                                <span :class="{ 'project-management': authActions && authActions.length }" @click="jumpProjectManagement">{{ $t('设置项目执行代理人') }}</span>。
                            </div>
                            {{ $t('模板级别的执行代理人会覆盖业务级别的执行代理人配置，') + $t('若模板配置了执行代理人，业务的执行代理人白名单不会生效。') }}
                        </div>
                    </bk-form-item>
                    <bk-form-item property="notifyType" :label="$t('备注')">
                        <bk-input type="textarea" v-model.trim="formData.description" :rows="5" :placeholder="$t('请输入流程模板备注信息')"></bk-input>
                    </bk-form-item>
                    <bk-form-item property="defaultFlowType" :label="$t('任务类型偏好')">
                        <bk-select v-model="formData.defaultFlowType" :clearable="false">
                            <bk-option id="common" :name="$t('默认任务')"></bk-option>
                            <bk-option id="common_func" :name="$t('职能化任务')"></bk-option>
                        </bk-select>
                    </bk-form-item>
                </section>
            </bk-form>
            <div class="btn-wrap">
                <bk-button class="save-btn" theme="primary" :disabled="notifyTypeLoading || notifyGroupLoading" @click="onSaveConfig">{{ $t('保存') }}</bk-button>
                <bk-button theme="default" @click="closeTab">{{ $t('取消') }}</bk-button>
            </div>
            <bk-dialog
                width="400"
                ext-cls="common-dialog"
                :theme="'primary'"
                :mask-close="false"
                :show-footer="false"
                :value="isSaveConfirmDialogShow"
                @cancel="isSaveConfirmDialogShow = false">
                <div class="template-config-dialog-content">
                    <div class="leave-tips">{{ $t('保存已修改的配置信息吗？') }}</div>
                    <div class="action-wrapper">
                        <bk-button theme="primary" :disabled="notifyTypeLoading || notifyGroupLoading" @click="onConfirmClick">{{ $t('保存') }}</bk-button>
                        <bk-button theme="default" @click="closeTab">{{ $t('不保存') }}</bk-button>
                    </div>
                </div>
            </bk-dialog>
        </div>
    </bk-sideslider>
</template>

<script>
    import { mapState, mapMutations, mapActions } from 'vuex'
    import MemberSelect from '@/components/common/Individualization/MemberSelect.vue'
    import tools from '@/utils/tools.js'
    import { NAME_REG, STRING_LENGTH, TASK_CATEGORIES } from '@/constants/index.js'
    import i18n from '@/config/i18n/index.js'

    export default {
        name: 'TabTemplateConfig',
        components: {
            MemberSelect
        },
        props: {
            projectInfoLoading: Boolean,
            templateLabelLoading: Boolean,
            templateLabels: Array,
            isShow: Boolean,
            common: [String, Number]
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
                notifyTypeList: [],
                projectNotifyGroup: [],
                isSaveConfirmDialogShow: false,
                notifyTypeLoading: false,
                notifyGroupLoading: false,
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
                'projectBaseInfo': state => state.template.projectBaseInfo,
                'timeout': state => state.template.time_out
            }),
            ...mapState('project', {
                'authActions': state => state.authActions
            }),
            notifyGroup () {
                let list = []
                if (this.projectBaseInfo.notify_group) {
                    const defaultList = list.concat(this.projectBaseInfo.notify_group.map(item => {
                        return {
                            id: item.value,
                            name: item.text
                        }
                    }))
                    list = defaultList.concat(this.projectNotifyGroup)
                }
                return list
            }
        },
        created () {
            this.getNotifyTypeList()
            if (!this.common) {
                this.getProjectNotifyGroup()
            }
        },
        mounted () {
            this.$refs.nameInput.focus()
        },
        methods: {
            ...mapMutations('template/', [
                'setTplConfig'
            ]),
            ...mapActions([
                'getNotifyTypes',
                'getNotifyGroup'
            ]),
            async getNotifyTypeList () {
                try {
                    this.notifyTypeLoading = true
                    const res = await this.getNotifyTypes()
                    this.notifyTypeList = [{ text: i18n.t('任务状态') }].concat(res.data)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.notifyTypeLoading = false
                }
            },
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
            async getProjectNotifyGroup () {
                try {
                    this.notifyGroupLoading = true
                    const res = await this.getNotifyGroup({ project_id: this.$route.params.project_id })
                    this.projectNotifyGroup = res.data
                } catch (e) {
                    console.log(e)
                } finally {
                    this.notifyGroupLoading = false
                }
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
                if (this.authActions.includes('project_edit')) {
                    this.$router.push({ name: 'projectConfig', params: { id: this.$route.params.project_id } })
                }
            },
            getNotifyTypeHeader (h, data) {
                const col = this.notifyTypeList[data.$index]
                if (col.type) {
                    return h('div', { 'class': 'notify-table-heder' }, [
                        h('img', { 'class': 'notify-icon', attrs: { src: `data:image/png;base64,${col.icon}` } }, []),
                        h('span', { style: 'word-break: break-all;' }, [col.label])
                    ])
                } else {
                    return h('span', {}, [col.text])
                }
            },
            onSelectNotifyType (row, type, val) {
                const data = this.formData.notifyType[row]
                if (val) {
                    data.push(type)
                } else {
                    const index = data.findIndex(item => item === type)
                    if (index > -1) {
                        data.splice(index, 1)
                    }
                }
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
    .bk-form-checkbox {
        margin-right: 20px;
        margin-bottom: 6px;
        min-width: 96px;
        /deep/ .bk-checkbox-text {
            color: $greyDefault;
            font-size: 12px;
        }
    }
    /deep/ .bk-checkbox-text {
        display: inline-flex;
        align-items: center;
        width: 100px;
    }
    .notify-type-table {
        /deep/ .notify-table-heder {
            display: flex;
            align-items: center;
            .notify-icon {
                margin-right: 4px;
                width: 18px;
            }
        }
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
    .bloack {
        display: block;
    }
}
</style>
