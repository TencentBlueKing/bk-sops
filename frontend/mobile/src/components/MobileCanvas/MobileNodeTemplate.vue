/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="task-node">
        <div
            v-if="node.type === 'startpoint'"
            :class="['node-circle', node['status'] ? node['status'].toLowerCase() : '']">
            <div class="node-type-status">{{ i18n.start }}</div>
        </div>
        <div
            v-else-if="node.type === 'endpoint'"
            :class="['node-circle', node['status'] ? node['status'].toLowerCase() : '']">
            <div class="node-type-status">{{ i18n.end }}</div>
        </div>
        <div v-else-if="node.type === 'tasknode'">
            <div
                ref="nodeLocation"
                :name="'tip_' + node.id"
                :class="['bk-flow-location', node['status'] ? node['status'].toLowerCase() : '']"
                @click="onNodeClick(node, $event)">
                <div class="node-name">
                    <p class="name">{{ node.name }}</p>
                </div>
                <div class="task-name">{{ node.stage_name }}</div>
            </div>
        </div>
        <div
            v-else-if="node.type === 'subflow'"
            ref="nodeLocation"
            :class="['bk-flow-location', 'node-subflow', node['status'] ? node['status'].toLowerCase() : '']"
            @click="onNodeClick(node, $event)">
            <div class="node-name">
                <div :class="['subflow-node-icon', node['status'] ? node['status'].toLowerCase() : '']">
                    <van-icon name="plus" />
                </div>
                <p class="name">{{ node.name }}</p>
            </div>
            <div class="task-name">{{ node.stage_name }}</div>
        </div>
        <div
            v-else
            ref="nodeLocation"
            class="node-circle">
            <van-icon slot="icon" class-prefix="icon" :name="`node-${node.type}`" />
        </div>
    </div>
</template>

<script>
    import Tooltip from 'tooltip.js'
    import { mapActions, mapState } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'

    const NODE_ACTION = ['retry', 'skip', 'detail', 'timer', 'resume']

    export default {
        name: 'MobileNodeTemplate',
        props: {
            node: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        inject: ['refreshTaskStatus'],
        data () {
            return {
                nodeTooltipInstance: {},
                i18n: {
                    start: window.gettext('开始'),
                    end: window.gettext('结束'),
                    detail: window.gettext('执行详情'),
                    retry: window.gettext('重试'),
                    skip: window.gettext('跳过'),
                    sub: window.gettext('查看子流程'),
                    editTime: window.gettext('修改时间'),
                    skipSuccess: window.gettext('跳过成功'),
                    skipFailed: window.gettext('跳过失败'),
                    resume: window.gettext('继续')
                }
            }
        },
        computed: {
            ...mapState({
                taskId: state => state.taskId
            })
        },
        destroyed () {
            this.$el.removeEventListener('click', this.handleNodeClick, false)
            this.clearNodeTooltipInstance()
        },
        mounted () {
            this.$el.addEventListener('click', this.handleNodeClick, false)
        },
        methods: {
            ...mapActions('task', [
                'getTask',
                'instanceNodeResume',
                'instanceNodeSkip',
                'getNodeRetryData'
            ]),
            handleNodeClick (e) {
                const nodeAction = global.$(e.target).data('action')
                if (nodeAction) {
                    this.onNodeOperationClick(nodeAction)
                }
            },
            onNodeClick (node) {
                const pipelineTree = this.$store.state.pipelineTree
                if (this.node.type === 'subflow') {
                    const subTree = pipelineTree.activities[node.id].pipeline
                    if (subTree) {
                        // 当前树替换成子流程树
                        this.$store.commit('setPipelineTree', subTree)
                    }
                } else {
                    const componentCode = pipelineTree.activities[node.id].component.code
                    if (!this.node.componentCode) {
                        this.$set(this.node, 'componentCode', componentCode)
                    }
                    if (this.node.type === 'tasknode' && this.node.status) {
                        let tip = null
                        if (!this.nodeTooltipInstance[node.id]) {
                            const el = global.$(`[name=tip_${node.id}]`)[0]
                            tip = new Tooltip(el, {
                                placement: 'bottom',
                                html: true,
                                title: this.getNodeBtnTpl(node)
                            })
                            this.nodeTooltipInstance[node.id] = tip
                        } else {
                            tip = this.nodeTooltipInstance[node.id]
                            tip.hide()
                        }
                        tip.show()
                    }
                }
            },

            getNodeBtnTpl (node) {
                const btnList = []
                if (node.status === 'RUNNING') {
                    if (node.componentCode === 'sleep_timer') {
                        btnList.push({ type: 'timer', text: this.i18n.editTime })
                    }
                    btnList.push({ type: 'resume', text: this.i18n.resume })
                } else if (node.status === 'FAILED') {
                    btnList.push({ type: 'retry', text: this.i18n.retry })
                    btnList.push({ type: 'skip', text: this.i18n.skip })
                }
                btnList.push({ type: 'detail', text: this.i18n.detail })
                return this.nodeBtnTplFactory(btnList)
            },

            nodeBtnTplFactory (btnList) {
                return `
                    <div class="btn-wrapper">
                    ${btnList.map(btn => `
                        <div class="tooltip-btn" data-action="${btn.type}">${btn.text}</div>
                    `).join('')}
                    </div>
                    `
            },

            onNodeOperationClick (operation) {
                if (!this.operating) {
                    this.operating = true
                    if (NODE_ACTION.includes(operation)) {
                        this[operation]()
                    }
                    this.operating = false
                }
            },
            detail () {
                this.$store.commit('setNode', this.node)
                this.$router.push({ name: 'task_nodes' })
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
            async retry () {
                this.$toast.loading({ mask: true, message: this.i18n.loading })
                const task = await this.getTask({ id: this.taskId })
                const pipelineTree = JSON.parse(task.pipeline_tree)
                const taskId = this.taskId
                const params = {
                    taskId: taskId,
                    nodeId: this.node.id,
                    componentCode: pipelineTree.activities[this.node.id].component.code
                }
                try {
                    const response = await this.getNodeRetryData(params)
                    params.inputs = response.data.inputs
                    const newInputs = {}
                    for (const k of Object.keys(params.inputs)) {
                        newInputs[`${params.componentCode}.${k}`] = { source_tag: `${params.componentCode}.${k}`, value: params.inputs[k] }
                    }
                    params.inputs = newInputs
                } catch (e) {
                    errorHandler(e, this)
                }
                this.$toast.clear()
                this.operating = false
                this.$router.push({ name: 'task_reset', params: params })
            },
            async skip () {
                try {
                    this.$toast.loading({ mask: true, message: this.i18n.loading })
                    const response = await this.instanceNodeSkip({ id: this.taskId, nodeId: this.node.id })
                    if (response.result) {
                        global.bus.$emit('notify', { message: this.i18n.skipSuccess })
                        setTimeout(() => {
                            this.refreshTaskStatus()
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
            async resume () {
                try {
                    const response = await this.instanceNodeResume({ id: this.taskId, nodeId: this.node.id })
                    if (response.result) {
                        this.refreshTaskStatus()
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
            async timer () {
                this.$toast.loading({ mask: true, message: this.i18n.loading })
                const task = await this.getTask({ id: this.taskId })
                const pipelineTree = JSON.parse(task.pipeline_tree)
                const taskId = this.taskId
                const params = {
                    taskId: taskId,
                    nodeId: this.node.id,
                    componentCode: pipelineTree.activities[this.node.id].component.code
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
    @import '../../../static/style/var.scss';

    .bk-flow-location {
        width: 152px;
        height: 90px;
        text-align: center;
        background: $white;
        position: relative;
        .node-name {
            width: 100%;
            font-size: $fs-12;
            height: 60px;
            line-height: 60px;
            background: #fafafa;
            border: 1px solid #a9adb5;
            border-bottom: none;
            overflow: hidden;
            .name {
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                padding: 0 10px;
                height: 100%;
            }
        }
        .task-name {
            height: 30px;
            line-height: 30px;
            font-size: $fs-14;
            color: $white;
            background: #53699d;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
    }

    .node-subflow.failed {
        border-top-color: #ff5757;
    }

    .node-subflow.finished {
        border-top-color: #30d878;
    }

    .node-subflow.suspended {
        border-top-color: #f8b53f;
    }

    .node-subflow {
        border-top: 5px solid #53699d;
        .node-name {
            height: 55px;
        }
        .subflow-node-icon {
            position: absolute;
            top: -2px;
            left: 0;
            width: 24px;
            height: 19px;
            line-height: 19px;
            color: $white;
            background: #53699d;
            > i {
                vertical-align: middle;
            }
        }

        .subflow-node-icon.failed {
            background: #ff5757;
        }
        .subflow-node-icon.finished {
            background: #30d878;
        }
        .bsubflow-node-icon.suspended {
            background: #f8b53f;
        }
    }

    .bk-flow-location.failed {
        .node-name {
            border-color: #ff5757;
        }
        .task-name {
            background: #ff5757;
        }
    }

    .bk-flow-location.finished {
        .node-name {
            border-color: #30d878;
        }
        .task-name {
            background: #30d878;
        }
    }

    .bk-flow-location.running, .bk-flow-location.suspended {
        .node-name {
            border-color: #f8b53f;
        }
        .task-name {
            background: #f8b53f;
        }
    }

    .node-circle{
        width: 60px;
        height: 60px;
        line-height: 60px;
        font-size: 30px;
        color: #53699d;
        text-align: center;
        background: #fff;
        border-radius: 50%;
        border: 1px dashed #b1b5bc;
        .icon{
            display: block;
            margin-top: 14px;
        }
        .node-type-status{
            background: #53699d;
            border-radius: 25px;
            display: block;
            font-size: $fs-12;
            color: $white;
            width: 50px;
            height: 50px;
            line-height: 50px;
            vertical-align: middle;
            margin: 4px;
        }
        &.finished{
            border-color: #2fca55;
            color: #2fca55;
            .node-type-status{
                background: #2fca55;
            }
        }
        &.failed{
            border-color: #ea3636;
            color: #ea3636;
            .node-type-status{
                background: #ea3636;
            }
        }
        &.suspended{
            border-color: #ff9c01;
            color: #ff9c01;
            .node-type-status{
                background: #ff9c01;
            }
        }
    }

    .task-node {
        /deep/ .tooltip {
            z-index: 4;
            &[x-placement^="top"] {
                padding-bottom: 5px;
                .tooltip-arrow {
                    border-width: 5px 5px 0 5px;
                    border-left-color: transparent;
                    border-right-color: transparent;
                    border-bottom-color: transparent;
                    bottom: 0;
                    left: calc(50% - 5px);
                    margin-top: 0;
                    margin-bottom: 0;
                }
            }
            &[x-placement^="bottom"] {
                padding-top: 5px;
                .tooltip-arrow {
                    border-width: 0 5px 5px 5px;
                    border-left-color: transparent;
                    border-right-color: transparent;
                    border-top-color: transparent;
                    top: 0;
                    left: calc(50% - 5px);
                    margin-top: 0;
                    margin-bottom: 0;
                }
            }
            .tooltip-arrow {
                position: absolute;
                margin: 5px;
                width: 0;
                height: 0;
                border-style: solid;
                border-color: #333333;
            }
            .tooltip-inner {
                color: #ffffff;
                border-radius: 4px;
                padding: 10px;
                text-align: center;
                background: #333333;
                .btn-wrapper {
                    display: flex;
                }
            }
            .tooltip-btn {
                display: inline-block;
                margin-right: 5px;
                font-size: 12px;
                cursor: pointer;
                &:hover {
                    color: #3c96ff;
                }
                &:last-child {
                    margin-right: 0;
                }
            }
        }
    }
</style>
