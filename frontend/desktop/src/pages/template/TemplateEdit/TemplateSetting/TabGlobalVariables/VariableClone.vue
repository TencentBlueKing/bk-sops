<template>
    <bk-dialog
        width="850"
        ext-cls="common-dialog variable-clone-dialog"
        :theme="'primary'"
        :mask-close="false"
        :header-position="'left'"
        :title="$t('跨流程克隆')"
        :value="isVarCloneDialogShow"
        :auto-close="false"
        :on-close="onCancel"
        @value-change="toggleShow">
        <bk-steps ext-cls="step-area" :steps="stepsConfig" :cur-step.sync="curStep"></bk-steps>
        <div v-show="curStep === 1" class="task-container" v-bkloading="{ isLoading: taskListPending, opacity: 0.3, zIndex: 100 }">
            <div class="task-wrapper">
                <div class="filtrate-wrapper">
                    <div class="task-search">
                        <bk-select
                            :value="selectedTplType"
                            class="bk-select-inline"
                            :popover-width="260"
                            :clearable="false"
                            @selected="onChooseTplType">
                            <bk-option
                                v-for="(option, index) in templateType"
                                :key="index"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </div>
                    <div class="task-search">
                        <bk-select
                            v-if="selectedTplType === 'publicProcess'"
                            v-model="selectedTplCategory"
                            class="bk-select-inline"
                            :popover-width="260"
                            :disabled="taskCategoryLoading"
                            :clearable="false"
                            @selected="onChooseTplCategory">
                            <bk-option
                                v-for="(option, index) in templateCategories"
                                :key="index"
                                :id="option.value"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                        <bk-select
                            v-else
                            v-model="selectedTplLabel"
                            class="bk-select-inline"
                            ext-popover-cls="label-select"
                            key="label-select"
                            :placeholder="$t('请选择标签')"
                            :popover-width="260"
                            :disabled="templateLabelLoading"
                            :display-tag="true"
                            :multiple="true"
                            @change="onLabelChange">
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
                                    <i v-if="selectedTplLabel.includes(item.id)" class="bk-option-icon bk-icon icon-check-1"></i>
                                </div>
                            </bk-option>
                        </bk-select>
                    </div>
                    <div class="task-search">
                        <bk-input
                            class="search-input"
                            :placeholder="$t('请输入关键字')"
                            :right-icon="'bk-icon icon-search'"
                            :clearable="true"
                            v-model.trim="searchWord"
                            @input="onSearchInput">
                        </bk-input>
                    </div>
                </div>
                <div class="task-list">
                    <ul v-if="!isNoData" class="grouped-list">
                        <li
                            v-for="template in templateList"
                            :key="template.id"
                            :title="template.name"
                            :class="[
                                'task-item',
                                {
                                    'task-item-selected': selectedTpl.id === template.id,
                                    'permission-disable': !hasPermission(action, template.auth_actions)
                                }
                            ]"
                            @click="onSelectTpl(template)">
                            <div class="task-item-icon">{{ template.name.substr(0,1).toUpperCase() }}</div>
                            <div class="task-item-name-box">
                                <div class="task-item-name">{{ template.name }}</div>
                            </div>
                            <div class="apply-permission-mask">
                                <bk-button theme="primary" size="small">{{ $t('申请权限') }}</bk-button>
                            </div>
                        </li>
                    </ul>
                    <NoData
                        v-else-if="!taskListPending"
                        :type="isSearch ? 'search-empty' : 'empty'"
                        :message="isSearch ? $t('搜索结果为空') : ''"
                        @searchClear="handleSearchClear">
                    </NoData>
                </div>
            </div>
            <div class="task-footer" v-if="selectError">
                <span class="error-info">{{ $t('请选择流程模版') }}</span>
            </div>
        </div>
        <div v-show="curStep === 2" class="variable-container" v-bkloading="{ isLoading: variableLoading, opacity: 0.3, zIndex: 100 }">
            <p class="selected-tpl-name">{{ $t('流程名称') + $t('：') + selectedTpl.name }}</p>
            <p class="variable-table-label">{{ $t('变量信息') }}</p>
            <div class="variable-table">
                <div class="variable-header">
                    <bk-checkbox
                        :value="isSelectAll"
                        :indeterminate="isIndeterminate"
                        :disabled="!variableList.length"
                        class="variable-checkbox"
                        @change="onSelectAll">
                    </bk-checkbox>
                    <span class="t-head col-name">{{ $t('名称') }}</span>
                    <span class="t-head col-key">Key</span>
                    <span class="t-head col-type">{{ $t('类型') }}</span>
                </div>
                <ul class="variable-list" v-if="variableList.length">
                    <li class="variable-item" v-for="variable in variableList" :key="variable.key">
                        <bk-checkbox
                            class="col-item-checkbox"
                            :value="variable.checked"
                            @change="onChooseVariable(variable)">
                        </bk-checkbox>
                        <span class="col-item col-name ellipsis" v-bk-overflow-tips="{ distance: 0 }">
                            {{ variable.name }}
                        </span>
                        <div class="col-item col-key" :class="{ 'length-overrun': !variable.lengthMatch }">
                            <p v-bk-overflow-tips="{ distance: 0 }" class="ellipsis">{{ variable.key }}</p>
                            <p v-if="!variable.lengthMatch">{{ $t('无法克隆此变量，因克隆后变量长度超限') }}</p>
                        </div>
                        <span class="col-item col-type">
                            {{ variable.type }}
                        </span>
                    </li>
                </ul>
                <div v-else class="empty-variable-tips">
                    <NoData message="$t('该流程暂无自定义全局变量')"></NoData>
                </div>
            </div>
            <div class="variable-footer">
                <bk-checkbox :value="isSelectAll" :disabled="!variableList.length" class="variable-checkbox" @change="onSelectAll">
                </bk-checkbox>
                <span class="mr24">{{ $t('全选所有变量') }}</span>
                <span>{{ $t('已选择 x 个变量', { num: selectedVarList.length }) }}</span>
            </div>
        </div>
        <div class="dialog-footer" slot="footer">
            <bk-button
                v-if="curStep === 2"
                theme="primary"
                :disabled="variableLoading || !selectedVarList.length"
                data-test-id="taskList_form_confirmCloneBtn"
                @click="onCloneVarConfirm">
                {{ $t('确定') }}
            </bk-button>
            <bk-button
                :theme="curStep === 1 ? 'primary' : 'default'"
                :disabled="taskListPending || variableLoading"
                data-test-id="taskList_form_toggleStepBtn"
                @click="toggleStep">
                {{ curStep === 1 ? $t('下一步') : $t('上一步') }}
            </bk-button>
            <bk-button data-test-id="taskList_form_cancelCloneBtn" @click="onCancel">{{ $t('取消') }}</bk-button>
        </div>
    </bk-dialog>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import toolsUtils from '@/utils/tools.js'
    import { mapActions, mapState } from 'vuex'
    import permission from '@/mixins/permission.js'
    import NoData from '@/components/common/base/NoData.vue'
    import { STRING_LENGTH } from '@/constants/index.js'

    export default {
        name: 'VariableCloneDialog',
        components: {
            NoData
        },
        mixins: [permission],
        props: {
            isVarCloneDialogShow: {
                type: Boolean,
                default: false
            },
            varTypeList: {
                type: Array,
                default: () => ([])
            },
            globalVariableList: {
                type: Array,
                default: () => ([])
            }
        },
        data () {
            const { project_id } = this.$route.params
            return {
                projectId: project_id,
                stepsConfig: [
                    { title: i18n.t('选择流程'), icon: 1 },
                    { title: i18n.t('选择变量'), icon: 2 }
                ],
                curStep: 1,
                taskCategory: [],
                selectedTpl: {},
                taskListPending: true,
                selectError: false,
                templateList: [],
                templateType: [
                    {
                        id: 'businessProcess',
                        name: i18n.t('项目流程')
                    },
                    {
                        id: 'publicProcess',
                        name: i18n.t('公共流程')
                    }
                ],
                selectedTplType: 'businessProcess',
                selectedTplCategory: 'all',
                selectedTplLabel: [],
                searchWord: '',
                templateLabels: [],
                templateLabelLoading: false,
                variableLoading: false,
                isSelectAll: false,
                variableList: [], // 变量列表
                selectedVarList: [],
                totalPage: 0,
                currentPage: 0,
                pollingTimer: null,
                isThrottled: false, // 滚动节流 是否进入cd
                templateListDom: null
            }
        },
        computed: {
            ...mapState({
                'permissionMeta': state => state.permissionMeta
            }),
            ...mapState('project/', {
                'projectName': state => state.projectName,
                'projectAuthActions': state => state.authActions
            }),
            templateCategories () {
                const list = toolsUtils.deepClone(this.taskCategory)
                list.unshift({ value: 'all', name: i18n.t('全部分类') })
                return list.map(m => ({ value: m.value, name: m.name }))
            },
            isNoData () {
                return this.templateList.length === 0
            },
            action () {
                return this.selectedTplType === 'businessProcess' ? ['flow_view'] : ['common_flow_view']
            },
            isIndeterminate () {
                const selectedLength = this.selectedVarList.length
                if (selectedLength && (selectedLength !== this.variableList.length)) {
                    return true
                }
                return false
            },
            isSearch () {
                return this.searchWord || this.selectedTplLabel.length
            }
        },
        created () {
            this.onSearchInput = toolsUtils.debounce(this.searchInputHandler, 500)
        },
        beforeDestroy () {
            this.templateListDom && this.templateListDom.removeEventListener('scroll', this.handleTableScroll)
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            ...mapActions('templateList/', [
                'loadTemplateList'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo',
                'loadTemplateData'
            ]),
            ...mapActions('project/', [
                'getProjectLabelsWithDefault'
            ]),
            
            async getListData () {
                this.taskListPending = true
                try {
                    const {
                        selectedTplType,
                        projectId,
                        currentPage,
                        selectedTplLabel,
                        searchWord,
                        selectedTplCategory
                    } = this
                    const limit = 15
                    let params = {
                        limit,
                        offset: currentPage * limit,
                        pipeline_template__name__icontains: searchWord || undefined
                    }
                    if (selectedTplType === 'businessProcess') {
                        params = { ...params, project__id: projectId, order_by: '-id' }
                        if (selectedTplLabel) {
                            params = { ...params, label_ids: selectedTplLabel.join(',') }
                        }
                    } else {
                        params = { ...params, common: 1 }
                        if (selectedTplCategory !== 'all') {
                            params = { ...params, category: selectedTplCategory }
                        }
                    }
                    const respData = await this.loadTemplateList(params)
                    const { template_id } = this.$route.query
                    const list = respData.results.filter(item => item.id !== Number(template_id))
                    this.totalPage = Math.floor(respData.count / limit)
                    this.templateList = this.templateList.concat(list)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.taskListPending = false
                }
            },
            /**
             * 加载模板标签列表
             */
            async getTemplateLabelList () {
                try {
                    this.templateLabelLoading = true
                    const res = await this.getProjectLabelsWithDefault(this.projectId)
                    this.templateLabels = res.data
                } catch (e) {
                    console.log(e)
                } finally {
                    this.templateLabelLoading = false
                }
            },
            /**
             * 加载模板分类列表
             */
            async getTaskCategory () {
                try {
                    this.taskCategoryLoading = true
                    const res = await this.loadProjectBaseInfo()
                    this.taskCategory = res.data.task_categories
                } catch (e) {
                    console.log(e)
                } finally {
                    this.taskCategoryLoading = false
                }
            },
            async toggleShow (val) {
                if (val) {
                    this.getTemplateLabelList()
                    this.getTaskCategory()
                    await this.getListData()
                    if (!this.templateListDom) {
                        this.$nextTick(() => {
                            const templateListDom = document.querySelector('.task-list')
                            templateListDom && templateListDom.addEventListener('scroll', this.handleTableScroll)
                            this.templateListDom = templateListDom
                        })
                    }
                } else {
                    this.onCancel()
                }
            },
            onSelectTpl (template) {
                if (this.hasPermission(this.action, template.auth_actions)) {
                    this.selectError = false
                    this.selectedTpl = template
                } else {
                    let resourceData = {}
                    if (this.selectedTplType === 'businessProcess') {
                        resourceData = {
                            flow: [{
                                id: template.id,
                                name: template.name
                            }],
                            project: [{
                                id: template.project.id,
                                name: template.project.name
                            }]
                        }
                    } else {
                        resourceData = {
                            common_flow: [{
                                id: template.id,
                                name: template.name
                            }]
                        }
                    }
                    this.applyForPermission(this.action, template.auth_actions, resourceData)
                }
            },
            // 切换步骤
            toggleStep () {
                if (!this.selectedTpl.id) {
                    this.selectError = true
                    return
                }
                this.variableList = []
                if (this.curStep === 1) {
                    this.isSelectAll = false
                    this.selectedVarList = []
                    this.curStep = 2
                    this.getVariableList()
                } else {
                    this.curStep = 1
                }
            },
            /**
             * 获取模板详情
             */
            async getVariableList () {
                try {
                    this.variableLoading = true
                    const data = {
                        templateId: this.selectedTpl.id,
                        common: this.selectedTplType === 'publicProcess'
                    }
                    const templateData = await this.loadTemplateData(data)
                    const pipelineData = JSON.parse(templateData.pipeline_tree)
                    const constants = pipelineData.constants
                    this.variableList = Object.values(constants).reduce((acc, cur) => {
                        const result = this.varTypeList.find(value => value.code === cur.custom_type && value.tag === cur.source_tag)
                        const checkTypeList = ['component_inputs', 'component_outputs']
                        if (result && !checkTypeList.includes(cur.source_type)) {
                            cur.type = result.name
                            cur.checked = false
                            cur.lengthMatch = true
                            acc.push(cur)
                        }
                        return acc
                    }, [])
                } catch (e) {
                    console.warn(e)
                } finally {
                    this.variableLoading = false
                }
            },
            // 确定克隆变量
            onCloneVarConfirm () {
                let constants = this.variableList.filter(item => item.checked)
                const indexList = []
                const variableKeys = this.globalVariableList.map(item => {
                    indexList.push(item.index)
                    return item.key
                })
                const maxIndex = Math.max(...indexList)
                const cloneErrorList = []
                constants = toolsUtils.deepClone(constants).map((item, index) => {
                    const key = this.setCloneKey(item.key, variableKeys)
                    if (key.slice(2, -1).length > STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH) {
                        cloneErrorList.push(item.key)
                    } else {
                        item.key = key
                        item.index = maxIndex + index + 1
                        item.source_info = {}
                    }
                    return item
                })
                if (cloneErrorList.length) {
                    this.variableList.forEach(item => {
                        if (cloneErrorList.includes(item.key)) {
                            item.lengthMatch = false
                        }
                    })
                } else {
                    this.$emit('onCloneVarConfirm', constants)
                    this.$bkMessage({
                        message: i18n.t('变量克隆成功！'),
                        offsetY: 80,
                        theme: 'success'
                    })
                }
            },
            setCloneKey (key, variableKeys) {
                let newKey = key
                if (variableKeys.includes(key)) {
                    newKey = key.slice(0, -1) + '_clone}'
                }
                if (variableKeys.includes(newKey)) {
                    newKey = this.setCloneKey(newKey, variableKeys)
                }
                return newKey
            },
            // 取消变量克隆
            onCancel () {
                this.curStep = 1
                this.selectedTplType = 'businessProcess'
                this.selectedTplCategory = 'all'
                this.selectedTplLabel = []
                this.searchWord = ''
                this.clearSearch()
                this.$emit('onCloneVarCancel')
            },
            // 变量勾选切换
            onChooseVariable (variable) {
                const index = this.selectedVarList.findIndex(item => item === variable.key)
                if (index > -1) {
                    this.selectedVarList.splice(index, 1)
                } else {
                    this.selectedVarList.push(variable.key)
                }
                variable.checked = !variable.checked
                this.isSelectAll = this.selectedVarList.length === this.variableList.length
            },
            // 变量全选
            onSelectAll () {
                this.isSelectAll = !this.isSelectAll
                this.selectedVarList = []
                this.variableList.forEach(item => {
                    if (this.isSelectAll) {
                        this.selectedVarList.push(item.key)
                        item.checked = true
                    } else {
                        item.checked = false
                    }
                })
            },
            searchInputHandler () {
                this.clearSearch()
                this.getListData()
            },
            handleSearchClear () {
                this.selectedTplCategory = 'all'
                this.selectedTplLabel = []
                this.searchWord = ''
                this.searchInputHandler()
            },
            async onChooseTplType (value) {
                this.selectedTplType = value
                this.searchWord = ''
                this.clearSearch()
                if (value === 'businessProcess') {
                    this.selectedTplLabel = []
                } else {
                    this.selectedTplCategory = 'all'
                }
                await this.getListData()
            },
            onLabelChange () {
                this.clearSearch()
                this.getListData()
            },
            onChooseTplCategory (value) {
                this.selectedTplCategory = value
                this.clearSearch()
                this.getListData()
            },
            clearSearch () {
                this.currentPage = 0
                this.templateList = []
                this.selectedTpl = {}
                this.selectError = false
            },
            /**
             * 滚动加载
             */
            handleTableScroll () {
                if (this.currentPage < this.totalPage && !this.isThrottled) {
                    this.isThrottled = true
                    this.pollingTimer = setTimeout(() => {
                        this.isThrottled = false
                        const el = this.templateListDom
                        if (el.scrollHeight - el.offsetHeight - el.scrollTop < 10) {
                            this.currentPage += 1
                            clearTimeout(this.pollingTimer)
                            this.getListData()
                        }
                    }, 500)
                }
            }
        }
    }
</script>

<style lang="scss">
    .variable-clone-dialog .bk-dialog {
        .bk-dialog-header {
            margin-top: -20px;
            padding: 18px 0 26px 24px;
            border-bottom: none;
        }
    }
</style>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
@import '@/scss/mixins/multiLineEllipsis.scss';
@import '@/scss/config.scss';
.step-area {
    width: 268px;
    margin: 0 0 28px 24px;
}
.task-container {
    position: relative;
    .task-wrapper {
        width: 850px;
        height: 100%;
        .task-list {
            height: 280px;
            overflow-y: auto;
            @include scrollbar;
            .grouped-list {
                margin: 16px 0 0 24px;
            }
        }
        .search-list {
            padding-top: 40px;
        }
        .filtrate-wrapper {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 12px;
            margin: 0 50px 0 24px;
            border-bottom: 1px solid #e2e4ed;
            .bk-select-inline,
            .search-input {
                width: 248px;
            }
        }
    }
    .task-search {
        position: relative;
        height: 32px;
        .search-input {
            width: 260px;
        }
    }
    .task-item {
        position: relative;
        display: inline-block;
        margin-left: 17px;
        margin-bottom: 16px;
        width: 248px;
        cursor: pointer;
        background: #dcdee5;
        border-radius: 2px;
        overflow: hidden;
        &:nth-child(3n + 1) {
            margin-left: 0;
        }
        .task-item-icon {
            float: left;
            width: 56px;
            height: 56px;
            line-height: 56px;
            background: #c4c6cc;
            text-align: center;
            color: #ffffff;
            font-size: 28px;
            overflow: hidden;
        }
        .task-item-name {
            color: #313238;
            word-break: break-all;
            @include multiLineEllipsis(14px, 2);
            &:after {
                background: #dcdee5
            }
        }
        .apply-permission-mask {
            display: none;
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            text-align: center;
            .bk-button {
                margin-top: 12px;
            }
        }
        &.permission-disable {
            background: #f7f7f7;
            .task-item-icon {
                color: #dcdee5;
                background: #f7f7f7;
                border: 1px solid #dcdee5;
            }
            .task-item-name-box {
                border: 1px solid #dcdee5;
                border-left: none;
            }
            .task-item-name {
                color: #c4c6cc;
                &:after {
                    background: #f7f7f7;
                }
            }
            .apply-permission-mask {
                background: rgba(255, 255, 255, 0.6);
                text-align: center;
            }
            .bk-button {
                height: 32px;
                line-height: 30px;
            }
            &:hover .apply-permission-mask {
                display: block;
            }
        }
    }
    .task-item-name-box {
        display: table-cell;
        vertical-align: middle;
        margin-left: 56px;
        padding: 0 15px;
        height: 56px;
        width: 205px;
        font-size: 12px;
    }
    .task-item-selected {
        .task-item-icon {
            background: #666a7c;
            color: #ffffff;
        }
        .task-item-name, .task-item-name-box {
            background: #838799;
            color: #ffffff;
            &:after {
                background: #838799
            }
        }
    }
    .task-footer {
        position: absolute;
        right: 210px;
        bottom: -40px;
        .error-info {
            margin-right: 20px;
            font-size: 12px;
            color: #ea3636;
        }
    }
}
.variable-container {
    position: relative;
    padding: 0 24px 16px;
    .selected-tpl-name {
        color: #63656E;
        line-height: 22px;
        margin-bottom: 16px;
    }
    .variable-table-label {
        color: #313238;
        margin-bottom: 12px;
    }
    .variable-table {
        position: relative;
        border: 1px solid #dcdee5;
        font-size: 12px;
        .variable-checkbox,
        .col-item-checkbox {
            position: absolute;
            left: 16px;
        }
        .col-name {
            margin-left: 40px;
            width: 170px;
        }
        .col-key {
            width: 300px;
            &.length-overrun {
                line-height: 24px !important;
                margin: 5px 0;
                p:last-child {
                    color: #ff5656;
                }
            }
        }
        .col-type {
            flex: 1;
        }
        .ellipsis {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
    }
    .variable-header {
        height: 42px;
        display: flex;
        align-items: center;
        background: #fafbfd;
        border-bottom: 1px solid #dcdee5;
        .t-head {
            height: 42px;
            line-height: 42px;
            color: #313238;
        }
    }
    .variable-list {
        max-height: 300px;
        overflow-y: auto;
        @include scrollbar;
        .variable-item {
            position: relative;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #dcdee5;
            .col-item {
                min-height: 42px;
                line-height: 42px;
                padding-right: 10px;
            }
            &:last-child {
                border-bottom: none;
            }
        }
    }
    .empty-variable-tips {
        height: 280px;
    }
    .variable-footer {
        position: absolute;
        left: 24px;
        bottom: -40px;
        display: flex;
        align-items: center;
        font-size: 12px;
        color: #313238;
        .bk-form-checkbox {
            margin: 1px 8px 0 0;
        }
        .mr24 {
            font-size: 14px;
            margin-right: 24px;
        }
        
    }
}
</style>
