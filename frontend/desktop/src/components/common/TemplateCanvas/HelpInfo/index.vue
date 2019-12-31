/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="help-info-wrap">
        <div
            v-if="isShowHotKey"
            :class="['hot-key-container', { 'min-top': editable }]">
            <transition name="wrapperLeft">
                <div :class="['hot-key-panel', { 'min-top': !editable }]">
                    <template>
                        <p class="text title">{{ commonTitle }}</p>
                        <p class="text">Ctrl + (+) {{i18n.zoomIn}}</p>
                        <p class="text">Ctrl + (-) {{i18n.zoomOut}}</p>
                        <p class="text">Ctrl + 0 {{i18n.reduction}}</p>
                        <p class="text">Ctrl + {{i18n.zoom}}</p>
                        <p class="text" v-show="editable">{{commonCtrl}} + {{i18n.multiple}}</p>
                        <p class="text" v-show="editable">[{{i18n.afterSelect}}] {{ i18n.moveNode }}</p>
                        <span class="close" @click.stop="onCloseHotkeyInfo"><i class="common-icon-dark-circle-close"></i></span>
                    </template>
                </div>
            </transition>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    const isMac = /macintosh|mac os x/i.test(navigator.userAgent.toLowerCase())
    const hotKeyTriggeringConditions = [
        { emit: 'onZoomIn', keyCodes: [107, 187], ctrl: true },
        { emit: 'onZoomOut', keyCodes: [109, 189], ctrl: true },
        { emit: 'onResetPosition', keyCodes: [96, 48], ctrl: true }
    ]
    export default {
        name: 'HelpInfo',
        props: {
            isShowHotKey: {
                type: Boolean,
                default: false
            },
            editable: {
                type: Boolean,
                default: true
            }
        },
        data () {
            return {
                i18n: {
                    reset: gettext('：撤销'),
                    restore: gettext('：恢复'),
                    zoomIn: gettext('：放大'),
                    zoomOut: gettext('：缩小'),
                    zoom: gettext(' 鼠标滚动：缩放'),
                    reduction: gettext('：还原'),
                    multiple: gettext('鼠标左键单击 ：连续选中（或取消）节点'),
                    selectAll: gettext('选中所有节点'),
                    afterSelect: gettext('选中后'),
                    delNode: gettext('：删除节点'),
                    moveNode: gettext('箭头（上下左右）：移动流程元素'),
                    cancel: gettext('：取消选中')
                },
                isMac,
                commonTitle: isMac ? 'Mac' : 'Windows',
                commonCtrl: isMac ? 'Command' : 'Ctrl',
                hotKeyTriggeringConditions,
                zoomOriginPosition: {
                    x: 0,
                    y: 0
                }
            }
        },
        mounted () {
            document.body.addEventListener('keydown', this.handlerKeyDown, false)
            document.body.addEventListener('keyup', this.handlerKeyUp, false)
            document.querySelector('.canvas-flow-wrap').addEventListener('mousewheel', this.onMouseWheel, false)
            document.querySelector('.canvas-flow-wrap').addEventListener('DOMMouseScroll', this.onMouseWheel, false)
            document.querySelector('.canvas-flow-wrap').addEventListener('mousemove', this.onCanvasMouseMove, false)
        },
        beforeDestroy () {
            document.body.removeEventListener('keydown', this.handlerKeyDown, false)
            document.body.addEventListener('keyup', this.handlerKeyUp, false)
        },
        methods: {
            onCloseHotkeyInfo () {
                this.$emit('onCloseHotkeyInfo')
            },
            handlerKeyDown (e) {
                const ctrl = window.event.ctrlKey
                const action = this.hotKeyTriggeringConditions.find(m => m.keyCodes.indexOf(e.keyCode) > -1 && !!ctrl === m.ctrl)
                if (action && this.isUsable(action.emit)) {
                    e.preventDefault()
                    this.$emit(action.emit, action.params)
                }
            },
            isUsable (emitName) {
                // 只读模式可用快捷键列表
                const readOnlyModeCanUse = ['onZoomIn', 'onZoomOut', 'onResetPosition']
                if (!this.editable && readOnlyModeCanUse.indexOf(emitName) < -1) {
                    return false
                }
                return true
            },
            // 滚轮缩放
            onMouseWheel (e) {
                if (!e.ctrlKey) {
                    return false
                }
                e.preventDefault()
                const ev = e || window.event
                let down = true
                down = ev.wheelDelta ? ev.wheelDelta < 0 : ev.detail > 0
                if (down) {
                    this.$emit('onZoomOut', this.zoomOriginPosition)
                } else {
                    this.$emit('onZoomIn', this.zoomOriginPosition)
                }
                return false
            },
            onCanvasMouseMove (e) {
                const { x: offsetX, y: offsetY } = document.querySelector('.canvas-flow-wrap').getBoundingClientRect()
                this.zoomOriginPosition.x = e.pageX - offsetX
                this.zoomOriginPosition.y = e.pageY - offsetY
            }
        }
    }
</script>
<style lang="scss" scoped>
.help-info-wrap {
    position: absolute;
    left: 0;
    top: 0;
    z-index: 5;
}
.hot-key-container {
    .hot-key-panel {
        position: absolute;
        left: 80px;
        top: 124px;
        padding: 20px;
        width: 304px;
        border-radius: 10px;
        background-color: #777A85;
        transition: all 0.5s ease;
        &.min-top {
            left: 40px;
            top: 70px;
        }
        .title {
            margin-bottom: 20px;
        }
        .text {
            font-size: 12px;
            line-height: 17px;
            color: #FFFFFF;
        }
        .close {
            display: inline-block;
            position: absolute;
            right: 10px;
            top: 10px;
            width: 16px;
            height: 16px;
            line-height: 16px;
            text-align: center;
            cursor: pointer;
            .common-icon-dark-circle-close {
                color: #ffffff;
            }
        }
    }
}
</style>
