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
        <div v-if="isShowHotKey" class="hot-key-container">
            <transition name="wrapperLeft">
                <div v-if="isMac" class="hot-key-panel">
                    <p class="text title">Mac</p>
                    <p class="text">Ctrl + (+) {{i18n.zoomIn}}</p>
                    <p class="text">Ctrl + (-) {{i18n.zoomOut}}</p>
                    <p class="text">Ctrl + o {{i18n.reduction}}</p>
                    <span class="close" @click.stop="onCloseHotkeyInfo"><i class="common-icon-dark-circle-close"></i></span>
                </div>
                <div v-else class="hot-key-panel">
                    <p class="text title">Windows</p>
                    <p class="text">Ctrl + (+) {{i18n.zoomIn}}</p>
                    <p class="text">Ctrl + (-) {{i18n.zoomOut}}</p>
                    <p class="text">Ctrl + o {{i18n.reduction}}</p>
                    <span class="close" @click.stop="onCloseHotkeyInfo"><i class="common-icon-dark-circle-close"></i></span>
                </div>
            </transition>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    const isMac = /macintosh|mac os x/i.test(navigator.userAgent.toLowerCase())
    export default {
        name: 'HelpInfo',
        props: {
            isShowHotKey: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                i18n: {
                    reset: gettext('：撤销'),
                    restore: gettext('：恢复'),
                    zoomIn: gettext('：放大'),
                    zoomOut: gettext('：缩小'),
                    reduction: gettext('：还原'),
                    multiple: gettext('鼠标左键单击 ：连续选中节点'),
                    selectAll: gettext('选中所有节点'),
                    afterSelect: gettext('选中后'),
                    delNode: gettext('：删除节点'),
                    moveNode: gettext('箭头（上下左右）：移动流程元素'),
                    cancel: gettext('：取消选中')
                },
                isMac
            }
        },
        mounted () {
            document.body.addEventListener('keydown', this.handerKeyDown, false)
        },
        beforeDestroy () {
            document.body.removeEventListener('keydown', this.handerKeyDown, false)
        },
        methods: {
            onCloseHotkeyInfo () {
                this.$emit('onCloseHotkeyInfo')
            },
            handerKeyDown (e) {
                const ctrl = window.event.ctrlKey
                if ((e.keyCode === 107 || e.keyCode === 187) && ctrl) {
                    e.preventDefault()
                    this.$emit('onZoomIn')
                }
                if ((e.keyCode === 109 || e.keyCode === 189) && ctrl) {
                    e.preventDefault()
                    this.$emit('onZoomOut')
                }
                if (e.keyCode === 79 && ctrl) {
                    e.preventDefault()
                    this.$emit('onResetPosition')
                }
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
