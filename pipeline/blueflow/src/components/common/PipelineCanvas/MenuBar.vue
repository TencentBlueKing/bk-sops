/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="menu-wrapper">
        <div class="menu-bar">
            <div class="menu-title">
                <h3>{{ i18n.tools }}</h3>
            </div>
            <ul>
                <li v-for="item in nodeDict"
                    :key="item.type"
                    :class="[
                        'node-type-item',
                        `common-icon-node-${item.type}`,
                        {'node-type-has-sub': isNodeTypeHasSub(item.type)},
                        {'node-source': !isNodeTypeHasSub(item.type)},
                        {'active-node-type' : activeNodeType === item.type && showNodeList}
                    ]"
                    :data-type="item.type"
                    v-bktooltips.right="item.name"
                    @click.stop="onSelectNode(item.type)"
                />
            </ul>
        </div>
        <transition name="slideLeft">
            <div class="node-list" v-if="showNodeList">
                <div class="list-container" v-bkloading="{isLoading: loading, opacity: 1}">
                    <i :class="['common-icon-pin', 'node-list-pin', {actived: isPinActived}]" @click.stop="onClickPin"></i>
                    <div class="search-node-wraper">
                        <input class="search-input" :placeholder="i18n.placeholder" v-model="searchStr" @input="onSearchInput"/>
                        <i class="common-icon-search"></i>
                    </div>
                    <div v-if="!showNoDataPanel" class="atom-list-wrapper">
                        <template v-if="isGrouped">
                            <div
                                v-for="item in listInPanel"
                                :key="item.type"
                                v-if="item.list && item.list.length"
                                class="collapse-panel">
                                <BaseCollapse>
                                    <template slot="header" class="panel-header">
                                        <img class="header-icon" :src="item.group_icon||defaultTypeIcon"/>
                                        <span class="header-title">{{item.group_name}}</span>
                                    </template>
                                    <template slot="content">
                                        <div
                                            v-for="atom in item.list"
                                            class="atom-item node-source"
                                            :key="activeNodeType === 'tasknode' ? atom.tag_code : atom.id"
                                            :data-atomid="activeNodeType === 'tasknode' ? atom.code : atom.template_id"
                                            :data-version="activeNodeType === 'tasknode' ? '' : atom.version"
                                            :data-atomname="atom.name.replace(/\s/g, '')"
                                            :data-type="activeNodeType">
                                            <p>{{atom.name}}</p>
                                        </div>
                                    </template>
                                </BaseCollapse>
                            </div>
                        </template>
                        <div v-else class="list-content clearfix">
                            <div
                                v-for="atom in listInPanel"
                                class="atom-item node-source"
                                :key="activeNodeType === 'tasknode' ? atom.tag_code : atom.id"
                                :data-atomid="activeNodeType === 'tasknode' ? atom.code : atom.template_id"
                                :data-version="activeNodeType === 'tasknode' ? '' : atom.version"
                                :data-atomname="atom.name.replace(/\s/g, '')"
                                :data-type="activeNodeType">
                                <p>{{atom.name}}</p>
                            </div>
                        </div>
                    </div>
                    <NoData v-else></NoData>
                </div>
            </div>
        </transition>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapGetters, mapActions, mapMutations } from 'vuex'
import domUtils  from '@/utils/dom.js'
import toolsUtils  from '@/utils/tools.js'
import BaseCollapse from '../base/BaseCollapse.vue'
import NoData from '../base/NoData.vue'
import { NODE_DICT } from '@/constants/index.js'
const nodeTypeList = ['startpoint', 'endpoint', 'parallelgateway', 'convergegateway', 'branchgateway', 'tasknode', 'subflow']
const nodeTypeSubList = ['tasknode', 'subflow']
const node_list = Object.keys(NODE_DICT).map(key => {
    return {
        type: key,
        name: NODE_DICT[key]
    }
})

export default {
    name: 'MenuBar',
    props: {
        singleAtomListLoading: {
            type: Boolean
        },
        subAtomListLoading: {
            type: Boolean
        },
        atomTypeList: {
            type: Object,
            required: true
        },
        searchAtomResult: {
            type: Array
        }
    },
    components: {
        BaseCollapse,
        NoData
    },
    data () {
        return {
            i18n: {
                tools: gettext("工具"),
                placeholder: gettext("请输入名称")
            },
            nodeDict: node_list,
            nodeTypeList,
            activeNodeType: null,
            searchStr: '',
            showNodeList: false,
            isCollapseAll: false,
            isPinActived: false,
            searchMode: false,
            defaultTypeIcon: require('@/assets/images/atom-type-default.svg')
        }
    },
    computed: {
        loading () {
            if (this.activeNodeType === 'tasknode') {
                return this.singleAtomListLoading
            } else if (this.activeNodeType === 'subflow') {
                return this.subAtomListLoading
            }
        },
        listInPanel () {
            if (this.searchMode) {
                return this.searchAtomResult
            } else {
                return this.activeNodeType ? this.atomTypeList[this.activeNodeType] : []
            }
        },
        isGrouped () {
            return !this.searchMode
        },
        showNoDataPanel () {
            return this.activeNodeType && !this.listInPanel.length
        }
    },
    created () {
        this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
    },
    mounted () {
        window.addEventListener('click', this.handleOutOfMenuBarClick, false)
    },
    beforeDestroy () {
        window.removeEventListener('click', this.handleOutOfMenuBarClick, false)
    },
    methods: {
        onSelectNode (node) {
            if (this.isNodeTypeHasSub(node)) {
                this.activeNodeType = node
                this.showNodeList = true
            } else {
                if (this.isPinActived) return
                this.activeNodeType = null
                this.showNodeList = false
            }
            this.isCollapseAll = true
            this.searchMode = false
            this.searchStr = ''
        },
        onClickPin () {
            this.isPinActived = !this.isPinActived
        },
        onResetPosition () {
            this.$emit('onResetPosition')
        },
        handleOutOfMenuBarClick (event) {
            const that = this
            const nodeListDOM = document.querySelector(".node-list")
            if (this.showNodeList && !this.isPinActived && !domUtils.nodeContains(nodeListDOM, event.target)) {
                that.showNodeList = false
            }
        },
        searchInputhandler () {
            if (this.searchStr.length){
                this.searchMode = true
                this.$emit('onSearchAtom', {
                    type: this.activeNodeType,
                    text: this.searchStr
                })
            } else {
                this.searchMode = false
            }
        },
        isNodeTypeHasSub (node){
            return nodeTypeSubList.indexOf(node) > -1
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.menu-wrapper {
    position: relative;
    float: left;
    width: 60px;
    height: 100%;
    z-index: 4;
}
.menu-title {
    padding: 0 14px;
    text-align: center;
    h3 {
        margin: 0;
        padding: 16px 0;
        font-size: 14px;
        font-weight: normal;
        line-height: 1;
        border-bottom: 1px solid $commonBorderColor;
    }
}
.menu-bar {
    position: relative;
    height: 100%;
    background: $commonBgColor;
    border: 1px solid $commonBorderColor;
    z-index: 3;
}
.node-type-item {
    position: relative;
    padding: 15px 0;
    font-size: 28px;
    text-align: center;
    cursor: move;
    transition: all 0.5s ease;
    &:hover {
        color: $blueDefault;
    }
    &.node-type-has-sub {
        cursor: pointer;
        &:hover{
            background: $whiteDefault;
        }
        &::after {
            position: absolute;
            bottom: 0;
            right: 0;
            content: '';
            width: 0;
            height: 0;
            border-style: solid;
            border-width: 0 0 8px 8px;
            border-color: transparent transparent $blackDefault transparent;
        }
    }
    &.active-node-type {
        color: $blueDefault;
        background: $whiteDefault;
        &::after {
            border-color: transparent transparent $blueDefault transparent;
        }
    }
}
.node-list {
    position: absolute;
    top: 50px;
    margin-left: 60px;
    width: 300px;
    height: calc(100% - 50px);
    background: $whitePanelBg;
    border-right: 1px solid $commonBorderColor;
    z-index: 2;
    .list-container {
        height: 100%;
        /deep/ .collapse-panel {
            .content-wrapper {
                padding-right: 0;
            }
        }
    }
}
.node-list-pin {
    position: absolute;
    top: 4px;
    right: 10px;
    font-size: 24px;
    color: $greyDark;
    cursor: pointer;
    z-index: 1;
    &:hover {
        color: $greyStatus;
    }
    &.actived {
        color: $greenDefault;
    }
}
.search-node-wraper {
    position: relative;
    padding-top: 30px;
    padding-bottom: 10px;
    text-align: center;
    .search-input {
        padding: 4px 40px 4px 20px;
        width: 280px;
        height: 30px;
        font-size: 14px;
        border-radius: 16px;
        border: 1px solid $commonBorderColor;
        outline: none;
        &:focus {
            border-color: $blueDefault;
            & + .common-icon-search {
                color: $blueDefault;
            }
        }

    }
    .common-icon-search {
        position: absolute;
        right: 30px;
        top: 36px;
        color: $commonBorderColor;
    }
}
.atom-list-wrapper {
    height: calc(100% - 71px);
    overflow-y: auto;
    @include scrollbar;
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
        font-weight: bold;
        overflow: hidden;
    }
    .list-content {
        padding: 10px;
        padding-right: 0;
    }
    .atom-item {
        float: left;
        display: table;
        margin-right: 8px;
        margin-bottom: 10px;
        padding: 10px;
        width: 134px;
        height: 58px;
        font-size: 12px;
        color: $greyDefault;
        background: $whiteNodeBg;
        border: 1px solid $commonBorderColor;
        text-align: center;
        word-break: break-all;
        overflow: hidden;
        cursor: move;
        &:nth-child(2n) {
            margin-right: 0;
        }
        &:hover {
            background: $blueDashBg;
            border-color: $blueDefault;
        }
        p {
            display: table-cell;
            vertical-align: middle;
        }
    }
}
</style>
