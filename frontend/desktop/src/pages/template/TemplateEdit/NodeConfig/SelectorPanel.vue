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
        <div class="search-area">
            <bk-select
                class="select-group"
                v-model="selectedGroup"
                :clearable="false"
                @selected="onSelectGroup">
                <bk-option
                    v-for="item in groupList"
                    :key="item.type"
                    :id="item.type"
                    :name="item.group_name">
                </bk-option>
            </bk-select>
            <bk-input
                class="search-input"
                v-model="searchStr"
                right-icon="bk-icon icon-search"
                :placeholder="$t('请输入名称')"
                :clearable="true"
                @input="onSearchInput"
                @clear="onClearSearch">
            </bk-input>
        </div>
        <div class="list-wrapper">
            <template v-if="listInPanel.length > 0">
                <!-- 全部插件类表 -->
                <template v-if="searchStr === '' && selectedGroup === 'all'">
                    <bk-collapse ext-cls="group-collapse" v-for="group in listInPanel" :key="group.type">
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
                            <ul slot="content" class="list-item-wrap">
                                <template v-for="(item, index) in group.list">
                                    <li
                                        v-if="!isSubflow || item.hasPermission"
                                        :class="['list-item', { selected: getSelectedStatus(item) }]"
                                        :key="index"
                                        @click="onSelect(item)">
                                        <span class="node-name">{{ item.name }}</span>
                                        <span v-if="isSubflow" class="view-tpl" @click.stop="onViewSubflow(item)">
                                            <i class="common-icon-box-top-right-corner"></i>
                                        </span>
                                    </li>
                                    <li
                                        v-else
                                        class="list-item text-permission-disable"
                                        :key="item.id"
                                        v-cursor
                                        @click="onApplyPermission(item)">
                                        {{ item.name }}
                                    </li>
                                </template>
                                <div class="node-empty" v-if="group.list.length === 0">
                                    <no-data></no-data>
                                </div>
                            </ul>
                        </bk-collapse-item>
                    </bk-collapse>
                </template>
                <!-- 搜索结果插件列表 -->
                <template v-else>
                    <ul slot="content" class="list-item-wrap">
                        <template v-for="(item, index) in searchResult">
                            <li
                                v-if="!isSubflow || item.hasPermission"
                                :class="['list-item', { selected: getSelectedStatus(item) }]"
                                :key="index"
                                @click="onSelect(item)">
                                <span class="node-name">{{ item.name }}</span>
                                <span v-if="isSubflow" class="view-tpl" @click.stop="onViewSubflow(item)">
                                    <i class="common-icon-box-top-right-corner"></i>
                                </span>
                            </li>
                            <li
                                v-else
                                class="list-item text-permission-disable"
                                :key="item.id"
                                v-cursor
                                @click="onApplyPermission(item)">
                                {{ item.name }}
                            </li>
                        </template>
                        <div class="node-empty" v-if="searchResult.length === 0">
                            <no-data></no-data>
                        </div>
                    </ul>
                </template>
            </template>
            <no-data v-else></no-data>
        </div>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
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
            atomTypeList: {
                type: Object
            },
            isSubflow: {
                type: Boolean,
                default: false
            },
            basicInfo: {
                type: Object
            }
        },
        data () {
            return {
                selectedGroup: 'all', // 标准插件/子流程搜索分组
                searchStr: '',
                searchResult: []
            }
        },
        computed: {
            listData () {
                return this.isSubflow ? this.atomTypeList.subflow.groups : this.atomTypeList.tasknode
            },
            listInPanel () {
                return (this.searchStr === '' && this.selectedGroup === 'all') ? this.listData : this.searchResult
            },
            groupList () {
                const list = []
                list.push({
                    type: 'all',
                    group_name: this.isSubflow ? i18n.t('所有分类') : i18n.t('所有分组')
                })
                this.listData.forEach(item => {
                    list.push({
                        type: item.type,
                        group_name: item.group_name
                    })
                })
                return list
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
            onSelectGroup (val) {
                this.selectedGroup = val
                this.searchInputhandler()
            },
            onClearSearch () {
                this.searchInputhandler()
            },
            searchInputhandler () {
                let listData = this.listData
                const result = []
                if (this.selectedGroup !== 'all') {
                    const list = listData.find(item => item.type === this.selectedGroup)
                    listData = [list]
                }
                if (this.searchStr !== '') {
                    const reg = new RegExp(this.searchStr)
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
                            group.list.forEach(node => {
                                result.push(node)
                            })
                        }
                    })
                }
                this.searchResult = result
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
                    return item.id === this.basicInfo.tpl
                }
                return item.code === this.basicInfo.plugin
            },
            // 查看子流程
            onViewSubflow (tpl) {
                const { href } = this.$router.resolve({
                    name: 'templatePanel',
                    params: {
                        type: 'edit',
                        project_id: tpl.project.id
                    },
                    query: {
                        template_id: tpl.id
                    }
                })
                window.open(href, '_blank')
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
.search-area {
    float: right;
    margin: 16px;
    .select-group {
        float: left;
        width: 220px;
    }
    .search-input {
        float: left;
        margin-left: 10px;
        width: 260px;
    }
}
.list-wrapper {
    height: calc(100vh - 234px);
    border-top: 1px solid #e2e4ed;
    overflow: auto;
    clear: both;
    @include scrollbar;
    .group-collapse {
        .bk-collapse-item {
            border-bottom: 1px solid #e2e4ed;
            /deep/ {
                .bk-collapse-item-header {
                    width: 100%;
                    background: #fafbfd;
                }
                .bk-collapse-item-content {
                    padding: 0;
                }
            }
            &.bk-collapse-item-active {
                /deep/ .bk-collapse-item-header {
                    border-bottom: 1px solid #e2e4ed;
                }
            }
        }
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
.list-item-wrap {
    .list-item {
        padding-left: 38px;
        height: 40px;
        line-height: 40px;
        color: #63656e;
        font-size: 12px;
        border-bottom: 1px solid #e2e4ed;
        cursor: pointer;
        &:last-child {
            border-bottom: none;
        }
        &.selected .node-name {
            color: #3a84ff;
        }
        &:hover {
            color: #3a84ff;
            background: #e1ecff;
        }
        .view-tpl {
            float: right;
            margin-right: 34px;
        }
    }
    .node-empty {
        padding: 20px 0;
    }
}
</style>
