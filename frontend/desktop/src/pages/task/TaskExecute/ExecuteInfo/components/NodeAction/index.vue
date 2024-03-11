<template>
    <div class="action-wrapper" v-if="isShowActionWrap">
        <bk-button
            v-if="isShowContinueBtn"
            theme="primary"
            data-test-id="taskExecute_form_continueBtn"
            @click="onContinueClick">
            {{ $t('继续执行') }}
        </bk-button>
        <template v-if="executingStates.includes(realTimeState.state)">
            <bk-button
                v-if="realTimeState.state !== 'PENDING_PROCESSING' && (isLegacySubProcess || isSubProcessNode)"
                theme="primary"
                data-test-id="taskExecute_form_pauseBtn"
                @click="onPauseClick">
                {{ $t('暂停执行') }}
            </bk-button>
            <bk-button
                v-if="nodeDetailConfig.component_code === 'pause_node'"
                theme="primary"
                data-test-id="taskExecute_form_resumeBtn"
                @click="onResumeClick">
                {{ $t('确认继续') }}
            </bk-button>
            <bk-button
                v-else-if="nodeDetailConfig.component_code === 'bk_approve'"
                theme="primary"
                data-test-id="taskExecute_form_approvalBtn"
                @click="onApprovalClick">
                {{ $t('审批') }}
            </bk-button>
            <bk-button
                v-else-if="!isLegacySubProcess"
                data-test-id="taskExecute_form_mandatoryFailBtn"
                @click="onForceFail">
                {{ $t('强制终止') }}
            </bk-button>
        </template>
        <template v-if="isShowRetryBtn || isShowSkipBtn">
            <span
                v-bk-tooltips="{
                    content: $t('节点自动重试中，暂时无法手动重试'),
                    disabled: !autoRetryInfo.h || autoRetryInfo.m === autoRetryInfo.c
                }">
                <bk-button
                    theme="primary"
                    v-if="isShowRetryBtn"
                    data-test-id="taskExecute_form_retryBtn"
                    :disabled="autoRetryInfo.h && autoRetryInfo.m !== autoRetryInfo.c"
                    @click="onRetryClick">
                    {{ isSubProcessNode ? $t('重试子流程') : $t('重试') }}
                </bk-button>
            </span>
            <bk-button
                theme="default"
                v-if="isShowSkipBtn"
                data-test-id="taskExecute_form_skipBtn"
                @click="onSkipClick">
                {{ isSubProcessNode ? $t('跳过子流程') : $t('跳过') }}
            </bk-button>
        </template>
    </div>
</template>

<script>
    import { NODE_DICT } from '@/constants/index.js'
    export default {
        name: 'nodeAction',
        props: {
            realTimeState: {
                type: Object,
                default: () => ({})
            },
            nodeDetailConfig: {
                type: Object,
                default: () => ({})
            },
            nodeStateMapping: {
                type: Object,
                default: () => ({})
            },
            subprocessTasks: {
                type: Object,
                default: () => ({})
            },
            subprocessNodesState: {
                type: Object,
                default: () => ({})
            },
            pipelineData: {
                type: Object,
                default: () => ({})
            },
            executeInfo: {
                type: Object,
                default: () => ({})
            },
            subprocessState: {
                type: String,
                default: ''
            },
            subprocessPipeline: {
                type: Object,
                default: () => ({})
            },
            autoRetryInfo: {
                type: Object,
                default: () => ({})
            }
        },
        data () {
            return {
                executingStates: ['RUNNING', 'PENDING_PROCESSING', 'PENDING_APPROVAL', 'PENDING_CONFIRMATION']
            }
        },
        computed: {
            isSubProcessNode () {
                return this.nodeDetailConfig.component_code === 'subprocess_plugin'
            },
            isLegacySubProcess () {
                return this.nodeDetailConfig.type === 'SubProcess'
            },
            isShowActionWrap () {
                // 任务终止时禁止节点操作
                if (this.state === 'REVOKED' || (!this.isSubProcessNode && this.subprocessState === 'REVOKED')) {
                    return false
                }
                // 判断父级节点是否存在失败后跳过
                if (this.nodeDetailConfig.taskId) {
                    const parentIds = this.nodeDetailConfig.root_node.split('-')
                    const isFailedSkip = parentIds.some(id => {
                        const { state, skip } = this.nodeStateMapping[id] || {}
                        return state === 'FINISHED' && skip
                    })

                    if (isFailedSkip) {
                        return false
                    }

                    // 检查根节点的状态，如果有撤销的状态，则不继续执行
                    const rootNodeStates = Object.keys(this.subprocessTasks).reduce((acc, taskId) => {
                        const stateInfo = this.subprocessTasks[taskId]
                        if (parentIds.includes(stateInfo.node_id)) {
                            const { state } = this.subprocessNodesState[taskId]
                            acc.push(state)
                        }
                        return acc
                    }, [])

                    if (rootNodeStates.includes('REVOKED')) {
                        return false
                    }
                }
                const executeState = this.executingStates.includes(this.realTimeState.state)
                return executeState
                    || this.isShowRetryBtn
                    || this.isShowSkipBtn
                    || this.isShowContinueBtn
            },
            isShowSkipBtn () {
                let isShow = false
                if (this.realTimeState.state === 'FAILED') {
                    const { type } = this.location
                    if (type === 'tasknode') {
                        // 任务节点和独立子任务节点
                        const activity = this.pipelineData.activities[this.nodeDetailConfig.node_id]
                        isShow = activity.skippable
                    } else if (type !== 'subflow') {
                        // 网关节点
                        isShow = true
                    }
                }
                return isShow
            },
            isShowRetryBtn () {
                let isShow = false
                if (this.realTimeState.state === 'FAILED') {
                    const activity = this.pipelineData.activities[this.nodeDetailConfig.node_id]
                    isShow = this.location.type === 'tasknode' ? activity.retryable : false
                }
                return isShow
            },
            isShowContinueBtn () {
                if (this.isLegacySubProcess) {
                    return [this.realTimeState.state, this.executeInfo.state].includes('SUSPENDED')
                } else if (this.isSubProcessNode) {
                    const { taskId } = this.subprocessPipeline
                    const taskState = this.subprocessNodesState[taskId]?.state
                    return [this.realTimeState.state, taskState].includes('SUSPENDED')
                }
                return false
            },
            location () {
                const { node_id, subprocess_stack = [] } = this.nodeDetailConfig
                return this.pipelineData.location.find(item => {
                    if (item.id === node_id || subprocess_stack.includes(item.id)) {
                        return true
                    }
                })
            },
            subProcessTaskId () { // 独立子流程节点的任务id
                return this.nodeDetailConfig.taskId
            },
            nodeName () {
                const { name, type } = this.nodeDetailConfig
                return name || NODE_DICT[type]
            }
        },
        methods: {
            onRetryClick () {
                const info = {
                    name: this.nodeName,
                    taskId: this.subProcessTaskId,
                    isSubProcessNode: this.isSubProcessNode,
                    isSubNode: !!this.nodeDetailConfig.root_node
                }
                this.$emit('onRetryClick', this.nodeDetailConfig.node_id, info)
            },
            onSkipClick () {
                const info = {
                    name: this.nodeName,
                    taskId: this.subProcessTaskId,
                    isSubProcessNode: this.isSubProcessNode
                }
                this.$emit('onSkipClick', this.nodeDetailConfig.node_id, info)
            },
            onResumeClick () {
                this.$emit('onResumeClick', this.nodeDetailConfig.node_id, this.subProcessTaskId)
            },
            onApprovalClick () {
                this.$emit('onApprovalClick', this.nodeDetailConfig.node_id, this.subProcessTaskId)
            },
            onModifyTimeClick () {
                this.$emit('onModifyTimeClick', this.nodeDetailConfig.node_id, this.subProcessTaskId)
            },
            onForceFail () {
                // 节点绑定的是父流程的taskId，独立子流程节点操作应从子流程树中取taskId
                const taskId = this.isSubProcessNode ? this.subprocessPipeline.taskId : this.subProcessTaskId
                const info = {
                    name: this.nodeName,
                    taskId,
                    isSubProcessNode: this.isSubProcessNode
                }
                this.$emit('onForceFail', this.nodeDetailConfig.node_id, info)
            },
            onPauseClick () {
                // 节点绑定的是父流程的taskId，独立子流程节点操作应从子流程树中取taskId
                const taskId = this.isSubProcessNode ? this.subprocessPipeline.taskId : this.subProcessTaskId
                const info = {
                    taskId,
                    name: this.nodeName,
                    independent: this.isSubProcessNode
                }
                this.$emit('onPauseClick', this.nodeDetailConfig.node_id, info)
            },
            onContinueClick () {
                // 节点绑定的是父流程的taskId，独立子流程节点操作应从子流程树中取taskId
                const taskId = this.isSubProcessNode ? this.subprocessPipeline.taskId : this.subProcessTaskId
                const info = {
                    taskId,
                    name: this.nodeName,
                    independent: this.isSubProcessNode
                }
                this.$emit('onContinueClick', this.nodeDetailConfig.node_id, info)
            }
        }
    }
</script>
