<template>
    <bk-tab
        :active.sync="curTab"
        type="unborder-card"
        @tab-change="onTabChange">
        <!-- 内置插件 -->
        <bk-tab-panel v-bind="{ name: 'built_in', label: $t('内置插件') }">
            <template v-if="builtInPlugin.length > 0">
                <div class="group-area">
                    <div
                        :class="['group-item', {
                            active: group.type === activeGroup
                        }]"
                        v-for="group in builtInPlugin"
                        :key="group.type"
                        :data-test-id="`templateEdit_list_${group.sort_key_group_en}`"
                        @click="onSelectGroup(group.type)">
                        <img v-if="group.group_icon" class="group-icon-img" :src="group.group_icon" />
                        <i v-else :class="['group-icon-font', getIconCls(group.type)]"></i>
                        <span v-html="group.group_name"></span>
                        <span>{{ `(${group.list.length})` }}</span>
                    </div>
                </div>
                <div class="selector-area" ref="selectorArea">
                    <template v-if="activeGroupPlugin.length > 0">
                        <li
                            v-for="(item, index) in activeGroupPlugin"
                            :class="['list-item', { active: item.code === basicInfo.plugin }]"
                            :key="index"
                            :title="item.name"
                            :data-test-id="`templateEdit_list_${item.code.replace(/_(\w)/g, (strMatch, p1) => p1.toUpperCase())}`"
                            @click="$emit('select', item)">
                            <span class="node-name" v-if="item.highlightName" v-html="item.highlightName"></span>
                            <span class="node-name" v-else>{{ item.name }}</span>
                        </li>
                    </template>
                    <bk-exception v-else class="exception-part" type="empty" scene="part"></bk-exception>
                </div>
            </template>
            <bk-exception v-else class="exception-part" type="empty" scene="part"></bk-exception>
        </bk-tab-panel>
        <!-- 第三方插件 -->
        <bk-tab-panel v-bind="{ name: 'third_party', label: $t('第三方插件') }" v-bkloading="{ isLoading: thirdPartyPluginLoading }">
            <ul v-if="thirdPartyPlugin.length" class="third-party-list">
                <li
                    :class="['plugin-item', { 'is-active': plugin.code === basicInfo.plugin }]"
                    v-for="(plugin, index) in thirdPartyPlugin"
                    :key="index"
                    @click="onSelectThirdPartyPlugin(plugin)">
                    <img class="plugin-logo" :src="plugin.logo_url" alt="">
                    <div>
                        <p class="plugin-title">{{ plugin.name }}</p>
                        <p
                            class="plugin-desc"
                            v-bk-overflow-tips="{ placement: 'bottom-end', extCls: 'plugin-desc-tips' }">
                            {{ plugin.introduction || '--' }}
                        </p>
                        <p class="plugin-contact">{{ $t('由') + ' ' + plugin.contact + ' ' + $t('提供') }}</p>
                    </div>
                </li>
            </ul>
            <bk-exception v-else class="exception-part" type="empty" scene="part"></bk-exception>
        </bk-tab-panel>
    </bk-tab>
</template>
<script>
    import { SYSTEM_GROUP_ICON } from '@/constants/index.js'

    export default {
        name: 'Plugin',
        components: {
            // NoData
        },
        props: {
            basicInfo: Object,
            builtInPlugin: {
                type: Array,
                default: () => ([])
            }
        },
        data () {
            return {
                curTab: 'built_in',
                activeGroup: this.getDefaultActiveGroup(),
                thirdPartyPlugin: [],
                thirdPartyPluginLoading: false,
                pluginOffset: 0,
                searchStr: ''
            }
        },
        computed: {
            activeGroupPlugin () {
                const group = this.builtInPlugin.find(item => item.type === this.activeGroup)
                return group ? group.list : []
            }
        },
        created () {
            this.getThirdPartyPlugin()
        },
        methods: {
            // 获取内置插件默认展开的分组，没有选择展开第一组，已选择展开选中的那组
            getDefaultActiveGroup () {
                let activeGroup = ''
                if (this.basicInfo.plugin) {
                    this.builtInPlugin.some(group => {
                        if (group.list.find(item => item.code === this.basicInfo.plugin)) {
                            activeGroup = group.type
                            return true
                        }
                    })
                } else {
                    if (this.builtInPlugin.length > 0) {
                        activeGroup = this.builtInPlugin[0].type
                    }
                }
                return activeGroup
            },
            // 内置插件分组icon classname
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
            // 加载第三方插件列表
            async getThirdPartyPlugin () {
                if (this.thirdPartyPluginLoading) {
                    return
                }
                try {
                    this.thirdPartyPluginLoading = true
                    const limit = 12
                    const params = {
                        limit,
                        offset: this.pluginOffset,
                        search_term: this.searchStr,
                        exclude_not_deployed: true
                    }
                    const resp = await this.$store.dispatch('atomForm/loadPluginServiceList', params)
                    const { next_offset, plugins, return_plugin_count } = resp.data
                    const pluginList = plugins.map(item => {
                        return Object.assign({}, item.plugin, item.profile)
                    })
                    if (return_plugin_count < limit) {
                        this.thirdPartyPlugin = pluginList
                    } else {
                        this.thirdPartyPlugin.push(...pluginList)
                    }
                    this.pluginOffset = next_offset
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.thirdPartyPluginLoading = false
                }
            },
            // 切换tab
            onTabChange () {},
            // 选择内置插件分组
            onSelectGroup (val) {
                this.activeGroup = val
                this.$refs.selectorArea.scrollTop = 0
            },
            async onSelectThirdPartyPlugin (plugin) {
                try {
                    const resp = await this.$store.dispatch('atomForm/loadPluginServiceMeta', { plugin_code: plugin.code })
                    const { code, versions, description } = resp.data
                    const versionList = versions.sort().map(version => {
                        return { version }
                    })
                    const data = {
                        code,
                        name: plugin.name,
                        list: versionList,
                        desc: description,
                        id: 'remote_plugin'
                    }
                    this.$emit('select', data)
                } catch (error) {
                    console.warn(error)
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.bk-tab {
    >>> .bk-tab-section {
        padding: 0;
        .bk-tab-content {
            height: calc(100vh - 110px);
            overflow: hidden;
        }
    }
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
.third-party-list {
    height: calc(100vh - 110px);
    overflow: auto;
    @include scrollbar;
    .plugin-item {
        height: 80px;
        display: flex;
        align-items: center;
        cursor: pointer;
        padding: 0 59px 0 38px;
        color: #63656e;
        font-size: 12px;
        .plugin-logo {
            width: 48px;
            height: 48px;
            margin-right: 16px;
            flex-shrink: 0;
        }
        .plugin-title {
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .plugin-desc {
            width: 645px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }
        .plugin-contact {
            color: #c4c6cc;
            font-weight: 700;
        }
        &.is-active, &:hover {
            background: hsl(218, 100%, 94%);
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
.exception-part {
    margin-top: 100px;
}
</style>
