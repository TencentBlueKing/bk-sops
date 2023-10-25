<template>
    <div :class="['variable-panel', { 'is-hide': !isPanelShow, 'variable-edit-panel': isVariableEdit }]" :style="{ width: `${sideWidth}px` }">
        <div v-if="!isPanelShow" class="variable-nav" @click="togglePanelShow">
            <i class="bk-icon icon-angle-double-left"></i>
            <span class="text">{{ $t('执行方案') }}</span>
        </div>
        <VariableEdit
            v-else-if="isVariableEdit"
            ref="variableEdit"
            :is-view-mode="isViewMode"
            :common="common"
            :variable-data="selectVariable"
            @closeEditingPanel="isVariableEdit = false"
            @onSaveVariable="onSaveVariable">
        </VariableEdit>
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
                <bk-button :text="true" class="f12" @click="onDeleteVarList">{{ $t('批量删除' )}}</bk-button>
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
                                :key="variable.id"
                                class="var-item"
                                @click="onEditVariable(variable)">
                                <VariableItem
                                    :variable-data="variable"
                                    :panel-type="panelType"
                                    :is-view-mode="isViewMode"
                                    :new-clone-keys="newCloneKeys"
                                    :variable-cited="variableCited"
                                    :variable-checked="deleteVarList.some(item => item.key === variable.key)"
                                    :internal-variable="internalVariable"
                                    @onChooseVariable="onChooseVariable"
                                    @onCloneVariable="onCloneVariable"
                                    @onDeleteVariable="onDeleteVariable">
                                </VariableItem>
                            </li>
                        </ul>
                    </bk-collapse-item>
                </bk-collapse>
            </div>
        </template>
        <!--可拖拽-->
        <template>
            <div class="resize-trigger" @mousedown.left="handleMousedown($event)"></div>
            <i :class="['resize-proxy', 'left']" ref="resizeProxy"></i>
            <div class="resize-mask" ref="resizeMask"></div>
        </template>
        <variableClone
            :is-var-clone-dialog-show="isVarCloneDialogShow"
            :var-type-list="varTypeList"
            :global-variable-list="variableList"
            @onCloneVarConfirm="onCloneVarConfirm"
            @onCloneVarCancel="isVarCloneDialogShow = false">
        </variableClone>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import { mapMutations, mapState, mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import VariableItem from './VariableItem.vue'
    import VariableEdit from './VariableEdit.vue'
    import VariableClone from './VariableClone.vue'
    export default {
        name: 'variablePanel',
        components: {
            VariableItem,
            VariableEdit,
            VariableClone
        },
        props: {
            isViewMode: Boolean,
            common: Boolean
        },
        data () {
            return {
                panelType: 'simple',
                variableCited: {}, // 全局变量被任务节点、网关节点以及其他全局变量引用情况
                varListLoading: false,
                varTypeList: [],
                activeCollapse: ['show', 'hide', 'system'],
                isPanelShow: true,
                sideWidth: 180,
                isVariableEdit: false,
                selectVariable: {},
                isVarCloneDialogShow: false,
                newCloneKeys: [],
                deleteVarList: [] // 批量删除变量
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'gateways': state => state.template.gateways,
                'outputs': state => state.template.outputs,
                'constants': state => state.template.constants,
                'internalVariable': state => state.template.internalVariable
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
            }
        },
        created () {
            this.setVariableType()
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
                'addVariable'
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
                this.sideWidth = type === 'simple' ? 180 : 280
            },
            togglePanelShow () {
                this.isPanelShow = true
                this.sideWidth = this.panelType === 'simple' ? 180 : 280
            },
            handleMousedown (event) {
                this.updateResizeMaskStyle()
                this.updateResizeProxyStyle()
                document.addEventListener('mousemove', this.handleMouseMove)
                document.addEventListener('mouseup', this.handleMouseUp)
            },
            handleMouseMove (event) {
                const nodeConfigDom = document.querySelector('.node-config-panel')
                const maxWith = window.innerWidth - 400 - (nodeConfigDom ? 600 : 0)
                let width = window.innerWidth - event.clientX
                width = width > maxWith ? maxWith : width
                const resizeProxy = this.$refs.resizeProxy
                resizeProxy.style.right = `${width}px`
            },
            updateResizeMaskStyle () {
                const resizeMask = this.$refs.resizeMask
                resizeMask.style.display = 'block'
                resizeMask.style.cursor = 'col-resize'
            },
            updateResizeProxyStyle () {
                const resizeProxy = this.$refs.resizeProxy
                resizeProxy.style.visibility = 'visible'
                resizeProxy.style.right = `${this.sideWidth}px`
            },
            handleMouseUp () {
                const resizeMask = this.$refs.resizeMask
                const resizeProxy = this.$refs.resizeProxy
                resizeProxy.style.visibility = 'hidden'
                resizeMask.style.display = 'none'
                const tplSideDom = document.querySelector('.template-side')
                this.sideWidth = resizeProxy.style.right.slice(0, -2)
                const right = Number(this.sideWidth)
                if (right >= 280) { // 详细模式
                    this.panelType = 'detail'
                } else if (right < 180) { // 收起模式
                    this.isPanelShow = false
                    this.sideWidth = 24
                } else { // 简洁模式
                    this.panelType = 'simple'
                }
                const nodeConfigDom = document.querySelector('.node-config-panel')
                if (nodeConfigDom) {
                    const { width: tplSideWidth } = tplSideDom.getBoundingClientRect()
                    nodeConfigDom.style.width = `${tplSideWidth - right}px`
                }
                document.removeEventListener('mousemove', this.handleMouseMove)
                document.removeEventListener('mouseup', this.handleMouseUp)
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
                if (isChecked) {
                    this.deleteVarList.push(variable)
                } else {
                    const index = this.deleteVarList.findIndex(item => item.key === variable.key)
                    if (index > -1) {
                        this.deleteVarList.splice(index, 1)
                    }
                }
            },
            onDeleteVarList () {
                if (!this.deleteVarListLen) return
                let title = ''
                if (this.deleteVarListLen === 1) {
                    title = i18n.t('确认删除') + i18n.t('全局变量') + `【${this.deleteVarList[0].key}】?`
                } else {
                    title = i18n.t('确认删除所选的x个变量？', { num: this.deleteVarListLen })
                }
                const h = this.$createElement
                this.$bkInfo({
                    subHeader: h('div', { class: 'custom-header' }, [
                        h('div', {
                            class: 'custom-header-title',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [title]),
                        h('div', {
                            class: 'custom-header-sub-title bk-dialog-header-inner',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('删除变量将导致所有变量引用失效，请及时检查并更新节点配置')])
                    ]),
                    extCls: 'dialog-custom-header-title',
                    maskClose: false,
                    width: 450,
                    confirmLoading: true,
                    cancelText: this.$t('取消'),
                    confirmFn: async () => {
                        await this.getVariableCitedData() // 删除变量后更新引用数据
                        this.deleteVarList.forEach(variableData => {
                            this.deleteVariable(variableData.key)
                        })
                        this.deleteVarList = []
                    }
                })
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
            onAddVariable () {
                this.selectVariable = {
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
                    version: 'legacy'
                }
                this.isVariableEdit = true
                this.sideWidth = 400
            },
            onEditVariable (variable) {
                this.isVariableEdit = true
                this.selectVariable = variable
                this.sideWidth = 400
            },
            onSaveVariable () {
                this.isVariableEdit = false
                this.$emit('templateDataChanged')
                this.getVariableCitedData() // 新增或者编辑变量后更新引用数据
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
.variable-panel {
    width: 180px;
    height: 100%;
    display: flex;
    flex-direction: column;
    position: relative;
    padding: 18px 0;
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
        margin: 0 16px 16px;
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
    &.is-hide {
        border: none;
        background: transparent;
    }
    &.variable-edit-panel {
        padding: 0;
    }
}
</style>
