<template>
    <div class="select-panel">
        <p class="title">{{$t('标准运维插件')}}</p>
        <bk-input
            class="search-input"
            v-model.trim="searchStr"
            right-icon="bk-icon icon-search"
            :placeholder="$t('请输入插件名称')"
            :clearable="true"
            data-test-id="templateEdit_form_searchPlugin"
            @input="handleSearchEmpty"
            @clear="handleSearch"
            @enter="handleSearch">
        </bk-input>
        <div class="plugin-wrap">
            <div class="left-wrap">
                <bk-tab
                    :active="curTab"
                    type="unborder-card"
                    :label-height="42"
                    @tab-change="onTabChange">
                    <bk-tab-panel name="builtIn" :label="$t('内置插件')"></bk-tab-panel>
                    <bk-tab-panel name="thirdParty" :label="$t('第三方插件')"></bk-tab-panel>
                </bk-tab>
                <!--内置插件分类-->
                <div v-if="curTab === 'builtIn' && builtInPluginGroup.length > 0" class="group-area">
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
                        <span class="group-name" v-html="group.group_name" v-bk-overflow-tips></span>
                        <span class="count">{{ group.list.length }}</span>
                    </div>
                </div>
                <!--第三方插件分类-->
                <div
                    v-if="curTab === 'thirdParty' && isThirdPartyGroupShow"
                    class="group-area"
                    v-bkloading="{ isLoading: thirdPluginTagsLoading || thirdPluginLoading }">
                    <template v-for="group in thirdPluginGroup">
                        <div
                            :class="['group-item', {
                                active: group.id === thirdActiveGroup
                            }]"
                            v-if="group.isShow"
                            :key="group.id"
                            :data-test-id="`templateEdit_thirdList_${group.id}`"
                            @click="onSelectThirdGroup(group.id)">
                            <span class="group-name" v-html="group.name" v-bk-overflow-tips></span>
                        </div>
                    </template>
                </div>
            </div>
            <div class="right-wrap" v-bkloading="{ isLoading: thirdPluginTagsLoading || thirdPluginLoading }">
                <p
                    v-if="bkPluginDevelopUrl"
                    class="plugin-dev-doc"
                    @click="jumpToPluginDev">
                    {{ $t('找不到想要的插件？可以尝试自己动手开发！') }}
                </p>
                <!--内置插件列表-->
                <div
                    v-show="curTab === 'builtIn' && builtInPluginGroup.length > 0 && activeGroupPlugin.length > 0"
                    class="selector-area"
                    ref="selectorArea">
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
                </div>
                <!--第三方插件列表-->
                <div
                    v-show="curTab === 'thirdParty' && thirdPartyPlugin.length > 0"
                    class="third-party-list">
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
                </div>
                <NoData
                    v-if="isNoDataShow"
                    :type="searchStr ? 'search-empty' : 'empty'"
                    :message="searchStr ? $t('搜索结果为空') : ''"
                    @searchClear="handleSearch('')">
                </NoData>
            </div>
        </div>
    </div>
</template>
<script>
    import { SYSTEM_GROUP_ICON } from '@/constants/index.js'
    import NoData from '@/components/common/base/NoData.vue'
    import CancelRequest from '@/api/cancelRequest.js'

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
                thirdActiveGroup: '',
                thirdPluginGroup: [],
                thirdPluginTagsLoading: false,
                thirdPluginLoading: false,
                thirdPluginPageLimit: 15,
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
            },
            isThirdPartyGroupShow () {
                return this.thirdPluginGroup && this.thirdPluginGroup.some(item => item.isShow)
            },
            isNoDataShow () {
                let isShow = false
                if (this.curTab === 'builtIn') {
                    isShow = !this.builtInPluginGroup.length || !this.activeGroupPlugin.length
                } else {
                    isShow = !this.thirdPartyPlugin.length
                }
                return isShow
            }
        },
        async mounted () {
            if (this.isThirdParty) {
                await this.getThirdPluginGroup()
                this.setThirdParScrollLoading()
            }
        },
        beforeDestroy () {
            const listWrapEl = document.querySelector('.third-party-list')
            listWrapEl && listWrapEl.removeEventListener('scroll', this.handleThirdParPluginScroll, false)
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
                try {
                    this.thirdPluginLoading = true
                    const source = new CancelRequest()
                    // 搜索时拉取全量插件列表
                    const params = {
                        fetch_all: this.searchStr ? true : undefined,
                        limit: this.thirdPluginPageLimit,
                        offset: this.thirdPluginOffset,
                        search_term: this.searchStr || undefined,
                        exclude_not_deployed: true,
                        tag_id: this.thirdActiveGroup || undefined,
                        cancelToken: source.token
                    }
                    const resp = await this.$store.dispatch('atomForm/loadPluginServiceList', params)
                    const { next_offset, plugins, return_plugin_count } = resp.data
                    const searchStr = this.escapeRegExp(this.searchStr)
                    const reg = new RegExp(searchStr, 'i')
                    const pluginTagIds = []
                    let pluginList = plugins.map(item => {
                        const pluginItem = Object.assign({}, item.plugin, item.profile)
                        if (this.searchStr !== '') {
                            pluginItem.highlightName = item.plugin.name.replace(reg, `<span style="color: #ff9c01;">${this.searchStr}</span>`)
                            pluginTagIds.push(item.profile.tag || -1)
                        }
                        return pluginItem
                    })
                    if (this.searchStr) {
                        // 当第三方插件搜索时，反向映射插件分类
                        this.thirdPluginGroup.forEach(group => {
                            if (pluginTagIds.includes(group.id)) {
                                group.isShow = true
                                if (!this.thirdActiveGroup) {
                                    this.thirdActiveGroup = group.id
                                }
                            }
                        })
                        pluginList = pluginList.filter(item => this.thirdActiveGroup === (item.tag || -1))
                    }
                    this.thirdPluginOffset = return_plugin_count ? next_offset : 0
                    this.thirdPartyPlugin.push(...pluginList)
                    if (next_offset === -1 || return_plugin_count < this.thirdPluginPageLimit) {
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
                const listWrapEl = document.querySelector('.third-party-list')
                listWrapEl.addEventListener('scroll', this.handleThirdParPluginScroll, false)
                const height = listWrapEl.getBoundingClientRect().height

                // 计算出每页加载的条数
                // 规则为容器高度除以每条的高度，考虑到后续可能需要触发容器滚动事件，在实际可容纳的条数上再增加1条
                // @notice: 每个流程条目的高度需要固定，目前取的css定义的高度80px
                if (height > 0) {
                    this.thirdPluginPageLimit = Math.ceil(height / 80) + 1
                }
                this.getThirdPartyPlugin()
            },
            // 滚动加载逻辑
            handleThirdParPluginScroll (e) {
                if (this.thirdPluginLoading || this.isThirdPluginCompleteLoading) {
                    return
                }
                const { scrollTop, clientHeight, scrollHeight } = e.target
                if (scrollHeight - scrollTop - clientHeight < 10) {
                    this.getThirdPartyPlugin()
                }
            },
            // 切换tab
            async onTabChange (val) {
                this.curTab = val
                // 获取第三方插件分组
                if (!this.thirdPluginGroup.length) {
                    await this.getThirdPluginGroup()
                }
                // 切换tab时需要重新搜索
                this.handleSearch(this.searchStr)
                // 监听滚动
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
                    // 搜索时清空插件分类，由插件列表反向映射插件分类
                    this.thirdPluginGroup.forEach(item => {
                        item.isShow = !val
                    })
                    this.thirdActiveGroup = val ? '' : this.thirdPluginGroup[0]?.id
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
            // 获取第三方插件分组
            async getThirdPluginGroup () {
                try {
                    this.thirdPluginTagsLoading = true
                    let tagId = ''
                    // 插件重选时，选择对应的分类id
                    if (this.isThirdParty && this.crtPlugin) {
                        const pluginInfo = await this.$store.dispatch('atomForm/loadPluginServiceAppDetail', { plugin_code: this.crtPlugin })
                        const tagInfo = pluginInfo.data.tag_info
                        tagId = tagInfo ? tagInfo.id : -1
                    }
                    const resp = await this.$store.dispatch('atomForm/getThirdPluginTags')
                    if (resp.result) {
                        this.thirdActiveGroup = tagId || (this.searchStr ? '' : resp.data[0].id)
                        this.thirdPluginGroup = resp.data.map(item => {
                            return { ...item, isShow: true }
                        })
                    }
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.thirdPluginTagsLoading = false
                }
            },
            // 选中第三方插件分组
            onSelectThirdGroup (val) {
                this.thirdActiveGroup = val
                this.thirdPartyPlugin = []
                this.isThirdPluginCompleteLoading = false
                this.thirdPluginOffset = 0
                this.getThirdPartyPlugin()
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
                        plugin_contact: plugin.contact,
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
@import '@/scss/mixins/scrollbar.scss';
.select-panel {
    position: absolute;
    top: -54px;
    left: -615px;
    width: 600px;
    height: 790px;
    background: #fff;
    box-shadow: 0 0 4px 0 #0000004d;
    z-index: 2;
    .title {
        font-size: 14px;
        line-height: 22px;
        color: #63656e;
        font-weight: 700;
        margin: 21px 24px;
    }
    .search-input {
        position: absolute;
        top: 16px;
        right: 20px;
        width: 180px;
    }
    .plugin-wrap {
        position: relative;
        display: flex;
        height: calc(100% - 64px);
        background: #fff;
    }
    .left-wrap {
        width: 214px;
        background: #f5f7fa;
        border-radius: 0 2px 0 0;
        /deep/.bk-tab {
            .bk-tab-label-wrapper {
                margin-left: 0 !important;
            }
            .bk-tab-section {
                padding: 0;
            }
        }
        .group-area {
            height: calc(100% - 42px);
            width: 100%;
            padding-top: 16px;
            overflow: auto;
            @include scrollbar;
            .group-item {
                position: relative;
                display: flex;
                align-items: center;
                height: 40px;
                padding: 0 16px 0 24px;
                font-size: 14px;
                color: #63656e;
                cursor: pointer;
                i {
                    flex-shrink: 0;
                    font-size: 16px;
                    color: #979ba5;
                    margin: 2px 4px 0 0;
                }
                .group-name {
                    flex: 1;
                    line-height: 22px;
                    padding-right: 5px;
                    overflow: hidden;
                    white-space: nowrap;
                    text-overflow: ellipsis;
                }
                .count {
                    flex-shrink: 0;
                    padding: 0 8px;
                    line-height: 16px;
                    font-size: 12px;
                    color: #979ba5;
                    background: #f0f1f5;
                    border-radius: 2px;
                }
                &:hover {
                    background: #eaebf0;
                }
                &.active {
                    color: #3a84ff;
                    background: #ffffff;
                    .count {
                        color: #fff;
                        background: #a3c5fd;
                    }
                    &::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 0;
                        display: inline-block;
                        width: 3px;
                        height: 40px;
                        background: #3a84ff;
                    }
                }
            }
        }
    }
    .right-wrap {
        flex: 1;
        margin-left: 8px;
        .plugin-dev-doc {
            position: absolute;
            right: 15px;
            top: 15px;
            z-index: 2;
            font-size: 12px;
            color: #3a84ff;
            cursor: pointer;
        }
        .selector-area {
            height: 100%;
            font-size: 12px;
            color: #63656e;
            border-radius: 2px;
            overflow: auto;
            @include scrollbar;
            .list-item {
                height: 32px;
                width: 100%;
                line-height: 32px;
                padding: 0 16px;
                border-radius: 2px;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
                cursor: pointer;
                &:hover {
                    background: #fafbfd;
                }
                &.active {
                    color: #3a84ff;
                    background: #e1ecff;
                }
            }
        }
        .third-party-list {
            height: 100%;
            overflow: auto;
            @include scrollbar;
            .plugin-item {
                display: flex;
                position: relative;
                height: 78px;
                line-height: 18px;
                padding: 10px 18px 10px 12px;
                color: #63656e;
                font-size: 12px;
                cursor: pointer;
                .plugin-logo {
                    width: 56px;
                    height: 56px;
                    margin-right: 12px;
                    flex-shrink: 0;
                }
                .plugin-title {
                    font-weight: 700;
                    margin-bottom: 4px;
                }
                .plugin-desc {
                    width: 274px;
                    display: -webkit-box;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    word-break: break-all;
                    -webkit-line-clamp: 2;
                    -webkit-box-orient: vertical;
                }
                .plugin-contact {
                    position: absolute;
                    top: 10px;
                    right: 24px;
                    display: none;
                    color: #979ba5;
                    line-height: 20px;
                }
                &:hover {
                    background: #fafbfd;
                    .plugin-contact {
                        display: block;
                    }
                }
                &.is-active {
                    background: #e1ecff;
                    .plugin-title {
                        color: #3a84ff;
                    }
                    .plugin-contact {
                        display: block;
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
        .no-data-wrapper {
            margin-top: 50px;
        }
    }
    &::before {
        background: #fff;
        border-color: #ebf0f5 #ebf0f5 #fff #fff;
        border-style: solid;
        border-width: 1px;
        content: "";
        display: block;
        height: 6px;
        position: absolute;
        right: -4px;
        top: 140px;
        transform: rotate(45deg);
        width: 6px;
    }
}
</style>
