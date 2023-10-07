<template>
    <bk-sideslider
        :title="$t('执行设置')"
        :is-show="true"
        :width="800"
        :quick-close="true"
        :before-close="beforeClose">
        <div class="config-wrapper" slot="content">
            <bk-form
                ref="configForm"
                class="form-area"
                :model="formData"
                :label-width="140">
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
                        :project_id="projectId"
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
                            :placeholder="proxyPlaceholder"
                            :value="formData.executorProxy"
                            @change="formData.executorProxy = $event">
                        </member-select>
                        <div class="executor-proxy-desc">
                            {{ $t('推荐留空使用') }}
                            <span
                                :class="{ 'project-management': authActions && authActions.length, 'disabled': isViewMode }"
                                @click="jumpProjectManagement">
                                {{ $t('项目执行代理人设置') }}
                            </span>
                            {{ $t('以便统一管理，也可单独配置流程执行代理人覆盖项目的设置') }}
                        </div>
                    </bk-form-item>
                    <bk-form-item property="notifyType" :label="$t('备注')" data-test-id="tabTemplateConfig_form_notifyType">
                        <bk-input type="textarea" :readonly="isViewMode" v-model.trim="formData.description" :rows="5" :placeholder="$t('请输入流程模板备注信息')"></bk-input>
                    </bk-form-item>
                </section>
            </bk-form>
            <div class="btn-wrap">
                <bk-button class="save-btn" theme="primary" data-test-id="tabTemplateConfig_form_saveBtn" @click="onSaveConfig">{{ isViewMode ? $t('编辑') : $t('保存') }}</bk-button>
                <bk-button v-if="!isViewMode" theme="default" data-test-id="tabTemplateConfig_form_cancelBtn" @click="closeTab">{{ $t('取消') }}</bk-button>
            </div>
        </div>
    </bk-sideslider>
</template>

<script>
    import { mapState, mapMutations, mapActions } from 'vuex'
    import MemberSelect from '@/components/common/Individualization/MemberSelect.vue'
    import tools from '@/utils/tools.js'
    import i18n from '@/config/i18n/index.js'
    import NotifyTypeConfig from './NotifyTypeConfig.vue'
    import permission from '@/mixins/permission.js'

    export default {
        name: 'TabTemplateConfig',
        components: {
            MemberSelect,
            NotifyTypeConfig
        },
        mixins: [permission],
        props: {
            common: [String, Number],
            isViewMode: Boolean
        },
        data () {
            const { notify_type, notify_receivers, description, executor_proxy } = this.$store.state.template
            return {
                formData: {
                    description,
                    executorProxy: executor_proxy ? [executor_proxy] : [],
                    receiverGroup: notify_receivers.receiver_group.slice(0),
                    notifyType: [notify_type.success.slice(0), notify_type.fail.slice(0)]
                },
                proxyPlaceholder: ''
            }
        },
        computed: {
            ...mapState({
                'infoBasicConfig': state => state.infoBasicConfig
            }),
            ...mapState('project', {
                'projectId': state => state.project_id,
                'projectName': state => state.projectName,
                'authActions': state => state.authActions
            })
        },
        mounted () {
            // 模板没有设置执行代理人时，默认使用项目下的执行代理人
            if (!this.formData.executorProxy.length) {
                this.setExecutorProxy()
            }
        },
        methods: {
            ...mapMutations('template/', [
                'setTplConfig'
            ]),
            ...mapActions('project', [
                'getProjectConfig'
            ]),
            getTemplateConfig () {
                const { description, executorProxy, receiverGroup, notifyType } = this.formData
                return {
                    description,
                    executor_proxy: executorProxy.length === 1 ? executorProxy[0] : '',
                    receiver_group: receiverGroup,
                    notify_type: { success: notifyType[0], fail: notifyType[1] }
                }
            },
            jumpProjectManagement () {
                if (this.isViewMode) return
                if (this.authActions.includes('project_edit')) {
                    const { href } = this.$router.resolve({
                        name: 'projectConfig',
                        params: { id: this.projectId }
                    })
                    window.open(href, '_blank')
                } else {
                    const resourceData = {
                        project: [{
                            id: this.projectId,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission(['project_edit'], this.authActions, resourceData)
                }
            },
            onSelectNotifyConfig (formData) {
                const { notifyType, receiverGroup } = formData
                this.formData.notifyType = notifyType
                this.formData.receiverGroup = receiverGroup
            },
            onSaveConfig () {
                if (this.isViewMode) {
                    const { params, query, name } = this.$route
                    this.$router.push({
                        name,
                        params: { ...params, type: 'edit' },
                        query
                    })
                    return
                }
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
            beforeClose () {
                const { description, executor_proxy, notify_receivers, notify_type } = this.$store.state.template
                const originData = {
                    description,
                    executor_proxy,
                    receiver_group: notify_receivers.receiver_group,
                    notify_type
                }
                const editingData = this.getTemplateConfig()
                if (tools.isDataEqual(originData, editingData)) {
                    this.closeTab()
                    return true
                } else {
                    this.$bkInfo({
                        ...this.infoBasicConfig,
                        confirmFn: () => {
                            this.closeTab()
                        }
                    })
                    return false
                }
            },
            closeTab () {
                this.$emit('closeTab')
            },
            // 获取代理人设置数据
            async setExecutorProxy () {
                try {
                    const resp = await this.getProjectConfig(this.projectId)
                    if (resp.result) {
                        const { executor_proxy, executor_proxy_exempts } = resp.data
                        this.proxyPlaceholder = i18n.t('项目执行代理人(n)；免代理用户(m)', {
                            n: executor_proxy || '--',
                            m: executor_proxy_exempts || '--'
                        })
                    }
                } catch (e) {
                    console.log(e)
                }
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
        padding: 16px;
        height: calc(100% - 49px);
        background: #f5f7fa;
        overflow-y: auto;
        @include scrollbar;
    }
    .form-section {
        margin-bottom: 30px;
        padding-bottom: 24px;
        background: #fff;
        box-shadow: 0 2px 4px 0 #1919290d;
        border-radius: 2px;
        & > h4 {
            position: relative;
            height: 32px;
            line-height: 31px;
            padding-left: 24px;
            margin: 0 0 10px;
            color: #313238;
            font-weight: bold;
            font-size: 12px;
            border-bottom: 1px solid #dcdee5;
        }
        .tip-desc {
            font-weight: normal;
            margin-left: 16px;
            color: #979ba5;
        }
        /deep/.bk-form-item {
            padding: 0 24px;
            .bk-label {
                text-align: left;
            }
            .bk-form-content {
                float: inherit;
                margin-left: 0 !important;
            }
        }
    }
    .btn-wrap {
        padding: 8px 24px;
        border-top: 1px solid #c4c6cc;
        background: #fafbfd;
        border-radius: 2px;
        .bk-button {
            margin-right: 10px;
            padding: 0 25px;
        }
    }
    .user-selector {
        display: block;
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
