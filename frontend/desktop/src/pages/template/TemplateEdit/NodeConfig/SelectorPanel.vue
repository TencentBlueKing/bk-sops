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
                <div class="list-table">
                    <div class="table-head">
                        <div class="th-item tpl-name">{{ $t('流程名称') }}</div>
                        <div class="th-item tpl-label">
                            <span>{{ $t('标签') }}</span>
                            <div v-if="!common" class="label-select-wrap">
                                <div
                                    class="selected-label-name"
                                    v-bk-tooltips="{
                                        placement: 'bottom-left',
                                        allowHtml: 'true',
                                        theme: 'light',
                                        hideOnClick: false,
                                        extCls: 'tpl-label-popover',
                                        content: '#tpl-label-popover-content',
                                        onShow: handleLabelSelectorOpen,
                                        onHide: handleLabelSelectorClose
                                    }">
                                    <span v-bk-overflow-tips class="label-content" :style="getLabelStyle(activeGroup)">{{ selectedLabelName }}</span>
                                    <i :class="['bk-icon', 'icon-angle-down', { 'active': isLabelSelectorOpen }]"></i>
                                </div>
                                <div id="tpl-label-popover-content">
                                    <div
                                        v-for="item in labels"
                                        v-bk-overflow-tips
                                        :class="['tpl-label-item', { 'active': activeGroup === item.id }]"
                                        :key="item.id"
                                        @click="onSelectGroup(item.id)">
                                        <span
                                            class="label-content"
                                            :style="getLabelStyle(item.id)">
                                            {{ item.name }}
                                        </span>
                                    </div>
                                </div>
                                <!-- <bk-popover
                                    placement="bottom-left"
                                    theme="light"
                                    :arrow="false"
                                    :width="200"
                                    :on-show="handleLabelSelectorOpen"
                                    :on-hide="handleLabelSelectorClose"
                                    trigger="click"
                                    :tippy-options="{
                                        hideOnClick: false,
                                        duration: [0, 0]
                                    }"
                                    ext-cls="tpl-label-popover">
                                    <div class="selected-label-name">
                                        <span class="label-content" :style="getLabelStyle(activeGroup)">{{ selectedLabelName }}</span>
                                        <i :class="['bk-icon', 'icon-angle-down', { 'active': isLabelSelectorOpen }]"></i>
                                    </div>
                                    <div slot="content">
                                        <div
                                            v-for="item in labels"
                                            :class="['tpl-label-item', { 'active': activeGroup === item.id }]"
                                            :key="item.id"
                                            @click="onSelectGroup(item.id)">
                                            <span
                                                class="label-content"
                                                :style="getLabelStyle(item.id)">
                                                {{ item.name }}
                                            </span>
                                        </div>
                                    </div>
                                </bk-popover> -->
                            </div>
                        </div>
                    </div>
                    <div class="tpl-list" v-bkloading="{ isLoading: sublistLoading || searchLoading, zIndex: 10 }">
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
                                <div class="tpl-name name-content">
                                    <div class="name" v-if="item.highlightName" v-html="item.highlightName"></div>
                                    <div class="name" v-else>{{ item.name }}</div>
                                    <span class="view-tpl" @click.stop="$emit('viewSubflow', item.id)">
                                        <i class="common-icon-box-top-right-corner"></i>
                                    </span>
                                </div>
                                <div v-if="!common && item.template_labels.length > 0" class="tpl-label labels-wrap">
                                    <span
                                        v-for="label in item.template_labels"
                                        v-bk-overflow-tips
                                        class="label-item"
                                        :key="label.id"
                                        :style="getLabelStyle(label.label_id)">
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
    </div>
</template>

<script>
    import NoData from '@/components/common/base/NoData.vue'
    import toolsUtils from '@/utils/tools.js'
    import i18n from '@/config/i18n/index.js'
    import permission from '@/mixins/permission.js'
    import { SYSTEM_GROUP_ICON, DARK_COLOR_LIST } from '@/constants/index.js'
    import { mapActions } from 'vuex'

    export default {
        name: 'SelectorPanel',
        components: {
            NoData
        },
        mixins: [permission],
        props: {
            sublistLoading: Boolean,
            templateLabels: Array, // 模板标签
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
                searchData: [],
                isSelectLoading: false,
                darkColorList: DARK_COLOR_LIST,
                searchStr: '',
                searchResult: [],
                isLabelSelectorOpen: false,
                activeGroup: this.isSubflow ? '' : this.getDefaultActiveGroup(),
                searchLoading: false
            }
        },
        computed: {
            activeList () {
                if (!this.isSubflow) {
                    const group = this.listInPanel.find(item => item.type === this.activeGroup)
                    return group ? group.list : []
                }
                return []
            },
            labels () {
                const list = this.templateLabels.slice(0)
                list.unshift({
                    id: 0,
                    name: i18n.t('默认全部')
                })
                return list
            },
            selectedLabelName () {
                if (this.isSubflow && this.activeGroup) {
                    return this.templateLabels.find(item => item.id === this.activeGroup).name
                }
                return ''
            }
        },
        created () {
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions('templateList', [
                'loadTemplateList'
            ]),
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
            getLabelStyle (id) {
                if (id) {
                    const label = this.templateLabels.find(item => item.id === Number(id))
                    if (!label) return {}
                    return {
                        background: label.color,
                        color: this.darkColorList.includes(label.color) ? '#fff' : '#262e4f'
                    }
                }
                return { color: '#000000', minWidth: 'unset', padding: '2px' }
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
            async searchInputhandler () {
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
                } else if (this.searchStr !== '') {
                    this.searchLoading = true
                    try {
                        const reg = new RegExp(this.searchStr, 'i')
                        const data = {
                            pipeline_template__name__icontains: this.searchStr || undefined
                        }
                        const resp = await this.loadTemplateList(data)
                        this.handleSubflowList(resp).forEach(tpl => {
                            let matchLabel = true
                            let matchName = true
                            const tplCopy = { ...tpl }
                            if (this.activeGroup) {
                                matchLabel = tpl.template_labels.find(label => label.label_id === Number(this.activeGroup))
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
                    } catch (e) {
                        console.log(e)
                    } finally {
                        this.searchLoading = false
                    }
                } else {
                    result = this.listData
                }

                this.listInPanel = result
            },
            handleSubflowList (data) {
                const list = []
                const reqPermission = this.common ? ['common_flow_view'] : ['flow_view']
                data.objects.forEach(item => {
                    // 克隆模板可以引用被克隆的模板，模板不可以引用自己
                    if (this.type === 'clone' || item.id !== Number(this.template_id)) {
                        item.hasPermission = this.hasPermission(reqPermission, item.auth_actions)
                        list.push(item)
                    }
                })
                return list
            },
            handleLabelSelectorOpen () {
                this.isLabelSelectorOpen = true
            },
            handleLabelSelectorClose () {
                this.isLabelSelectorOpen = false
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
    padding: 17px 24px;
    height: 100%;
    .pagination {
        margin: 5px
    }
    .list-table {
        border: 1px solid #dcdee5;
        border-radius: 3px;
        .table-head {
            display: flex;
            align-items: center;
            padding: 12px;
            background: #fafbfd;
            border-bottom: 1px solid hsl(227, 15%, 88%);
            .th-item {
                color: #313238;
                font-size: 12px;
                font-weight: 500;
            }
            .tpl-name {
                flex: 0 0 auto;
                width: 420px;
            }
            .tpl-label {
                display: flex;
                align-items: center;
                .label-select-wrap {
                    cursor: pointer;
                    .selected-label-name {
                        display: flex;
                        align-items: center;
                        transition: transform .3s cubic-bezier(.4, 0, .2, 1);
                        & > i {
                            font-size: 14px;
                            &.active {
                                transform: rotate(-180deg);
                            }
                        }
                    }
                    .label-content {
                        display: inline-block;
                        margin-left: 4px;
                        max-width: 144px;
                        min-width: 40px;
                        padding: 2px 6px;
                        font-size: 12px;
                        line-height: 1;
                        color: #63656e;
                        border-radius: 8px;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        cursor: pointer;
                    }
                }
            }
        }
    }
    .tpl-list {
        max-height: calc(100vh - 160px);
        overflow: auto;
        @include scrollbar;
    }
    .tpl-item {
        display: flex;
        min-height: 40px;
        align-items: center;
        color: #63656e;
        border-bottom: 1px solid #dcdee5;
        cursor: pointer;
        &:hover:not(.text-permission-disable), &.active:not(.text-permission-disable) {
            background: #e1ecff;
            .name, .view-tpl {
                color: #3a84ff;
            }
        }
        &:last-child {
            border: none;
        }
        .name-content {
            display: flex;
            align-items: center;
            flex: 0 0 auto;
            width: 420px;
        }
        .name {
            padding: 0 13px;
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
            padding-right: 13px;
            .label-item {
                display: inline-block;
                max-width: 144px;
                min-width: 40px;
                margin: 4px 0 4px 4px;
                padding: 2px 6px;
                font-size: 12px;
                line-height: 1;
                color: #63656e;
                border-radius: 8px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                cursor: pointer;
            }
        }
    }
    .tpl-loading {
        height: 40px;
        bottom: 0;
        left: 0;
        font-size: 14px;
        text-align: center;
        margin-top: 10px;
    }
}
</style>
<style lang="scss">
    .tpl-label-popover {
        background: #ffffff;
        .tippy-tooltip {
            padding: 7px 0;
            max-height: 180px;
            overflow: auto;
        }
        .tpl-label-item {
            padding: 4px 13px;
            cursor: pointer;
            &:hover {
                background: #eaf3ff;
            }
            &.active {
                background: #f4f6fa;
            }
            .label-content {
                display: inline-block;
                max-width: 144px;
                min-width: 40px;
                padding: 2px 6px;
                font-size: 12px;
                line-height: 1;
                color: #63656e;
                border-radius: 8px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                cursor: pointer;
            }
        }
    }
</style>
