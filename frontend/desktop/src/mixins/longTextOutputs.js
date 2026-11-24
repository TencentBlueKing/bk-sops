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
 * 输出参数中的第三方插件长文本（含运行中的流式输出）：排在表格最前，整行用 LongTextViewer 显示
 * 使用方需有 outputsInfo（输出数组）和 nodeDetailConfig
 * 节点结束后，若本页收到过该输出的流式事件（finishedStream），继续显示其中的思考过程，正文用正式输出
 */
import LongTextViewer from '@/components/common/LongTextViewer.vue'
import { URL_REG } from '@/constants/index.js'

// 插件在 Outputs schema 中用 contentMediaType 声明的类型 → 长文本显示格式；未声明时按 markdown
const MEDIA_TYPE_FORMATS = {
    'text/markdown': 'markdown',
    'text/plain': 'text'
}

export default {
    components: {
        LongTextViewer
    },
    props: {
        // 第三方插件输出 key → 声明的 contentMediaType
        outputMediaTypes: {
            type: Object,
            default: () => ({})
        },
        // 运行中第三方插件的流式输出 { key, events, text, status }，null 表示不展示
        streamingOutput: {
            type: Object,
            default: null
        },
        // 节点结束前最近收到的流式事件 { key, events }，null 表示没有
        finishedStream: {
            type: Object,
            default: null
        }
    },
    computed: {
        outputRows () {
            if (!Array.isArray(this.outputsInfo)) return []
            const rows = this.outputsInfo
            if (!this.streamingOutput) return rows
            const { key } = this.streamingOutput
            const streamingRow = { name: key, value: '', ...rows.find(item => item.key === key), key, streaming: true }
            return [streamingRow, ...rows.filter(item => item.key !== key)]
        },
        longTextOutputs () {
            return this.outputRows.filter(item => this.getTextFormat(item))
        },
        // 其余输出按原样显示；Code 模式下 outputsInfo 为字符串，原样返回
        plainOutputs () {
            if (!Array.isArray(this.outputsInfo)) return this.outputsInfo
            return this.outputRows.filter(item => !this.getTextFormat(item))
        },
        // 思考过程 + 正式输出正文；没有思考过程时返回 null，按普通长文本显示
        finishedOutputEvents () {
            if (!this.finishedStream) return null
            const { key, events } = this.finishedStream
            const thinking = events.filter(event => event.type.startsWith('THINKING_'))
            const output = this.outputRows.find(item => item.key === key)
            if (!thinking.length || !output || typeof output.value !== 'string') return null
            if (thinking[thinking.length - 1].type !== 'THINKING_END') thinking.push({ type: 'THINKING_END' })
            return [
                ...thinking,
                { type: 'TEXT_MESSAGE_START', messageId: 'output', role: 'assistant' },
                { type: 'TEXT_MESSAGE_CONTENT', messageId: 'output', delta: output.value },
                { type: 'TEXT_MESSAGE_END', messageId: 'output' }
            ]
        },
        streamingStatusText () {
            return {
                streaming: this.$t('生成中，最终结果以节点完成后的输出为准'),
                done: this.$t('生成完毕，等待节点结束'),
                reconnecting: this.$t('连接中断，正在重连'),
                broken: this.$t('连接中断，节点结束后将显示最终输出')
            }[this.streamingOutput && this.streamingOutput.status] || ''
        }
    },
    methods: {
        // 交给 LongTextViewer 的 AG-UI 事件：流式中用实时事件，结束后用保留的思考过程；返回同一数组，避免重画
        getOutputEvents (output) {
            if (output.streaming) return this.streamingOutput.events
            return this.finishedStream && output.key === this.finishedStream.key ? this.finishedOutputEvents : null
        },
        // 长文本显示格式（markdown | text）：流式行、声明为 markdown 或含换行的字符串；空表示按原单元格显示
        getTextFormat (output) {
            if (this.nodeDetailConfig.component_code !== 'remote_plugin') return ''
            const mediaType = this.outputMediaTypes[output.key]
            const format = MEDIA_TYPE_FORMATS[mediaType] || 'markdown'
            if (output.streaming) return format
            const { value } = output
            if (typeof value !== 'string' || !value || URL_REG.test(value)) return ''
            return value.includes('\n') || mediaType === 'text/markdown' ? format : ''
        }
    }
}
