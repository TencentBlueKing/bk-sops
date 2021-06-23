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
            <div :class="['panel-fixed-pin', { 'actived': isFixedNodeMenu }]" @click.stop="onClickPin">
                <i class="common-icon-pin"></i>
            </div>
            <div class="search-wrap">
                <bk-input
                    class="search-input"
                    v-model.trim="searchStr"
                    right-icon="bk-icon icon-search"
                    :placeholder="$t('请输入名称')"
                    :clearable="true"
                    @input="onNameSearch"
                    @clear="searchInputhandler">
                </bk-input>
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
            </div>
            <div class="node-list-wrap" v-bkloading="{ isLoading: loading, opacity: 1 }">
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
            common: {
                type: [String, Number],
                default: ''
            }
        },
        data () {
            const selectedGroup = this.activeNodeListType === 'subflow' ? [] : ''
            return {
                isPinActived: false,
                selectedGroup,
                searchStr: '',
                searchResult: [],
                isShowGroup: true,
                defaultTypeIcon: require('@/assets/images/atom-type-default.svg')
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
            }
        },
        watch: {
            activeNodeListType (val) {
                this.searchStr = ''
                this.searchResult = []
                this.selectedGroup = val === 'subflow' ? [] : ''
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
            searchInputhandler () {
                const result = []
                this.searchResult = []
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
    .panel-fixed-pin {
        position: absolute;
        top: 16px;
        right: 16px;
        padding: 7px 8px 8px;
        line-height: 1;
        border: 1px solid #c4c6cc;
        border-radius: 2px;
        font-size: 14px;
        text-align: center;
        color: #999999;
        cursor: pointer;
        z-index: 1;
        &:hover {
            color: #707379;
        }
        &.actived {
            color: #52699d;
        }
    }
    .search-wrap {
        padding: 16px;
        border-bottom: 1px solid #ccd0dd;
        background: #ffffff;
        .search-input {
            margin-bottom: 10px;
            width: 220px;
        }
    }
    .node-list-wrap {
        height: calc(100% - 107px);
        overflow-y: auto;
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
