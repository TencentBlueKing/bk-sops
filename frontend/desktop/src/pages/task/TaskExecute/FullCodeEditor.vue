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
            :value="value"
            :options="{ readOnly: true, language: 'json' }">
        </code-editor>
    </div>
</template>
<script>
    import CodeEditor from '@/components/common/CodeEditor.vue'

    export default {
        name: 'FullCodeEditor',
        components: {
            CodeEditor
        },
        props: {
            value: String
        },
        data () {
            return {
                isFullScreen: false
            }
        },
        beforeDestroy () {
            document.body.removeEventListener('keyup', this.handleQuick, false)
        },
        methods: {
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
            }
        }
    }
</script>
<style lang="scss" scoped>
    .full-code-editor {
        background: #ffffff;
        &.full-status {
            position: fixed;
            top: 0;
            right: 0;
            bottom: 0;
            left: 0;
            height: 100vh;
            z-index: 3000;
            .code-editor {
                height: calc(100% - 38px);
            }
        }
        .tool-area {
            padding: 0 20px;
            height: 38px;
            line-height: 38px;
            text-align: right;
            background: #202024;
            .zoom-icon {
                font-size: 14px;
                color: #ffffff;
                cursor: pointer;
            }
        }
        .code-editor {
            height: 300px;
        }
    }
</style>
