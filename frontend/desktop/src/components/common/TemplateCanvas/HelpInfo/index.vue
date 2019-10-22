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
                <div class="hot-key-panel">
                    <p class="text title">Mac</p>
                    <p
                        v-for="(text, index) in hotKeys"
                        :key="index"
                        class="text">
                        {{ text }}
                    </p>
                    <span class="close" @click.stop="onCloseHotkeyInfo"><i class="common-icon-dark-circle-close"></i></span>
                </div>
            </transition>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
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
                hotKeys: [
                    gettext('Command + z ：撤销/Undo'),
                    gettext('Command + Shift + z ：恢复/Redo'),
                    gettext('Ctrl + (+) ：放大'),
                    gettext('Ctrl + (-) ：缩小'),
                    gettext('Command + 鼠标左键单击 ：连续选中节点'),
                    gettext('Command + A ：选中所有节点'),
                    gettext('[选中后] Command + Del ：删除节点'),
                    gettext('[选中后] 箭头（上下左右）：移动流程元素'),
                    gettext('[选中后] Esc：取消选中')
                ]
            }
        },
        methods: {
            onCloseHotkeyInfo () {
                this.$emit('onCloseHotkeyInfo')
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
