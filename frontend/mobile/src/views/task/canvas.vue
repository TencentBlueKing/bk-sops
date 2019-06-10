/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="page-view">
        <div :class="[taskStateClass, taskStateColor]">{{ taskStateName }}</div>
        <MobileCanvas v-if="!loading" :canvas-data="canvasData" ref="canvas"></MobileCanvas>
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
                    v-else-if="taskState === 'PAUSE' && !operating"
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

    const TASK_STATE = {
        'CREATED': [window.gettext('未执行'), 'info'],
        'RUNNING': [window.gettext('执行中'), 'info'],
        'SUSPENDED': [window.gettext('暂停'), 'warning'],
        'NODE_SUSPENDED': [window.gettext('节点暂停'), 'warning'],
        'FAILED': [window.gettext('失败'), 'danger'],
        'FINISHED': [window.gettext('完成'), 'success'],
        'REVOKED': [window.gettext('撤销'), 'danger']
    }

    export default {
        name: '',
        components: {
            MobileCanvas
        },
        provide () {
            return {
                refreshTaskStatus: this.setTaskStatusTimer
            }
        },
        data () {
            return {
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
                    tip: window.gettext('提示'),
                    executeStart: window.gettext('开始执行任务'),
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
        methods: {
            ...mapActions('task', [
                'getTask',
                'getTaskStatus',
                'instanceStart',
                'instancePause',
                'instanceRevoke'
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
                            if (data.state === 'RUNNING' || data.state === 'FAILED') {
                                if (this.$refs.canvas) {
                                    this.$refs.canvas.setCanvasPosition(node)
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
                        if (this.taskState === 'RUNNING') {
                            this.setTaskStatusTimer()
                        }
                        this.updateTaskNodes(taskState.data);
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
                        global.bus.$emit('notify', { message: this.i18n.executeStart })
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
            async taskResume () {
                try {
                    const response = await this.instanceResume(this.instance_id)
                    if (response.result) {
                        this.setTaskStatusTimer()
                        global.bus.$emit('notify', { message: window.gettext('任务继续成功') })
                    } else {
                        errorHandler(response, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.pending.task = false
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
