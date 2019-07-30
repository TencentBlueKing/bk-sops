/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <tippy
        v-if="show"
        :to="'tip_' + node.id"
        placement="bottom"
        arrow="true"
        theme="dark"
        interactive="true"
        :ref="'tooltip_' + node.id"
        watch-props="true">
        <div v-if="node.type === 'tasknode'" class="tooltip">
            <template v-if="node.componentCode === 'sleep_timer' && node.status === 'RUNNING'">
                <div class="tooltip-btn" @click="onNodeOperationClick('editTime')">{{ i18n.editTime }}</div>
            </template>
            <template v-else>
                <template v-if="node.status !== 'RUNNING'">
                    <div class="tooltip-btn" @click="onNodeExecuteDetail">{{ i18n.detail }}</div>
                    <template v-if="node.status === 'FAILED'">
                        <div class="tooltip-btn" @click="onNodeOperationClick('retry')">{{ i18n.retry }}</div>
                        <div class="tooltip-btn" @click="onNodeOperationClick('skip')">{{ i18n.skip }}</div>
                    </template>
                </template>
                <template v-else>
                    <div class="tooltip-btn" @click="onNodeOperationClick('resume')">{{ i18n.detail }}</div>
                </template>
            </template>
        </div>
        <div v-else-if="node.type === 'subflow'" class="tooltip-btn">{{ i18n.sub }}</div>
    </tippy>
</template>

<script>

    import { mapActions, mapState } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'Tooltips',
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
                i18n: {
                    i18n: window.gettext('加载中'),
                    detail: window.gettext('执行详情'),
                    editTime: window.gettext('修改时间'),
                    retry: window.gettext('重试'),
                    skip: window.gettext('跳过'),
                    skipSuccess: window.gettext('跳过成功'),
                    skipFailed: window.gettext('跳过失败'),
                    sub: window.gettext('查看子流程')
                },
                operating: false,
                show: true
            }
        },
        computed: {
            ...mapState({
                taskId: state => state.taskId
            })
        },
        beforeDestroy () {
            this.onBeforeDestroy()
        },
        methods: {
            ...mapActions('task', [
                'getTask',
                'instanceNodeResume',
                'instanceNodeSkip',
                'getNodeRetryData'
            ]),
            onNodeOperationClick (operation) {
                if (!this.operating) {
                    this.operating = true
                    this[operation]()
                }
            },
            onNodeExecuteDetail () {
                this.show = false
                this.$router.push({ name: 'task_nodes', params: { node: this.node } })
            },
            onBeforeDestroy () {
                this.show = false
                global.$('.tippy-popper').remove()
            },
            async retry () {
                this.show = false
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
                    this.show = false
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
                }
            },
            async resume () {
                try {
                    this.show = false
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
                }
            },
            async editTime () {
                this.show = false
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
    .tippy-popper{
        line-height: 1.2;
    }
    .tooltip {
        display: table;
        .tooltip-btn {
            display: table-cell;
            font-size: 14px;
            vertical-align: middle;
            + .tooltip-btn:before {
                content: "|";
                display: inline-block;
                color: rgba(255, 255, 255, 0.6);
                margin: 0 10px;
            }
        }
    }
</style>
