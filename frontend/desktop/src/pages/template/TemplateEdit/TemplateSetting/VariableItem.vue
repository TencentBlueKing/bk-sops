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
    <li
        :class="[
            'clearfix',
            'variable-item',
            { 'variable-editing': isVariableEditing && theKeyOfEditing === constant.key }
        ]">
        <div class="variable-content" @click="onEditVariable(constant.key)">
            <i v-if="!isSystemVar" class="col-item-drag bk-icon icon-sort"></i>
            <i v-else class="common-icon-lock-disable"></i>
            <span class="col-item col-name">
                <p
                    class="col-constant-name"
                    :title="constant.name">
                    {{constant.name}}
                </p>
            </span>
            <span class="col-item col-key">
                <p class="col-constant-key">{{constant.key}}</p>
                <a
                    class="col-key-copy"
                    href="javascript:void(0)"
                    v-bk-tooltips.click="{
                        content: i18n.copied,
                        placements: ['bottom']
                    }"
                    @click.stop="onCopyKey(constant.key)">
                    {{ i18n.copy }}
                </a>
            </span>
            <span class="col-item col-attributes">
                <span class="icon-wrap">
                    <i
                        v-if="constant.source_type !== 'component_outputs'"
                        class="common-icon-show-left"
                        v-bk-tooltips="{
                            content: i18n.inputs,
                            placements: ['bottom']
                        }">
                    </i>
                    <i
                        v-else
                        class="common-icon-hide-right color-org"
                        v-bk-tooltips="{
                            content: i18n.outputs,
                            placements: ['bottom']
                        }">
                    </i>
                    <i
                        v-if="constant.show_type === 'show'"
                        class="common-icon-eye-show"
                        v-bk-tooltips="{
                            content: i18n.show,
                            placements: ['bottom']
                        }">
                    </i>
                    <i
                        v-else
                        class="common-icon-eye-hide color-org"
                        v-bk-tooltips="{
                            content: i18n.hide,
                            placements: ['bottom']
                        }">
                    </i>
                </span>
            </span>
            <span class="col-item col-output">
                <div @click.stop>
                    <bk-switcher
                        size="small"
                        :selected="outputs.indexOf(constant.key) > -1"
                        @change="onChangeVariableOutput(constant.key, $event)">
                    </bk-switcher>
                </div>
            </span>
            <i
                v-if="!isSystemVar"
                class="col-item-delete common-icon-dark-circle-close"
                @click.stop="onDeleteVariable(constant.key, index)">
            </i>
        </div>
        <div
            v-if="isShowVariableEdit"
            :key="`${constant.key}-edit`">
            <VariableEdit
                ref="editVariablePanel"
                :variable-data="variableData"
                :variable-type-list="variableTypeList"
                :is-new-variable="false"
                @scrollPanelToView="scrollPanelToView"
                @onChangeEdit="onChangeEdit">
            </VariableEdit>
        </div>
    </li>
</template>
<script>
    import '@/utils/i18n.js'
    import VariableEdit from './VariableEdit.vue'
    export default {
        name: 'VariableItem',
        components: {
            VariableEdit
        },
        props: ['constant', 'isSystemVar', 'isVariableEditing', 'outputs', 'theKeyOfEditing', 'variableData', 'variableTypeList'],
        data () {
            return {
                i18n: {
                    copied: gettext('已复制'),
                    inputs: gettext('输入'),
                    outputs: gettext('输出'),
                    show: gettext('显示'),
                    hide: gettext('隐藏'),
                    copy: gettext('复制')
                },
                copyText: ''
            }
        },
        computed: {
            isShowVariableEdit () {
                return this.isVariableEditing && this.theKeyOfEditing === this.constant.key && !this.isSystemVar
            }
        },
        methods: {
            /**
             * 变量 key 复制
             */
            onCopyKey (key) {
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
                e.clipboardData.setData('text/html', this.copyText)
                e.clipboardData.setData('text/plain', this.copyText)
                e.preventDefault()
            },
            onChangeVariableOutput (key, checked) {
                this.$emit('onChangeVariableOutput', { key, checked })
            },
            onDeleteVariable (key, index) {
                this.$emit('onDeleteVariable', { key, index })
            },
            onEditVariable (key) {
                if (this.isSystemVar) return
                this.$emit('onEditVariable', key)
            },
            scrollPanelToView (index) {
                this.$emit('scrollPanelToView', index)
            },
            onChangeEdit (val) {
                this.$emit('onChangeEdit', val)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
$localBorderColor: #d8e2e7;
.variable-header, .variable-list {
    position: relative;
    font-size: 12px;
    .col-name {
        width: 100px;
    }
    .col-key {
        width: 128px;
    }
    .col-attributes {
        padding-left: 4px;
        width: 70px;
        .icon-wrap {
            vertical-align: middle;
            line-height: 1;
            display: inline-block;
            .common-icon-show-left {
                color: #219f42;
                font-size: 14px;
            }
            .common-icon-hide-right {
                font-size: 14px;
            }
            .common-icon-eye-show {
                margin-left: 8px;
                color: #219f42;
                font-size: 15px;
            }
            .common-icon-eye-hide {
                margin-left: 8px;
                font-size: 15px;
            }
            .color-org{
                color: #de9524;
            }
        }
    }
    .col-output {
        width: 50px;
    }
}
.variable-header {
    padding: 0 20px 0 45px;
    background: #ecf0f4;
    border-bottom: 1px solid $localBorderColor;
    .t-head {
        float: left;
        height: 40px;
        line-height: 40px;
        font-size: 14px;
    }
}

.variable-item {
    position: relative;
    cursor: pointer;
    &:hover {
        background: $blueStatus;
    }
    &.variable-editing {
        background: $blueStatus;
    }
    .variable-content {
        display: table;
        padding: 0 20px 0 45px;
        height: 40px;
        line-height: 40px;
        &:hover {
            .col-item-drag {
                display: inline-block;
            }
            .col-item-delete {
                display: inline-block;
            }
        }
        .col-item-delete {
            color: #c4c6cc;
            &:hover {
                color: #979ba5;
            }
        }
    }
}
.col-item {
    display: table-cell;
    font-size: 12px;
    vertical-align: middle;
    word-break: break-all;
    text-align: left;
    border-bottom: 1px solid #ebebeb;
}
.col-item-drag {
    display: none;
    position: absolute;
    top: 15px;
    left: 20px;
    color: #979ba5;
    cursor: move;
    &:hover {
        color: #348aff;
    }
}
.col-item-delete {
    display: none;
    position: absolute;
    top: 15px;
    right: 20px;
    font-size: 14px;
    color: #979ba5;
}
.col-name {
    .col-constant-name {
        width: 90px;
        overflow: hidden;
        text-overflow:ellipsis;
        white-space: nowrap;
    }
}
.col-key {
    position: relative;
    .col-constant-key {
        display: inline-block;
        width: 90px;
        vertical-align: middle;
        line-height: 2;
    }
    .col-key-copy {
        margin-left: 2px;
        color: #52699d;
        text-decoration: underline;
    }
}
.col-output {
    .bk-switcher .bk-switcher-small {
        margin-left: 32px;
    }
    .bk-switcher.bk-switcher-small {
        width: 28px;
        height: 16px;
        line-height: 10px;
    }
    .bk-switcher.bk-switcher-small:after {
        top: 1px;
        width: 14px;
        height: 14px;
    }
    .bk-switcher.bk-switcher-small.is-checked:after {
        margin-left: -15px;
    }
}
.variable-edit-td {
    padding: 0;
    width: 412px;
}
.empty-variable-tip {
    margin-top: 120px;
}
.tooltip-content {
    margin-bottom: 20px;
    &:last-child {
        margin-bottom: 0;
    }
    h4 {
        margin-top: 0;
        margin-bottom: 10px;
    }
}
.common-icon-lock-disable {
    position: absolute;
    top: 18px;
    left: 20px;
    color: #979ba5;
}
.system-constants-item {
    cursor: default;
}
</style>
