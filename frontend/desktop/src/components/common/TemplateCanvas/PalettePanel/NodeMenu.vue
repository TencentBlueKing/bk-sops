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
    <transition name="slideLeft">
        <div class="node-menu" v-if="showNodeMenu" v-bk-clickoutside="handleClickOutSide">
            <i
                :class="[
                    'common-icon-left-pin',
                    'node-list-pin',
                    { 'actived': isFixedNodeMenu }
                ]"
                @click.stop="onClickPin"></i>
            <div class="search-wrap">
                <bk-input
                    class="search-input"
                    v-model="searchStr"
                    right-icon="bk-icon icon-search"
                    :placeholder="i18n.placeholder"
                    @input="onSearchInput" />
            </div>
            <div class="node-list-wrap">
                <template v-if="listInPanel.length > 0">
                    <template v-if="searchStr === ''">
                        <bk-collapse v-for="group in listInPanel" :key="group.type">
                            <bk-collapse-item :name="group.group_name">
                                <div class="group-header">
                                    <img class="header-icon" :src="group.group_icon || defaultTypeIcon" />
                                    <span class="header-title">{{group.group_name}}
                                        <span class="header-atom">
                                            {{group.list.length}}{{i18n.num}}
                                        </span>
                                    </span>
                                </div>
                                <div slot="content" class="node-item-wrap">
                                    <node-item
                                        v-for="(node, index) in group.list"
                                        :key="index"
                                        :type="activeNodeListType"
                                        :node="node">
                                    </node-item>
                                </div>
                            </bk-collapse-item>
                        </bk-collapse>
                    </template>
                </template>
                <no-data v-else></no-data>
            </div>
        </div>
    </transition>
</template>
<script>
    import NoData from '@/components/common/base/NoData.vue'
    import NodeItem from './NodeItem.vue'

    export default {
        name: 'NodeMenu',
        components: {
            NoData,
            NodeItem
        },
        props: {
            showNodeMenu: {
                type: Boolean,
                default: false
            },
            activeNodeListType: {
                type: String,
                default: ''
            },
            isFixedNodeMenu: {
                type: Boolean,
                default: false
            },
            nodes: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                loading: false,
                isPinActived: false,
                searchStr: '',
                isNoSearchResult: false,
                isNoData: false,
                taskNodeList: [],
                subflowList: [],
                searchResult: [],
                isShowGroup: true,
                pending: {
                    tasknode: false,
                    subflow: false
                },
                defaultTypeIcon: require('@/assets/images/atom-type-default.svg'),
                i18n: {
                    placeholder: gettext('请输入名称'),
                    num: gettext('个')
                }
            }
        },
        computed: {
            listInPanel () {
                return this.searchStr === '' ? this.nodes : this.searchResult
            }
        },
        methods: {
            onClickPin () {
                this.$emit('onToggleNodeMenuFixed', !this.isFixedNodeMenu)
            },
            onSearchInput () {},
            handleClickOutSide () {
                debugger
                this.$emit('onHideNodeMenu')
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    @import '@/scss/mixins/multiLineEllipsis.scss';
    .node-menu {
        position: absolute;
        top: 0;
        margin-left: 60px;
        width: 300px;
        height: 100%;
        background: #fefcfc;
        border-right: 1px solid #dddddd;
        z-index: 2;
    }
    .node-list-pin {
        position: absolute;
        top: 4px;
        right: 10px;
        font-size: 24px;
        color: #999999;
        cursor: pointer;
        z-index: 1;
        &:hover {
            color: #727272;
        }
        &.actived {
            color: #30d878;
        }
    }
    .search-wrap {
        position: relative;
        padding-top: 30px;
        padding-bottom: 10px;
        text-align: center;
    }
    .node-list-wrap {
        height: calc(100% - 71px);
        overflow-y: auto;
        @include scrollbar;
    }
    .group-header {
        .header-icon {
            float: left;
            margin-top: 17px;
            width: 16px;
            height: 16px;
        }
        .header-title {
            display: inline-block;
            margin-left: 10px;
            width: 210px;
            font-size: 14px;
            overflow: hidden;
            .header-atom {
                float: right;
                color: #a9b2bd;
                font-size: 12px;
            }
        }
    }
    .node-item-wrap {
        overflow: hidden;
    }
</style>
