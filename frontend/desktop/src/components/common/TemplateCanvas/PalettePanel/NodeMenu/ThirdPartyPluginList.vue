<template>
    <div class="third-party-plugin-list" ref="thirdPartyPluginPanel">
        <div class="search-wrap">
            <bk-input
                style="width: 100%;"
                v-model.trim="searchStr"
                right-icon="bk-icon icon-search"
                :placeholder="$t('搜索插件')"
                :clearable="true"
                @change="handleSearchChange"
                @clear="handleSearchClear"
                @enter="handleSearch">
            </bk-input>
        </div>
        <div class="plugin-list-wrap" v-bkloading="{ isLoading: pluginListLoading }">
            <div class="plugin-list">
                <node-item
                    v-for="plugin in pluginList"
                    class="node-item"
                    type="tasknode"
                    :key="plugin.id"
                    :node="{
                        plugin_type: 'third-praty',
                        code: 'remote_plugin',
                        template_id: tplId,
                        name: plugin.code,
                        desc: plugin.introduction,
                        group_icon: '',
                        group_name: '',
                        nodeName: plugin.name,
                        logo_url: plugin.logo_url
                    }">
                </node-item>
                <NoData
                    v-if="pluginList.length === 0"
                    :type="searchStr ? 'search-empty' : 'empty'"
                    :message="searchStr ? $t('搜索结果为空') : ''"
                    @searchClear="handleSearchClear">
                </NoData>
            </div>
        </div>
    </div>
</template>
<script>
    import NodeItem from '../NodeItem.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'ThirdPartyPluginList',
        components: {
            NodeItem,
            NoData
        },
        data () {
            return {
                tplId: this.$route.query.template_id,
                pluginList: [],
                pluginListLoading: false,
                pagelimit: 15, // 默认值
                pluginPageOffset: 0,
                isCompleteLoading: false,
                searchStr: ''
            }
        },
        mounted () {
            // 设置滚动加载
            const listWrapEl = this.$refs.thirdPartyPluginPanel.querySelector('.plugin-list')
            listWrapEl.addEventListener('scroll', this.handleScrollLoading, false)
            const height = listWrapEl.getBoundingClientRect().height

            // 计算出每页加载的条数
            // 规则为容器高度除以每条的高度，考虑到后续可能需要触发容器滚动事件，在实际可容纳的条数上再增加1条
            // @notice: 每个流程条目的高度需要固定，目前取的css定义的高度70px
            if (height > 0) {
                this.pagelimit = Math.ceil(height / 70) + 1
            }
            this.getPluginList()
        },
        beforeDestroy () {
            const listWrapEl = this.$refs.thirdPartyPluginPanel.querySelector('.plugin-list')
            listWrapEl.removeEventListener('scroll', this.handleScrollLoading, false)
        },
        methods: {
            async getPluginList () {
                if (this.pluginListLoading) {
                    return
                }
                try {
                    this.pluginListLoading = true
                    const params = {
                        limit: this.pagelimit,
                        offset: this.pluginPageOffset,
                        search_term: this.searchStr,
                        exclude_not_deployed: true
                    }
                    const resp = await this.$store.dispatch('atomForm/loadPluginServiceList', params)
                    const { next_offset, plugins, return_plugin_count } = resp.data
                    const list = plugins.map(item => {
                        return Object.assign({}, item.plugin, item.profile)
                    })
                    this.pluginPageOffset = next_offset
                    this.pluginList.push(...list)
                    this.isCompleteLoading = return_plugin_count < this.pagelimit
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.pluginListLoading = false
                }
            },
            // 滚动加载逻辑
            handleScrollLoading (e) {
                if (this.pluginListLoading || this.isCompleteLoading) {
                    return
                }
                const { scrollTop, clientHeight, scrollHeight } = e.target
                const isScrollBottom = scrollHeight === (scrollTop + clientHeight)
                if (isScrollBottom) {
                    this.getPluginList()
                }
            },
            handleSearchChange (val) {
                if (val === '') {
                    this.handleSearchClear()
                }
            },
            handleSearchClear () {
                this.searchStr = ''
                this.handleSearch()
            },
            handleSearch (val) {
                this.pluginList = []
                this.pluginPageOffset = 0
                this.getPluginList()
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
.third-party-plugin-list {
    height: 100%;
}
.search-wrap {
    padding: 12px 11px 14px 12px;
    border-bottom: 1px solid #ccd0dd;
    background: #ffffff;
}
.plugin-list-wrap {
    height: calc(100% - 60px);
    .plugin-list {
        height: 100%;
        overflow: auto;
        @include scrollbar;
    }
}
</style>
