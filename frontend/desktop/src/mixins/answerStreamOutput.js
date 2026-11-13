/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
/**
 * 第三方插件节点的只读回答流，交给输出参数显示：
 * - 运行中：实时回答放在 streamingOutput（{ key, events, text, status }）
 * - 结束后：正式输出里没有思考过程，用 finishedStream（{ key, events }）显示。来源是本页运行中收到的事件，
 *   没有时（刷新页面、之后再打开）向同一接口请求，插件从会话记录返回本次执行的思考过程
 * 订阅键 = 模式、项目、任务、节点、子流程栈、loop、retry，变化时换连接；组件销毁时断开
 * 使用方需有 executeInfo、nodeDetailConfig、adminView
 */
import { mapState } from 'vuex'
import AnswerStream from '@/utils/answerStream.js'

// 节点执行 → 最近一次收到的 { key, events }；放在组件外，详情面板重建后仍可用，避免重复请求，只保留最近若干个
const finishedStreams = new Map()
const MAX_FINISHED_STREAMS = 20

function rememberStream (identity, value) {
    finishedStreams.delete(identity)
    finishedStreams.set(identity, value)
    if (finishedStreams.size > MAX_FINISHED_STREAMS) finishedStreams.delete(finishedStreams.keys().next().value)
}

export default {
    data () {
        return {
            answerStream: null,
            answerStreamKey: '',
            streamingOutput: null,
            // 收到事件时加一，让 finishedStream 重新读取 finishedStreams
            answerStreamVersion: 0
        }
    },
    computed: {
        ...mapState('project', {
            'answerStreamProjectId': state => state.project_id
        }),
        // 同一次节点执行的标识，与执行状态无关
        answerStreamIdentity () {
            const { loop, retry } = this.executeInfo
            const { component_code, instance_id, node_id, subprocess_stack } = this.nodeDetailConfig
            if (this.adminView || component_code !== 'remote_plugin') return ''
            return JSON.stringify([this.answerStreamProjectId, instance_id, node_id, subprocess_stack, loop, retry])
        },
        answerStreamTarget () {
            const identity = this.answerStreamIdentity
            if (!identity) return ''
            const { state } = this.executeInfo
            if (state === 'RUNNING') return `live:${identity}`
            if (['FINISHED', 'FAILED'].includes(state) && !finishedStreams.has(identity)) return `history:${identity}`
            return ''
        },
        finishedStream () {
            if (this.streamingOutput || this.answerStreamVersion < 0) return null
            return finishedStreams.get(this.answerStreamIdentity) || null
        }
    },
    watch: {
        answerStreamTarget: {
            handler (val) {
                if (val === this.answerStreamKey) return
                this.closeAnswerStream()
                if (val) this.openAnswerStream(val)
            },
            immediate: true
        }
    },
    beforeDestroy () {
        this.closeAnswerStream()
    },
    methods: {
        openAnswerStream (key) {
            const [mode, identity] = [key.slice(0, key.indexOf(':')), key.slice(key.indexOf(':') + 1)]
            const [projectId, instanceId, nodeId, subprocessStack, loop] = JSON.parse(identity)
            this.answerStreamKey = key
            this.answerStream = new AnswerStream({
                projectId,
                instanceId,
                nodeId,
                subprocessStack,
                loop,
                onChange: (state) => {
                    // 实时回答：插件确认支持流式（收到 ready）后才展示；不支持时保持原有展示
                    if (mode === 'live') {
                        this.streamingOutput = ['connecting', 'unsupported'].includes(state.status) ? null : state
                    }
                    if (state.events.length) {
                        rememberStream(identity, { key: state.key, events: state.events })
                        this.answerStreamVersion++
                    }
                }
            })
            this.answerStream.open()
        },
        closeAnswerStream () {
            if (this.answerStream) {
                this.answerStream.close()
                this.answerStream = null
            }
            this.answerStreamKey = ''
            this.streamingOutput = null
        }
    }
}
