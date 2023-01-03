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
    <div class="tag-input">
        <div class="rf-form-wrapper">
            <template v-if="formMode">
                <el-input
                    v-if="showPassword"
                    type="text"
                    v-model="inputValue"
                    :disabled="isDisabled"
                    :show-password="showPassword"
                    :placeholder="placeholder"
                    @input="handleInputChange">
                </el-input>
                <div v-else class="rf-form-wrap" :class="{ 'input-focus': input.focus, 'input-disable': isDisabled }">
                    <div
                        ref="input"
                        class="div-input"
                        :class="{
                            'input-before': !input.value
                        }"
                        :contenteditable="!isDisabled"
                        :data-placeholder="placeholder"
                        @mouseup="handleInputMouseUp"
                        @focus="handleInputFocus"
                        @blur="handleInputBlur "
                        @keydown="handleInputKeyDown"
                        @input="handleInputChange">
                    </div>
                </div>
                <transition>
                    <div
                        class="rf-select-list"
                        :style="`left: ${varListPositionLeft}px`"
                        v-show="showVarList && isListOpen">
                        <ul class="rf-select-content">
                            <li
                                class="rf-select-item"
                                v-for="item in varList"
                                :key="item"
                                @click.stop="onSelectVal(item)">
                                {{ item }}
                            </li>
                        </ul>
                    </div>
                </transition>
            </template>
            <span v-else class="rf-view-value">{{ viewValue }}</span>
        </div>
        <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{ validateInfo.message }}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState } from 'vuex'
    import dom from '@/utils/dom.js'
    import { getFormMixins } from '../formMixins.js'

    const VAR_REG = /\$[^\}]*$/

    export const attrs = {
        placeholder: {
            type: String,
            required: false,
            default: '',
            desc: 'placeholder'
        },
        disabled: {
            type: Boolean,
            required: false,
            default: false,
            desc: gettext('禁用表单输入')
        },
        showPassword: {
            type: Boolean,
            required: false,
            default: false,
            desc: gettext('是否以密码模式显示')
        },
        value: {
            type: [String, Number],
            required: false,
            default: ''
        },
        showVarList: {
            type: Boolean,
            default: false,
            inner: true
        }
    }
    export default {
        name: 'TagInput',
        mixins: [getFormMixins(attrs)],
        data () {
            return {
                isListOpen: false,
                input: {
                    value: '',
                    focus: false
                },
                varList: [],
                varListPositionLeft: 0
            }
        },
        computed: {
            ...mapState({
                'internalVariable': state => state.template.internalVariable
            }),
            constantArr: {
                get () {
                    let Keylist = []
                    if (this.constants) {
                        Keylist = [...Object.keys(this.constants)]
                    }
                    if (this.internalVariable) {
                        Keylist = [...Keylist, ...Object.keys(this.internalVariable)]
                    }
                    return Keylist
                },
                set (val) {
                    this.varList = val
                }
            },

            inputValue: {
                get () {
                    return this.value
                },
                set (val) {
                    this.updateForm(val)
                }
            },
            viewValue () {
                if (this.value === '' || this.value === undefined) {
                    return '--'
                } else {
                    return this.showPassword ? '******' : this.value
                }
            },
            isDisabled () {
                return !this.editable || this.disable
            }
        },
        created () {
            window.addEventListener('click', this.handleListShow, false)
        },
        beforeDestroy () {
            window.removeEventListener('click', this.handleListShow, false)
        },
        methods: {
            handleListShow (e) {
                if (!this.isListOpen) {
                    return
                }
                const listPanel = document.querySelector('.rf-select-list')
                if (listPanel && !dom.nodeContains(listPanel, e.target)) {
                    this.isListOpen = false
                }
            },
            onSelectVal (val) {
                const divInputDom = document.querySelector('.tag-input .div-input')
                divInputDom.innerText = divInputDom.innerText.replace(VAR_REG, val)
                const replacedValue = this.value.replace(VAR_REG, val)
                this.input.value = replacedValue
                this.updateForm(replacedValue)
                this.isListOpen = false
                this.handleInputBlur()
            },
            // 文本框点击
            handleInputMouseUp (e) {
                // 判断是否点到变量节点上
                let isVarTagDom = false
                const varTagDoms = document.querySelectorAll('.tag-input .var-tag')
                if (varTagDoms && varTagDoms.length) {
                    isVarTagDom = Array.from(varTagDoms).some(item => dom.nodeContains(item, e.target))
                }
                if (isVarTagDom) {
                    const varText = e.target.innerText
                    const varTextHtml = `<span contenteditable="false" class="var-tag">${varText}</span>`
                    const divInputDom = document.querySelector('.tag-input .div-input')
                    // 记录光标的位置
                    const selection = window.getSelection()
                    const varTextOffset = selection.anchorOffset
                    // 替换内容
                    divInputDom.innerHTML = divInputDom.innerHTML.replace(varTextHtml, varText)
                    // 变量左侧文本的长度
                    let startToVarTextLength = 0
                    // 选取符合条件的文本节点
                    const textNode = Array.from(divInputDom.childNodes).find(item => {
                        if (item.nodeName === '#text' && item.textContent.indexOf(varText) > -1) {
                            startToVarTextLength = item.textContent.split(varText)[0].length
                            return true
                        }
                    })
                    selection.collapse(textNode, startToVarTextLength + varTextOffset)
                }
            },
            // 文本框获取焦点
            handleInputFocus () {
                this.input.focus = true
                const input = this.$refs.input
                // 设置光标到最后
                const selection = window.getSelection()
                selection.selectAllChildren(input)
                selection.collapseToEnd()
            },
            // 文本框输入
            handleInputChange (e) {
                const { innerText, innerHTML } = e.target
                this.input.value = innerText
                this.updateForm(innerText)
                const matchResult = innerText.match(VAR_REG)
                if (matchResult && matchResult[0]) {
                    const regStr = matchResult[0].replace(/[\$\{\}]/g, '\\$&')
                    const inputReg = new RegExp(regStr)
                    this.varList = this.constantArr.filter(item => {
                        return inputReg.test(item)
                    })
                    // 计算变量下拉列表的left
                    if (!this.isListOpen && this.varList.length) {
                        const newDom = document.createElement('span')
                        newDom.innerHTML = innerHTML.split(0, -1)
                        const tagInput = document.querySelector('.tag-input')
                        tagInput.appendChild(newDom)
                        let inputValueWidth = newDom.offsetWidth || 0
                        tagInput.removeChild(newDom)
                        inputValueWidth = inputValueWidth > 380 ? 380 : inputValueWidth
                        this.varListPositionLeft = inputValueWidth
                    }
                } else {
                    this.varList = []
                }
                this.isListOpen = !!this.varList.length
            },
            // 文本框失焦
            handleInputBlur  (e) {
                this.input.focus = false
                const varRegexp = /\s?\${[a-zA-Z_]\w*}\s?/g
                const innerHtml = this.input.value.replace(varRegexp, (match) => {
                    return ` <span contenteditable="false" class="var-tag">${match.trim()}</span> ` // 两边留空格保持间距
                })
                const divInputDom = document.querySelector('.tag-input .div-input')
                divInputDom.innerHTML = innerHtml
            },
            // 文本框按键事件
            handleInputKeyDown (e) {
                switch (e.code) {
                    case 'Enter':
                    case 'NumpadEnter':
                    case 'ArrowDown':
                    case 'ArrowUp':
                        e.preventDefault()
                        break
                    default:
                        return false
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';

.tag-input {
    /deep/ .el-input__inner {
        padding: 0 10px;
    }
    .rf-form-wrapper {
        position: relative;
        .rf-select-list {
            position: absolute;
            top: 40px;
            right: 0;
            width: 238px;
            background: #ffffff;
            border-radius: 2px;
            box-shadow: 0 0 8px 1px rgba(0, 0, 0, 0.1);
            overflow-y: hidden;
            z-index: 100;
        }
        .rf-select-content {
            max-height: 100px;
            overflow: auto;
            @include scrollbar;
        }
        .rf-select-item {
            padding: 0 10px;
            line-height: 32px;
            font-size: 12px;
            cursor: pointer;
            &:hover {
                background: #eef6fe;
                color: #3a84ff;
            }
        }
    }
    .rf-form-wrap {
        line-height: 32px;
        padding: 0 10px;
        border: 1px solid #c4c6cc;
        border-radius: 2px;
        margin-top: 20px;
        &.input-focus {
            border-color: #3a84ff;
        }
        &.input-disable {
            cursor: not-allowed;
            background-color: #fafbfd;
            border-color: #dcdee5;
        }
    }
    .div-input {
        color: #63656e;
        white-space: nowrap;
        overflow: hidden;
        /deep/.var-tag {
            line-height: 20px;
            padding: 1px 4px;
            background: #f0f1f5;
            cursor: pointer;
            &:hover {
                background: #eaebf0;
            }
        }
        &.input-before::before {
            content: attr(data-placeholder);
            color: #c4c6cc;
        }
    }
}
</style>
