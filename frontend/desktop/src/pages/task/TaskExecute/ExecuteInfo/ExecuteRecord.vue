<template>
    <div class="execute-record">
        <template v-if="Object.keys(executeInfo).length && !notPerformedSubNode">
            <section class="info-section abnormal-section" data-test-id="taskExecute_form_exceptionInfo" v-if="executeInfo.ex_data">
                <p class="hide-html-text" v-html="executeInfo.failInfo"></p>
                <div class="show-html-text" :class="{ 'is-fold': !isExpand }" v-html="executeInfo.failInfo"></div>
                <span class="expand-btn" v-if="isExpandTextShow" @click="isExpand = !isExpand">{{ isExpand ? $t('收起') : $t('显示全部') }}</span>
            </section>
            <section class="info-section" data-test-id="taskExecute_form_executeInfo">
                <ul class="operation-table" v-if="isReadyStatus">
                    <li>
                        <p class="th">{{ $t('执行结果') }}</p>
                        <p class="td">{{ nodeState || '--' }}</p>
                    </li>
                    <li>
                        <p class="th">{{ $t('开始时间') }}</p>
                        <p class="td">{{ executeInfo.start_time || '--' }}</p>
                    </li>
                    <li>
                        <p class="th">{{ $t('结束时间') }}</p>
                        <p class="td">{{ executeInfo.finish_time || '--' }}</p>
                    </li>
                    <li>
                        <p class="th">{{ $t('耗时') }}</p>
                        <p class="td">{{ executeInfo.finish_time && getLastTime(executeInfo.elapsed_time) || '--' }}</p>
                    </li>
                </ul>
                <NoData v-else :message="$t('暂无执行信息')"></NoData>
            </section>
            <!-- 任务节点才允许展示输入、输出配置 -->
            <template v-if="['tasknode', 'subflow'].includes(location.type)">
                <InputParams
                    :admin-view="adminView"
                    :inputs="executeInfo.inputs"
                    :render-config="executeInfo.renderConfig"
                    :constants="executeInfo.constants"
                    :render-data="executeInfo.renderData">
                </InputParams>
                <OutputParams
                    :is-ready-status="isReadyStatus"
                    :admin-view="adminView"
                    :outputs="executeInfo.outputsInfo"
                    :node-detail-config="nodeDetailConfig">
                </OutputParams>
            </template>
        </template>
        <NoData v-else :message="$t('暂无执行信息')"></NoData>
    </div>
</template>

<script>
    import tools from '@/utils/tools.js'
    import InputParams from './InputParams.vue'
    import OutputParams from './OutputParams.vue'
    import NoData from '@/components/common/base/NoData.vue'
    export default {
        name: 'executeRecord',
        components: {
            InputParams,
            OutputParams,
            NoData
        },
        props: {
            adminView: {
                type: Boolean,
                default: false
            },
            loading: {
                type: Boolean,
                default: false
            },
            location: {
                type: Object,
                default: () => ({})
            },
            isReadyStatus: {
                type: Boolean,
                default: false
            },
            nodeState: {
                type: String,
                default: ''
            },
            executeInfo: {
                type: Object,
                default: () => ({})
            },
            nodeDetailConfig: {
                type: Object,
                default: () => ({})
            },
            notPerformedSubNode: {
                type: Boolean,
                default: false
            },
            isSubProcessNode: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                isExpand: false,
                isExpandTextShow: false
            }
        },
        mounted () {
            const showDom = document.querySelector('.show-html-text')
            const hideDom = document.querySelector('.hide-html-text')
            if (showDom && hideDom) {
                const showDomHeight = showDom.getBoundingClientRect().height
                const hideDomHeight = hideDom.getBoundingClientRect().height
                this.isExpandTextShow = hideDomHeight > showDomHeight
            }
        },
        methods: {
            getLastTime (time) {
                return tools.timeTransform(time)
            },
            onSkipSubProcess () {
                const taskInfo = this.executeInfo.outputsInfo.find(item => item.key === 'task_url')
                if (taskInfo) {
                    window.open(taskInfo.value, '_blank')
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
.execute-record {
    /deep/.abnormal-section {
        position: relative;
        font-size: 12px;
        margin-bottom: 8px !important;
        color: #313238;
        background: #fff3e1;
        border: 1px solid #ffb848;
        border-radius: 2px;
        word-break: break-all;
        .hide-html-text {
            position: absolute;
            z-index: -1;
        }
        .hide-html-text,
        .show-html-text {
            margin: 8px 16px;
        }
        .is-fold {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: normal;
            display: -webkit-box;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 10;
        }
        .expand-btn {
            position: absolute;
            right: 16px;
            bottom: 8px;
            padding-left: 5px;
            color: #3a84ff;
            background: #fff3e1;
            cursor: pointer;
        }
        a {
            color: #3a84ff;
        }
    }
    .not-fail {
        color: #979ba5;
        font-size: 12px;
        padding-left: 15px;
    }
    .operation-table {
        display: flex;
        align-items: center;
        padding: 12px 24px;
        margin-bottom: 24px;
        border: none;
        border-radius: 2px;
        background: #fafbfd;
        li {
            width: 30%;
            font-size: 12px;
            line-height: 26px;
            .th {
                font-weight: 400;
                color: #979ba5;
                margin-bottom: 2px;
                background: #fafbfd;
            }
            .td {
                color: #313238;
            }
            &:first-child,
            &:last-child {
                width: 20%;
            }
        }
    }
    .info-section {
        position: relative;
        .subprocee-link {
            display: flex;
            align-items: center;
            position: absolute;
            right: 0;
            top: 0;
            font-size: 12px;
            color: #3a84ff;
            cursor: pointer;
            i {
                margin-right: 6px;
            }
        }
    }
    /deep/.input-section,
    /deep/.outputs-section {
        font-size: 12px;
        .origin-value {
            position: absolute;
            top: 0;
            right: 0;
            display: flex;
            align-items: center;
            font-size: 12px;
            color: #63656e;
            .bk-switcher {
                top: 1px;
                margin-right: 8px;
            }
        }
    }
    .full-code-editor {
        flex: 1;
        margin: 20px 0 0 48px;
    }
    /deep/.no-data-wrapper {
        .no-data-wording {
            font-size: 12px;
            color: #63656e;
        }
    }
    /deep/.exception-part {
        margin-top: 20px;
        .part-text {
            font-size: 12px;
            color: #979ba5;
        }
    }
    .ex-data-wrap {
        /deep/ pre {
            white-space: pre-wrap;
        }
    }
    .perform-log {
        width: 100%;
    }
    .info-section:not(:last-child) {
        margin-bottom: 32px;
    }
    .no-data-wrapper {
        height: 150px;
        margin-top: 32px;
    }
}
</style>
