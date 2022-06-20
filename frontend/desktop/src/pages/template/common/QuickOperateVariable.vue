/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div
        class="quick-operate-panel"
        v-bkloading="{ isLoading: isPanelLoading }"
        @click.stop>
        <div class="header-wrap">
            <span>{{ $t('选择操作') }}</span>
            <bk-select v-model="selectOperate" ext-popover-cls="operate-popover" @change="handleOperateChange">
                <bk-option
                    v-for="(operate, index) in operationList"
                    :key="index"
                    :id="operate.name"
                    :name="operate.name">
                </bk-option>
            </bk-select>
        </div>
        <div class="operate-wrap" @click="isShowErrorMsg = false">
            <div
                class="template-item"
                v-for="(template, index) in selectOperateInfo.template"
                :key="index">
                <template v-if="selectOperateInfo.operators[template]">
                    <bk-select
                        v-model="selectOperateInfo.operators[template].value"
                        ext-popover-cls="variable-field-popover"
                        @change="handleVarFieldChange">
                        <bk-option
                            v-for="(field, fieldIndex) in varFiledList"
                            :key="fieldIndex"
                            :id="field.key"
                            :name="field.key + $t('（') + field.description + $t('）')">
                        </bk-option>
                    </bk-select>
                </template>
                <template v-else-if="selectOperateInfo.params[template]">
                    <bk-input v-model="selectOperateInfo.params[template].value"></bk-input>
                </template>
                <template v-else>
                    <span>{{ template }}</span>
                </template>
            </div>
        </div>
        <p v-if="isShowErrorMsg" class="error-msg">{{ $t('请填写完整参数') }}</p>
        <div class="btn-wrap">
            <bk-button class="mr5" theme="primary" @click="onGenerateMakoTemp">{{ $t('生成并复制代码') }}</bk-button>
            <bk-button @click="onResetMakoTemp">{{ $t('重置') }}</bk-button>
        </div>
        <div class="render-wrap">{{ makoTemplate }}</div>
    </div>
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
                operationList: [],
                selectOperateInfo: {},
                globalVarFiled: [],
                varFiledList: [],
                isShowErrorMsg: false,
                makoTemplate: ''
            }
        },
        computed: {
            ...mapState({
                'internalVariable': state => state.template.internalVariable
            })
        },
        created () {
            this.handleQuickInsertPanel()
        },
        mounted () {
            window.addEventListener('mouseup', this.handleClickOutside)
        },
        beforeDestroy () {
            this.selectOperate = ''
            this.onResetMakoTemp()
            window.removeEventListener('mouseup', this.handleClickOutside)
        },
        methods: {
            ...mapActions('template/', [
                'getMakoOperations',
                'getVariableFieldExplain'
            ]),
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
                this.onResetMakoTemp()
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
                replaceArr.forEach(item => {
                    makoTemplate = makoTemplate.replace(`{${item.name}}`, item.value)
                })
                this.makoTemplate = makoTemplate
                this.onCopyKey(makoTemplate)
            },
            // 重置mako模板
            onResetMakoTemp () {
                Object.values(this.selectOperateInfo.operators).forEach(item => {
                    item.value = ''
                })
                this.handleVarFieldChange()
            },
            // 操作快捷框关闭判断
            handleClickOutside (e) {
                const panelDom = document.querySelector('.quick-operate-panel')
                const operateDom = document.querySelector('.operate-popover')
                const varFieldDom = document.querySelector('.variable-field-popover')
                if ((!panelDom || !panelDom.contains(e.target))
                    && (!operateDom || !operateDom.contains(e.target))
                    && (!varFieldDom || !varFieldDom.contains(e.target))) {
                    this.$emit('closePanel')
                }
            },
            /**
             * 变量 key 复制
             */
            onCopyKey (key) {
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
.quick-operate-panel {
    position: absolute !important;
    top: 45px;
    right: 0px;
    width: 506px;
    padding: 16px;
    background: #fff;
    z-index: 20;
    border: 1px solid #eaedf2;
    box-shadow: 0px 2px 6px 0px rgba(101,101,101,0.10);
    cursor: default;
    .tippy-tooltip {
        padding: 16px;
        color: #666666;
        font-size: 14px;
    }
    .header-wrap {
        display: flex;
        align-items: center;
        padding-bottom: 16px;
        border-bottom: 1px solid #dcdee5;
        .bk-select {
            flex: 1;
            margin-left: 8px;
        }
    }
    .operate-wrap {
        width: 100%;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        margin: 5px 0 25px;
        .template-item {
            display: flex;
            align-items: center;
            margin-top: 10px;
            & > span {
                flex-shrink: 0;
            }
            .bk-select {
                width: 300px;
                margin: 0 5px;
            }
            .bk-form-control {
                width: 100px;
                margin: 0 5px;
            }
        }
    }
    .error-msg {
        margin-bottom: 8px;
        font-size: 12px;
        color: #ff5757;
    }
    .render-wrap {
        width: 474px;
        height: 192px;
        padding: 9px 15px;
        margin-top: 8px;
        color: #979ba5;
        background: #f0f1f5;
        border-radius: 4px;
        overflow-y: auto;
        @include scrollbar;
    }
}
</style>
