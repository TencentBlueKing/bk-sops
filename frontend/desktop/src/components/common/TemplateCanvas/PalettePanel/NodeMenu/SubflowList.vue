<template>
    <div class="subflow-list-panel" ref="subflowListPanel">
        <div class="search-wrap">
            <!-- 公共流程没有标签搜索 -->
            <template v-if="!common && isFilterLabelMode">
                <bk-select
                    v-model="labels"
                    ext-cls="label-select"
                    ext-popover-cls="label-select node-menu-panel-popover"
                    :placeholder="$t('请选择标签')"
                    :display-tag="true"
                    :multiple="true"
                    :clearable="true"
                    :searchable="true"
                    @clear="handleSearch"
                    @change="handleSearch">
                    <bk-option
                        v-for="(item, index) in templateLabels"
                        :key="index"
                        :id="item.id"
                        :name="item.name">
                        <div class="label-select-option">
                            <span
                                class="label-select-color"
                                :style="{ background: item.color }">
                            </span>
                            <span>{{item.name}}</span>
                            <i v-if="labels.includes(item.id)" class="bk-option-icon bk-icon icon-check-1"></i>
                        </div>
                    </bk-option>
                </bk-select>
                <div class="thumb-icon" @click="handleChangeSearchMode('text')">
                    <i class="common-icon-search"></i>
                </div>
            </template>
            <template v-else>
                <div v-if="!common" class="thumb-icon" @click="handleChangeSearchMode('label')">
                    <i class="common-icon-arrow-down"></i>
                </div>
                <bk-input
                    v-model.trim="searchStr"
                    :style="`width: ${common ? '100%' : '225px'};`"
                    right-icon="bk-icon icon-search"
                    :placeholder="$t('请输入流程名称')"
                    :clearable="true"
                    @paste="handleTestSearchPaste"
                    @change="handleTextSearchChange"
                    @clear="handleTextSearchClear"
                    @enter="handleSearch">
                </bk-input>
            </template>
        </div>
        <div class="tpl-list-wrap" v-bkloading="{ isLoading: listLoading }">
            <div class="tpl-list">
                <template v-for="tpl in tableList">
                    <node-item
                        v-if="tpl.hasPermission"
                        class="node-item"
                        type="subflow"
                        :key="tpl.id"
                        :node="tpl">
                    </node-item>
                    <div v-else class="node-item" :key="tpl.id">
                        <div
                            v-cursor
                            class="name-wrapper text-permission-disable"
                            @click="onApplyPermission(tpl)">
                            {{ tpl.name }}
                        </div>
                    </div>
                </template>
                <NoData
                    v-if="tableList.length === 0"
                    class="exception-part"
                    :type="(labels.length || searchStr) ? 'search-empty' : 'empty'"
                    :message="(labels.length || searchStr) ? $t('搜索结果为空') : ''"
                    @searchClear="handleTextSearchClear">
                </NoData>
            </div>
        </div>
    </div>
</template>
<script>
    import permission from '@/mixins/permission.js'
    import tools from '@/utils/tools.js'
    import NodeItem from '../NodeItem.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'SubflowList',
        components: {
            NodeItem,
            NoData
        },
        mixins: [permission],
        props: {
            common: Boolean, // 是否为公共流程列表
            isShow: Boolean,
            templateLabels: Array
        },
        data () {
            return {
                isFilterLabelMode: !this.common,
                tplList: [],
                listLoading: false,
                labels: [],
                searchStr: '',
                limit: 20,
                crtPage: 1,
                isCompleteLoading: false
            }
        },
        computed: {
            tableList () {
                // 除流程克隆的情况，流程列表中需要过滤掉url中template_id对应的流程
                if (this.$route.params.type === 'clone') {
                    return this.tplList
                }
                return this.tplList.filter(tpl => {
                    return tpl.id !== Number(this.$route.query.template_id)
                })
            }
        },
        watch: {
            isShow (val) {
                if (val) {
                    if (this.crtPage === 1 && this.tplList.length === 0) {
                        this.setScrollLoading()
                    }
                }
            }
        },
        mounted () {
            if (this.isShow) {
                this.setScrollLoading()
            }
        },
        beforeDestroy () {
            const listWrapEl = this.$refs.subflowListPanel.querySelector('.tpl-list')
            listWrapEl.removeEventListener('scroll', this.handleScroll, false)
        },
        methods: {
            // 加载项目流程或公共流程列表
            async getTplList () {
                if (this.listLoading) {
                    return
                }
                try {
                    this.listLoading = true
                    const searchStr = tools.escapeRegExp(this.searchStr)
                    const data = {
                        label_ids: this.labels.join(','),
                        pipeline_template__name__icontains: searchStr || undefined,
                        limit: this.limit,
                        offset: (this.crtPage - 1) * this.limit
                    }
                    if (this.common) {
                        data.common = true
                    } else {
                        data.project__id = this.$route.params.project_id
                    }
                    const resp = await this.$store.dispatch('templateList/loadTemplateList', data)
                    const reqPermission = this.common ? ['common_flow_view'] : ['flow_view']
                    const results = []
                    resp.results.forEach(tpl => {
                        tpl.hasPermission = this.hasPermission(reqPermission, tpl.auth_actions)
                        tpl.tplSource = this.common ? 'common' : 'business'
                        const tplCopy = { ...tpl }
                        // 高亮搜索匹配的文字部分
                        if (searchStr !== '') {
                            const reg = new RegExp(searchStr, 'i')
                            if (reg.test(tpl.name)) {
                                tplCopy.highlightName = tplCopy.name.replace(reg, `<span style="color: #ff5757;">${searchStr}</span>`)
                            }
                        }
                        results.push(tplCopy)
                    })
                    this.tplList.push(...results)
                    this.isCompleteLoading = resp.count === this.tplList.length
                } catch (e) {
                    console.log(e)
                } finally {
                    this.listLoading = false
                }
            },
            setScrollLoading () {
                // 设置滚动加载
                const listWrapEl = this.$refs.subflowListPanel.querySelector('.tpl-list')
                listWrapEl.addEventListener('scroll', this.handleScroll, false)
                const height = listWrapEl.getBoundingClientRect().height

                // 计算出每页加载的条数
                // 规则为容器高度除以每条的高度，考虑到后续可能需要触发容器滚动事件，在实际可容纳的条数上再增加1条
                // @notice: 每个流程条目的高度需要固定，目前取的css定义的高度40px
                if (height > 0) {
                    this.limit = Math.ceil(height / 40) + 1
                }
                this.getTplList()
            },
            // 切换搜索模式，按标签过滤和文本过滤
            handleChangeSearchMode (type) {
                this.isFilterLabelMode = type === 'label'
                if (this.searchStr !== '' || this.labels.length > 0) {
                    this.searchStr = ''
                    this.labels = []
                    this.handleSearch()
                }
            },
            handleTestSearchPaste (value, event) {
                const paste = (event.clipboardData || window.clipboardData).getData('text')
                this.searchStr = value + paste
                this.tplList = []
                this.handleSearch()
            },
            handleTextSearchChange (val) {
                if (val === '') {
                    this.handleTextSearchClear()
                }
            },
            // 清除文本搜索
            handleTextSearchClear () {
                this.searchStr = ''
                this.labels = []
                this.handleSearch()
            },
            handleSearch () {
                this.tplList = []
                this.crtPage = 1
                this.getTplList()
            },
            handleScroll (e) {
                if (this.listLoading || this.isCompleteLoading) {
                    return
                }
                const { scrollTop, clientHeight, scrollHeight } = e.target
                const isScrollBottom = scrollHeight === (scrollTop + clientHeight)
                if (isScrollBottom) {
                    this.crtPage += 1
                    this.getTplList()
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
                            id: this.$store.state.project.project_id,
                            name: this.$store.state.project.projectName
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
    .subflow-list-panel {
        height: 100%;
    }
    .search-wrap {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 11px 14px 12px;
        border-bottom: 1px solid #ccd0dd;
        background: #ffffff;
        .label-select {
            width: 225px;
        }
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
    .tpl-list-wrap {
        height: calc(100% - 60px);
        .tpl-list {
            height: 100%;
            overflow: auto;
            @include scrollbar;
        }
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
        ::v-deep .name-wrapper {
            padding: 0 14px;
            height: 40px;
            line-height: 40px;
            color: #63656e;
            font-size: 12px;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 1;
        }
    }
    .exception-part {
        margin-top: 60px;
    }
</style>
