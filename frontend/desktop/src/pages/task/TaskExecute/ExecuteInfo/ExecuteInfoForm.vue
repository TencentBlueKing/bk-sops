<template>
    <section class="info-section" data-test-id="taskExecute_form_excuteInfo">
        <h4 class="common-section-title">{{ $t('基础信息') }}</h4>
        <ul class="operation-table">
            <li v-if="isSubProcessNode">
                <span class="th">{{ $t('流程模板') }}</span>
                <span v-if="templateName" class="td">
                    {{ templateName }}
                    <i class="commonicon-icon common-icon-jump-link" @click="onSkipSubTemplate"></i>
                </span>
                <span v-else class="td">
                    {{ '--' }}
                </span>
            </li>
            <template v-else>
                <li>
                    <span class="th">{{ $t('标准插件') }}</span>
                    <span class="td">{{ executeInfo.plugin_name || '--' }}</span>
                </li>
                <li>
                    <span class="th">{{ $t('插件版本') }}</span>
                    <span class="td">{{ executeInfo.plugin_version || '--' }}</span>
                </li>
            </template>
            <li>
                <span class="th">{{ $t('节点名称') }}</span>
                <span class="td">{{ nodeActivity.name || '--' }}</span>
            </li>
            <li>
                <span class="th">{{ $t('步骤名称') }}</span>
                <span class="td">{{ nodeActivity.stage_name || '--' }}</span>
            </li>
            <li v-if="isSubProcessNode">
                <span class="th">{{ $t('执行方案') }}</span>
                <span class="td">{{ schemeTextValue || '--' }}</span>
            </li>
            <li>
                <span class="th">{{ $t('是否可选') }}</span>
                <span class="td">{{ nodeActivity.optional ? $t('是') : $t('否') }}</span>
            </li>
            <li>
                <span class="th">{{ $t('失败处理') }}</span>
                <span class="error-handle-td td" v-if="nodeActivity.ignorable || nodeActivity.skippable || nodeActivity.retryable || nodeActivity.auto_retry">
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
                        {{ $t('在') + $tc('秒', nodeActivity.auto_retry.interval) + $t('后') + $t('，') + $t('自动重试') + ' ' + nodeActivity.auto_retry.times + ' ' + $t('次') }}
                    </template>
                </span>
                <span v-else class="td">{{ '--' }}</span>
            </li>
            <!-- <li>
                <span class="th">{{ $t('超时控制') }}</span>
                <span class="td">{{ timeoutTextValue }}</span>
            </li> -->
            <li v-if="isSubProcessNode">
                <span class="th">{{ $t('总是使用最新版本') }}</span>
                <span class="td">{{ !('always_use_latest' in componentValue) ? '--' : componentValue.always_use_latest ? $t('是') : $t('否') }}</span>
            </li>
        </ul>
    </section>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'

    export default {
        props: {
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
                if (this.nodeActivity.component) {
                    return this.nodeActivity.component.data.subprocess.value
                }
                return {}
            }
        },
        mounted () {
            if (this.nodeActivity.original_template_id) {
                this.getTemplateData()
            }
        },
        methods: {
            ...mapActions('template/', [
                'getTemplatePublicData',
                'getCommonTemplatePublicData'
            ]),
            async getTemplateData () {
                const { template_source, scheme_id_list: schemeIds } = this.componentValue
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
                this.schemeTextValue = templateData.data.schemes.reduce((acc, cur) => {
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
        border: 1px solid #dcdee5 !important;
        border-bottom: none !important;
        li {
            display: flex;
            height: 42px;
            line-height: 41px;
            color: #63656e;
            border-bottom: 1px solid #dcdee5;
            .th {
                width: 140px;
                font-weight: 400;
                color: #313238;
                padding-left: 12px;
                border-right: 1px solid #dcdee5;
                background: #fafbfd;
            }
            .td {
                flex: 1;
                position: relative;
                padding-left: 12px;
            }
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
    .common-icon-jump-link {
        position: absolute;
        top: 15px;
        right: 10px;
        color: #3a84ff;
        cursor: pointer;
    }
    
</style>
