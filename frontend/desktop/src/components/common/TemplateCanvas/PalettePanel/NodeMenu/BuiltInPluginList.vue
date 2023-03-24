<template>
    <div class="built-in-plugin-list">
        <div class="search-wrap">
            <template v-if="isSelectGroupMode">
                <bk-select
                    style="width: 225px;"
                    ext-popover-cls="node-menu-panel-popover"
                    :clearable="true"
                    :searchable="true"
                    @clear="handleSelectedGroupClear"
                    @selected="handleSelectGroup">
                    <bk-option
                        v-for="item in builtInPlugins"
                        class="node-item-option"
                        :key="item.type"
                        :id="item.type"
                        :name="item.group_name">
                    </bk-option>
                </bk-select>
                <div class="thumb-icon" @click="handleChangeGroupMode(false)">
                    <i class="common-icon-search"></i>
                </div>
            </template>
            <template v-else>
                <div class="thumb-icon" @click="handleChangeGroupMode(true)">
                    <i class="common-icon-arrow-down"></i>
                </div>
                <bk-input
                    v-model.trim="searchStr"
                    style="width: 225px;"
                    right-icon="bk-icon icon-search"
                    :placeholder="$t('搜索插件')"
                    :clearable="true"
                    @change="handleSearchChange"
                    @clear="handleSearchClear"
                    @enter="handleSearch">
                </bk-input>
            </template>
        </div>
        <div class="plugin-list-wrap">
            <template v-if="!searchMode">
                <bk-collapse v-for="group in pluginList" :key="group.type">
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
                                <node-item class="node-item" type="tasknode" :key="index" :node="node">
                                </node-item>
                            </template>
                            <div class="node-empty" v-if="group.list.length === 0">
                                <NoData
                                    class="exception-part"
                                    :type="searchStr ? 'search-empty' : 'empty'"
                                    :message="searchStr ? $t('搜索结果为空') : ''"
                                    @searchClear="handleSearchClear">
                                </NoData>
                            </div>
                        </div>
                    </bk-collapse-item>
                </bk-collapse>
            </template>
            <div v-else class="search-result">
                <template v-for="(node, index) in pluginList">
                    <node-item class="node-item" type="tasknode" :key="index" :node="node">
                    </node-item>
                </template>
                <NoData
                    v-if="pluginList.length === 0"
                    class="exception-part"
                    :type="searchStr ? 'search-empty' : 'empty'"
                    :message="searchStr ? $t('搜索结果为空') : ''"
                    @searchClear="handleSearchClear">
                </NoData>
            </div>
        </div>
    </div>
</template>
<script>
    import { SYSTEM_GROUP_ICON } from '@/constants/index.js'
    import tools from '@/utils/tools.js'
    import NodeItem from '../NodeItem.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'BuiltInPluginList',
        components: {
            NodeItem,
            NoData
        },
        props: {
            builtInPlugins: {
                type: Array,
                default: () => ([])
            }
        },
        data () {
            return {
                isSelectGroupMode: false,
                pluginList: this.builtInPlugins.slice(0),
                searchMode: false,
                searchStr: ''
            }
        },
        methods: {
            getIconCls (type) {
                const systemType = SYSTEM_GROUP_ICON.find(item => new RegExp(item).test(type))
                if (systemType) {
                    return `common-icon-sys-${systemType.toLowerCase()}`
                }
                return 'common-icon-sys-default'
            },
            // 选择插件分组
            handleSelectGroup (val) {
                this.searchMode = true
                this.searchStr = ''
                this.pluginList = this.builtInPlugins.find(group => group.group_name === val).list.slice(0)
            },
            handleSelectedGroupClear () {
                this.searchMode = false
                this.pluginList = this.builtInPlugins.slice(0)
            },
            // 切换分组搜索和文本搜索
            handleChangeGroupMode (val) {
                this.isSelectGroupMode = val
                this.searchStr = ''
                this.searchMode = false
                this.pluginList = this.builtInPlugins.slice(0)
            },
            // 文本搜索
            handleSearch (val) {
                const result = []
                this.searchMode = true
                if (val !== '') {
                    const searchStr = tools.escapeRegExp(val)
                    const reg = new RegExp(searchStr, 'i')
                    this.builtInPlugins.forEach(group => {
                        if (group.list.length > 0) {
                            group.list.forEach(node => {
                                if (reg.test(node.name)) {
                                    result.push(node)
                                }
                            })
                        }
                    })
                } else {
                    this.builtInPlugins.forEach(group => {
                        if (group.list.length > 0) {
                            result.push(...group.list.map(item => item.list[item.list.length - 1]))
                        }
                    })
                }
                this.pluginList = result
            },
            handleSearchChange (val) {
                if (val === '') {
                    this.handleSearchClear()
                }
            },
            // 清空搜索
            handleSearchClear (val) {
                this.searchStr = ''
                this.searchMode = false
                this.pluginList = this.builtInPlugins.slice(0)
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    .built-in-plugin-list {
        height: 100%;
    }
    .search-wrap {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 11px 14px 12px;
        border-bottom: 1px solid #ccd0dd;
        background: #ffffff;
        .thumb-icon {
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
    }
    .plugin-list-wrap {
        height: calc(100% - 60px);
        overflow: auto;
        @include scrollbar;
    }
    .exception-part {
        margin-top: 100px;
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
