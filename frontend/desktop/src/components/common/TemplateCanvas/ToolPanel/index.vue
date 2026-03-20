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
    <transition name="wrapperLeft">
        <div class="tool-position">
            <div
                :class="['tool-icon', {
                    'actived': showSmallMap
                }]"
                v-bk-tooltips="{
                    content: $t('缩略视图'),
                    delay: 300,
                    placements: ['bottom']
                }"
                @click="onShowMap">
                <i class="common-icon-thumbnail-view"></i>
            </div>
            <div class="zoom-wrapper">
                <i
                    class="common-icon-zoom-add"
                    :class="{ 'disabled': zoomRatio === 150 }"
                    v-bk-tooltips="{
                        content: $t('放大'),
                        delay: 300,
                        placements: ['bottom']
                    }"
                    @click="onZoomIn">
                </i>
                <p class="zoom-ratio">{{ zoomRatio + '%' }}</p>
                <i
                    class="common-icon-zoom-minus"
                    :class="{ 'disabled': zoomRatio === 25 }"
                    v-bk-tooltips="{
                        content: $t('缩小'),
                        delay: 300,
                        placements: ['bottom']
                    }"
                    @click="onZoomOut">
                </i>
            </div>
            <div class="square-wrapper">
                <div
                    class="tool-icon"
                    v-bk-tooltips="{
                        content: $t('复位'),
                        delay: 300,
                        placements: ['bottom']
                    }"
                    @click="onResetPosition">
                    <i class="common-icon-reset"></i>
                </div>
                <div
                    :class="['tool-icon', {
                        'actived': isSelectionOpen
                    }]"
                    v-if="editable"
                    v-bk-tooltips="{
                        content: $t('节点框选'),
                        delay: 300,
                        placements: ['bottom']
                    }"
                    @click="onOpenFrameSelect">
                    <i class="common-icon-node-selection"></i>
                </div>
                <div
                    class="tool-icon"
                    v-if="editable"
                    v-bk-tooltips="{
                        content: $t('排版'),
                        delay: 300,
                        placements: ['bottom']
                    }"
                    @click="onFormatPosition">
                    <i class="common-icon-typesetting"></i>
                </div>
                <div
                    class="ai-format-wrap"
                    v-if="editable">
                    <div
                        :class="['tool-icon', 'ai-format-icon', { 'disabled': aiFormatLoading, 'actived': isShowAiProgress }]"
                        v-bk-tooltips="{
                            content: $t('AI排版'),
                            delay: 300,
                            placements: ['bottom']
                        }"
                        @click="onAIFormatPosition">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1102.769 1024" version="1.1" class="ai-icon-svg">
                            <rect x="551.4" y="78.8" width="551.3" height="78.8" rx="39.4" class="ai-icon-line" />
                            <rect x="551.4" y="315.1" width="551.3" height="78.8" rx="39.4" class="ai-icon-line" />
                            <rect x="551.4" y="630.2" width="551.3" height="78.8" rx="39.4" class="ai-icon-line" />
                            <rect x="551.4" y="866.5" width="551.3" height="78.8" rx="39.4" class="ai-icon-line" />
                            <rect x="0" y="0" width="472.6" height="472.6" rx="78.8" class="ai-icon-box" />
                            <path d="M236 106 L271 201 L366 236 L271 271 L236 366 L201 271 L106 236 L201 201 Z" class="ai-icon-star" />
                            <rect x="0" y="551.4" width="472.6" height="472.6" rx="78.8" class="ai-icon-box" />
                            <path d="M236 690 L256 758 L324 787.7 L256 817 L236 885 L216 817 L148 787.7 L216 758 Z" class="ai-icon-star" />
                        </svg>
                    </div>
                    <div class="ai-progress-popover" v-if="isShowAiProgress">
                        <bk-progress
                            :percent="aiProgress / 100"
                            :stroke-width="8"
                            :show-text="true"
                            ext-cls="ai-generate-progress"
                            color="#3a84ff">
                        </bk-progress>
                    </div>
                </div>
            </div>
            <div
                :class="['tool-icon', {
                    'actived': isAllSelected
                }]"
                v-if="isShowSelectAllTool"
                v-bk-tooltips="{
                    content: selectNodeName,
                    delay: 300,
                    placements: ['bottom']
                }"
                @click="onToggleAllNode">
                <i :class="['common-icon-checked-all', { 'tool-disable': isSelectAllToolDisabled }]">
                </i>
            </div>
            <div
                :class="['tool-icon', {
                    'actived': isShowHotKey
                }]"
                v-bk-tooltips="{
                    content: $t('快捷键'),
                    delay: 300,
                    placements: ['bottom']
                }"
                @click="onToggleHotKeyInfo">
                <i class="common-icon-hot-key"></i>
            </div>
            <div
                :class="['tool-icon', {
                    'actived': isPerspective
                }]"
                v-bk-tooltips="{
                    content: $t('变量引用预览'),
                    delay: 300,
                    placements: ['bottom']
                }"
                @click="onTogglePerspective">
                <i class="common-icon-perspective"></i>
            </div>
            <div
                class="tool-icon"
                v-if="isShowSelectAllTool"
                v-bk-tooltips="{
                    content: $t('导出'),
                    delay: 300,
                    placements: ['bottom']
                }"
                @click="onExportScheme">
                <i class="common-icon-export-scheme"></i>
            </div>
        </div>
    </transition>
</template>
<script>
    import i18n from '@/config/i18n/index.js'

    export default {
        name: 'ToolPanel',
        props: {
            editable: {
                type: Boolean,
                default: true
            },
            isShowSelectAllTool: {
                type: Boolean,
                default: false
            },
            isSelectAllToolDisabled: {
                type: Boolean,
                default: false
            },
            isAllSelected: {
                type: Boolean,
                default: false
            },
            isSelectionOpen: {
                type: Boolean,
                default: false
            },
            showSmallMap: {
                type: Boolean,
                default: false
            },
            zoomRatio: {
                type: Number,
                default: 100
            },
            isShowHotKey: {
                type: Boolean,
                default: false
            },
            isPerspective: {
                type: Boolean,
                default: false
            },
            aiFormatLoading: {
                type: Boolean,
                default: false
            },
            aiFormatResult: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                aiProgress: 0,
                isShowAiProgress: false,
                progressTimer: null
            }
        },
        computed: {
            selectNodeName () {
                return this.isAllSelected ? i18n.t('全选') : i18n.t('反选')
            }
        },
        watch: {
            aiFormatLoading (val) {
                if (val) {
                    this.startFakeProgress()
                } else {
                    if (this.aiFormatResult === 'fail') {
                        this.cancelFakeProgress()
                    } else {
                        this.stopFakeProgress()
                    }
                }
            }
        },
        beforeDestroy () {
            this.clearProgressTimer()
        },
        methods: {
            clearProgressTimer () {
                if (this.progressTimer) {
                    clearInterval(this.progressTimer)
                    this.progressTimer = null
                }
            },
            startFakeProgress () {
                this.aiProgress = 0
                this.isShowAiProgress = true
                this.clearProgressTimer()
                // 分层次增长：快速→中速→慢速→极慢
                const phases = [
                    { target: 30, duration: 5000, interval: 200 }, // 0-30%：5秒内快速增长
                    { target: 60, duration: 15000, interval: 500 }, // 30-60%：15秒内中速增长
                    { target: 85, duration: 30000, interval: 1000 }, // 60-85%：30秒内慢速增长
                    { target: 99, duration: 40000, interval: 2000 } // 85-99%：40秒内极慢增长
                ]
                let phaseIndex = 0
                const runPhase = () => {
                    if (phaseIndex >= phases.length) return
                    const phase = phases[phaseIndex]
                    // 记录当前阶段的起始进度，用于计算增量
                    const startProgress = this.aiProgress
                    // 计算当前阶段的总步数和每步增量
                    const steps = phase.duration / phase.interval
                    const progressPerStep = (phase.target - startProgress) / steps
                    let currentStep = 0
                    // 按阶段配置的间隔定时递增进度
                    this.progressTimer = setInterval(() => {
                        currentStep++
                        const newProgress = Math.min(
                            Math.floor(startProgress + currentStep * progressPerStep),
                            phase.target
                        )
                        this.aiProgress = newProgress
                        // 当前阶段完成后，清除定时器并进入下一阶段
                        if (newProgress >= phase.target) {
                            this.clearProgressTimer()
                            phaseIndex++
                            runPhase()
                        }
                    }, phase.interval)
                }
                runPhase()
            },
            stopFakeProgress () {
                // 请求成功：跳到100%，短暂停留后隐藏
                this.clearProgressTimer()
                this.aiProgress = 100
                setTimeout(() => {
                    this.isShowAiProgress = false
                    this.aiProgress = 0
                }, 500)
            },
            cancelFakeProgress () {
                // 请求失败：停留在当前进度，短暂停留后隐藏
                this.clearProgressTimer()
                setTimeout(() => {
                    this.isShowAiProgress = false
                    this.aiProgress = 0
                }, 1000)
            },
            onAIFormatPosition () {
                if (this.aiFormatLoading) return
                this.$emit('onAIFormatPosition')
            },
            onShowMap () {
                this.$emit('onShowMap')
            },
            onZoomIn () {
                this.$emit('onZoomIn')
            },
            onZoomOut () {
                this.$emit('onZoomOut')
            },
            onResetPosition () {
                this.$emit('onResetPosition')
            },
            onFormatPosition () {
                this.$emit('onFormatPosition')
            },
            onToggleAllNode () {
                this.$emit('onToggleAllNode', !this.isAllSelected)
            },
            onOpenFrameSelect () {
                this.$emit('onOpenFrameSelect')
            },
            onToggleHotKeyInfo () {
                this.$emit('onToggleHotKeyInfo')
            },
            onTogglePerspective () {
                this.$emit('onTogglePerspective')
            },
            onExportScheme () {
                this.$emit('onExportScheme')
            }
        }
    }
</script>
<style lang="scss" scoped>
    .tool-position {
        height: 36px;
        display: flex;
        align-items: center;
        padding: 0 12px;
        & > *:not(:last-child) {
            position: relative;
            &::after {
                content: '';
                height: 15px;
                width: 1px;
                position: absolute;
                right: -12px;
                top: 5px;
                background: #dcdee5;
            }
        }
    }
    .tool-icon {
        height: 24px;
        width: 24px;
        padding: 0 4px;
        margin-right: 20px;
        color: #919eb5;
        cursor: pointer;
        &:last-child {
            margin-right: 0;
        }
        &:hover {
            color: #699df4;
            background: #f4f7ff;
            border-radius: 1px;
        }
        &.actived {
            color: #3a84ff;
            background: #f4f7ff;
            border-radius: 1px;
        }
        .tool-disable {
            cursor: not-allowed;
            opacity: 0.3;
        }
    }
    .ai-format-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 !important;
        .ai-icon-svg {
            width: 17px !important;
            height: 17px !important;
            display: block;
            flex-shrink: 0;
            .ai-icon-line {
                fill: currentColor;
                opacity: 0.5;
            }
            .ai-icon-box {
                fill: currentColor;
            }
            .ai-icon-star {
                fill: #fff;
            }
        }
    }
    .zoom-wrapper, .square-wrapper {
        height: 24px;
        display: flex;
        align-items: center;
        margin-right: 20px;
        .common-icon-zoom-add, .common-icon-zoom-minus {
            font-size: 18px;
            color: #919eb5;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
            &.disabled {
                color: #ccc;
                cursor: not-allowed;
            }
        }
        .zoom-ratio {
            width: 32px;
            text-align: center;
            font-size: 12px;
            transform: scale(.8);
            color: #c4c6cc;
        }
        .tool-icon {
            margin-right: 16px;
            &:last-child {
                margin-right: 0;
            }
        }
        .ai-format-wrap {
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            .tool-icon {
                margin-right: 0;
                &.disabled {
                    color: #3a84ff;
                    cursor: not-allowed;
                    &:hover {
                        color: #c4c6cc;
                        background: none;
                    }
                }

            }
            .ai-progress-popover {
                position: absolute;
                top: 40px;
                left: 50%;
                transform: translateX(-50%);
                width: 300px;
                padding: 3px 10px;
                background: #fff;
                border-radius: 2px;
                box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.15);
                z-index: 10;
                box-sizing: border-box;
                &::before {
                    content: '';
                    position: absolute;
                    top: -4px;
                    left: 50%;
                    transform: translateX(-50%) rotate(45deg);
                    width: 8px;
                    height: 8px;
                    background: #fff;
                    box-shadow: -1px -1px 2px 0 rgba(0, 0, 0, 0.1);
                }
                ::v-deep .ai-generate-progress{
                    .progress-text{
                        font-size: 14px !important;
                        white-space: nowrap;
                        color: #63656e;
                        margin: 0 10px;
                    }
                }
            }
        }
    }
</style>
