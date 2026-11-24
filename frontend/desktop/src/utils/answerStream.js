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
 * 第三方插件节点运行中的只读回答流（taskflow/api/nodes/answer_stream）
 *
 * 服务端每次连接都从本次执行开头回放，重连后回放出内容时清空重画，因此不会产生缺口；
 * 若重连时执行已结束、队列已清理（没有可回放内容），保留断线前已收到的内容。
 * state.events：本轮 AG-UI 事件（思考过程、正文），交给小鲸消息组件渲染；state.text：正文原文
 * status: connecting | streaming | done | reconnecting | broken | unsupported
 */
const RETRY_DELAYS = [1000, 2000, 4000]

export default class AnswerStream {
    constructor ({ projectId, instanceId, nodeId, subprocessStack, loop, onChange }) {
        const params = new URLSearchParams({ instance_id: instanceId, node_id: nodeId })
        if (subprocessStack) params.append('subprocess_stack', subprocessStack)
        if (loop) params.append('loop', loop)
        this.url = `${window.SITE_URL}taskflow/api/nodes/answer_stream/${projectId}/?${params.toString()}`
        this.onChange = onChange
        this.source = null
        this.retryTimer = null
        this.retries = 0
        this.closed = false
        // 新连接或新一轮回放出第一段内容前，不清空已显示的文本
        this.pendingClear = false
        this.state = { key: '', events: [], text: '', status: 'connecting' }
    }

    open () {
        if (this.closed) return
        const source = new EventSource(this.url)
        this.source = source
        const on = (name, handler) => {
            source.addEventListener(name, (event) => {
                // 旧连接的迟到事件直接丢弃
                if (this.source !== source) return
                handler(event.data ? JSON.parse(event.data) : {})
            })
        }
        on('ready', ({ output_key: key }) => {
            this.retries = 0
            this.pendingClear = true
            this.update({ key: key || 'output', status: 'streaming' })
        })
        // 新一轮开始（RUN_STARTED）：同样等第一段内容到达再清空，避免画面闪空
        on('reset', () => {
            this.pendingClear = true
        })
        on('agui', event => this.append(event))
        on('end', () => {
            // 回放没有新内容时保留已收到的内容；结束正在生成的消息（如思考中、正文中断开）
            this.pendingClear = false
            if (this.state.events.length) this.append({ type: 'RUN_FINISHED' })
            this.finish('done')
        })
        on('unsupported', () => this.finish('unsupported'))
        source.onerror = () => {
            if (this.source !== source) return
            this.closeSource()
            if (this.retries >= RETRY_DELAYS.length) {
                this.update({ status: 'broken' })
                return
            }
            this.update({ status: 'reconnecting' })
            this.retryTimer = setTimeout(() => this.open(), RETRY_DELAYS[this.retries++])
        }
    }

    append (event) {
        let { events, text } = this.state
        if (this.pendingClear) {
            this.pendingClear = false
            events = []
            text = ''
        }
        // 冻结后 Vue 不再深度监听每个事件
        events.push(Object.freeze(event))
        if (['TEXT_MESSAGE_CONTENT', 'TEXT_MESSAGE_CHUNK'].includes(event.type)) text += event.delta || ''
        this.update({ events, text })
    }

    update (patch) {
        this.state = { ...this.state, ...patch }
        if (!this.closed) this.onChange(this.state)
    }

    finish (status) {
        this.closeSource()
        this.update({ status })
    }

    closeSource () {
        if (this.source) {
            this.source.close()
            this.source = null
        }
    }

    close () {
        this.closed = true
        clearTimeout(this.retryTimer)
        this.closeSource()
    }
}
