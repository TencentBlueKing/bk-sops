/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
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
            }
        },
        computed: {
            selectNodeName () {
                return this.isAllSelected ? i18n.t('全选') : i18n.t('反选')
            }
        },
        methods: {
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
        &.actived, &:hover {
            color: #3a84ff;
            background: #f4f7ff;
            border-radius: 1px;
        }
        .tool-disable {
            cursor: not-allowed;
            opacity: 0.3;
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
    }
</style>
