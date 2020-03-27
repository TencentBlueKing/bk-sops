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
                    <p class="text title">{{ commonTitle + i18n.shortcuts }}</p>
                    <span class="close" @click.stop="onCloseHotkeyInfo"><i class="common-icon-dark-circle-close"></i></span>
                    <table>
                        <tbody>
                            <tr>
                                <td>Ctrl + (+):</td>
                                <td>{{ i18n.zoomIn }}</td>
                            </tr>
                            <tr>
                                <td>Ctrl + (-):</td>
                                <td>{{ i18n.zoomOut }}</td>
                            </tr>
                            <tr>
                                <td>Ctrl + 0:</td>
                                <td>{{ i18n.reduction }}</td>
                            </tr>
                            <tr>
                                <td>{{ i18n.scroll }}:</td>
                                <td>{{ i18n.zoom }}</td>
                            </tr>
                            <template v-show="editable">
                                <tr>
                                    <td>{{ commonCtrl }} {{ i18n.click }}:</td>
                                    <td>{{ i18n.multiple }}</td>
                                </tr>
                                <tr>
                                    <td>[{{ i18n.afterSelect }}]{{ i18n.arrowMove }}:</td>
                                    <td>{{ i18n.moveNode }}</td>
                                </tr>
                                <tr>
                                    <td>[{{i18n.afterSelect}}] Delete:</td>
                                    <td>{{ i18n.delNode }}</td>
                                </tr>
                            </template>
                        </tbody>
                    </table>
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
                    reset: gettext('撤销'),
                    restore: gettext('恢复'),
                    shortcuts: gettext('快捷键列表'),
                    zoomIn: gettext('放大'),
                    zoomOut: gettext('缩小'),
                    scroll: gettext('鼠标滚动'),
                    zoom: gettext('缩放'),
                    reduction: gettext('还原'),
                    click: gettext('鼠标左键单击'),
                    multiple: gettext('连续选中（或取消）节点'),
                    selectAll: gettext('选中所有节点'),
                    afterSelect: gettext('选中后'),
                    delNode: gettext('删除节点'),
                    arrowMove: gettext('箭头（上下左右）'),
                    moveNode: gettext('移动流程元素'),
                    cancel: gettext('取消选中')
                },
                isMac,
                commonTitle: isMac ? 'Mac' : 'Windows',
                commonCtrl: isMac ? 'Command' : 'Ctrl',
                hotKeyTriggeringConditions
            }
        },
        mounted () {
            document.body.addEventListener('keydown', this.handlerKeyDown, false)
        },
        beforeDestroy () {
            document.body.removeEventListener('keydown', this.handlerKeyDown, false)
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
        top: 80px;
        padding: 20px;
        width: 340px;
        border-radius: 4px;
        background-color: #fafbfd;
        font-size: 12px;
        line-height: 17px;
        color: #63656e;
        transition: all 0.5s ease;
        box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.15);
        &.min-top {
            left: 40px;
            top: 70px;
        }
        .title {
            margin-bottom: 10px;
        }
        .close {
            display: inline-block;
            position: absolute;
            right: 10px;
            top: 10px;
            width: 16px;
            height: 16px;
            font-size: 16px;
            line-height: 16px;
            text-align: center;
            cursor: pointer;
            .common-icon-dark-circle-close {
                color: #c4c6cc;
            }
        }
        table {
            width: 100%;
        }
    }
}
</style>
