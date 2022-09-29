<template>
    <section class="info-section" data-test-id="taskExecute_form_excuteInfo">
        <h4 class="common-section-title">{{ $t('节点基础信息') }}</h4>
        <table class="operation-table">
            <tr v-if="isSubProcessNode">
                <th>{{ $t('流程模板') }}</th>
                <td v-if="templateName">
                    {{ templateName }}
                    <i class="commonicon-icon common-icon-jump-link" @click="onSkipSubTemplate"></i>
                </td>
                <td v-else>
                    {{ '--' }}
                </td>
            </tr>
            <template v-else>
                <tr>
                    <th>{{ $t('标准插件') }}</th>
                    <td>{{ executeInfo.plugin_name || '--' }}</td>
                </tr>
                <tr>
                    <th>{{ $t('插件版本') }}</th>
                    <td>{{ executeInfo.plugin_version || '--' }}</td>
                </tr>
            </template>
            <tr>
                <th>{{ $t('节点名称') }}</th>
                <td>{{ nodeActivity.name || '--' }}</td>
            </tr>
            <tr>
                <th>{{ $t('步骤名称') }}</th>
                <td>{{ nodeActivity.stage_name || '--' }}</td>
            </tr>
            <tr v-if="isSubProcessNode">
                <th>{{ $t('执行方案') }}</th>
                <td>{{ schemeTextValue || '--' }}</td>
            </tr>
            <tr>
                <th>{{ $t('是否可选') }}</th>
                <td>{{ nodeActivity.optional ? $t('是') : $t('否') }}</td>
            </tr>
            <tr>
                <th>{{ $t('失败处理') }}</th>
                <td class="error-handle-td" v-if="nodeActivity.ignorable || nodeActivity.skippable || nodeActivity.retryable || nodeActivity.auto_retry">
                    <template v-if="nodeActivity.ignorable">
                        <span class="error-handle-icon"><span class="text">AS</span></span>
                        {{ $t('自动跳过') }};
                    </template>
                    <template v-if="nodeActivity.skippable">
                        <span class="error-handle-icon"><span class="text">MS</span></span>
                        {{ $t('手动跳过') }};
                    </template>
                    <template v-if="nodeActivity.retryable">
                        <span class="error-handle-icon"><span class="text">MR</span></span>
                        {{ $t('手动重试') }};
                    </template>
                    <template v-if="nodeActivity.auto_retry && nodeActivity.auto_retry.enable">
                        <span class="error-handle-icon"><span class="text">AR</span></span>
                        {{ $t('在') + $tc('秒', 0) + $t('后') + $t('，') + $t('自动重试') + ' ' + nodeActivity.auto_retry.times + ' ' + $t('次') }}
                    </template>
                </td>
                <td v-else>{{ '--' }}</td>
            </tr>
            <tr>
                <th>{{ $t('超时控制') }}</th>
                <td>{{ timeoutTextValue }}</td>
            </tr>
            <tr v-if="isSubProcessNode">
                <th>{{ $t('总是使用最新版本') }}</th>
                <td>{{ !('always_use_latest' in nodeActivity) ? '--' : nodeActivity.always_use_latest ? $t('是') : $t('否') }}</td>
            </tr>
        </table>
        <template v-if="!isReadyStatus">
            <InputParams
                :inputs="executeInfo.inputs"
                :render-config="executeInfo.renderConfig"
                :render-data="executeInfo.renderData">
            </InputParams>
            <OutputParams
                :outputs="executeInfo.outputsInfo"
                :node-detail-config="nodeDetailConfig">
            </OutputParams>
        </template>
    </section>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'
    import InputParams from './InputParams.vue'
    import OutputParams from './OutputParams.vue'

    export default {
        components: {
            InputParams,
            OutputParams
        },
        props: {
            isReadyStatus: {
                type: Boolean,
                default: false
            },
            nodeActivity: {
                type: Object,
                default: () => ({})
            },
            executeInfo: {
                type: Object,
                default: () => ({})
            },
            nodeDetailConfig: {
                type: Object,
                default: () => ({})
            },
            isSubProcessNode: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                templateName: '',
                schemeTextValue: ''
            }
        },
        computed: {
            ...mapState('project', {
                'projectId': state => state.project_id,
                'projectName': state => state.projectName
            }),
            timeoutTextValue () {
                const timeoutConfig = this.nodeActivity['timeout_config']
                if (!timeoutConfig || !timeoutConfig.enable) return '--'
                const actionText = timeoutConfig.action === 'forced_fail' ? i18n.t('强制失败') : i18n.t('强制失败后跳过')
                return i18n.t('超时') + ' ' + timeoutConfig.seconds + ' ' + i18n.tc('秒', 0) + i18n.t('后') + i18n.t('则') + actionText
            },
            componentValue () {
                return this.nodeActivity.component.data.subprocess.value
            }
        },
        mounted () {
            if (this.nodeActivity.original_template_id) {
                this.getTemplateData()
                this.getSchemeTextValue()
            }
        },
        methods: {
            ...mapActions('template/', [
                'getTemplatePublicData',
                'getCommonTemplatePublicData'
            ]),
            ...mapActions('task/', [
                'loadTaskScheme'
            ]),
            async getTemplateData () {
                const { template_source } = this.componentValue
                const data = {
                    templateId: this.nodeActivity.original_template_id,
                    project__id: this.projectId
                }
                let templateData = {}
                if (template_source === 'common') {
                    templateData = await this.getCommonTemplatePublicData(data)
                } else {
                    templateData = await this.getTemplatePublicData(data)
                }
                this.templateName = templateData.data.name
            },
            async getSchemeTextValue () {
                const { scheme_id_list: schemeIds, template_source } = this.componentValue
                const schemeList = await this.loadTaskScheme({
                    project_id: this.projectId,
                    template_id: this.nodeActivity.original_template_id,
                    isCommon: template_source === 'common'
                }) || []
                this.schemeTextValue = schemeList.reduce((acc, cur) => {
                    if (schemeIds.includes(cur.id)) {
                        acc = acc ? acc + ',' + cur.name : cur.name
                    }
                    return acc
                }, '')
            },
            onSkipSubTemplate () {
                const { href } = this.$router.resolve({
                    name: this.componentValue.template_source === 'common' ? 'projectCommonTemplatePanel' : 'templatePanel',
                    params: { type: 'view' },
                    query: { template_id: this.nodeActivity.original_template_id }
                })
                window.open(href, '_blank')
            }
        }
    }
</script>

<style lang="scss" scoped>
    .operation-table {
        font-size: 12px;
        table-layout: fixed;
        margin-top: 12px;
        th {
            width: 140px;
            font-weight: 400;
            color: #313238 !important;
            background: #fafbfd !important;
        }
        td {
            position: relative;
            color: #63656e;
        }
    }
    .error-handle-icon {
        display: inline-block;
        line-height: 12px;
        color: #ffffff;
        background: #979ba5;
        border-radius: 2px;
        .text {
            display: inline-block;
            font-size: 12px;
            transform: scale(0.8);
        }
    }
    /deep/.input-section,
    /deep/.outputs-section {
        position: relative;
        border: 1px solid #dde4eb;
        background: #fff;
        h4 {
            flex-shrink: 0;
            width: 140px;
            padding: 16px 0 0 12px;
            margin: 0;
            background: #fafbfd;
            font-weight: 400;
            border-right: 1px solid #dde4eb;
        }
        .origin-value {
            position: absolute;
            right: 16px;
            top: 16px;
        }
        .input-table,
        .outputs-table {
            margin-left: 0 !important;
            padding: 35px 16px 16px;
            th,
            .table-header {
                font-weight: normal;
                background: #fff;
            }
            td {
                background: #fff;
            }
        }
        .full-code-editor {
            flex: 1;
            margin: 50px 16px 16px;
        }
        .no-data-wrapper {
            background: #fff !important;
            .no-data-wording {
                color: #63656e;
                font-size: 12px;
            }
        }
    }
    .input-section {
        margin-top: 24px;
        margin-bottom: -1px;
    }
    .common-icon-jump-link {
        position: absolute;
        top: 12px;
        right: 10px;
        color: #3a84ff;
        cursor: pointer;
    }
    
</style>
