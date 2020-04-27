/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
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
                class="tool-icon"
                v-bk-tooltips="{
                    content: i18n.zoomIn,
                    delay: 1000,
                    placements: ['bottom']
                }"
                @click="onZoomIn">
                <i class="common-icon-zoom-in"></i>
            </div>
            <div
                class="tool-icon"
                v-bk-tooltips="{
                    content: i18n.zoomOut,
                    delay: 1000,
                    placements: ['bottom']
                }"
                @click="onZoomOut">
                <i class="common-icon-zoom-out"></i>
            </div>
            <div
                class="tool-icon"
                v-bk-tooltips="{
                    content: i18n.resetZoom,
                    delay: 1000,
                    placements: ['bottom']
                }"
                @click="onResetPosition">
                <i class="common-icon-reduction"></i>
            </div>
            <div
                :class="['tool-icon', {
                    'actived': isSelectionOpen
                }]"
                v-if="editable"
                v-bk-tooltips="{
                    content: i18n.nodeSelection,
                    delay: 1000,
                    placements: ['bottom']
                }"
                @click="onOpenFrameSelect">
                <i class="common-icon-marquee"></i>
            </div>
            <div
                class="tool-icon"
                v-if="editable"
                v-bk-tooltips="{
                    content: i18n.formatPosition,
                    delay: 1000,
                    placements: ['bottom']
                }"
                @click="onFormatPosition">
                <i class="common-icon-four-square"></i>
            </div>
            <div
                class="tool-icon"
                v-if="isShowSelectAllTool"
                v-bk-tooltips="{
                    content: selectNodeName,
                    delay: 1000,
                    placements: ['bottom']
                }"
                @click="onToggleAllNode">
                <i :class="[
                    isAllSelected ? 'common-icon-black-hook' : 'common-icon-black-box',
                    { 'tool-disable': isSelectAllToolDisabled }]">
                </i>
            </div>
            <div
                class="tool-icon"
                v-bk-tooltips="{
                    content: i18n.hotKey,
                    delay: 1000,
                    placements: ['bottom']
                }"
                @click="onToggleHotKeyInfo">
                <i class="common-icon-flash"></i>
            </div>
        </div>
    </transition>
</template>
<script>
    import '@/utils/i18n.js'

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
            }
        },
        data () {
            return {
                i18n: {
                    resetZoom: gettext('复位'),
                    zoomIn: gettext('放大'),
                    zoomOut: gettext('缩小'),
                    nodeSelection: gettext('节点框选'),
                    formatPosition: gettext('排版'),
                    choiceAll: gettext('全选'),
                    cancelChoiceAll: gettext('反选'),
                    hotKey: gettext('快捷键')
                },
                isShowHotKey: false
            }
        },
        computed: {
            selectNodeName () {
                return this.isAllSelected ? this.i18n.choiceAll : this.i18n.cancelChoiceAll
            }
        },
        methods: {
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
            }
        }
    }
</script>
<style lang="scss" scoped>
    .tool-icon {
        display: inline-block;
        margin: 0 15px;
        color: #ffffff;
        cursor: pointer;
        &:first-child {
            margin-left: 20px;
        }
        &:last-child {
            margin-right: 15px;
        }
        &.actived {
            color: #3480ff;
        }
        .tool-disable {
            cursor: not-allowed;
            opacity: 0.3;
        }
    }
</style>
