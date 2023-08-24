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
                    @blur="$emit('blur')"
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
                        v-bk-clickoutside="handleClickOutSide"
                        @mouseup="handleInputMouseUp"
                        @focus="handleInputFocus"
                        @keydown="handleInputKeyDown"
                        @input="handleInputChange">
                    </div>
                </div>
                <transition>
                    <div
                        class="rf-select-list"
                        :style="varListPosition"
                        v-show="showVarList && isListOpen">
                        <ul class="rf-select-content">
                            <li
                                class="rf-select-item"
                                v-for="item in varList"
                                v-bk-overflow-tips
                                :key="item"
                                :class="{ 'is-hover': hoverKey === item }"
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
    import i18n from '@/config/i18n/index.js'
    import { mapState } from 'vuex'
    import dom from '@/utils/dom.js'
    import { getFormMixins } from '../formMixins.js'

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
            desc: i18n.t('禁用表单输入')
        },
        showPassword: {
            type: Boolean,
            required: false,
            default: false,
            desc: i18n.t('是否以密码模式显示')
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
                    value: this.value,
                    focus: false
                },
                varList: [],
                varListPosition: '',
                hoverKey: '',
                selection: {}
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
        watch: {
            isListOpen (val) {
                if (!val) {
                    this.hoverKey = ''
                    const selectDom = this.$el.querySelector('.rf-select-content')
                    selectDom.scrollTo({ top: 0 })
                }
            },
            value (val) {
                this.input.value = val
                if (!this.input.focus) {
                    this.$nextTick(() => {
                        const divInputDom = this.$el.querySelector('.div-input')
                        if (divInputDom) {
                            divInputDom.innerHTML = this.value
                        }
                    })
                }
            }
        },
        created () {
            window.addEventListener('click', this.handleListShow, false)
        },
        mounted () {
            const divInputDom = this.$el.querySelector('.div-input')
            if (divInputDom) {
                divInputDom.innerHTML = this.value
                this.handleInputBlur()
            }
        },
        beforeDestroy () {
            window.removeEventListener('click', this.handleListShow, false)
        },
        methods: {
            handleListShow (e) {
                if (!this.isListOpen) {
                    return
                }
                const parent = e.target.offsetParent
                let classList = parent ? parent.classList : null
                classList = classList && Array.from(classList.values())
                const listPanel = this.$el.querySelector('.rf-select-list')
                if (listPanel && !dom.nodeContains(listPanel, e.target) && classList[0] !== 'rf-form-wrapper') {
                    this.isListOpen = false
                }
            },
            onSelectVal (val) {
                // 替换内容
                const { focusNode, anchorOffset, previousElementSibling } = this.selection
                const divInputDom = this.$el.querySelector('.div-input')
                const { outerHTML, id } = previousElementSibling || {}
                const previousDomContent = outerHTML || ''
                // 光标左边文本内容
                let matchText = focusNode.data.slice(0, anchorOffset)
                const varRegexp = /\s?\${[a-zA-Z_][\w|.]*}\s?/g
                matchText = matchText.split(varRegexp).pop()
                // 拿到字段最后以$开头的部分
                matchText = matchText.replace(/(.*)(\$[^\}]*)/, ($0, $1, $2) => $2)
                const focusNodeContent = focusNode.data.slice(0, anchorOffset - matchText.length) + val + focusNode.data.slice(anchorOffset)
                const replaceContent = previousDomContent + focusNodeContent
                divInputDom.innerHTML = divInputDom.innerHTML.replace(previousDomContent + focusNode.data, replaceContent)
                // 更新表单
                const replacedValue = divInputDom.innerText
                this.input.value = replacedValue
                this.updateForm(replacedValue)
                // 清空/关闭
                this.isListOpen = false
                this.hoverKey = ''
                this.selection = {}
                this.input.focus = true
                // 设置光标在变量后面
                this.$nextTick(() => {
                    const selection = window.getSelection()
                    let previousDom = null
                    const textNode = Array.from(divInputDom.childNodes).find(item => {
                        const previousDomMatch = id ? id === previousDom?.id : true
                        if (previousDomMatch && item.nodeName === '#text' && item.textContent.indexOf(val) > -1) {
                            return true
                        }
                        previousDom = item
                        return false
                    })
                    selection.collapse(textNode, anchorOffset - matchText.length + val.length)
                })
            },
            // 文本框点击
            handleInputMouseUp (e) {
                if (this.isDisabled) return
                // 判断是否点到变量节点上
                let isVarTagDom = false
                const varTagDoms = this.$el.querySelectorAll('.var-tag')
                if (varTagDoms && varTagDoms.length) {
                    isVarTagDom = Array.from(varTagDoms).some(item => dom.nodeContains(item, e.target))
                }
                if (isVarTagDom) {
                    const varText = e.target.innerText
                    const divInputDom = this.$el.querySelector('.div-input')
                    // 记录光标的位置
                    const selection = window.getSelection()
                    const varTextOffset = selection.anchorOffset
                    // 上一个相邻的tag
                    const tagNodes = Array.from(divInputDom.childNodes).filter(item => item.nodeName !== '#text')
                    const index = tagNodes.findIndex(item => item.id === e.target.id)
                    const previousTagDom = tagNodes[index - 1]
                    // 替换内容
                    divInputDom.innerHTML = divInputDom.innerHTML.replace(e.target.outerHTML, varText)
                    // 变量左侧文本的长度
                    let startToVarTextLength = 0
                    let previousDom = null
                    // 选取符合条件的文本节点
                    const textNode = Array.from(divInputDom.childNodes).find(item => {
                        const previousDomMatch = previousTagDom ? previousTagDom.id === previousDom?.id : true
                        if (previousDomMatch && item.nodeName === '#text' && item.textContent.indexOf(varText) > -1) {
                            startToVarTextLength = item.textContent.split(varText)[0].length
                            return true
                        }
                        previousDom = item
                        return false
                    })
                    selection.collapse(textNode, startToVarTextLength + varTextOffset)
                } else if (this.input.value) {
                    this.handleInputChange(e)
                }
            },
            // 文本框获取焦点
            handleInputFocus (e) {
                this.input.focus = true
                const selection = window.getSelection()
                if (!this.input.value) return
                setTimeout(() => {
                    let focusSelection = null
                    const { nodeName, lastChild } = selection.focusNode
                    if (nodeName === 'DIV') {
                        focusSelection = {
                            anchorOffset: lastChild.textContent.length,
                            focusNode: lastChild
                        }
                    } else if (nodeName === '#text') {
                        focusSelection = selection
                    }
                    this.handleInputChange(e, focusSelection)
                }, 0)
            },
            // 文本框输入
            handleInputChange (e, selection) {
                if (!selection) {
                    const { innerText } = e.target
                    this.input.value = innerText
                    this.updateForm(innerText)
                }
                let matchResult = []
                const { focusNode, anchorOffset } = selection || window.getSelection()
                if (!focusNode.data) {
                    this.isListOpen = false
                    return
                }
                const offsetText = focusNode.data.substring(0, anchorOffset)
                const varRegexp = /\s?\${[a-zA-Z_][\w|.]*}\s?/g
                let matchText = offsetText.split(varRegexp).pop()
                // 拿到字段最后以$开头的部分
                matchText = matchText.replace(/(.*)(\$[^\}]*)/, ($0, $1, $2) => $2)
                // 判断是否为变量格式
                if (matchText === '$') {
                    matchResult = ['$']
                } else if (/^\${[a-zA-Z_]*[\w|.]*/.test(matchText)) {
                    matchResult = [matchText]
                }
                if (matchResult && matchResult[0]) {
                    const regStr = matchResult[0].replace(/[\$\{\}]/g, '\\$&')
                    const inputReg = new RegExp(regStr)
                    this.varList = this.constantArr.filter(item => {
                        return inputReg.test(item)
                    })
                    // 计算变量下拉列表的left
                    this.isListOpen = false
                    if (this.varList.length) {
                        const { width: inputWidth, top: inputTop } = this.$el.querySelector('.rf-form-wrap').getBoundingClientRect()
                        let previousDomWidth = 0
                        let previousDomLeft = 0
                        const { previousElementSibling } = focusNode
                        this.selection = {
                            previousElementSibling,
                            focusNode,
                            anchorOffset
                        }
                        if (previousElementSibling) {
                            previousDomWidth = previousElementSibling.offsetWidth || 0
                            previousDomLeft = previousElementSibling.offsetLeft || 0
                        }
                        const newDom = document.createElement('span')
                        newDom.innerHTML = offsetText
                        this.$el.appendChild(newDom)
                        const focusValueWidth = newDom.offsetWidth || 0
                        this.$el.removeChild(newDom)
                        let right = inputWidth - 238 - previousDomLeft - previousDomWidth - focusValueWidth
                        right = right > 0 ? right : 0
                        this.varListPositionRight = right
                        this.$nextTick(() => {
                            const { height: varListHeight } = document.querySelector('.rf-select-list').getBoundingClientRect()
                            const top = window.innerHeight < inputTop + 30 + varListHeight + 50 ? -95 : 30
                            this.varListPosition = `right: ${right}px; top: ${top}px`
                        })
                    }
                } else {
                    this.varList = []
                }
                this.isListOpen = !!this.varList.length
            },
            // 点击到input外面
            handleClickOutSide (e) {
                if (!this.input.focus) return
                const parent = e.target.offsetParent
                const classList = parent ? parent.classList : null
                const unFocus = !parent || (classList && !Array.from(classList.values()).some(key => {
                    return ['tag-input', 'tippy-tooltip', 'tippy-content', 'rf-select-list'].includes(key)
                }))
                if (unFocus && e.target.className !== 'var-tag') {
                    this.handleInputBlur()
                }
            },
            // 文本框失焦
            handleInputBlur  (e) {
                this.$emit('blur')
                this.input.focus = false
                // 支持所有变量（系统变量，内置变量，自定义变量）
                const varRegexp = /\s?\${[a-zA-Z_][\w|.]*}\s?/g
                const innerHtml = this.input.value.replace(varRegexp, (match) => {
                    if (this.constantArr.includes(match)) {
                        return `<span contenteditable="false" class="var-tag" id="${Math.random()}">${match}</span>` // 两边留空格保持间距
                    }
                    return match
                })
                const divInputDom = this.$el.querySelector('.div-input')
                divInputDom.innerHTML = innerHtml
            },
            // 文本框按键事件
            handleInputKeyDown (e) {
                switch (e.code) {
                    case 'Enter':
                    case 'NumpadEnter':
                        e.preventDefault()
                        this.handleKeyEnter()
                        break
                    case 'ArrowDown':
                    case 'ArrowUp':
                        e.preventDefault()
                        this.handleDocumentKeydown(event)
                        break
                    default:
                        return false
                }
            },
            handleKeyEnter () {
                if (!this.hoverKey) return
                this.onSelectVal(this.hoverKey)
            },
            handleDocumentKeydown (event) {
                const len = this.varList.length
                if (len) {
                    event.preventDefault()
                    event.stopPropagation()
                    let curIndex = this.varList.findIndex(item => item === this.hoverKey)
                    curIndex = event.code === 'ArrowDown' ? curIndex + 1 : curIndex - 1
                    curIndex = curIndex > len - 1 ? 0 : (curIndex < 0 ? len - 1 : curIndex)
                    const option = this.varList[curIndex]
                    if (option) {
                        this.hoverKey = option
                        const selectDom = this.$el.querySelector('.rf-select-content')
                        const hoverItemDom = selectDom.querySelector('.is-hover')
                        if (hoverItemDom) {
                            selectDom.scrollTo({
                                top: 32 * (curIndex < 3 ? 0 : curIndex - 2)
                            })
                        }
                    }
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
            top: 30px;
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
            padding: 2px 0;
            overflow: auto;
            @include scrollbar;
        }
        .rf-select-item {
            padding: 0 10px;
            line-height: 32px;
            font-size: 12px;
            cursor: pointer;
            overflow: hidden;
            text-overflow: ellipsis;
            &.is-hover,
            &:hover {
                background: #f5f7fa;
            }
        }
    }
    .rf-form-wrap {
        line-height: 32px;
        padding: 0 10px;
        border: 1px solid #c4c6cc;
        border-radius: 2px;
        &.input-focus {
            border-color: #3a84ff;
        }
        &.input-disable {
            cursor: not-allowed;
            background-color: #fafbfd;
            border-color: #dcdee5;
            .div-input {
                height: 32px;
            }
            /deep/.var-tag {
                cursor: not-allowed;
            }
        }
    }
    .div-input {
        height: 32px;
        line-height: 18px;
        padding: 7px 0;
        color: #63656e;
        white-space: nowrap;
        overflow: hidden;
        /deep/.var-tag {
            padding: 0px 4px;
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
