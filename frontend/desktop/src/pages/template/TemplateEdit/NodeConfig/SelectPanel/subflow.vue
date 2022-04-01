<template>
    <div class="subflow-select-panel">
        <p>请选择流程进行节点配置</p>
        <div class="type-select-wrapper">
            <bk-select style="width: 240px;" :value="tplType" :clearable="false" @change="onTplTypeChange">
                <bk-option id="project" name="项目流程"></bk-option>
                <bk-option id="common" name="公共流程"></bk-option>
            </bk-select>
            <bk-input v-model="searchStr" placeholder="请输入流程名称" style="width: 240px;" @change="handleNameSearch"></bk-input>
        </div>
        <div class="list-table">
            <div class="table-head">
                <div class="th-item tpl-name">{{ $t('流程名称') }}</div>
                <div class="th-item tpl-label">
                    <span>{{ $t('标签') }}</span>
                    <div v-if="!commonTpl" class="label-select-wrap">
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
                                @click="onSelectLabel(item.id)">
                                <span
                                    class="label-content"
                                    :style="getLabelStyle(item.id)">
                                    {{ item.name }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="tpl-list" v-bkloading="{ isLoading: listLoading }">
                <template v-if="tplList.length > 0">
                    <div
                        v-for="item in tplList"
                        v-cursor="{ active: !item.hasPermission }"
                        :class="['tpl-item', {
                            'active': String(item.id) === String(basicInfo.tpl),
                            'text-permission-disable': !item.hasPermission
                        }]"
                        :key="item.id"
                        @click="onSelectTpl(item)">
                        <div class="tpl-name name-content">
                            <div class="name" v-if="item.highlightName" v-html="item.highlightName"></div>
                            <div class="name" v-else>{{ item.name }}</div>
                            <span class="view-tpl" @click.stop="onViewTpl(item.id)">
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
                <bk-exception v-else class="exception-part" type="empty" scene="part"></bk-exception>
            </div>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import permission from '@/mixins/permission.js'
    import { DARK_COLOR_LIST } from '@/constants/index.js'

    export default {
        name: 'Subflow',
        mixins: [permission],
        props: {
            common: [String, Number],
            basicInfo: Object,
            templateLabels: Array // 模板标签
        },
        data () {
            return {
                tplType: 'project', // 项目流程 project，公共流程 common
                tplList: [],
                listLoading: false,
                isLabelSelectorOpen: false,
                activeGroup: '',
                selectedLabelName: '',
                searchStr: '',
                selectedLabels: [],
                currentPage: 0
            }
        },
        computed: {
            labels () {
                const list = this.templateLabels.slice(0)
                list.unshift({
                    id: 0,
                    name: i18n.t('默认全部')
                })
                return list
            },
            commonTpl () {
                return this.common || this.tplType === 'common'
            }
        },
        created () {
            this.getTplList()
        },
        methods: {
            // 加载项目流程或公共流程列表
            async getTplList () {
                if (this.listLoading) {
                    return
                }
                try {
                    this.listLoading = true
                    const { params } = this.$route
                    const searchStr = this.escapeRegExp(this.searchStr)
                    const labels = this.activeGroup
                    const limit = 30
                    const data = {
                        label_ids: labels || undefined,
                        pipeline_template__name__icontains: searchStr || undefined,
                        limit,
                        offset: this.currentPage * limit
                    }
                    if (this.commonTpl) {
                        data.common = true
                    } else {
                        data.project__id = params.project_id
                    }
                    const resp = await this.$store.dispatch('templateList/loadTemplateList', data)
                    this.totalPage = Math.floor(resp.count / this.limit)
                    const reqPermission = this.commonTpl ? ['common_flow_view'] : ['flow_view']
                    const result = []
                    resp.results.forEach(tpl => {
                        // 除流程克隆的情况，流程列表中需要过滤掉url中template_id对应的流程
                        if (this.$route.params.type === 'clone' || tpl.id !== Number(this.$route.query.template_id)) {
                            tpl.hasPermission = this.hasPermission(reqPermission, tpl.auth_actions)
                            let matchLabel = true
                            let matchName = true
                            const tplCopy = { ...tpl }
                            if (labels) {
                                matchLabel = tpl.template_labels.find(label => label.label_id === Number(labels))
                            }
                            if (searchStr !== '') {
                                const reg = new RegExp(searchStr, 'i')
                                if (!reg.test(tpl.name)) {
                                    matchName = false
                                } else {
                                    tplCopy.highlightName = tplCopy.name.replace(reg, `<span style="color: #ff5757;">${searchStr}</span>`)
                                }
                            }
                            if (matchLabel && matchName) {
                                result.push(tplCopy)
                            }
                        }
                    })
                    this.tplList = result
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
                this.currentPage = 0
                this.getTplList()
            },
            handleLabelSelectorOpen () {
                this.isLabelSelectorOpen = true
            },
            handleLabelSelectorClose () {
                this.isLabelSelectorOpen = false
            },
            escapeRegExp (str) {
                if (typeof str !== 'string') {
                    return ''
                }
                return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, '\\$&')
            },
            handleNameSearch (val) {

            },
            // 选择标签
            onSelectLabel () {
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
            onViewTpl (id) {
                let pathData = {}
                if (this.commonTpl) {
                    pathData = {
                        name: 'commonTemplatePanel',
                        params: {
                            type: 'edit'
                        },
                        query: {
                            template_id: id,
                            common: '1'
                        }
                    }
                } else {
                    pathData = {
                        name: 'templatePanel',
                        params: {
                            type: 'edit',
                            project_id: this.$route.params.project_id
                        },
                        query: {
                            template_id: id
                        }
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
    padding: 26px 32px;
    height: 100%;
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
    max-height: calc(100vh - 204px);
    overflow: auto;
    @include scrollbar;
    .no-data-wrapper {
        margin: 100px 0;
    }
}
.tpl-item {
    display: flex;
    min-height: 40px;
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
.type-select-wrapper {
    display: flex;
    align-items: center;
    justify-content: space-between;
}
</style>
<style lang="scss">
@import '@/scss/mixins/scrollbar.scss';
    .tpl-label-popover {
        background: #ffffff;
        .tippy-tooltip {
            padding: 7px 0;
            max-height: 180px;
            overflow: auto;
            @include scrollbar;
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
    .selector-panel .bk-tab{
        .bk-tab-header {
            padding-left: 17px;
        }
        .bk-tab-section {
            display: none;
        }
    }
    .plugin-desc-tips {
        .tippy-arrow {
            left: 370px !important;
        }
    }
</style>
