<template>
    <bk-select
        ref="tplSelect"
        :value="value"
        class="bk-select-inline"
        ext-popover-cls="tpl-select-popover"
        :searchable="true"
        :placeholder="$t('请选择')"
        :clearable="true"
        :disabled="isViewMode"
        enable-scroll-load
        :scroll-loading="{ isLoading: template.scrollLoading }"
        :show-empty="false"
        :loading="template.loading"
        :remote-method="onTplSearch"
        @selected="onSelectedTemplate"
        @clear="onClearTemplate"
        @scroll-end="onSelectScrollLoad">
        <bk-option-group
            v-for="(group, index) in template.list"
            :name="group.name"
            :key="index"
            :show-collapse="group.showCollapse"
            :is-collapse="group.isCollapse"
            @collapse="group.isCollapse = $event">
            <span slot="group-name">
                <i class="common-icon-next-triangle-shape" :class="{ 'triangle-down': !group.isCollapse }"></i>
                {{ group.name }}
                ({{ group.count }})
            </span>
            <bk-option v-for="childOption in group.children"
                :key="childOption.id"
                :id="childOption.id"
                :name="childOption.name">
                <span class="name" v-if="childOption.highlightName" v-html="childOption.highlightName"></span>
                <span class="name" v-else>{{ childOption.name }}</span>
                <i class="common-icon-box-top-right-corner ml10" @click.stop="onViewTpl(item)"></i>
            </bk-option>
        </bk-option-group>
    </bk-select>
</template>

<script>
    import { mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import permission from '@/mixins/permission.js'
    import CancelRequest from '@/api/cancelRequest.js'
    export default {
        name: 'TplSelect',
        mixins: [permission],
        props: {
            value: [String, Number],
            isViewMode: Boolean,
            project_id: [String, Number],
            common: [String, Number],
            nodeConfig: Object
        },
        data () {
            return {
                defaultTpl: null,
                subFlowLoading: false,
                template: {
                    list: [
                        {
                            name: this.$t('项目流程'),
                            count: 0,
                            showCollapse: true,
                            isCollapse: false,
                            children: []
                        },
                        {
                            name: this.$t('公共流程'),
                            count: 0,
                            showCollapse: true,
                            isCollapse: false,
                            children: []
                        }
                    ],
                    loading: true,
                    scrollLoading: false,
                    disabled: false
                },
                totalPage: 1,
                tplPagination: {
                    current: 1,
                    count: 0,
                    limit: 15
                },
                isLoadCommonTpl: false,
                flowName: null
            }
        },
        watch: {},
        async created () {
            await this.getTemplateList()
            // 初始化时选中的模板是否存在已被拿到
            const isMatch = this.template.list.some(group => {
                return group.children.some(item => item.id === this.value)
            })
            if (!isMatch) {
                this.defaultTpl = this.value
                await this.addDefaultTemplate()
            }
            this.template.loading = false
        },
        methods: {
            ...mapActions('template/', [
                'loadTemplateData'
            ]),
            ...mapActions('templateList/', [
                'loadTemplateList'
            ]),
            async getTemplateList (add, isCommon = this.isLoadCommonTpl) {
                try {
                    const { limit, current } = this.tplPagination
                    const offset = (current - 1) * limit
                    const params = {
                        limit: 15,
                        offset,
                        published: true,
                        pipeline_template__name__icontains: this.flowName || undefined
                    }
                    const source = new CancelRequest()
                    params.cancelToken = source.token
                    if (isCommon) {
                        params.common = 1
                    } else {
                        params.project__id = this.project_id
                    }
                    const tplListData = await this.loadTemplateList(params)
                    const result = []
                    tplListData.results.forEach(tpl => {
                        tpl.isCommon = isCommon
                        const tplCopy = { ...tpl }
                        // 高亮搜索匹配的文字部分
                        const searchStr = this.escapeRegExp(this.flowName)
                        if (searchStr !== '') {
                            const reg = new RegExp(searchStr, 'i')
                            if (reg.test(tpl.name)) {
                                tplCopy.highlightName = tplCopy.name.replace(reg, `<span style="color: #ff9c01;">${this.flowName}</span>`)
                            }
                        }
                        // 只记录非默认流程
                        if (this.defaultTpl !== tpl.id) {
                            result.push(tplCopy)
                        }
                    })

                    // 当项目列表为空或轮到公共流程加载时, 添加公共流程分组
                    if (isCommon && !this.template.list[1]) {
                        this.template.list.push({
                            name: this.$t('公共流程'),
                            showCollapse: true,
                            isCollapse: false,
                            children: result
                        })
                    } else if (!isCommon && !tplListData.count) {
                        this.template.list[0].children = []
                    } else {
                        if (add) {
                            this.template.list[isCommon ? 1 : 0].children.push(...result)
                        } else {
                            this.template.list[isCommon ? 1 : 0].children = result
                        }
                    }
                    this.template.list[isCommon ? 1 : 0].count = tplListData.count
                    this.tplPagination.count = tplListData.count
                    const totalPage = Math.ceil(this.tplPagination.count / limit)
                    if (!totalPage) {
                        this.totalPage = 1
                    } else {
                        this.totalPage = totalPage
                    }
                    // 项目流程第一次加载时, 移除公共流程分组(为了实现滚动加载)
                    if (!isCommon && current === 1) {
                        this.template.list.splice(1, 1)
                    }

                    // 开始重新加载公共流程列表
                    if (!isCommon && (totalPage === 1 || this.totalPage <= current)) {
                        this.isLoadCommonTpl = true
                        this.resetTplPagination()
                        await this.getTemplateList()
                    }
                } catch (e) {
                    console.log(e)
                    this.template.loading = false
                } finally {
                    this.template.scrollLoading = false
                }
            },
            // 添加初始化时默认选中模板
            async addDefaultTemplate () {
                try {
                    const isCommon = this.common || this.nodeConfig.template_source === 'common'
                    const resp = await this.loadTemplateData({
                        templateId: this.defaultTpl,
                        common: isCommon,
                        checkPermission: true
                    })
                    if (this.isCommon) {
                        if (this.template.list[1]) {
                            const { children } = this.template.list[1]
                            children.unshift(resp)
                        } else {
                            this.template.list[1] = {
                                name: this.$t('公共流程'),
                                showCollapse: true,
                                isCollapse: false,
                                children: [resp]
                            }
                        }
                    } else {
                        const { children } = this.template.list[0]
                        children.unshift(resp)
                    }
                } catch (error) {
                    console.warn(error)
                    this.template.loading = false
                }
            },
            escapeRegExp (str) {
                if (typeof str !== 'string') {
                    return ''
                }
                return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, '\\$&')
            },
            resetTplPagination () {
                this.totalPage = 1
                this.tplPagination = {
                    current: 1,
                    count: 0,
                    limit: 15
                }
            },
            async onTplSearch (val) {
                tools.debounce(await this.handleTplSearch(val), 200)
            },
            // 下拉框搜索
            handleTplSearch (val) {
                this.isLoadCommonTpl = false
                this.tplPagination.current = 1
                this.flowName = val
                const optionsDom = document.querySelector('.bk-options')
                optionsDom && optionsDom.scrollTo(0, 0)
                return new Promise((resolve) => {
                    this.getTemplateList(false).then(() => {
                        resolve()
                    })
                })
            },
            // 下拉框滚动加载
            onSelectScrollLoad () {
                if (this.totalPage !== this.tplPagination.current) {
                    this.tplPagination.current += 1
                    this.template.scrollLoading = true
                    this.getTemplateList(true)
                }
            },
            onSelectedTemplate (id) {
                const templateList = this.template.list
                let tpl = {}

                if (id === undefined) {
                    return
                }

                templateList.some(group => {
                    return group.children.some(item => {
                        if (item.id === id) {
                            tpl = item
                            return true
                        }
                    })
                })
                const reqPermission = tpl.isCommon ? ['common_flow_view'] : ['flow_view']
                const hasPermission = this.hasPermission(reqPermission, tpl.auth_actions)
                if (hasPermission) {
                    this.version = tpl.version
                    this.$emit('select', tpl)
                } else {
                    this.onApplyPermission(tpl)
                }
            },
            onClearTemplate () {
                this.isLoadCommonTpl = false
                this.resetTplPagination()
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
                if (tpl.isCommon) {
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
.tpl-select-popover {
    .bk-option-group {
        margin-bottom: 8px;

        /deep/.bk-option-group-name {
            border-bottom: none;
            .bk-option-group-prefix {
                display: none;
            }
            i {
                position: relative;
                top: -2px;
            }
            .triangle-down {
                display: inline-block;
                transform: rotate(90deg);
            }
        }
        .bk-group-options {
            .bk-option {
                padding: 0 18px 0 24px;
                /deep/.bk-option-content {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding-right: 0;
                }
                &:hover {
                    color: #63656e;
                    background: #f5f7fa;
                }
                &.is-selected {
                    color: #3a84ff;
                    background: #e1ecff;
                }
                &:first-child {
                    margin-top: 0;
                }
                .common-icon-box-top-right-corner {
                    color: #63656e;
                    &:hover {
                        color: #3a84ff;
                    }
                }
            }
        }
    }
}
</style>
