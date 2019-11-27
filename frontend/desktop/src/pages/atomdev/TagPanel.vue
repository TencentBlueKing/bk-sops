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
    <div class="tag-panel">
        <ul class="tag-list">
            <draggable
                :group="{
                    name: 'tag',
                    pull: 'clone',
                    put: false
                }"
                ghost-class="tag-ghost"
                filter=".disabled"
                :sort="false"
                :list="list"
                :clone="handleTagClone"
                @end="handleDragEnd">
                <li
                    :class="['tag-item', { 'disabled': disabled }]"
                    v-for="(item, name) in tags"
                    v-bk-tooltips="{
                        content: item.tag,
                        placement: 'right',
                        boundary: 'window',
                        delay: 500
                    }"
                    :key="name"
                    :draggable="true">
                    <i :class="getIconCls(item)"></i>
                </li>
            </draggable>
        </ul>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import draggable from 'vuedraggable'
    import tools from '@/utils/tools.js'

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
                draggedCount: 1
            }
        },
        computed: {
            list () {
                const list = []
                Object.keys(this.tags).forEach(tag => {
                    list.push(this.tags[tag])
                })
                return list
            }
        },
        methods: {
            getIconCls (tag) {
                const type = tag.config.type
                return ['tag-icon', `common-icon-tag-${type}`]
            },
            handleTagClone (origin) {
                const tag = tools.deepClone(origin)
                tag.config.attrs.name.value = gettext('表单项') + this.draggedCount
                tag.config.tag_code = `form_${this.draggedCount}`

                return tag
            },
            handleDragEnd (event) {
                if (event.pullMode === 'clone') {
                    this.draggedCount += 1
                }
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
        overflow-y: auto;
        @include scrollbar;
        .tag-item {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 48px;
            color: #62667d;
            font-size: 32px;
            user-select: none;
            overflow: hidden;
            &:not(.disabled):hover {
                color: #3a84ff;;
                cursor: move;
            }
            &.disabled {
                cursor: not-allowed;
            }
            .tag-icon {
                display: inline-block;
            }
        }
    }
</style>
