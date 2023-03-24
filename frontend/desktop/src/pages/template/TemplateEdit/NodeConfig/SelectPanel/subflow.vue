<template>
    <div class="subflow-select-panel" ref="subflowSelectPanel">
        <p class="select-title">请选择流程进行节点配置</p>
        <div class="type-select-wrapper">
            <!-- 公共流程编辑不显示切换流程类型下拉框 -->
            <bk-select
                v-if="!common"
                style="width: 240px;"
                :value="tplType"
                :clearable="false"
                @change="onTplTypeChange">
                <bk-option id="business" name="项目流程"></bk-option>
                <bk-option id="common" name="公共流程"></bk-option>
            </bk-select>
            <bk-input
                v-model="searchStr"
                class="search-text-input"
                placeholder="请输入流程名称"
                :clearable="true"
                right-icon="bk-icon icon-search"
                @paste="handleSearchPaste"
                @change="handleSearchEmpty"
                @clear="handleSearch"
                @enter="handleSearch">
            </bk-input>
        </div>
        <div class="list-table">
            <div class="table-head">
                <div class="th-item tpl-name">{{ $t('流程名称') }}</div>
                <div class="th-item tpl-label">
                    <span>{{ $t('标签') }}</span>
                    <div v-if="!commonTpl" class="label-select-wrap">
                        <bk-select
                            v-model="labels"
                            class="tpl-label-filter"
                            ext-popover-cls="label-select"
                            :searchable="true"
                            :clearable="false"
                            :multiple="true"
                            @selected="onSelectLabel">
                            <i slot="trigger" class="bk-icon icon-funnel filter-icon"></i>
                            <bk-option
                                v-for="option in templateLabels"
                                :key="option.id"
                                :id="option.id"
                                :name="option.name">
                                <div class="label-select-option">
                                    <span
                                        class="label-select-color"
                                        :style="{ background: option.color }">
                                    </span>
                                    <span>{{option.name}}</span>
                                    <i v-if="labels.includes(option.id)" class="bk-option-icon bk-icon icon-check-1"></i>
                                </div>
                            </bk-option>
                        </bk-select>
                    </div>
                </div>
            </div>
            <!-- 加一层div用来放bkLoading -->
            <div v-bkloading="{ isLoading: listLoading }">
                <div class="tpl-list">
                    <template v-if="tableList.length > 0">
                        <div
                            v-for="item in tableList"
                            v-cursor="{ active: !item.hasPermission }"
                            :class="['tpl-item', {
                                'active': String(item.id) === String(nodeConfig.template_id),
                                'text-permission-disable': !item.hasPermission
                            }]"
                            :key="item.id"
                            @click="onSelectTpl(item)">
                            <div class="tpl-name name-content">
                                <div class="name" v-if="item.highlightName" v-html="item.highlightName"></div>
                                <div class="name" v-else>{{ item.name }}</div>
                                <span class="view-tpl" @click.stop="onViewTpl(item)">
                                    <i class="common-icon-box-top-right-corner"></i>
                                </span>
                            </div>
                            <!-- 公共流程列表不展示标签 -->
                            <div v-if="!commonTpl && item.template_labels.length > 0" class="tpl-label labels-wrap">
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
                    <NoData
                        v-else
                        :type="searchStr ? 'search-empty' : 'empty'"
                        :message="searchStr ? $t('搜索结果为空') : ''"
                        @searchClear="handleSearch('')">
                    </NoData>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
    import permission from '@/mixins/permission.js'
    import { DARK_COLOR_LIST } from '@/constants/index.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'Subflow',
        components: {
            NoData
        },
        mixins: [permission],
        props: {
            common: [String, Number],
            nodeConfig: {
                type: Object,
                default: () => ({})
            },
            templateLabels: Array // 模板标签
        },
        data () {
            return {
                // 项目流程 business，公共流程 common, 公共流程编辑默认都是common
                tplType: this.common ? 'common' : (this.nodeConfig.template_source || 'business'),
                tplList: [],
                listLoading: false,
                isLabelSelectorOpen: false,
                isCompleteLoading: false,
                selectedLabelName: '',
                searchStr: '',
                labels: [],
                limit: 20, // 每页的条数，默认值，在mounted会根据屏幕高度动态计算
                crtPage: 1 // 分页加载当前页数
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
            },
            commonTpl () {
                return this.common || this.tplType === 'common'
            }
        },
        mounted () {
            // 设置滚动加载
            const listWrapEl = this.$refs.subflowSelectPanel.querySelector('.tpl-list')
            listWrapEl.addEventListener('scroll', this.handleScroll, false)
            const maxHeight = window.getComputedStyle(listWrapEl).maxHeight

            // 计算出每页加载的条数
            // 规则为容器高度除以每条的高度，考虑到后续可能需要触发容器滚动事件，在实际可容纳的条数上再增加1条
            // @notice: 每个流程条目的高度需要固定，目前取的css定义的高度40px
            if (maxHeight) {
                const height = Number(maxHeight.replace('px', ''))
                this.limit = Math.ceil(height / 40) + 1
            }
            this.getTplList()
        },
        beforeDestroy () {
            const listWrapEl = this.$refs.subflowSelectPanel.querySelector('.tpl-list')
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
                    const searchStr = this.escapeRegExp(this.searchStr)
                    const data = {
                        label_ids: this.labels.join(','),
                        pipeline_template__name__icontains: this.searchStr || undefined,
                        limit: this.limit,
                        offset: (this.crtPage - 1) * this.limit
                    }
                    if (this.commonTpl) {
                        data.common = true
                    } else {
                        data.project__id = this.$route.params.project_id
                    }
                    const resp = await this.$store.dispatch('templateList/loadTemplateList', data)
                    const reqPermission = this.commonTpl ? ['common_flow_view'] : ['flow_view']
                    const result = []
                    resp.results.forEach(tpl => {
                        tpl.hasPermission = this.hasPermission(reqPermission, tpl.auth_actions)
                        const tplCopy = { ...tpl }
                        // 高亮搜索匹配的文字部分
                        if (searchStr !== '') {
                            const reg = new RegExp(searchStr, 'i')
                            if (reg.test(tpl.name)) {
                                tplCopy.highlightName = tplCopy.name.replace(reg, `<span style="color: #ff9c01;">${this.searchStr}</span>`)
                            }
                        }
                        result.push(tplCopy)
                    })
                    this.tplList.push(...result)
                    this.isCompleteLoading = resp.count === this.tplList.length
                } catch (e) {
                    console.log(e)
                } finally {
                    this.listLoading = false
                }
            },
            getLabelStyle (id) {
                if (id) {
                    const label = this.templateLabels.find(item => item.id === Number(id))
                    if (!label) return {}
                    return {
                        background: label.color,
                        color: DARK_COLOR_LIST.includes(label.color) ? '#fff' : '#262e4f'
                    }
                }
                return { color: '#000000', minWidth: 'unset', padding: '2px' }
            },
            // 流程类型切换
            onTplTypeChange (val) {
                this.tplType = val
                this.crtPage = 1
                this.tplList = []
                this.labels = []
                this.getTplList()
            },
            // 滚动加载
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
            escapeRegExp (str) {
                if (typeof str !== 'string') {
                    return ''
                }
                return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, '\\$&')
            },
            handleSearchPaste (value, event) {
                const paste = (event.clipboardData || window.clipboardData).getData('text')
                this.searchStr = value + paste
                this.crtPage = 1
                this.tplList = []
                this.getTplList()
            },
            // 搜索框清空后触发搜索
            handleSearchEmpty (val) {
                if (val === '') {
                    this.handleSearch('')
                }
            },
            handleSearch (val) {
                this.searchStr = val
                this.crtPage = 1
                this.tplList = []
                this.getTplList()
            },
            // 选择标签
            onSelectLabel () {
                this.crtPage = 1
                this.tplList = []
                this.getTplList()
            },
            // 选择流程
            onSelectTpl (tpl) {
                if (tpl.hasPermission) {
                    this.$emit('select', tpl)
                } else {
                    this.onApplyPermission(tpl)
                }
            },
            // 查看流程
            onViewTpl (tpl) {
                if (!tpl.hasPermission) {
                    this.onApplyPermission(tpl)
                    return
                }
                const { name } = this.$route
                const routerName = name === 'commonTemplatePanel'
                    ? 'commonTemplatePanel'
                    : this.commonTpl
                        ? 'projectCommonTemplatePanel'
                        : 'templatePanel'
                const pathData = {
                    name: routerName,
                    params: {
                        type: 'view',
                        project_id: name === 'commonTemplatePanel' ? undefined : this.$route.params.project_id
                    },
                    query: {
                        template_id: tpl.id,
                        common: name === 'templatePanel' ? undefined : '1'
                    }
                }
                const { href } = this.$router.resolve(pathData)
                window.open(href, '_blank')
            },
            // 申请权限
            onApplyPermission (tpl) {
                let reqPerm, resourceData
                if (this.commonTpl) {
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
.subflow-select-panel {
    padding: 25px 32px 20px;
    height: 100%;
}
.select-title {
    margin-bottom: 16px;
    padding-bottom: 10px;
    font-size: 14px;
    color: #313238;
    font-weight: bold;
    border-bottom: 1px solid #dcdee5;
}
.type-select-wrapper {
    position: relative;
    height: 32px;
    .search-text-input {
        position: absolute;
        top: 0;
        right: 0;
        width: 240px;
    }
}
.list-table {
    margin-top: 16px;
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
            > span {
                flex-shrink: 0;
            }
            .label-select-wrap {
                cursor: pointer;
            }
            .tpl-label-filter {
                width: 260px;
                height: 16px;
                line-height: 16px;
                border: none;
                &:hover {
                    .filter-icon {
                        color: #3a84ff;
                    }
                }
                .filter-icon {
                    margin-left: 4px;
                    color: #c4c6cc;
                }
            }
        }
    }
}
.tpl-list {
    max-height: calc(100vh - 260px);
    overflow: auto;
    @include scrollbar;
}
.tpl-item {
    display: flex;
    height: 40px;
    align-items: center;
    color: #63656e;
    border-top: 1px solid #dcdee5;
    cursor: pointer;
    &:hover:not(.text-permission-disable), &.active:not(.text-permission-disable) {
        background: #e1ecff;
        .name, .view-tpl {
            color: #3a84ff;
        }
    }
    &:first-of-type {
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
</style>
