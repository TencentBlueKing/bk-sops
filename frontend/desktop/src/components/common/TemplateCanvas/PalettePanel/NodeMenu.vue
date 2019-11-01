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
            <div :class="['panel-fixed-pin', { 'actived': isFixedNodeMenu }]" @click.stop="onClickPin">
                <i class="common-icon-pin"></i>
            </div>
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
                                    <img v-if="group.group_icon" class="group-icon-img" :src="group.group_icon" />
                                    <i v-else :class="['group-icon-font', getIconCls(group.type)]"></i>
                                    <span class="header-title">{{group.group_name}}
                                        <span class="header-atom">
                                            ({{group.list.length}})
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
                                    <div class="node-empty" v-if="group.list.length === 0">
                                        <no-data></no-data>
                                    </div>
                                </div>
                            </bk-collapse-item>
                        </bk-collapse>
                    </template>
                    <template v-else>
                        <div class="search-result">
                            <node-item
                                v-for="(node, index) in searchResult"
                                :key="index"
                                :type="activeNodeListType"
                                :node="node">
                            </node-item>
                        </div>
                    </template>
                </template>
                <no-data v-else></no-data>
            </div>
        </div>
    </transition>
</template>
<script>
    import '@/utils/i18n.js'
    import NoData from '@/components/common/base/NoData.vue'
    import NodeItem from './NodeItem.vue'
    import dom from '@/utils/dom.js'
    import toolsUtils from '@/utils/tools.js'
    import { SYSTEM_GROUP_ICON } from '@/constants/index.js'

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
                    placeholder: gettext('请输入名称')
                }
            }
        },
        computed: {
            listInPanel () {
                return this.searchStr === '' ? this.nodes : this.searchResult
            }
        },
        watch: {
            activeNodeListType () {
                this.searchStr = ''
            }
        },
        created () {
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            getIconCls (type) {
                const systemType = SYSTEM_GROUP_ICON.find(item => new RegExp(item).test(type))
                if (systemType) {
                    return `common-icon-sys-${systemType.toLowerCase()}`
                }
                return 'common-icon-sys-default'
            },
            onClickPin () {
                this.$emit('onToggleNodeMenuFixed', !this.isFixedNodeMenu)
            },
            searchInputhandler () {
                if (this.searchStr !== '') {
                    const reg = new RegExp(this.searchStr)
                    const result = []
                    this.nodes.forEach(group => {
                        if (group.list.length > 0) {
                            group.list.forEach(node => {
                                if (reg.test(node.name)) {
                                    result.push(node)
                                }
                            })
                        }
                    })
                    this.searchResult = result
                }
            },
            handleClickOutSide (e) {
                if (!this.isFixedNodeMenu) {
                    if (dom.parentClsContains('palette-item', e.target)) {
                        return
                    }
                    this.$emit('onCloseNodeMenu')
                }
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
        width: 293px;
        height: 100%;
        background: #fefcfc;
        border-right: 1px solid #dddddd;
        z-index: 2;
    }
    .panel-fixed-pin {
        position: absolute;
        top: 16px;
        right: 14px;
        width: 32px;
        height: 32px;
        line-height: 32px;
        border: 1px solid #c4c6cc;
        border-radius: 2px;
        font-size: 14px;
        text-align: center;
        color: #999999;
        cursor: pointer;
        z-index: 1;
        &:hover {
            color: #727272;
        }
        &.actived {
            color: #52699d;
        }
    }
    .search-wrap {
        padding: 16px 56px 16px 14px;
        border-bottom: 1px solid #ccd0dd;
    }
    .node-list-wrap {
        height: calc(100% - 71px);
        overflow-y: auto;
        @include scrollbar;
    }
    .bk-collapse-item {
        border-bottom: 1px solid #e2e4ed;
        /deep/ .bk-collapse-item-header {
            background: #ffffff;
        }
        /deep/ .bk-collapse-item-content {
            padding: 0;
            border-top: 1px solid #e2e4ed;
        }
    }
    .group-header {
        height: 42px;
        overflow: hidden;
        .group-icon-font {
            float: left;
            margin-top: 13px;
            font-size: 16px;
            color: #52699d;
        }
        .group-icon-img {
            float: left;
            margin-top: 13px;
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
                color: #a9b2bd;
                font-size: 12px;
            }
        }
    }
    .node-item-wrap {
        overflow: hidden;
    }
    .node-empty {
        padding: 16px 0;
    }
    .search-result {
        padding: 20px 10px;
    }
</style>
