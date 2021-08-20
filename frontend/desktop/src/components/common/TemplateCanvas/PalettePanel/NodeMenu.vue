/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
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
            <div class="title-wrap">
                <span>{{ pluginTitle }}</span>
                <div :class="['panel-fixed-pin', { 'actived': isFixedNodeMenu }]" @click.stop="onClickPin">
                    <i class="common-icon-pin"></i>
                </div>
            </div>
            <!-- 内置插件/第三方插件tab -->
            <bk-tab
                v-if="activeNodeListType === 'tasknode'"
                :active.sync="curPluginTab"
                type="unborder-card"
                @tab-change="setSearchInputShow(true)">
                <bk-tab-panel v-bind="{ name: 'build_in_plugin', label: $t('内置插件') }"></bk-tab-panel>
                <bk-tab-panel v-bind="{ name: 'third_praty_plugin', label: $t('第三方插件') }"></bk-tab-panel>
            </bk-tab>
            <div class="search-wrap">
                <template v-if="isSearch">
                    <div
                        class="select-btn"
                        v-if="curPluginTab === 'build_in_plugin'"
                        @click="setSelectInputShow">
                        <i class="common-icon-arrow-down"></i>
                    </div>
                    <bk-input
                        v-if="isSearch"
                        class="search-input"
                        v-model.trim="searchStr"
                        right-icon="bk-icon icon-search"
                        :placeholder="$t('搜索插件')"
                        :clearable="true"
                        @input="onNameSearch"
                        @clear="searchInputhandler">
                    </bk-input>
                </template>
                <template v-else>
                    <bk-select
                        v-if="activeNodeListType === 'tasknode'"
                        v-model="selectedGroup"
                        :clearable="true"
                        :searchable="true"
                        @change="searchInputhandler">
                        <bk-option
                            v-for="item in groupList"
                            class="node-item-option"
                            :key="item.type"
                            :id="item.type"
                            :name="item.group_name">
                        </bk-option>
                    </bk-select>
                    <bk-select
                        v-else-if="activeNodeListType === 'subflow' && !common"
                        key="subflow-select"
                        ext-popover-cls="label-select"
                        v-model="selectedGroup"
                        :display-tag="true"
                        :multiple="true"
                        :clearable="true"
                        :searchable="true"
                        @change="searchInputhandler">
                        <bk-option
                            v-for="(item, index) in templateLabels"
                            class="node-item-option"
                            :key="index"
                            :id="item.id"
                            :name="item.name">
                            <div class="label-select-option">
                                <span
                                    class="label-select-color"
                                    :style="{ background: item.color }">
                                </span>
                                <span>{{item.name}}</span>
                                <i class="bk-option-icon bk-icon icon-check-1"></i>
                            </div>
                        </bk-option>
                    </bk-select>
                    <div class="search-btn" @click="setSearchInputShow(false)">
                        <i class="common-icon-search"></i>
                    </div>
                </template>
            </div>
            <!-- 内置插件 -->
            <div
                v-show="curPluginTab === 'build_in_plugin'"
                class="node-list-wrap"
                v-bkloading="{ isLoading: loading, opacity: 1 }">
                <template v-if="listInPanel.length > 0">
                    <template v-if="!isSearchMode">
                        <template v-if="activeNodeListType === 'tasknode'">
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
                                        <template v-for="(node, index) in group.list">
                                            <node-item
                                                v-if="activeNodeListType !== 'subflow' || node.hasPermission"
                                                class="node-item"
                                                :key="index"
                                                :type="activeNodeListType"
                                                :node="node">
                                            </node-item>
                                            <div
                                                v-else
                                                :key="index"
                                                class="node-item">
                                                <div
                                                    v-cursor
                                                    class="name-wrapper text-permission-disable"
                                                    @click="onApplyPermission(node)">
                                                    {{ node.name }}
                                                </div>
                                            </div>
                                        </template>
                                        <div class="node-empty" v-if="group.list.length === 0">
                                            <no-data></no-data>
                                        </div>
                                    </div>
                                </bk-collapse-item>
                            </bk-collapse>
                        </template>
                        <div v-else class="node-item-wrap">
                            <template v-for="(node, index) in listInPanel">
                                <node-item
                                    v-if="node.hasPermission"
                                    class="node-item"
                                    :key="index"
                                    :type="activeNodeListType"
                                    :node="node">
                                </node-item>
                                <div
                                    v-else
                                    :key="index"
                                    class="node-item">
                                    <div
                                        v-cursor
                                        class="name-wrapper text-permission-disable"
                                        @click="onApplyPermission(node)">
                                        {{ node.name }}
                                    </div>
                                </div>
                            </template>
                        </div>
                    </template>
                    <template v-else>
                        <div class="search-result">
                            <template v-for="(node, index) in listInPanel">
                                <node-item
                                    v-if="activeNodeListType !== 'subflow' || node.hasPermission"
                                    class="node-item"
                                    :key="index"
                                    :type="activeNodeListType"
                                    :node="node">
                                </node-item>
                                <div
                                    v-else
                                    :key="index"
                                    class="node-item">
                                    <div
                                        v-cursor
                                        class="name-wrapper text-permission-disable"
                                        @click="onApplyPermission(node)">
                                        {{ node.name }}
                                    </div>
                                </div>
                            </template>
                        </div>
                    </template>
                </template>
                <no-data v-else></no-data>
            </div>
            <div
                v-show="curPluginTab === 'third_praty_plugin'"
                class="third-praty-list">
                <ul>
                    <li v-for="(item, index) in pluginList" :key="index">
                        <node-item
                            class="node-item"
                            type="tasknode"
                            :node="{
                                plugin_type: 'third-praty',
                                code: 'remote_plugin',
                                template_id: templateId,
                                name: item.code,
                                group_icon: '',
                                group_name: '',
                                nodeName: item.name,
                                logo_url: item.logo_url
                            }">
                        </node-item>
                    </li>
                </ul>
            </div>
        </div>
    </transition>
</template>
<script>
    import { mapState } from 'vuex'
    import NoData from '@/components/common/base/NoData.vue'
    import NodeItem from './NodeItem.vue'
    import dom from '@/utils/dom.js'
    import toolsUtils from '@/utils/tools.js'
    import permission from '@/mixins/permission.js'
    import { SYSTEM_GROUP_ICON } from '@/constants/index.js'

    export default {
        name: 'NodeMenu',
        components: {
            NoData,
            NodeItem
        },
        mixins: [permission],
        props: {
            templateLabels: Array,
            loading: Boolean,
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
            },
            pluginList: {
                type: Array,
                default () {
                    return []
                }
            },
            common: {
                type: [String, Number],
                default: ''
            },
            pluginLoading: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const selectedGroup = this.activeNodeListType === 'subflow' ? [] : ''
            const templateId = this.$route.query.template_id
            return {
                templateId: templateId,
                curPluginTab: 'build_in_plugin',
                isSearch: false,
                isPinActived: false,
                selectedGroup,
                searchStr: '',
                searchResult: [],
                isShowGroup: true,
                defaultTypeIcon: require('@/assets/images/atom-type-default.svg'),
                scrollDom: null
            }
        },
        computed: {
            ...mapState('project', {
                'projectId': state => state.project_id,
                'projectName': state => state.projectName
            }),
            isSearchMode () {
                if (this.activeNodeListType === 'tasknode') {
                    return this.searchStr !== '' || this.selectedGroup !== ''
                } else {
                    return this.searchStr !== '' || this.selectedGroup.length > 0
                }
            },
            listInPanel () {
                return this.isSearchMode ? this.searchResult : this.nodes
            },
            groupList () {
                if (this.activeNodeListType === 'tasknode') {
                    return this.nodes.map(item => {
                        return {
                            type: item.type,
                            group_name: item.group_name
                        }
                    })
                } else {
                    return this.templateLabels
                }
            },
            pluginTitle () {
                let title = ''
                if (this.curPluginTab === 'third_praty_plugin') {
                    title = this.$t('第三方插件节点')
                } else if (this.activeNodeListType === 'tasknode') {
                    title = this.$t('标准插件节点')
                } else {
                    title = this.$t('流程模板')
                }
                return title
            }
        },
        watch: {
            activeNodeListType (val) {
                this.isSearch = false
                this.curPluginTab = 'build_in_plugin'
                this.searchStr = ''
                this.searchResult = []
                this.selectedGroup = val === 'subflow' ? [] : ''
            },
            showNodeMenu (val) {
                if (val) {
                    this.$nextTick(() => {
                        this.scrollDom = document.querySelector('.third-praty-list')
                        if (this.scrollDom) {
                            this.scrollDom.addEventListener('scroll', this.handlePluginScroll)
                        }
                    })
                } else if (this.scrollDom) {
                    this.scrollDom.removeEventListener('scroll', this.handlePluginScroll)
                }
            }
        },
        created () {
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            getIconCls (type) {
                const systemType = SYSTEM_GROUP_ICON.find(item => new RegExp(item).test(type))
                if (this.activeNodeListType === 'subflow') {
                    return 'common-icon-subflow-mark'
                }
                if (systemType) {
                    return `common-icon-sys-${systemType.toLowerCase()}`
                }
                return 'common-icon-sys-default'
            },
            onClickPin () {
                this.$emit('onToggleNodeMenuFixed', !this.isFixedNodeMenu)
            },
            onNameSearch () {
                this.searchResult = []
                this.onSearchInput()
            },
            setSelectInputShow () {
                this.searchStr = ''
                this.isSearch = false
            },
            setSearchInputShow (isTab) {
                this.selectedGroup = this.activeNodeListType === 'subflow' ? [] : ''
                this.searchStr = ''
                const isThirdParty = this.curPluginTab === 'third_praty_plugin'
                this.isSearch = isTab ? isThirdParty : true
                if (isThirdParty) {
                    this.$emit('updatePluginList', undefined, 'search')
                }
            },
            handlePluginScroll () {
                const el = this.scrollDom
                if (el.scrollHeight - el.offsetHeight - el.scrollTop < 10) {
                    this.$emit('updatePluginList', this.searchStr, 'scroll')
                }
            },
            searchInputhandler () {
                const result = []
                this.searchResult = []
                if (this.curPluginTab === 'third_praty_plugin') {
                    this.$emit('updatePluginList', this.searchStr, 'search')
                    return
                }
                if (this.activeNodeListType === 'tasknode') {
                    let listData = this.nodes
                    if (this.selectedGroup) {
                        listData = this.nodes.filter(group => group.group_name === this.selectedGroup)
                    }
                    if (this.searchStr !== '') {
                        const reg = new RegExp(this.searchStr, 'i')
                        listData.forEach(group => {
                            if (group.list.length > 0) {
                                group.list.forEach(node => {
                                    if (reg.test(node.name)) {
                                        result.push(node)
                                    }
                                })
                            }
                        })
                    } else {
                        listData.forEach(group => {
                            if (group.list.length > 0) {
                                result.push(...group.list.map(item => item.list[item.list.length - 1]))
                            }
                        })
                    }
                } else {
                    const reg = new RegExp(this.searchStr, 'i')
                    this.nodes.forEach(node => {
                        let matchLabel = true
                        let matchName = true

                        if (this.selectedGroup.length > 0) {
                            matchLabel = this.selectedGroup.every(item => node.template_labels.find(label => label.label_id === Number(item)))
                        }
                        if (this.searchStr !== '') {
                            matchName = reg.test(node.name)
                        }

                        if (matchLabel && matchName) {
                            result.push(node)
                        }
                    })
                }

                this.searchResult = result
            },
            handleClickOutSide (e) {
                if (!this.isFixedNodeMenu) {
                    if (
                        dom.parentClsContains('palette-item', e.target) // 左侧节点
                        || dom.parentClsContains('node-item-option', e.target) // 搜索分组选项
                    ) {
                        return
                    }
                    this.selectedGroup = this.activeNodeListType === 'subflow' ? [] : ''
                    this.isSearch = false
                    this.$emit('onCloseNodeMenu')
                }
            },
            onApplyPermission (node) {
                let reqPerm, permissionData
                if (this.common) {
                    reqPerm = 'common_flow_view'
                    permissionData = {
                        common_flow: [{
                            id: node.id,
                            name: node.name
                        }]
                    }
                } else {
                    reqPerm = 'flow_view'
                    permissionData = {
                        flow: [{
                            id: node.id,
                            name: node.name
                        }],
                        project: [{
                            id: this.projectId,
                            name: this.projectName
                        }]
                    }
                }
                this.applyForPermission([reqPerm], [], permissionData)
            }
        }
    }
</script>
<style lang="scss">
    .node-menu {
        .bk-tab .bk-tab-section {
            display: none;
        }
        .search-wrap {
            .bk-select, .search-input {
                min-width: 227px;
            }
        }
    }
</style>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    .node-menu {
        position: absolute;
        top: 0;
        margin-left: 60px;
        width: 293px;
        height: 100%;
        background: #ffffff;
        border-right: 1px solid #dddddd;
        z-index: 2;
    }
    
    .title-wrap {
        height: 41px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 11px 0 14px;
        color: #303132;
        font-size: 14px;
        border-bottom: 1px solid #ccd0dd;
        .panel-fixed-pin {
            color: #999999;
            cursor: pointer;
            &:hover {
                color: #707379;
            }
            &.actived {
                color: #52699d;
            }
        }
    }
    .search-wrap {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 11px 14px 12px;
        border-bottom: 1px solid #ccd0dd;
        background: #ffffff;
        .search-btn, .select-btn {
            width: 32px;
            height: 32px;
            flex-shrink: 0;
            border: 1px solid #c4c6cc;
            border-radius: 3px;
            font-size: 14px;
            color: #979ba5;
            text-align: center;
            line-height: 28px;
            cursor: pointer;
        }
        .search-btn {
            margin-left: 11px;
            .common-icon-search {
                position: static;
            }
        }
        .select-btn {
            font-size: 12px;
            line-height: 30px;
            margin-right: 11px;
        }
    }
    .node-list-wrap {
        height: calc(100% - 107px);
        overflow-y: auto;
        @include scrollbar;
    }
    .third-praty-list {
        height: 687px;
        overflow: auto;
        @include scrollbar;
    }
    .node-item {
        background: #f0f1f5;
        border-top: 1px solid #e2e4ed;
        border-radius: 2px;
        overflow: hidden;
        cursor: move;
        user-select: none;
        &:first-child {
            border-top: none;
        }
        &:hover {
            background: #fafbfd;
        }
        /deep/ .name-wrapper {
            padding: 0 14px;
            height: 40px;
            line-height: 40px;
            color: #63656e;
            font-size: 12px;
        }
    }
    .bk-collapse-item {
        border-bottom: 1px solid #e2e4ed;
        /deep/ .bk-collapse-item-header {
            background: #ffffff;
            &:hover {
                background: #fafbfd;
            }
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
            &.common-icon-subflow-mark {
                font-size: 18px;
            }
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
</style>
