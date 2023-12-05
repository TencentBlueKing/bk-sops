<template>
    <div :class="['variable-panel', { 'is-hide': !isPanelShow }]" :style="{ width: `${width}px` }" :key="isPanelShow">
        <div v-if="!isPanelShow" class="variable-nav" @click="togglePanelShow">
            <i class="bk-icon icon-angle-double-left"></i>
            <span class="text">{{ $t('执行方案') }}</span>
        </div>
        <VariableEdit
            v-else-if="isVariableEdit"
            ref="variableEdit"
            :is-view-mode="isViewMode"
            :common="common"
            :variable-cited="variableCited"
            :variable-data="selectVariable"
            :hook-params="hookParams"
            @closeEditingPanel="closeEditingPanel"
            @onSaveVariable="onSaveVariable">
        </VariableEdit>
        <PluginFieldConfig
            v-else-if="isPluginFieldConfig"
            ref="pluginFieldConfig"
            :variable-cited="variableCited"
            :variable-data="selectVariable"
            :hook-params="hookParams"
            @closePanel="isPluginFieldConfig = false"
            @onAddVariable="onAddVariable"
            @onEditVariable="onEditVariable">
        </PluginFieldConfig>
        <template v-else>
            <div class="panel-title">
                <h4>{{ '变量面板' }}</h4>
                <div class="bk-button-group">
                    <bk-button
                        :class="{ 'is-selected': panelType === 'simple' }"
                        size="small"
                        v-bk-tooltips="$t('简洁模式')"
                        @click="togglePanelType('simple')">
                        <i class="common-icon-paper"></i>
                    </bk-button>
                    <bk-button
                        :class="{ 'is-selected': panelType === 'detail' }"
                        size="small"
                        v-bk-tooltips="$t('详细模式')"
                        @click="togglePanelType('detail')">
                        <i class="common-icon-paper"></i>
                    </bk-button>
                </div>
            </div>
            <bk-dropdown-menu v-if="!isViewMode" trigger="click" ref="largeDropdown" ext-cls="manger-variable-dropdown">
                <bk-button slot="dropdown-trigger" theme="primary" icon="plus">
                    {{ $t('新增变量') }}
                </bk-button>
                <ul class="bk-dropdown-list" slot="dropdown-content">
                    <li class="dropdown-item" @click="onAddVariable">{{ $t('新建自定义变量') }}</li>
                    <li
                        class="dropdown-item"
                        data-test-id="templateEdit_form_cloneVariable"
                        @click="isVarCloneDialogShow = true">
                        {{ $t('跨流程克隆') }}
                    </li>
                    <template v-if="!common">
                        <li class="line"></li>
                        <li
                            class="dropdown-item"
                            data-test-id="templateEdit_form_managerVariable"
                            @click="onManagerProjectVariable">
                            {{ $t('管理项目变量') }}
                        </li>
                    </template>
                </ul>
            </bk-dropdown-menu>
            <div class="variable-delete" v-if="deleteVarListLen">
                <bk-button :text="true" class="f12 mr5" @click="onSelectAll">{{ $t('全选' )}}</bk-button>
                <bk-button :text="true" class="f12" @click="deleteVarList = []">{{ $t('清空' )}}</bk-button>
                <span class="line"></span>
                <i18n
                    v-if="panelType === 'detail'"
                    tag="span"
                    path="varDeleteTxtTips"
                    class="variable-delete-txt"
                    v-bk-overflow-tips>
                    <span class="count">{{ deleteVarListLen }}</span>
                </i18n>
                <bk-button :text="true" class="f12" @click="isBatchDeleteDialogShow = true">{{ $t('批量删除' )}}</bk-button>
            </div>
            <div class="variable-collapse-wrap">
                <bk-collapse class="variable-collapse" v-model="activeCollapse" v-bkloading="{ isLoading: varListLoading, zIndex: 10 }">
                    <bk-collapse-item
                        v-for="key in Object.keys(variableMap)"
                        :key="key"
                        :name="key"
                        :hide-arrow="true">
                        <i class="common-icon-next-triangle-shape"></i>
                        {{ key === 'system' ? $t('系统变量') : key === 'show' ? $t('入参') : $t('非入参') }}
                        <span class="count">{{ $t('（') + variableMap[key].length + $t('）') }}</span>
                        <ul slot="content" class="var-list">
                            <li
                                v-for="variable in variableMap[key]"
                                :key="variable.key"
                                class="var-item">
                                <VariableItem
                                    :ref="`var-${variable.key}`"
                                    :variable-data="variable"
                                    :panel-type="panelType"
                                    :is-view-mode="isViewMode"
                                    :new-clone-keys="newCloneKeys"
                                    :variable-cited="variableCited"
                                    :variable-checked="deleteVarList.some(item => item.key === variable.key)"
                                    :internal-variable="internalVariable"
                                    :is-node-config-panel-show="isNodeConfigPanelShow"
                                    @onCitedNodeClick="onCitedNodeClick"
                                    @onEditVariable="onEditVariable(variable)"
                                    @onChooseVariable="onChooseVariable"
                                    @onCloneVariable="onCloneVariable"
                                    @onDeleteVariable="onDeleteVariable">
                                </VariableItem>
                            </li>
                        </ul>
                    </bk-collapse-item>
                </bk-collapse>
            </div>
            <!--变量快捷操作-->
            <QuickOperateVariableVue
                v-if="!isViewMode"
                :variable-list="variableList"
                class="quick-operate-btn">
            </QuickOperateVariableVue>
        </template>
        <!--可拖拽-->
        <template v-if="isPanelShow">
            <div class="resize-trigger" @mousedown.left="$emit('handleMousedown', 'variable')"></div>
        </template>
        <!--跨流程克隆变量-->
        <variableClone
            :is-var-clone-dialog-show="isVarCloneDialogShow"
            :var-type-list="varTypeList"
            :global-variable-list="variableList"
            @onCloneVarConfirm="onCloneVarConfirm"
            @onCloneVarCancel="isVarCloneDialogShow = false">
        </variableClone>
        <!--批量删除弹框-->
        <bk-dialog
            v-model="isBatchDeleteDialogShow"
            theme="primary"
            :mask-close="false"
            :title="$t('确认批量删除变量？')"
            :ok-text="$t('删除')"
            footer-position="center"
            :draggable="false"
            :loading="deleteLoading"
            ext-cls="batch-delete-dialog"
            @confirm="onConfirmBatchDelete"
            @cancel="isBatchDeleteDialogShow = false">
            <p class="tip-text">{{$t('以下自定义流程变量将被彻底删除')}}</p>
            <ul class="delete-var-list">
                <li
                    class="delete-var-item"
                    v-for="variable in deleteVarList"
                    :key="variable.key">
                    <span class="name">{{ variable.name }}</span>
                    <span class="key" v-bk-overflow-tips>{{ variable.key }}</span>
                </li>
            </ul>
        </bk-dialog>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import { mapMutations, mapState, mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import bus from '@/utils/bus.js'
    import VariableItem from './VariableItem.vue'
    import VariableEdit from './VariableEdit.vue'
    import VariableClone from './VariableClone.vue'
    import PluginFieldConfig from './PluginFieldConfig.vue'
    import QuickOperateVariableVue from './QuickOperateVariable.vue'
    export default {
        name: 'variablePanel',
        components: {
            VariableItem,
            VariableEdit,
            VariableClone,
            PluginFieldConfig,
            QuickOperateVariableVue
        },
        props: {
            isViewMode: Boolean,
            common: [String, Number],
            width: Number,
            isNodeConfigPanelShow: Boolean
        },
        data () {
            return {
                panelType: 'simple',
                variableCited: {}, // 全局变量被任务节点、网关节点以及其他全局变量引用情况
                varListLoading: false,
                varTypeList: [],
                activeCollapse: ['show', 'hide', 'system'],
                isPanelShow: true,
                isVariableEdit: false,
                isPluginFieldConfig: false,
                selectVariable: {},
                hookParams: {}, // 节点配置页变量勾选参数
                isVarCloneDialogShow: false,
                newCloneKeys: [],
                deleteLoading: false,
                isBatchDeleteDialogShow: false, // 批量删除弹框
                deleteVarList: [] // 批量删除变量
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'gateways': state => state.template.gateways,
                'outputs': state => state.template.outputs,
                'constants': state => state.template.constants,
                'internalVariable': state => state.template.internalVariable,
                'infoBasicConfig': state => state.infoBasicConfig
            }),
            variableList () {
                const userVars = Object.keys(this.constants)
                    .map(key => tools.deepClone(this.constants[key]))
                    .sort((a, b) => a.index - b.index)
                const sysVars = Object.keys(this.internalVariable)
                    .map(key => {
                        const values = tools.deepClone(this.internalVariable[key])
                        values.isSysVar = true
                        return values
                    }).sort((a, b) => b.index - a.index)
                return [...sysVars, ...userVars]
            },
            variableMap () {
                const varTypeList = tools.deepClone(this.varTypeList)
                return this.variableList.reduce((acc, cur) => {
                    this.$set(cur, 'type', '')
                    // 添加类型标识
                    if (cur.key in this.internalVariable) {
                        const varInfo = this.internalVariable[cur.key]
                        cur.type = varInfo.source_type === 'system' ? i18n.t('系统变量') : i18n.t('项目变量')
                    } else {
                        const result = varTypeList.find(item => item.code === cur.custom_type && item.tag === cur.source_tag)
                        const checkTypeList = ['component_inputs', 'component_outputs']
                        if (result && !checkTypeList.includes(cur.source_type)) {
                            cur.type = result.name
                        } else {
                            cur.type = cur.source_type === 'component_outputs' ? i18n.t('节点输出') : i18n.t('节点输入')
                        }
                    }
                    let type = 'hide'
                    // 根据输入输出分类
                    if (cur.source_type === 'system') {
                        type = 'system'
                        acc.system.push(cur)
                    } else if (cur.show_type === 'show') {
                        type = 'show'
                        acc.show.push(cur)
                    } else {
                        acc.hide.push(cur)
                    }
                    // 排序
                    acc[type] = acc[type].sort((a, b) => b.index - a.index)
                    return acc
                }, { show: [], hide: [], system: [] })
            },
            deleteVarListLen () {
                return this.deleteVarList.length
            },
            editVarList () {
                return this.variableList.filter(item => {
                    return !['system', 'project', 'component_outputs', 'component_inputs'].includes(item.source_type)
                })
            },
            isActivated () {
                if (!this.isPanelShow) {
                    return false
                }
                return this.isVariableEdit || this.isPluginFieldConfig || !!this.deleteVarListLen
            }
        },
        watch: {
            isActivated (val) {
                this.setVarPanelActivated(val)
                if (!val) {
                    this.hookParams = {}
                }
            },
            width (val) {
                if (val < 180) {
                    this.isPanelShow = false
                    this.isVariableEdit = false
                    this.isPluginFieldConfig = false
                } else if (val >= 180 && val < 280) {
                    this.panelType = 'simple'
                } else {
                    this.panelType = 'detail'
                }
            },
            isNodeConfigPanelShow (val) {
                if (!val) {
                    this.getVariableCitedData()
                }
            }
        },
        created () {
            this.setVariableType()

            // 节点配置页变量勾选
            bus.$on('variableHook', (data) => {
                if (!this.isPanelShow) {
                    this.isPanelShow = true
                    this.$emit('updateWidth', 400)
                }
                this.onAddVariable()
                this.hookParams = data
                const { cited_info: citedInfo = {} } = data
                Object.assign(this.selectVariable, {
                    ...data,
                    type: citedInfo.type
                })
                if (['reuse', 'reselect'].includes(citedInfo.type)) {
                    this.isVariableEdit = false
                    this.isPluginFieldConfig = true
                }
            })
        },
        mounted () {
            this.getVariableCitedData()
        },
        methods: {
            ...mapActions('template', [
                'getVariableCite',
                'loadCustomVarCollection'
            ]),
            ...mapMutations('template/', [
                'deleteVariable',
                'addVariable',
                'setVarPanelActivated'
            ]),
            async getVariableCitedData () {
                try {
                    const data = {
                        activities: this.activities,
                        gateways: this.gateways,
                        constants: { ...this.internalVariable, ...this.constants }
                    }
                    const resp = await this.getVariableCite(data)
                    if (resp.result) {
                        this.variableCited = resp.data.defined
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            async setVariableType () {
                try {
                    this.varListLoading = true
                    // 获取变量类型
                    this.varTypeList = await this.loadCustomVarCollection()
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.varListLoading = false
                }
            },
            togglePanelType (type) {
                this.panelType = type
                this.$emit('updateWidth', type === 'simple' ? 180 : 280)
            },
            togglePanelShow () {
                this.isPanelShow = true
                this.$emit('updateWidth', this.panelType === 'simple' ? 180 : 280)
            },
            // 跨流程克隆变量
            onCloneVarConfirm (constants = []) {
                constants.forEach(item => {
                    this.newCloneKeys.push(item.key)
                    this.addVariable(item)
                })
                this.isVarCloneDialogShow = false
            },
            // 点击跳转项目管理-管理项目变量
            onManagerProjectVariable () {
                const url = this.$router.resolve({
                    path: `/project/config/${this.$route.params.project_id}/`
                })
                window.open(url.href)
            },
            onSelectAll () {
                this.deleteVarList = tools.deepClone(this.editVarList)
            },
            onChooseVariable (variable, isChecked) {
                if (this.isNodeConfigPanelShow) return
                if (isChecked) {
                    this.deleteVarList.push(variable)
                } else {
                    const index = this.deleteVarList.findIndex(item => item.key === variable.key)
                    if (index > -1) {
                        this.deleteVarList.splice(index, 1)
                    }
                }
            },
            async onConfirmBatchDelete () {
                try {
                    this.deleteLoading = true
                    await this.getVariableCitedData() // 删除变量后更新引用数据
                    this.deleteVarList.forEach(variableData => {
                        this.deleteVariable(variableData.key)
                    })
                    this.deleteVarList = []
                    this.isBatchDeleteDialogShow = false
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.deleteLoading = false
                }
            },
            onCloneVariable (data) {
                const variableData = tools.deepClone(data)
                variableData.source_info = {}
                variableData.key = ''
                variableData.index = Object.keys(this.constants).length + 1
                this.variableData = variableData
            },
            onDeleteVariable (key) {
                this.deleteVariable(key)
                this.getVariableCitedData() // 删除变量后更新引用数据
                this.$bkMessage({
                    theme: 'success',
                    message: i18n.t('变量') + i18n.t('删除成功！')
                })
            },
            onAddVariable (params = {}) {
                this.selectVariable = {
                    type: 'create',
                    custom_type: 'input',
                    desc: '',
                    form_schema: {},
                    index: Object.keys(this.constants).length + 1,
                    key: '',
                    name: '',
                    show_type: 'show',
                    source_info: {},
                    source_tag: 'input.input',
                    source_type: 'custom',
                    validation: '^.+$',
                    is_condition_hide: false,
                    pre_render_mako: false,
                    value: '',
                    version: 'legacy',
                    ...params
                }
                this.isVariableEdit = true
                if (this.width < 400) {
                    this.$emit('updateWidth', 400)
                }
            },
            onEditVariable (variable) {
                this.isVariableEdit = true
                this.selectVariable = variable
                if (this.width < 400) {
                    this.$emit('updateWidth', 400)
                }
            },
            openVarCitedInfo (key) {
                this.isPanelShow = true
                this.panelType = 'detail'
                if (this.width < 400) {
                    this.$emit('updateWidth', 400)
                }
                this.$nextTick(() => {
                    const varItem = this.$refs[`var-${key}`]
                    if (varItem[0]) {
                        varItem[0].showCitedList = true
                    }
                })
            },
            onCitedNodeClick (data) {
                if (this.isNodeConfigPanelShow) return
                const { group, id } = data
                if (group === 'constants') {
                    this.onEditVariable(id)
                } else {
                    this.$emit('onCitedNodeClick', data)
                }
            },
            closeEditingPanel () {
                this.isVariableEdit = false
                // 关闭【变量编辑】面板时，如果【插件字段配置】已打开则selectVariable的部分字段值使用插件默认值
                if (this.isPluginFieldConfig) {
                    const { cited_info: citedInfo = {} } = this.hookParams
                    Object.assign(this.selectVariable, {
                        ...this.hookParams,
                        type: citedInfo.type
                    })
                }
            },
            onSaveVariable (variable = {}) {
                this.isVariableEdit = false
                this.isPluginFieldConfig = false
                this.$emit('templateDataChanged')
                this.getVariableCitedData() // 新增或者编辑变量后更新引用数据

                // 回填节点配置项勾选的变量值
                const { cited_info: citedInfo = {} } = this.hookParams
                if (citedInfo.type) {
                    bus.$emit('useVariable', {
                        type: citedInfo.type === 'create' ? 'insert' : 'replace',
                        code: citedInfo.tagCode,
                        key: variable.key,
                        variable
                    })
                }
            },
            // 关闭全局变量侧滑
            close () {
                if (this.isViewMode) {
                    return false
                }
                let isChange = false
                if (this.isVariableEdit) {
                    isChange = this.$refs.variableEdit.judgeDataChange()
                    if (isChange) {
                        this.$bkInfo({
                            ...this.infoBasicConfig,
                            confirmFn: () => {
                                this.isVariableEdit = false
                            }
                        })
                    } else {
                        this.isVariableEdit = false
                    }
                } else if (this.isPluginFieldConfig) {
                    isChange = true
                    this.isPluginFieldConfig = false
                }
                return isChange
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
.variable-panel {
    height: 100%;
    display: flex;
    flex-direction: column;
    position: relative;
    background: #fafbfd;
    border-left: 1px solid #dcdee5;
    .variable-nav {
        position: absolute;
        right: 0;
        top: 16px;
        display: flex;
        flex-direction: column;
        width: 24px;
        padding: 7px 1px;
        background: #699df4;
        border-radius: 4px 0 0 4px;
        font-size: 12px;
        line-height: 16px;
        text-align: center;
        color: #fff;
        cursor: pointer;
        .bk-icon {
            font-size: 14px;
            position: relative;
            left: -1px;
        }
    }
    .panel-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 18px 16px 16px;
        h4 {
            font-size: 14px;
            margin: 0;
            &::before {
                content: '';
                display: inline-block;
                width: 4px;
                height: 16px;
                position: relative;
                top: 2px;
                margin-right: 8px;
                background: #3a84ff;
                border-radius: 1px;
            }
        }
        .bk-button {
            padding: 0;
            min-width: 26px;
        }
    }
    /deep/.manger-variable-dropdown {
        width: 108px;
        margin: 0 0 16px 16px;
        .bk-button {
            width: 108px;
        }
        .bk-dropdown-content {
            padding: 8px 0;
        }
        .dropdown-item {
            height: 32px;
            font-size: 12px;
            line-height: 32px;
            text-align: center;
            padding: 0 10px 0 12px;
            color: #63656e;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
                background-color: #f0f1f5;
            }
        }
        .line {
            height: 1px;
            width: calc(100% - 22px);
            margin: 8px 10px 8px 12px;
            background: #dcdee5;
        }
    }
    .variable-delete {
        display: flex;
        align-items: center;
        padding: 4px 8px;
        margin: 0 0 5px 16px;
        background: #eaebf0;
        .line {
            flex-shrink: 0;
            display: inline-block;
            width: 1px;
            height: 16px;
            margin: 2px 8px 0 8px;
            background: #c4c6cc;
        }
        .variable-delete-txt {
            font-size: 12px;
            line-height: 20px;
            margin-left: 18px;
            color: #63656e;
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
            .count {
                color: #63656e;
                font-weight: 700;
            }
        }
        button {
            flex-shrink: 0;
            &:last-child {
                margin-left: 8px;
            }
        }
    }
    .variable-collapse-wrap {
        flex: 1;
        padding: 0 16px;
        overflow-y: auto;
        @include scrollbar;
    }
    /deep/.variable-collapse {
        .bk-collapse-item-header {
            display: flex;
            align-items: center;
            height: 32px;
            line-height: 32px;
            padding: 0;
            color: #313238;
            border-bottom: 1px solid #dcdee5;
            .count {
                font-size: 12px;
                color: #979ba5;
            }
        }
        .bk-collapse-item-content {
            padding: 0;
        }
        .common-icon-next-triangle-shape {
            display: inline-block;
            color: #3a84ff;
            margin: 0 3px;
            transition: all .2s linear;
        }
        .bk-collapse-item-active {
            .common-icon-next-triangle-shape {
                transform: rotate(90deg);
            }
        }
    }
    .quick-operate-btn {
        align-self: end;
        margin: 12px 0 18px;
        padding-right: 16px;
        line-height: 20px;
    }
    &.is-hide {
        border: none;
        background: transparent;
        &::before {
            content: '';
            display: inline-block;
            width: 2px;
            height: 100%;
            position: absolute;
            top: 0;
            right: 0;
            background: #699df4;
            border-radius: 4px 0 0 4px;
        }
    }
}
</style>
<style lang="scss">
.batch-delete-dialog {
    .bk-dialog-header {
        padding-bottom: 16px;
        .bk-dialog-header-inner {
            white-space: inherit;
        }
    }
    .bk-dialog-body {
        padding-top: 0;
        line-height: 20px;
        font-size: 12px;
        color: #63656e;
        .delete-var-list {
            margin-top: 8px;
            border: 1px solid #dcdee5;
            .delete-var-item {
                display: flex;
                align-items: center;
                height: 36px;
                padding: 0 16px;
                border-bottom: 1px solid #dcdee5;
                .name {
                    flex-shrink: 0;
                    margin-right: 8px;
                }
                .key {
                    color: #979ba5;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                &:last-child {
                    border: none;
                }
            }
        }
    }
    .bk-dialog-footer {
        padding: 8px 0 24px;
        border-top: none;
        background: #fff;
    }
}
</style>
