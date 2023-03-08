<template>
    <bk-tab
        :active="curTab"
        type="unborder-card"
        @tab-change="onTabChange">
        <bk-input
            class="search-input"
            v-model.trim="searchStr"
            right-icon="bk-icon icon-search"
            :placeholder="$t('请输入插件名称')"
            :clearable="true"
            data-test-id="templateEdit_form_searchPlugin"
            @change="handleSearchEmpty"
            @clear="handleSearch"
            @enter="handleSearch">
        </bk-input>
        <p
            v-if="bkPluginDevelopUrl"
            class="plugin-dev-doc"
            @click="jumpToPluginDev">
            {{ $t('找不到想要的插件？可以尝试自己动手开发！') }}
        </p>
        <!-- 内置插件 -->
        <bk-tab-panel name="builtIn" :label="$t('内置插件')">
            <template v-if="builtInPluginGroup.length > 0">
                <div class="group-area">
                    <div
                        :class="['group-item', {
                            active: group.type === activeGroup
                        }]"
                        v-for="group in builtInPluginGroup"
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
                            :class="['list-item', { active: item.code === crtPlugin }]"
                            :key="index"
                            :title="item.name"
                            :data-test-id="`templateEdit_list_${item.code.replace(/_(\w)/g, (strMatch, p1) => p1.toUpperCase())}`"
                            @click="$emit('select', item)">
                            <span class="node-name" v-if="item.highlightName" v-html="item.highlightName"></span>
                            <span class="node-name" v-else>{{ item.name }}</span>
                        </li>
                    </template>
                    <NoData
                        v-else
                        :type="searchStr ? 'search-empty' : 'empty'"
                        :message="searchStr ? $t('搜索结果为空') : ''"
                        @searchClear="handleSearch('')">
                    </NoData>
                </div>
            </template>
            <NoData
                v-else
                :type="searchStr ? 'search-empty' : 'empty'"
                :message="searchStr ? $t('搜索结果为空') : ''"
                @searchClear="handleSearch('')">
            </NoData>
        </bk-tab-panel>
        <!-- 第三方插件 -->
        <bk-tab-panel
            ref="thirdPartyPanel"
            name="thirdParty"
            :label="$t('第三方插件')"
            v-bkloading="{ isLoading: thirdPluginLoading }">
            <div class="third-party-list">
                <template v-if="thirdPartyPlugin.length > 0">
                    <div
                        :class="['plugin-item', { 'is-active': plugin.code === crtPlugin }]"
                        v-for="(plugin, index) in thirdPartyPlugin"
                        :key="index"
                        @click="onSelectThirdPartyPlugin(plugin)">
                        <img class="plugin-logo" :src="plugin.logo_url" alt="">
                        <div>
                            <p class="plugin-title" v-if="plugin.highlightName" v-html="plugin.highlightName"></p>
                            <p class="plugin-title" v-else>{{ plugin.name }}</p>
                            <p
                                class="plugin-desc"
                                v-bk-overflow-tips="{ placement: 'bottom-end', extCls: 'plugin-desc-tips' }">
                                {{ plugin.introduction || '--' }}
                            </p>
                            <p class="plugin-contact">{{ $t('由') + ' ' + plugin.contact + ' ' + $t('提供') }}</p>
                        </div>
                    </div>
                </template>
                <NoData
                    v-else
                    :type="searchStr ? 'search-empty' : 'empty'"
                    :message="searchStr ? $t('搜索结果为空') : ''"
                    @searchClear="handleSearch('')">
                </NoData>
            </div>
        </bk-tab-panel>
    </bk-tab>
</template>
<script>
    import { SYSTEM_GROUP_ICON } from '@/constants/index.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'Plugin',
        components: {
            NoData
        },
        props: {
            isThirdParty: Boolean,
            crtPlugin: String,
            builtInPlugin: {
                type: Array,
                default: () => ([])
            }
        },
        data () {
            return {
                curTab: this.isThirdParty ? 'thirdParty' : 'builtIn',
                builtInPluginGroup: this.builtInPlugin.slice(0),
                activeGroup: this.getDefaultActiveGroup(),
                thirdPartyPlugin: [],
                thirdPluginLoading: false,
                thirdPluginPagelimit: 15,
                isThirdPluginCompleteLoading: false,
                thirdPluginOffset: 0,
                searchStr: '',
                bkPluginDevelopUrl: window.BK_PLUGIN_DEVELOP_URL
            }
        },
        computed: {
            activeGroupPlugin () {
                const group = this.builtInPluginGroup.find(item => item.type === this.activeGroup)
                return group ? group.list : []
            }
        },
        mounted () {
            if (this.isThirdParty) {
                this.setThirdParScrollLoading()
            }
        },
        beforeDestroy () {
            const listWrapEl = this.$refs.thirdPartyPanel.$el.querySelector('.third-party-list')
            listWrapEl.removeEventListener('scroll', this.handleThirdParPluginScroll, false)
        },
        methods: {
            // 获取内置插件默认展开的分组，没有选择展开第一组，已选择展开选中的那组
            getDefaultActiveGroup () {
                let activeGroup = ''
                if (this.crtPlugin && !this.isThirdParty) {
                    this.builtInPlugin.some(group => {
                        if (group.list.find(item => item.code === this.crtPlugin)) {
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
                if (this.thirdPluginLoading) {
                    return
                }
                try {
                    this.thirdPluginLoading = true
                    const params = {
                        limit: this.thirdPluginPagelimit,
                        offset: this.thirdPluginOffset,
                        search_term: this.searchStr,
                        exclude_not_deployed: true
                    }
                    const resp = await this.$store.dispatch('atomForm/loadPluginServiceList', params)
                    const { next_offset, plugins, return_plugin_count } = resp.data
                    const searchStr = this.escapeRegExp(this.searchStr)
                    const reg = new RegExp(searchStr, 'i')
                    const pluginList = plugins.map(item => {
                        const pluginItem = Object.assign({}, item.plugin, item.profile)
                        if (this.searchStr !== '') {
                            pluginItem.highlightName = item.plugin.name.replace(reg, `<span style="color: #ff9c01;">${this.searchStr}</span>`)
                        }
                        return pluginItem
                    })
                    this.thirdPluginOffset = return_plugin_count ? next_offset : 0
                    this.thirdPartyPlugin.push(...pluginList)
                    if (return_plugin_count < this.thirdPluginPagelimit) {
                        this.isThirdPluginCompleteLoading = true
                    }
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.thirdPluginLoading = false
                }
            },
            // 设置第三方插件滚动加载事件
            setThirdParScrollLoading () {
                // 设置滚动加载
                const listWrapEl = this.$refs.thirdPartyPanel.$el.querySelector('.third-party-list')
                listWrapEl.addEventListener('scroll', this.handleThirdParPluginScroll, false)
                const height = listWrapEl.getBoundingClientRect().height

                // 计算出每页加载的条数
                // 规则为容器高度除以每条的高度，考虑到后续可能需要触发容器滚动事件，在实际可容纳的条数上再增加1条
                // @notice: 每个流程条目的高度需要固定，目前取的css定义的高度80px
                if (height > 0) {
                    this.thirdPluginPagelimit = Math.ceil(height / 80) + 1
                }
                this.getThirdPartyPlugin()
            },
            // 滚动加载逻辑
            handleThirdParPluginScroll (e) {
                if (this.thirdPluginLoading || this.isThirdPluginCompleteLoading) {
                    return
                }
                const { scrollTop, clientHeight, scrollHeight } = e.target
                const isScrollBottom = scrollHeight === (scrollTop + clientHeight)
                if (isScrollBottom) {
                    this.getThirdPartyPlugin()
                }
            },
            // 切换tab
            onTabChange (val) {
                this.curTab = val
                this.searchStr = ''
                console.log(this.thirdPartyPlugin, this.thirdPluginOffset)
                if (this.thirdPartyPlugin.length === 0 && this.thirdPluginOffset === 0) {
                    this.$nextTick(() => {
                        this.setThirdParScrollLoading()
                    })
                }
            },
            // 搜索框字符为空
            handleSearchEmpty (val) {
                if (val === '') {
                    this.handleSearch('')
                }
            },
            // 搜索逻辑
            handleSearch (val) {
                this.searchStr = val
                if (this.curTab === 'builtIn') {
                    this.setBuiltInPluginSearchResult(val)
                } else {
                    this.thirdPartyPlugin = []
                    this.thirdPluginOffset = 0
                    this.getThirdPartyPlugin()
                }
            },
            // 内置插件本地搜索
            setBuiltInPluginSearchResult (val) {
                let result = []
                if (val === '') {
                    result = this.builtInPlugin.slice(0)
                    this.activeGroup = this.getDefaultActiveGroup()
                } else {
                    const searchStr = this.escapeRegExp(val)
                    const reg = new RegExp(searchStr, 'i')
                    this.builtInPlugin.forEach(group => {
                        const { group_icon, group_name, type } = group
                        const list = []

                        if (reg.test(group_name)) { // 分组名称匹配
                            const hglGroupName = group_name.replace(reg, `<span style="color: #ff9c01;">${val}</span>`)
                            result.push({
                                ...group,
                                group_name: hglGroupName
                            })
                        } else if (group.list.length > 0) { // 单个插件或者子流程名称匹配
                            group.list.forEach(item => {
                                if (reg.test(item.name)) {
                                    const node = { ...item }
                                    node.highlightName = item.name.replace(reg, `<span style="color: #ff9c01;">${val}</span>`)
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
                this.builtInPluginGroup = result
            },
            escapeRegExp (str) {
                if (typeof str !== 'string') {
                    return ''
                }
                return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, '\\$&')
            },
            // 跳转到第三方插件开发稳单
            jumpToPluginDev () {
                window.open(this.bkPluginDevelopUrl, '_blank')
            },
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
.search-input {
    position: absolute;
    top: -46px;
    right: 20px;
    width: 300px;
}
.plugin-dev-doc {
    position: absolute;
    right: 15px;
    top: 15px;
    z-index: 2;
    font-size: 12px;
    color: #3a84ff;
    cursor: pointer;
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
.no-data-wrapper {
    margin-top: 50px;
}
</style>
