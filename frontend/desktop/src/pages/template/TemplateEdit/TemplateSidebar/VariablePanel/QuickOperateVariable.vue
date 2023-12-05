
<template>
    <bk-popover
        ref="popover"
        placement="top-end"
        theme="light"
        trigger="manual"
        :distance="4"
        width="480"
        ext-cls="quick-operate-popover"
        :arrow="false"
        :tippy-options="{ hideOnClick: false }">
        <bk-button :text="true" theme="primary" class="quick-operate-btn" @click="togglePopoverShow">
            {{ $t('变量快捷处理') }}
        </bk-button>
        <div
            slot="content"
            class="quick-operate-panel"
            v-bkloading="{ isLoading: isPanelLoading }"
            @click.stop>
            <bk-form form-type="vertical">
                <bk-form-item label="处理操作">
                    <bk-select v-model="selectOperate" ext-popover-cls="operate-popover" @change="handleOperateChange">
                        <bk-option
                            v-for="(operate, index) in operationList"
                            :key="index"
                            :id="operate.name"
                            :name="operate.name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item label="变量" :required="true">
                    <bk-select
                        v-model="selectVariable"
                        ext-popover-cls="variable-field-popover"
                        @change="handleVarFieldChange">
                        <bk-option
                            v-for="(field, fieldIndex) in varFiledList"
                            :key="fieldIndex"
                            :id="field.key"
                            :name="field.key + $t('（') + field.description + $t('）')">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
            </bk-form>
            <div class="operate-wrap">
                <div
                    class="template-item"
                    v-for="(template, index) in selectOperateInfo.template"
                    :key="index">
                    <template v-if="selectOperateInfo.operators[template]">
                        {{ '变量' }}
                    </template>
                    <template v-else-if="selectOperateInfo.params[template]">
                        <bk-input v-model="selectOperateInfo.params[template].value" @blur="onGenerateMakoTemp"></bk-input>
                    </template>
                    <template v-else>
                        <span>{{ template }}</span>
                    </template>
                </div>
            </div>
            <div :class="['render-wrap', { 'input-before': !makoTemplate }]" :data-placeholder="$t('选择变量后预览代码')">{{ makoTemplate }}</div>
            <div class="btn-wrap">
                <p v-if="isShowErrorMsg" class="error-msg">{{ $t('请填写完整参数') }}</p>
                <bk-button class="mr5" theme="primary" :disabled="isShowErrorMsg || !makoTemplate" @click="onCopyKey">{{ $t('复制代码') }}</bk-button>
                <bk-button @click="onCancel">{{ $t('取消') }}</bk-button>
            </div>
            
        </div>
    </bk-popover>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapState } from 'vuex'
    import tools from '@/utils/tools.js'

    export default {
        name: 'QuickOperateVariable',
        props: {
            variableList: Array
        },
        data () {
            return {
                isPanelLoading: false,
                selectOperate: '',
                selectVariable: '',
                operationList: [],
                selectOperateInfo: {},
                globalVarFiled: [],
                varFiledList: [],
                isShowErrorMsg: false,
                makoTemplate: '',
                isPopoverOpen: false
            }
        },
        computed: {
            ...mapState({
                'internalVariable': state => state.template.internalVariable
            })
        },
        mounted () {
            window.addEventListener('mouseup', this.handleClickOutside)
        },
        beforeDestroy () {
            window.removeEventListener('mouseup', this.handleClickOutside)
        },
        methods: {
            ...mapActions('template/', [
                'getMakoOperations',
                'getVariableFieldExplain'
            ]),
            togglePopoverShow () {
                this.isPopoverOpen = !this.isPopoverOpen
                if (this.isPopoverOpen) {
                    this.$refs['popover'].showHandler()
                    this.handleQuickInsertPanel()
                } else {
                    this.$refs['popover'].hideHandler()
                }
            },
            // 初始化快捷操作面板
            async handleQuickInsertPanel () {
                try {
                    this.isQuickInsertPanelShow = true
                    this.isPanelLoading = true
                    const [resp1, resp2] = await Promise.all([this.getMakoOperations(), this.getVariableFieldExplain()])
                    // 处理操作
                    const { operations } = resp1.data
                    if (operations && operations.length) {
                        this.operationList = operations
                        if (!this.selectOperate) {
                            this.selectOperate = operations[0].name
                        }
                    }
                    // 处理变量
                    const { variable_field_explain: varFiledExplain } = resp2.data
                    if (varFiledExplain && varFiledExplain.length) {
                        const list = varFiledExplain.reduce((acc, cur) => {
                            this.variableList.forEach(item => {
                                if (item.source_tag === cur.tag) {
                                    const listData = []
                                    cur.fields.forEach(field => {
                                        const varKey = item.key.replace(/^\$\{([^\}]*)\}$/, ($, $1) => $1)
                                        let description = field.description
                                        if (item.key in this.internalVariable && item.source_type !== 'system') {
                                            description = item.desc
                                        }
                                        listData.push({
                                            key: field.key.replace('KEY', varKey),
                                            type: field.type,
                                            description
                                        })
                                    })
                                    acc.push(...listData)
                                }
                            })
                            return acc
                        }, []) || []
                        this.globalVarFiled = list
                    }
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isPanelLoading = false
                }
            },
            // 切换操作方式
            handleOperateChange (val) {
                this.makoTemplate = ''
                let info = this.operationList.find(item => item.name === this.selectOperate)
                let operateVarList = []
                if (info) {
                    // 处理操作模板
                    info = tools.deepClone(info)
                    let tempStr = ''
                    info.template.forEach((item, index) => {
                        if (/\{[^\}]*\}$/.test(item) || index === info.template.length - 1) {
                            tempStr += item
                        } else {
                            tempStr += item + i18n.t('，')
                        }
                    })
                    info.template = tempStr.split(/\{|\}/g)
                    // 重新定义params和operators数据格式
                    info.params = info.params.reduce((acc, cur) => {
                        acc[cur.name] = {
                            value: '',
                            type: cur.type
                        }
                        return acc
                    }, {})
                    info.operators = info.operators.reduce((acc, cur) => {
                        acc[cur.name] = {
                            value: '',
                            type: cur.type
                        }
                        return acc
                    }, {})
                    // 重置可操作的变量列表
                    let typeList = new Set()
                    Object.values(info.operators).forEach(operator => {
                        typeList.add(operator.type)
                    })
                    typeList = [...typeList]
                    operateVarList = this.globalVarFiled.filter(item => typeList.includes(item.type))
                }
                this.selectOperateInfo = info || {}
                this.varFiledList = operateVarList || []
                // 重置mako模板
                this.selectVariable = ''
                this.handleVarFieldChange()
            },
            // 切换需要操作的变量
            handleVarFieldChange () {
                const { params } = this.selectOperateInfo
                Object.values(params).forEach(item => {
                    item.value = ''
                })
                this.makoTemplate = ''
            },
            // 生成mako模板
            onGenerateMakoTemp () {
                let { params, operators, mako_template: makoTemplate } = this.selectOperateInfo
                params = tools.deepClone(params)
                operators = tools.deepClone(operators)
                Object.keys(operators).forEach(key => {
                    operators[key].value = this.selectVariable
                })
                let isValidateFail = false
                const replaceObj = Object.assign({}, params, operators)
                const replaceArr = Object.keys(replaceObj).reduce((acc, key) => {
                    const values = replaceObj[key]
                    acc.push({
                        name: key,
                        value: values.value.replace(/^\$\{([^\}]*)\}$/, ($, $1) => $1)
                    })
                    if (!values.value) {
                        isValidateFail = true
                    }
                    return acc
                }, [])
                if (isValidateFail) {
                    this.isShowErrorMsg = true
                    return
                }
                this.isShowErrorMsg = false
                replaceArr.forEach(item => {
                    makoTemplate = makoTemplate.replace(`{${item.name}}`, item.value)
                })
                this.makoTemplate = makoTemplate
            },
            // 取消
            onCancel () {
                this.selectOperate = this.operationList[0].name
                this.selectVariable = ''
                this.handleVarFieldChange()
                this.isPopoverOpen = false
                this.$refs['popover'].hideHandler()
            },
            // 操作快捷框关闭判断
            handleClickOutside (e) {
                const panelDom = document.querySelector('.quick-operate-panel')
                const operateDom = document.querySelector('.operate-popover')
                const varFieldDom = document.querySelector('.variable-field-popover')
                const openPanelDom = document.querySelector('.quick-operate-btn')
                if ((!panelDom || !panelDom.contains(e.target))
                    && (!operateDom || !operateDom.contains(e.target))
                    && (!varFieldDom || !varFieldDom.contains(e.target))
                    && (!openPanelDom || !openPanelDom.contains(e.target))) {
                    this.isPopoverOpen = false
                    this.$refs['popover'].hideHandler()
                }
            },
            /**
             * 变量 key 复制
             */
            onCopyKey (key = this.makoTemplate) {
                this.copyText = key
                document.addEventListener('copy', this.copyHandler)
                document.execCommand('copy')
                document.removeEventListener('copy', this.copyHandler)
                this.copyText = ''
            },
            /**
             * 复制操作回调函数
             */
            copyHandler (e) {
                e.preventDefault()
                e.clipboardData.setData('text/html', this.copyText)
                e.clipboardData.setData('text/plain', this.copyText)
                this.$bkMessage({
                    message: i18n.t('已复制'),
                    theme: 'success'
                })
            }
        }
    }
</script>

<style lang="scss">
@import '@/scss/mixins/scrollbar.scss';
.quick-operate-popover {
    .tippy-tooltip {
        padding: 10px 24px 24px;
        border: 1px solid #dcdee5;
        background: #fff;
        box-shadow: 0 2px 6px 0 #0000001a;
        border-radius: 2px;
    }
}
.quick-operate-panel {
    background: #fff;
    z-index: 20;
    cursor: default;
    .tippy-tooltip {
        color: #666666;
        font-size: 14px;
    }
    .bk-form {
        display: flex;
        align-items: center;
        .bk-form-item {
            flex: 1;
            margin-top: 0 !important;
            .bk-label {
                font-size: 12px;
            }
            &:first-child {
                margin-right: 8px ;
            }
        }
    }
    .operate-wrap {
        width: 100%;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        margin-top: 15px;
        padding: 6px 16px 16px;
        color: #63656e;
        border: 1px solid #dcdee5;
        border-bottom: none;
        border-radius: 2px;
        .template-item {
            display: flex;
            align-items: center;
            margin-top: 10px;
            & > span {
                flex-shrink: 0;
            }
            .bk-form-control {
                width: 120px;
                margin: 0 5px;
            }
        }
    }
    .render-wrap {
        display: block;
        width: 100%;
        height: 192px;
        padding: 14px 15px;
        margin-bottom: 25px;
        line-height: 20px;
        color: #63656e;
        border: 1px solid #dcdee5;
        border-top: none;
        background: #f5f7fa;
        overflow-y: auto;
        @include scrollbar;
        &.input-before::before {
            content: attr(data-placeholder);
            color: #c4c6cc;
        }
    }
    .btn-wrap {
        display: flex;
        justify-content: flex-end;
        .error-msg {
            flex: 1;
            text-align: left;
            margin-bottom: 8px;
            font-size: 12px;
            color: #ff5757;
        }
    }
}
</style>
