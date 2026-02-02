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
    <div class="full-code-editor" :class="{ 'full-status': isFullScreen }">
        <div class="tool-area">
            <ScriptCodeDrownList
                ref="ScriptCodeDrownList"
                :read-only="options.readOnly"
                :input-data="inputData" />
            <i
                class="bk-icon icon-copy mr20"
                v-bk-tooltips="{
                    boundary: 'window',
                    content: $t('复制')
                }"
                @click="onCopyClick(value)">
            </i>
            <i
                class="bk-icon zoom-icon"
                :class="isFullScreen ? 'icon-un-full-screen' : 'icon-full-screen'"
                v-bk-tooltips="{
                    boundary: 'window',
                    content: isFullScreen ? $t('退出') : $t('全屏')
                }"
                @click="onToggleFullScreen">
            </i>
        </div>
        <code-editor
            ref="codeEditor"
            :key="isFullScreen"
            :value="value"
            :options="options"
            @input="onDataChange">
        </code-editor>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import CodeEditor from './CodeEditor.vue'
    import ScriptCodeDrownList from '@/components/common/aiBluekingComp/ScriptCodeDrownList.vue'

    export default {
        name: 'FullCodeEditor',
        components: {
            CodeEditor,
            ScriptCodeDrownList
        },
        props: {
            value: String,
            options: {
                type: Object,
                default: () => ({
                    readOnly: true,
                    language: 'json'
                })
            }
        },
        data () {
            return {
                copyText: '',
                isFullScreen: false,
                inputData: this.value || ''
            }
        },
        watch: {
            isFullScreen () {
                this.$emit('toggleFullScreen')
            }
        },
        beforeDestroy () {
            document.body.removeEventListener('keyup', this.handleQuick, false)
        },
        methods: {
            /**
             * 变量 key 复制
             */
            onCopyClick (key) {
                this.copyText = key
                document.addEventListener('copy', this.copyHandler)
                document.execCommand('copy')
                document.removeEventListener('copy', this.copyHandler)
                this.copyText = ''
            },
            /**
             * 复制操作回调函数
             */
            copyHandler (e) {
                e.preventDefault()
                e.clipboardData.setData('text/html', this.copyText)
                e.clipboardData.setData('text/plain', this.copyText)
                this.$bkMessage({
                    message: i18n.t('已复制'),
                    theme: 'success'
                })
            },
            onToggleFullScreen () {
                this.isFullScreen = !this.isFullScreen
                if (this.isFullScreen) {
                    document.body.addEventListener('keyup', this.handleQuick, false)
                    this.$bkMessage({
                        message: '按 Esc 即可退出全屏模式',
                        limit: 1,
                        delay: 3000
                    })
                } else {
                    document.body.removeEventListener('keyup', this.handleQuick, false)
                }
            },
            handleQuick (e) {
                if (e.keyCode === 27) {
                    this.isFullScreen = false
                }
            },
            onDataChange (val) {
                this.inputData = val
                this.$emit('input', val)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .full-code-editor {
        height: 100%;
        background: #ffffff;
        &.full-status {
            position: fixed;
            top: 0;
            right: 0;
            bottom: 0;
            left: 0;
            height: 100vh !important;
            z-index: 3000;
            margin: 0 !important;
        }
        .tool-area {
            padding: 0 20px;
            height: 38px;
            line-height: 38px;
            text-align: right;
            background: #202024;
            display: flex;
            align-items: center;
            justify-content: flex-end;

            .assistant-icon {
                width: 18px;
                height: 18px;
            }
            .zoom-icon {
                font-size: 14px;
                color: #ffffff;
                cursor: pointer;
            }
            .icon-copy {
                font-size: 18px;
                color: #ffffff;
                cursor: pointer;
            }
        }
        .code-editor {
            height: calc(100% - 38px);
        }
    }
</style>
