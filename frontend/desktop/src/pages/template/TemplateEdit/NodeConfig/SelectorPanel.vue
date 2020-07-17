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
                        <span>{{ group.group_name }}</span>
                        <span>{{ `(${group.list.length})` }}</span>
                    </div>
                </div>
                <div class="selector-area" ref="selectorArea">
                    <template v-if="activeList.length > 0">
                        <template v-for="(item, index) in activeList">
                            <li
                                v-if="!isSubflow || item.hasPermission"
                                :class="['list-item', { active: getSelectedStatus(item) }]"
                                :key="index"
                                :title="item.name"
                                @click="onSelect(item)">
                                <span class="node-name" v-html="item.name"></span>
                                <span v-if="isSubflow" class="view-tpl" @click.stop="$emit('viewSubflow', item.id)">
                                    <i class="common-icon-box-top-right-corner"></i>
                                </span>
                            </li>
                            <li
                                v-else
                                class="list-item text-permission-disable"
                                :key="item.id"
                                :title="item.name"
                                v-cursor
                                v-html="item.name"
                                @click="onApplyPermission(item)">
                            </li>
                        </template>
                    </template>
                    <no-data v-else></no-data>
                </div>
            </template>
            <no-data v-else></no-data>
        </div>
    </div>
</template>

<script>
    import NoData from '@/components/common/base/NoData.vue'
    import toolsUtils from '@/utils/tools.js'
    import permission from '@/mixins/permission.js'
    import { SYSTEM_GROUP_ICON } from '@/constants/index.js'

    export default {
        name: 'SelectorPanel',
        components: {
            NoData
        },
        mixins: [permission],
        props: {
            atomTypeList: Object,
            isSubflow: Boolean,
            basicInfo: Object
        },
        data () {
            const listData = this.isSubflow ? this.atomTypeList.subflow.groups : this.atomTypeList.tasknode
            return {
                listData,
                listInPanel: listData,
                searchStr: '',
                searchResult: [],
                activeGroup: this.getDefaultActiveGroup()
            }
        },
        computed: {
            activeList () {
                const group = this.listInPanel.find(item => item.type === this.activeGroup)
                return group ? group.list : []
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
            onSelectGroup (val) {
                this.activeGroup = val
                this.$refs.selectorArea.scrollTop = 0
            },
            onClearSearch () {
                this.searchInputhandler()
            },
            searchInputhandler () {
                let result = []
                if (this.searchStr === '') {
                    result = this.listData.slice(0)
                    this.activeGroup = this.getDefaultActiveGroup()
                } else {
                    const reg = new RegExp(this.searchStr, 'i')
                    this.listData.forEach(group => {
                        const list = []
                        if (group.list.length > 0) {
                            group.list.forEach(item => {
                                if (reg.test(item.name)) {
                                    const node = { ...item }
                                    node.name = item.name.replace(reg, `<span style="color: #ff5757;">${this.searchStr}</span>`)
                                    list.push(node)
                                }
                            })
                            if (list.length > 0) {
                                const { group_icon, group_name, type } = group
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
                this.listInPanel = result
            },
            /**
             * 选择插件/子流程
             */
            onSelect (val) {
                this.$emit('select', val)
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
                const { tplOperations, tplResource } = this.atomTypeList.subflow
                this.applyForPermission(['view'], tpl, tplOperations, tplResource)
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
    height: calc(100vh - 170px);
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
    .common-icon-box-top-right-corner {
        position: absolute;
        right: 20px;
        top: 14px;
    }
}
</style>
