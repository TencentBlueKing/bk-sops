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
    <div class="tag-panel">
        <draggable
            :group="{
                name: 'tag',
                pull: 'clone',
                put: false
            }"
            class="tag-list"
            ref="tagList"
            tag="ul"
            ghost-class="tag-ghost"
            filter=".disabled"
            handle=".drag-entry"
            :sort="false"
            :list="tagMenu"
            :clone="handleTagClone"
            @end="handleDragEnd">
            <template v-for="menuItem in tagMenu">
                <li
                    :class="['menu-item', 'has-sub-menu', { 'disabled': disabled }]"
                    v-if="menuItem.group"
                    :key="menuItem.group"
                    :draggable="false"
                    @mouseenter="handleMenuEnter($event, menuItem)"
                    @mouseleave="handleMenuLeave">
                    <i :class="['menu-icon', 'tag-default-icon', `common-icon-tag-${menuItem.group}`]"></i>
                    <i class="sub-icon common-icon-right-triangle"></i>
                    <div>{{ menuItem.group }}</div>
                </li>
                <li
                    v-else
                    :class="['menu-item', 'drag-entry', { 'disabled': disabled }]"
                    :key="menuItem.tag"
                    :draggable="true">
                    <div class="content">
                        <i :class="['menu-icon', 'tag-default-icon', `common-icon-tag-${menuItem.config.type}`]"></i>
                        <div>{{ menuItem.tag }}</div>
                    </div>
                </li>
            </template>
        </draggable>
        <div
            v-if="isSubMenuShow"
            class="sub-menu"
            ref="subMenu"
            :style="subMenuStyle"
            @mouseenter="isSubMenuShow = true"
            @mouseleave="isSubMenuShow = false">
            <draggable
                :group="{
                    name: 'tag',
                    pull: 'clone',
                    put: false
                }"
                ghost-class="tag-ghost"
                filter=".disabled"
                handle=".drag-entry"
                :list="subMenu"
                :sort="false"
                :clone="handleTagClone"
                @end="handleDragEnd">
                <div
                    v-for="item in subMenu"
                    :key="item.tag"
                    class="drag-entry">
                    <div class="content">{{ item.tag }}</div>
                </div>
            </draggable>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import draggable from 'vuedraggable'
    import tools from '@/utils/tools.js'

    const ORDER_GROUP_MAP = [
        {
            group: 'input',
            items: ['TagInput', 'TagMemberSelector', 'TagPassword', 'TagInt', 'TagTextarea']
        },
        {
            group: 'select',
            items: ['TagSelect', 'TagCascader', 'TagDatetime']
        },
        'TagRadio',
        'TagCheckbox',
        'TagButton',
        'TagUpload',
        'TagTree',
        'TagText',
        'TagIpSelector',
        'TagDatatable'
    ]

    export default {
        name: 'TagPanel',
        components: {
            draggable
        },
        props: {
            tags: {
                type: Object,
                default () {
                    return {}
                }
            },
            disabled: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                draggedCount: 1,
                isSubMenuShow: false,
                subMenu: [],
                subMenuStyle: {}
            }
        },
        computed: {
            tagMenu () {
                const menu = []
                ORDER_GROUP_MAP.forEach(tag => {
                    if (tag.items) {
                        const data = {
                            group: tag.group,
                            items: []
                        }
                        tag.items.forEach(item => {
                            if (this.tags[item]) {
                                data.items.push(this.tags[item])
                            }
                        })
                        menu.push(data)
                    } else {
                        if (this.tags[tag]) {
                            menu.push(this.tags[tag])
                        }
                    }
                })
                Object.keys(this.tags).forEach(tag => {
                    const item = this.tags[tag]
                    const existTag = menu.find(menuItem => {
                        return menuItem.items ? menuItem.items.find(subItem => subItem.tag === item.tag) : menuItem.tag === item.tag
                    })
                    if (!existTag) {
                        menu.push(item)
                    }
                })

                return menu
            }
        },
        methods: {
            handleTagClone (origin) {
                const tag = tools.deepClone(origin)
                tag.config.attrs.name.value = i18n.t('表单项') + this.draggedCount
                tag.config.tag_code = `form_${this.draggedCount}`

                return tag
            },
            handleDragEnd (event) {
                if (event.pullMode === 'clone') {
                    this.draggedCount += 1
                }
            },
            handleMenuEnter (event, group) {
                this.subMenu = group.items
                this.isSubMenuShow = true
                this.$nextTick(() => {
                    let verticalPos
                    const memuEl = event.target
                    const topGap = memuEl.offsetTop - this.$refs.tagList.$el.scrollTop
                    const tagListRect = this.$refs.tagList.$el.getBoundingClientRect()
                    const subMenuRect = this.$refs.subMenu.getBoundingClientRect()
                    if (topGap < 0) {
                        verticalPos = { top: '10px' }
                    } else if (subMenuRect.height + topGap > tagListRect.height) {
                        verticalPos = { bottom: '10px' }
                    } else {
                        verticalPos = { top: `${topGap + 10}px` }
                    }
                    this.subMenuStyle = verticalPos
                })
            },
            handleMenuLeave (event) {
                this.isSubMenuShow = false
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';

    .tag-panel {
        position: relative;
        height: 100%;
        background: #ffffff;
        text-align: center;
        & > header {
            margin: 0 10px;
            height: 60px;
            line-height: 60px;
            font-size: 18px;
            text-align: center;
            border-bottom: 1px solid rgb(238, 238, 238);
        }
    }
    .tag-list {
        height: 100%;
        overflow-x: hidden;
        overflow-y: auto;
        @include scrollbar;
        .menu-item {
            position: relative;
            padding: 10px 0;
            height: 68px;
            color: #62667d;
            font-size: 12px;
            user-select: none;
            &:not(.disabled):hover {
                color: #3a84ff;;
                cursor: move;
                &.has-sub-menu {
                    background: #ecedf3;
                    color: #62667d;
                    cursor: pointer;
                }
            }
            &.disabled {
                cursor: not-allowed;
            }
            .menu-icon {
                display: inline-block;
                font-size: 32px;
            }
            .sub-icon {
                position: absolute;
                right: 4px;
                top: 30px;
                font-size: 12px;
                transform: scale(0.6);
            }
        }
    }
    .sub-menu {
        position: absolute;
        right: -148px;
        padding: 6px 0;
        width: 152px;
        font-size: 12px;
        text-align: left;
        background: #ffffff;
        border-radius: 2px;
        box-shadow: 0 2px 6px 0 rgba(0, 0, 0, 0.3);
        z-index: 2;
        .drag-entry {
            padding: 0 12px;
            height: 28px;
            line-height: 28px;
            color: #62667d;
            &:hover {
                background: #ecedf3;
                color: #3a84ff;
                cursor: move;
            }
        }
    }
</style>
