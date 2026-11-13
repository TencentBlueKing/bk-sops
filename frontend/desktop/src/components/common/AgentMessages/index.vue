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
<template>
    <div>
        <div ref="mount"></div>
    </div>
</template>

<script>
    import installResizeTriggerFix from '@/utils/resizeTriggerFix.js'
    /**
     * 用小鲸的消息组件只读展示 AG-UI 事件（思考过程、正文）
     * events：本轮 AG-UI 事件数组。追加事件时增量渲染；换成新数组（如重新回放）时清空重画；每次渲染完成后触发 update
     * 小鲸组件是 Vue3，按需加载，只在第一次使用时下载
     */
    export default {
        name: 'AgentMessages',
        props: {
            events: {
                type: Array,
                default: () => []
            }
        },
        watch: {
            events: 'sync'
        },
        mounted () {
            // 小鲸组件流式时频繁滚动，容易触发 bk-magic-vue 残留的 scroll 监听报错
            installResizeTriggerFix()
            import(/* webpackChunkName: "agent-messages" */ './mount.js').then(({ default: mountAgentMessages }) => {
                if (this._isDestroyed) return
                this.view = mountAgentMessages(this.$refs.mount)
                this.sync()
            })
        },
        beforeDestroy () {
            if (this.view) {
                this.view.destroy()
                this.view = null
            }
        },
        methods: {
            sync () {
                const { view, events } = this
                if (!view) return
                if (events !== this.renderedEvents || events.length < this.renderedCount) {
                    view.clear()
                    this.renderedEvents = events
                    this.renderedCount = 0
                }
                events.slice(this.renderedCount).forEach(event => view.push(event))
                this.renderedCount = events.length
                view.rendered().then(() => this.$emit('update'))
            }
        }
    }
</script>
