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
 * 小鲸消息渲染（Vue3）：AG-UI 事件经 chat-helper 的 AGUIProtocol 转成消息，用 chat-x 的 MessageRender 逐条渲染，
 * 与小鲸对话中的思考过程、正文（Markdown、代码块高亮等）显示一致。只读：不连接 Agent，不发送、不停止。
 */
import { createApp, h, nextTick } from '@blueking/bkui-library'
import { AGUIProtocol, useMessage } from '@blueking/chat-helper'
import { MessageRender } from '@blueking/chat-x'
import '@blueking/chat-x/dist/index.css'

export default function mountAgentMessages (el) {
    const messageModule = useMessage({})
    const protocol = new AGUIProtocol()
    protocol.injectMessageModule(messageModule)

    // 沿用小鲸消息列表的类名（ai-message-container > message-group-messages），代码块、消息间距等样式都限定在它下面
    const app = createApp({
        render: () => h('div', { class: 'ai-message-container' }, [
            h('div', { class: 'message-group-messages' }, messageModule.list.value.map((message, index) => {
                return h(MessageRender, { key: message.messageId || index, message })
            }))
        ])
    })
    app.mount(el)

    return {
        push (event) {
            protocol.onMessage(event)
        },
        clear () {
            messageModule.list.value = []
        },
        // 等小鲸组件完成本次渲染
        rendered () {
            return nextTick()
        },
        destroy () {
            // 组件销毁时外层 DOM 可能还在做关闭动画：先固定高度，避免内容清空后高度变化触发外层的 scroll 事件
            el.style.height = `${el.offsetHeight}px`
            app.unmount()
        }
    }
}
