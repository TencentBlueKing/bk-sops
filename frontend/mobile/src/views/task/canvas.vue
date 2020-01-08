/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="page-view">
        <div :class="[taskStateClass, taskStateColor]">{{ taskStateName }}</div>
        <MobileCanvas
            v-if="!loading"
            :canvas-data="canvasData"
            ref="canvas"
            @nodeClick="onNodeClick"></MobileCanvas>
        <van-tabbar>
            <van-tabbar-item>
                <van-icon
                    v-if="taskState === 'CREATED' && !operating"
                    slot="icon"
                    class-prefix="icon"
                    name="play"
                    @click="onOperationClick('execute')" />
                <van-icon
                    v-else-if="taskState === 'RUNNING' && !operating"
                    slot="icon"
                    class-prefix="icon"
                    name="pause"
                    @click="onOperationClick('pause')" />
                <van-icon
                    v-else-if="taskState === 'SUSPENDED' && !operating"
                    slot="icon"
                    class-prefix="icon"
                    name="play"
                    @click="onOperationClick('resume')" />
                <van-icon
                    v-else
                    slot="icon"
                    class-prefix="icon"
                    name="pause"
                    class="disabled"
                    disabled />
            </van-tabbar-item>
            <van-tabbar-item>
                <van-icon
                    v-if="taskState !== 'CREATED' && taskState !== 'REVOKED' && taskState !== 'FINISHED' && !operating"
                    slot="icon"
                    class-prefix="icon"
                    name="revoke"
                    @click="onRevokeConfirm" />
                <van-icon
                    v-else
                    slot="icon"
                    class-prefix="icon"
                    name="revoke"
                    class="disabled"
                    disabled />
            </van-tabbar-item>
            <van-tabbar-item>
                <van-icon
                    v-if="!operating"
                    slot="icon"
                    class-prefix="icon"
                    name="file"
                    @click="onDetailClick" />
                <van-icon
                    v-else
                    class="disabled"
                    disabled
                    slot="icon"
                    class-prefix="icon"
                    name="file" />
            </van-tabbar-item>
        </van-tabbar>
        <template>
            <van-dialog v-model="revokeConfirmShow" :title="i18n.tip" show-cancel-button />
        </template>
    </div>
</template>
<script>
    import { errorHandler } from '@/utils/errorHandler.js'
    import MobileCanvas from '@/components/MobileCanvas/index.vue'
    import { mapActions } from 'vuex'
    import Tooltip from 'tooltip.js'

    const TASK_STATE = {
        'CREATED': [window.gettext('未执行'), 'muted'],
        'RUNNING': [window.gettext('执行中'), 'info'],
        'SUSPENDED': [window.gettext('暂停'), 'warning'],
        'NODE_SUSPENDED': [window.gettext('节点暂停'), 'warning'],
        'FAILED': [window.gettext('失败'), 'danger'],
        'FINISHED': [window.gettext('完成'), 'success'],
        'REVOKED': [window.gettext('撤销'), 'danger']
    }

    const NODE_ACTION = ['Retry', 'Skip', 'Detail', 'Timer', 'Resume']

    export default {
        name: '',
        components: {
            MobileCanvas
        },
        data () {
            return {
                nodeTooltipInstance: {},
                operating: false,
                revokeConfirmShow: false,
                taskId: 0,
                task: {},
                taskState: '',
                taskStateClass: '',
                taskStateName: '',
                taskStateColor: '',
                pipelineTree: {},
                timer: null,
                loading: true,
                i18n: {
                    detail: window.gettext('执行详情'),
                    retry: window.gettext('重试'),
                    skip: window.gettext('跳过'),
                    sub: window.gettext('查看子流程'),
                    editTime: window.gettext('修改时间'),
                    skipSuccess: window.gettext('跳过成功'),
                    skipFailed: window.gettext('跳过失败'),
                    retrySuccess: window.gettext('重试成功'),
                    resume: window.gettext('继续'),
                    executeStartFailed: window.gettext('开始执行任务失败'),
                    loading: window.gettext('加载中...')
                }
            }
        },
        computed: {
            canvasData () {
                this.pipelineTree = this.$store.state.pipelineTree
                const { line = [], location = [], gateways = {} } = this.pipelineTree
                return { lines: line, nodes: location, gateways: gateways }
            }
        },
        created () {
            this.loadData()
        },
        destroyed () {
            this.$el.removeEventListener('click', this.handleNodeActionClick, false)
            this.clearNodeTooltipInstance()
            this.cancelTaskStatusTimer()
        },
        mounted () {
            this.$el.addEventListener('click', this.handleNodeActionClick, false)
        },
        methods: {
            ...mapActions('task', [
                'getTask',
                'getTaskStatus',
                'instanceStart',
                'instancePause',
                'instanceResume',
                'instanceRevoke',
                'instanceNodeResume',
                'instanceNodeSkip',
                'getNodeRetryData',
                'instanceNodeRetry'
            ]),
            async loadData () {
                try {
                    this.$toast.loading({ mask: true, message: this.i18n.loading })
                    this.taskId = this.$route.query.taskId
                    this.task = await this.getTask({ id: this.taskId })
                    this.pipelineTree = JSON.parse(this.task.pipeline_tree)
                    this.$store.commit('setPipelineTree', this.pipelineTree)
                    await this.loadTaskStatus()
                    this.$nextTick(() => {
                        this.loading = false
                        this.$toast.clear()
                    })
                } catch (err) {
                    errorHandler(err, this)
                }
            },
            onOperationClick (operation) {
                if (!this.operating) {
                    this.operating = true
                    this[operation]()
                }
            },
            updateTaskNodes (taskState) {
                if (taskState.state !== 'CREATED') {
                    this.canvasData.nodes.forEach((node) => {
                        const data = taskState.children[node.id]
                        this.$set(node, 'data', data)
                        if (data) {
                            this.$set(node, 'status', data.state)
                            if (node.type === 'tasknode' || node.type === 'subflow') {
                                if (data.state === 'RUNNING') {
                                    if (this.$refs.canvas) {
                                        this.$refs.canvas.setCanvasPosition(node)
                                    }
                                } else {
                                    this.clearNodeTooltipInstance()
                                }
                            }
                        }
                    })
                }
            },
            async loadTaskStatus () {
                try {
                    const taskState = await this.getTaskStatus({ id: this.taskId })
                    if (taskState.result) {
                        this.taskState = taskState.data.state
                        this.updateTaskNodes(taskState.data)
                        if (this.taskState === 'RUNNING') {
                            this.setTaskStatusTimer()
                        }
                        ([this.taskStateClass, this.taskStateName, this.taskStateColor] = ['task-status', ...TASK_STATE[this.taskState]])
                    } else {
                        this.cancelTaskStatusTimer()
                        errorHandler(taskState, this)
                    }
                } catch (e) {
                    this.cancelTaskStatusTimer()
                    errorHandler(e, this)
                }
            },

            setTaskStatusTimer () {
                this.cancelTaskStatusTimer()
                this.timer = setTimeout(() => {
                    this.loadTaskStatus()
                }, 2000)
            },
            cancelTaskStatusTimer () {
                if (this.timer) {
                    clearTimeout(this.timer)
                    this.timer = null
                }
            },
            async execute () {
                try {
                    this.$toast.loading({ mask: true, message: this.i18n.loading })
                    const response = await this.instanceStart({ id: this.taskId })
                    if (response.result) {
                        this.setTaskStatusTimer()
                    } else {
                        errorHandler(response, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.$toast.clear()
                    this.operating = false
                }
            },
            async revoke () {
                try {
                    const response = await this.instanceRevoke({ id: this.taskId })
                    if (response.result) {
                        global.bus.$emit('notify', { message: window.gettext('撤销成功') })
                        setTimeout(() => {
                            this.setTaskStatusTimer()
                        }, 1000)
                    } else {
                        errorHandler(response, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.operating = false
                }
            },
            onDetailClick () {
                this.cancelTaskStatusTimer()
                this.$router.push({ path: '/task/detail', query: { taskId: String(this.taskId) } })
            },
            async pause () {
                try {
                    const response = await this.instancePause({ id: this.taskId })
                    if (response.result) {
                        global.bus.$emit('notify', { message: window.gettext('暂停成功') })
                    } else {
                        errorHandler(response, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.operating = false
                }
            },
            async resume () {
                try {
                    const response = await this.instanceResume({ id: this.taskId })
                    if (response.result) {
                        this.setTaskStatusTimer()
                        global.bus.$emit('notify', { message: window.gettext('任务继续成功') })
                    } else {
                        errorHandler(response, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.operating = false
                }
            },
            onRevokeConfirm () {
                this.$dialog.confirm({
                    message: window.gettext('撤销任务?')
                }).then(() => {
                    this.revokeConfirmShow = false
                    this.revoke()
                }).catch(() => {
                    this.revokeConfirmShow = false
                })
            },

            onNodeClick (node) {
                this.createTooltipInstance(node)
            },

            handleNodeActionClick (e) {
                const nodeAction = global.$(e.target).data('action')
                const nodeId = global.$(e.target).data('id')
                if (nodeId) {
                    const _node = this.canvasData.nodes.find(n => n.id === nodeId)
                    _node.componentCode = this.pipelineTree.activities[nodeId].component.code
                    if (nodeAction) {
                        this.onNodeOperationClick(nodeAction, _node)
                    }
                }
            },

            onNodeOperationClick (operation, node) {
                if (!this.operating) {
                    this.operating = true
                    if (NODE_ACTION.includes(operation)) {
                        this[`node${operation}`](node)
                    }
                }
            },

            createTooltipInstance (node) {
                if (node.type === 'tasknode' && node.status) {
                    let tip = null
                    if (!this.nodeTooltipInstance[node.id]) {
                        const nodeBtnTpl = this.getNodeBtnTpl(node)
                        if (nodeBtnTpl) {
                            const el = global.$(`[name=tip_${node.id}]`)[0]
                            tip = new Tooltip(el, {
                                placement: 'bottom',
                                html: true,
                                title: nodeBtnTpl
                            })
                            this.nodeTooltipInstance[node.id] = tip
                        }
                    } else {
                        tip = this.nodeTooltipInstance[node.id]
                        tip.hide()
                    }
                    if (tip) {
                        tip.show()
                    }
                }
            },

            getNodeBtnTpl (node) {
                const btnList = []
                node.componentCode = this.pipelineTree.activities[node.id].component.code
                if (node.status === 'RUNNING') {
                    if (node.componentCode === 'sleep_timer') {
                        btnList.push({ type: 'Timer', text: this.i18n.editTime })
                    } else if (node.componentCode === 'pause_node') {
                        btnList.push({ type: 'Resume', text: this.i18n.resume })
                    }
                } else if (node.status === 'FAILED') {
                    btnList.push({ type: 'Retry', text: this.i18n.retry })
                    btnList.push({ type: 'Skip', text: this.i18n.skip })
                    btnList.push({ type: 'Detail', text: this.i18n.detail })
                } else if (node.status === 'FINISHED') {
                    btnList.push({ type: 'Detail', text: this.i18n.detail })
                }
                if (btnList.length > 0) {
                    return this.nodeBtnTplFactory(btnList, node.id)
                } else {
                    return ''
                }
            },

            nodeBtnTplFactory (btnList, nodeId) {
                return `
                    <div class="btn-wrapper">
                    ${btnList.map(btn => `
                        <div class="tooltip-btn" data-action="${btn.type}" data-id="${nodeId}">${btn.text}</div>
                    `).join('')}
                    </div>
                    `
            },

            destroyTooltipInstance (id) {
                if (this.nodeTooltipInstance[id]) {
                    this.nodeTooltipInstance[id].dispose()
                    delete this.nodeTooltipInstance[id]
                }
            },
            clearNodeTooltipInstance () {
                Object.keys(this.nodeTooltipInstance).forEach(item => {
                    this.destroyTooltipInstance(item)
                })
            },

            nodeDetail (node) {
                this.$store.commit('setNode', node)
                this.$store.commit('setTaskId', this.taskId)
                this.$router.push({ name: 'task_nodes' })
            },

            async nodeRetry (node) {
                this.$toast.loading({ mask: true, message: this.i18n.loading })
                const params = {
                    taskId: this.taskId,
                    nodeId: node.id,
                    componentCode: node.componentCode
                }
                try {
                    const nodeRetryDataResponse = await this.getNodeRetryData(params)
                    if (nodeRetryDataResponse.result) {
                        const nodeRetryResponse = await this.instanceNodeRetry({
                            'instance_id': params.taskId,
                            'node_id': node.id,
                            'component_code': params.componentCode,
                            'inputs': JSON.stringify(nodeRetryDataResponse.data.inputs)
                        })
                        if (nodeRetryResponse.result) {
                            global.bus.$emit('notify', { message: this.i18n.retrySuccess })
                            setTimeout(() => {
                                this.setTaskStatusTimer()
                            }, 1000)
                        } else {
                            errorHandler(nodeRetryResponse, this)
                        }
                    } else {
                        errorHandler(nodeRetryDataResponse, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.$toast.clear()
                    this.operating = false
                    this.clearNodeTooltipInstance()
                }
            },
            async nodeSkip (node) {
                try {
                    this.$toast.loading({ mask: true, message: this.i18n.loading })
                    const response = await this.instanceNodeSkip({ id: this.taskId, nodeId: node.id })
                    if (response.result) {
                        global.bus.$emit('notify', { message: this.i18n.skipSuccess })
                        setTimeout(() => {
                            this.setTaskStatusTimer()
                        }, 1000)
                    } else {
                        errorHandler(response, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.$toast.clear()
                    this.operating = false
                    this.clearNodeTooltipInstance()
                }
            },
            async nodeResume (node) {
                try {
                    const response = await this.instanceNodeResume({ instance_id: this.taskId, node_id: node.id })
                    if (response.result) {
                        this.setTaskStatusTimer()
                    } else {
                        errorHandler(response, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.operating = false
                    this.clearNodeTooltipInstance()
                }
            },
            async nodeTimer (node) {
                this.$toast.loading({ mask: true, message: this.i18n.loading })
                const params = {
                    taskId: this.taskId,
                    nodeId: node.id,
                    componentCode: node.componentCode
                }
                const response = await this.getNodeRetryData(params)
                params.inputs = response.data.inputs
                this.$toast.clear()
                this.operating = false
                this.$router.push({ name: 'task_edit_timing', params: params })
            }
        }
    }
</script>

<style lang="scss" scoped>
    .page-view{
        -webkit-overflow-scrolling: auto;
        bottom: 50px;
    }
</style>
