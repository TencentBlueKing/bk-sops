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
    <div :class="['long-text-viewer', { 'full-status': isFullScreen }]">
        <div class="text-toolbar">
            <!-- 与 SOPS 其他切换一致：bk-button-group + is-selected；图标操作与 FullCodeEditor 一致：bk-icon + tooltip -->
            <div v-if="isMarkdown" class="bk-button-group">
                <bk-button size="small" :class="{ 'is-selected': !showRaw }" @click="showRaw = false">{{ $t('预览') }}</bk-button>
                <bk-button size="small" :class="{ 'is-selected': showRaw }" @click="showRaw = true">{{ $t('原文') }}</bk-button>
            </div>
            <i
                class="bk-icon icon-copy tool-icon"
                v-bk-tooltips="{ boundary: 'window', content: $t('复制原文') }"
                @click="onCopy">
            </i>
            <i
                :class="['bk-icon', 'tool-icon', isFullScreen ? 'icon-un-full-screen' : 'icon-full-screen']"
                v-bk-tooltips="{ boundary: 'window', content: isFullScreen ? $t('退出') : $t('全屏') }"
                @click="toggleFullScreen">
            </i>
        </div>
        <div v-if="isMarkdown && !showRaw" ref="box" class="text-box agent-text" @scroll="onScroll">
            <AgentMessages :events="previewEvents" @update="scrollToEnd"></AgentMessages>
        </div>
        <pre v-else ref="box" class="text-box" @scroll="onScroll">{{ text }}</pre>
        <slot></slot>
    </div>
</template>

<script>
    import AgentMessages from '@/components/common/AgentMessages/index.vue'
    /**
     * 多行长文本展示：保留换行、限高滚动，可复制原文、全屏查看（Esc 退出）
     * format 为 markdown 时默认用小鲸的消息组件渲染（代码块高亮等与小鲸一致），可切换原文；
     * 传入 events（AG-UI 事件）时渲染其中的思考过程和正文，text 为正文原文
     * follow 为 true 时（如流式输出）内容增长自动滚到底部，用户向上滚动后暂停跟随
     */
    export default {
        name: 'LongTextViewer',
        components: {
            AgentMessages
        },
        props: {
            text: {
                type: String,
                default: ''
            },
            format: {
                type: String,
                default: 'text' // text | markdown
            },
            follow: {
                type: Boolean,
                default: false
            },
            events: {
                type: Array,
                default: null
            }
        },
        data () {
            return {
                showRaw: false,
                followBottom: true,
                isFullScreen: false
            }
        },
        computed: {
            isMarkdown () {
                return this.format === 'markdown'
            },
            previewEvents () {
                if (this.events) return this.events
                return [
                    { type: 'TEXT_MESSAGE_START', messageId: 'text', role: 'assistant' },
                    { type: 'TEXT_MESSAGE_CONTENT', messageId: 'text', delta: this.text },
                    { type: 'TEXT_MESSAGE_END', messageId: 'text' }
                ]
            }
        },
        watch: {
            text: 'scrollToEnd',
            showRaw: 'scrollToEnd',
            isFullScreen: 'scrollToEnd'
        },
        beforeDestroy () {
            document.removeEventListener('keydown', this.onKeydown)
        },
        methods: {
            // 与 FullCodeEditor 一致：铺满窗口查看，Esc 或再次点击图标退出
            toggleFullScreen () {
                this.isFullScreen = !this.isFullScreen
                document[this.isFullScreen ? 'addEventListener' : 'removeEventListener']('keydown', this.onKeydown)
            },
            onKeydown (e) {
                if (e.key === 'Escape') this.toggleFullScreen()
            },
            onCopy () {
                document.addEventListener('copy', this.copyHandler)
                document.execCommand('copy')
                document.removeEventListener('copy', this.copyHandler)
            },
            copyHandler (e) {
                e.preventDefault()
                e.clipboardData.setData('text/plain', this.text)
                this.$bkMessage({
                    message: this.$t('已复制'),
                    theme: 'success'
                })
            },
            scrollToEnd () {
                if (!this.follow || !this.followBottom) return
                this.$nextTick(() => {
                    const el = this.$refs.box
                    if (el) el.scrollTop = el.scrollHeight
                })
            },
            onScroll () {
                const el = this.$refs.box
                if (this.follow && el) this.followBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 20
            }
        }
    }
</script>

<style lang="scss" scoped>
    .long-text-viewer {
        .text-toolbar {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            margin-bottom: 8px;
            .bk-button-group .bk-button {
                height: 24px;
                line-height: 22px;
                min-width: auto;
            }
            .tool-icon {
                margin-left: 16px;
                font-size: 16px;
                color: #979ba5;
                cursor: pointer;
                &:hover {
                    color: #3a84ff;
                }
            }
        }
        .text-box {
            max-height: 320px;
            margin: 0;
            padding: 8px 12px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-break: normal;
            overflow-wrap: anywhere;
            font-family: inherit;
            background: #f5f7fa;
            border-radius: 2px;
        }
        &.full-status {
            position: fixed;
            top: 0;
            right: 0;
            bottom: 0;
            left: 0;
            z-index: 3000;
            display: flex;
            flex-direction: column;
            padding: 16px 24px;
            background: #fff;
            .text-box {
                flex: 1;
                max-height: none;
                padding: 16px 24px;
                font-size: 14px;
            }
        }
        .agent-text {
            white-space: normal;
            background: #fff;
            border: 1px solid #dcdee5;
        }
    }
</style>
