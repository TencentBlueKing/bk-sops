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
    <div class="selector-panel">
        <bk-input
            class="search-input"
            v-model.trim="searchStr"
            right-icon="bk-icon icon-search"
            :placeholder="$t('请输入名称')"
            :clearable="true"
            @input="onSearchInput"
            @clear="onClearSearch">
        </bk-input>
        <div class="list-wrapper">
            <template v-if="!isSubflow">
                <template v-if="listInPanel.length > 0">
                    <div class="group-area">
                        <div
                            :class="['group-item', {
                                active: group.type === activeGroup
                            }]"
                            v-for="group in listInPanel"
                            :key="group.type"
                            @click="onSelectGroup(group.type)">
                            <img v-if="group.group_icon" class="group-icon-img" :src="group.group_icon" />
                            <i v-else :class="['group-icon-font', getIconCls(group.type)]"></i>
                            <span v-html="group.group_name"></span>
                            <span>{{ `(${group.list.length})` }}</span>
                        </div>
                    </div>
                    <div class="selector-area" ref="selectorArea">
                        <template v-if="activeList.length > 0">
                            <li
                                v-for="(item, index) in activeList"
                                :class="['list-item', { active: getSelectedStatus(item) }]"
                                :key="index"
                                :title="item.name"
                                @click="$emit('select', item)">
                                <span class="node-name" v-if="item.highlightName" v-html="item.highlightName"></span>
                                <span class="node-name" v-else>{{ item.name }}</span>
                            </li>
                        </template>
                        <no-data v-else></no-data>
                    </div>
                </template>
                <no-data v-else></no-data>
            </template>
            <div v-else class="subflow-list">
                <div v-if="!common" class="label-select-wrap">
                    <bk-select
                        class="select-group"
                        ext-popover-cls="label-select"
                        style="width: 270px;"
                        v-model="activeGroup"
                        :placeholder="$t('请选择标签')"
                        :display-tag="true"
                        :multiple="true"
                        :clearable="true"
                        :searchable="true"
                        @change="onSelectGroup">
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
                <div :class="['tpl-list', { 'has-label-select': !common }]">
                    <template v-if="listInPanel.length > 0">
                        <div
                            v-for="item in listInPanel"
                            v-cursor="{ active: !item.hasPermission }"
                            :class="['tpl-item', {
                                'active': getSelectedStatus(item),
                                'text-permission-disable': !item.hasPermission
                            }]"
                            :key="item.id"
                            @click="onTplClick(item)">
                            <div class="name-content">
                                <div class="name" v-if="item.highlightName" v-html="item.highlightName"></div>
                                <div class="name" v-else>{{ item.name }}</div>
                                <span class="view-tpl" @click.stop="$emit('viewSubflow', item.id)">
                                    <i class="common-icon-box-top-right-corner"></i>
                                </span>
                            </div>
                            <div v-if="!common && item.template_labels.length > 0" class="labels-wrap">
                                <span
                                    v-for="label in item.template_labels"
                                    class="label-item"
                                    :key="label.id"
                                    :style="{ background: label.color, color: darkColorList.includes(label.color) ? '#fff' : '#262e4f' }">
                                    {{ label.name }}
                                </span>
                            </div>
                        </div>
                    </template>
                    <no-data v-else></no-data>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import NoData from '@/components/common/base/NoData.vue'
    import toolsUtils from '@/utils/tools.js'
    import permission from '@/mixins/permission.js'
    import { SYSTEM_GROUP_ICON, DARK_COLOR_LIST } from '@/constants/index.js'

    export default {
        name: 'SelectorPanel',
        components: {
            NoData
        },
        mixins: [permission],
        props: {
            templateLabels: Array,
            atomTypeList: Object,
            isSubflow: Boolean,
            basicInfo: Object,
            common: [String, Number]
        },
        data () {
            const listData = this.isSubflow ? this.atomTypeList.subflow : this.atomTypeList.tasknode
            return {
                listData,
                listInPanel: listData,
                darkColorList: DARK_COLOR_LIST,
                searchStr: '',
                searchResult: [],
                activeGroup: this.isSubflow ? [] : this.getDefaultActiveGroup()
            }
        },
        computed: {
            activeList () {
                if (!this.isSubflow) {
                    const group = this.listInPanel.find(item => item.type === this.activeGroup)
                    return group ? group.list : []
                }
                return []
            }
        },
        created () {
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            // 获取默认展开的分组，没有选择展开第一组，已选择展开选中的那组
            getDefaultActiveGroup () {
                let activeGroup = ''
                const data = this.isSubflow ? this.atomTypeList.subflow.groups : this.atomTypeList.tasknode
                const propertyName = this.isSubflow ? 'id' : 'code'
                const id = this.isSubflow ? 'tpl' : 'plugin'
                if (this.basicInfo[id]) {
                    data.some(group => {
                        if (group.list.find(item => String(item[propertyName]) === String(this.basicInfo[id]))) {
                            activeGroup = group.type
                            return true
                        }
                    })
                } else {
                    if (data.length > 0) {
                        activeGroup = data[0].type
                    }
                }
                return activeGroup
            },
            getIconCls (type) {
                const systemType = SYSTEM_GROUP_ICON.find(item => new RegExp(item).test(type))
                if (this.isSubflow) {
                    return 'common-icon-subflow-mark'
                }
                if (systemType) {
                    return `common-icon-sys-${systemType.toLowerCase()}`
                }
                return 'common-icon-sys-default'
            },
            /**
             * 选择插件分组
             */
            onSelectGroup (val) {
                this.activeGroup = val
                if (this.isSubflow) {
                    this.searchInputhandler()
                } else {
                    this.$refs.selectorArea.scrollTop = 0
                }
            },
            onClearSearch () {
                this.searchInputhandler()
            },
            searchInputhandler () {
                let result = []
                if (!this.isSubflow) {
                    if (this.searchStr === '') {
                        result = this.listData.slice(0)
                        this.activeGroup = this.getDefaultActiveGroup()
                    } else {
                        const reg = new RegExp(this.searchStr, 'i')
                        this.listData.forEach(group => {
                            const { group_icon, group_name, type } = group
                            const list = []
    
                            if (reg.test(group_name)) { // 分组名称匹配
                                const hglGroupName = group_name.replace(reg, `<span style="color: #ff5757;">${this.searchStr}</span>`)
                                result.push({
                                    ...group,
                                    group_name: hglGroupName
                                })
                            } else if (group.list.length > 0) { // 单个插件或者子流程名称匹配
                                group.list.forEach(item => {
                                    if (reg.test(item.name)) {
                                        const node = { ...item }
                                        node.highlightName = item.name.replace(reg, `<span style="color: #ff5757;">${this.searchStr}</span>`)
                                        list.push(node)
                                    }
                                })
                                if (list.length > 0) {
                                    result.push({
                                        group_icon,
                                        group_name,
                                        type,
                                        list
                                    })
                                }
                            }
                        })
                        if (result.length > 0) {
                            this.activeGroup = result[0].type
                        }
                    }
                } else {
                    const reg = new RegExp(this.searchStr, 'i')
                    this.listData.forEach(tpl => {
                        let matchLabel = true
                        let matchName = true
                        const tplCopy = { ...tpl }

                        if (this.activeGroup.length > 0) {
                            matchLabel = this.activeGroup.every(item => tpl.template_labels.find(label => label.label_id === Number(item)))
                        }
                        if (this.searchStr !== '') {
                            if (!reg.test(tpl.name)) {
                                matchName = false
                            } else {
                                tplCopy.highlightName = tplCopy.name.replace(reg, `<span style="color: #ff5757;">${this.searchStr}</span>`)
                            }
                        }

                        if (matchLabel && matchName) {
                            result.push(tplCopy)
                        }
                    })
                }
                this.listInPanel = result
            },
            onTplClick (tpl) {
                if (tpl.hasPermission) {
                    this.$emit('select', tpl)
                } else {
                    this.onApplyPermission(tpl)
                }
            },
            /**
             * 插件/子流程选中状态
             */
            getSelectedStatus (item) {
                if (this.isSubflow) {
                    return String(item.id) === String(this.basicInfo.tpl)
                }
                return item.code === this.basicInfo.plugin
            },
            onApplyPermission (tpl) {
                let reqPerm, resourceData
                if (this.common) {
                    reqPerm = 'common_flow_view'
                    resourceData = {
                        common_flow: [{
                            id: tpl.id,
                            name: tpl.name
                        }]
                    }
                } else {
                    reqPerm = 'flow_view'
                    resourceData = {
                        flow: [{
                            id: tpl.id,
                            name: tpl.name
                        }],
                        project: [{
                            id: tpl.project.id,
                            name: tpl.project.name
                        }]
                    }
                }
                this.applyForPermission([reqPerm], [], resourceData)
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.selector-panel {
    position: relative;
}
.search-input {
    position: absolute;
    top: -45px;
    right: 20px;
    width: 300px;
}
.list-wrapper {
    height: calc(100vh - 60px);
}
.group-area {
    float: left;
    width: 270px;
    height: 100%;
    background-image: linear-gradient(to right, transparent 269px,#e2e4ed 0);
    background-color: #fafbfd;
    overflow: auto;
    @include scrollbar;
    .group-item {
        position: relative;
        padding: 0 18px;
        font-size: 14px;
        color: #63656e;
        height: 42px;
        line-height: 42px;
        border-bottom: 1px solid #e2e4ed;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        cursor: pointer;
        &:hover {
            color: #3a84ff;
        }
        &.active {
            color: #3a84ff;
            background: #ffffff;
            border-right: 1px solid #ffffff;
        }
    }
}
.selector-area {
    margin-left: 270px;
    height: 100%;
    font-size: 12px;
    color: #63656e;
    overflow: auto;
    @include scrollbar;
    .list-item {
        position: relative;
        padding: 0 40px 0 20px;
        height: 42px;
        line-height: 42px;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        cursor: pointer;
        &:hover {
            background: #e1ecff;
            color: #3a84ff;
        }
        &.active {
            background: #e1ecff;
            & > .node-name {
                color: #3a84ff;
            }
        }
    }
}
.subflow-list {
    height: 100%;
    .label-select-wrap {
        padding: 14px 20px;
        height: 60px;
        border-bottom: 1px solid #e2e4ed;
        .bk-select.is-focus {
            background: #ffffff;
        }
    }
    .tpl-list {
        height: 100%;
        overflow: auto;
        @include scrollbar;
        &.has-label-select {
            height: calc(100% - 60px);
        }
    }
    .tpl-item {
        display: flex;
        padding: 0 20px;
        min-height: 40px;
        align-items: center;
        justify-content: space-between;
        color: #63656e;
        cursor: pointer;
        &:hover:not(.text-permission-disable), &.active:not(.text-permission-disable) {
            background: #e1ecff;
            .name, .view-tpl {
                color: #3a84ff;
            }
        }
        .name-content {
            display: flex;
            align-items: center;
        }
        .name {
            font-size: 12px;
            max-width: 400px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }
        .view-tpl {
            margin-left: 10px;
            color: #9796a5;
            font-size: 14px;
        }
        .labels-wrap {
            width: 240px;
            .label-item {
                display: inline-block;
                margin: 4px 0 4px 4px;
                padding: 2px 6px;
                font-size: 12px;
                line-height: 1;
                color: #63656e;
                border-radius: 8px;
                cursor: pointer;
            }
        }
    }
}
</style>
