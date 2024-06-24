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
                    @input="handleInputChange"
                    @blur="handleBlur">
                </el-input>
                <div v-else class="rf-form-wrap" :class="{ 'input-focus': input.focus, 'input-disable': isDisabled }">
                    <div
                        ref="input"
                        class="div-input"
                        :class="{
                            'input-before': !input.value && !pasteIng
                        }"
                        :contenteditable="!isDisabled"
                        :data-placeholder="placeholder"
                        data-test-name="formTag_input_divInput"
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
                                :key="item.key"
                                :class="{ 'is-hover': hoverKey === item.key }"
                                @click.stop="onSelectVal(item.key)">
                                <span class="key">{{ item.key }}</span>
                                <span class="name" v-bk-overflow-tips>{{ item.name }}</span>
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
                selection: {},
                pasteIng: false // 粘贴中
            }
        },
        computed: {
            ...mapState({
                'internalVariable': state => state.template.internalVariable
            }),
            constantArr: {
                get () {
                    let KeyList = []
                    if (this.constants) {
                        KeyList = [...Object.values(this.constants)]
                    }
                    if (this.internalVariable) {
                        KeyList = [...KeyList, ...Object.values(this.internalVariable)]
                    }
                    return KeyList
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
                            divInputDom.innerText = this.value
                            this.updateInputHtml()
                        }
                    })
                }
            },
            render (val) {
                // 如果表单项开启了变量免渲染，不以tag展示
                if (!val) {
                    const divInputDom = this.$el.querySelector('.div-input')
                    divInputDom.innerText = this.value
                } else {
                    this.updateInputHtml()
                }
            },
            formMode (val) {
                if (val) {
                    this.$nextTick(() => {
                        const divInputDom = this.$el.querySelector('.div-input')
                        divInputDom.innerText = this.value
                        this.updateInputHtml()
                    })
                } else {
                    this.validate()
                }
            }
        },
        created () {
            window.addEventListener('click', this.handleListShow, false)
        },
        mounted () {
            const divInputDom = this.$el.querySelector('.div-input')
            if (divInputDom) {
                divInputDom.innerText = this.value
                if (this.render && this.value) {
                    this.updateInputHtml()
                }
                divInputDom.addEventListener('paste', this.handlePaste)
            }
        },
        beforeDestroy () {
            window.removeEventListener('click', this.handleListShow, false)
            const divInputDom = this.$el.querySelector('.div-input')
            if (divInputDom) {
                divInputDom.removeEventListener('paste', this.handlePaste)
            }
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
                // 获取选定对象
                const selection = getSelection()
                // 如果保存的有上次的光标对象
                if (this.lastEditRange) {
                    // 清除所有选区
                    selection.removeAllRanges()
                    // 添加最后光标还原之前的状态
                    selection.addRange(this.lastEditRange)
                }
                const range = selection.getRangeAt(0)
                const textNode = range.startContainer
                const rangeStartOffset = range.startOffset
                // 匹配光标前内容最后面变量部分
                const previousText = textNode.textContent.slice(0, rangeStartOffset)
                const matchText = previousText.replace(/(.*)(\$[^\}]*)/, ($0, $1, $2) => $2)
                // 需要补全的变量
                const addText = val.replace(matchText, '')
                textNode.insertData(rangeStartOffset, addText)
                range.setStart(textNode, rangeStartOffset + addText.length)
                // 将选区折叠为一个光标
                range.collapse(true)
                selection.removeAllRanges()
                selection.addRange(range)
                // 更新表单
                this.updateInputValue()
                // 清空/关闭
                this.isListOpen = false
                this.hoverKey = ''
                this.selection = {}
                this.input.focus = true
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
                    const varText = e.target.value
                    const divInputDom = this.$el.querySelector('.div-input')
                    const varTextNode = document.createTextNode(varText)
                    // 替换内容
                    Array.from(divInputDom.childNodes).some(node => {
                        if (node.id === e.target.id) {
                            divInputDom.replaceChild(varTextNode, node)
                            return true
                        }
                    })
                    const selection = window.getSelection()
                    const range = document.createRange()
                    range.selectNodeContents(varTextNode)
                    range.setStart(varTextNode, varTextNode.length)
                    range.collapse(true)
                    selection.removeAllRanges()
                    selection.addRange(range)
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
                if (this.pasteIng) return
                if (!selection) {
                    // 实时更新
                    this.updateInputValue()
                }
                let matchResult = []
                const { focusNode, anchorOffset } = selection || window.getSelection()
                if (!focusNode.data) {
                    this.isListOpen = false
                    return
                }
                // 获取文本
                this.lastEditRange = window.getSelection().getRangeAt(0)
                const offsetText = focusNode.data.substring(0, anchorOffset)
                let matchText = offsetText

                // 如果不包含$则不进行后续计算
                if (matchText.indexOf('$') === -1) {
                    this.isListOpen = false
                    return
                }

                // 过滤掉完整的变量格式文本
                const varRegexp = /\s?\${[a-zA-Z_][\w|.]*}\s?/g
                if (varRegexp.test(matchText)) {
                    matchText = offsetText.split(varRegexp).pop()
                }
                // 拿到字段最后以$开头的部分
                matchText = matchText.replace(/(.*)(\$[^\}]*)/, ($0, $1, $2) => $2)
                // 判断是否为变量格式
                if (matchText === '$') {
                    matchResult = ['$']
                } else if (/^\${[a-zA-Z_]*[\w|.]*/.test(matchText)) {
                    matchResult = [matchText]
                }
                if (matchResult && matchResult[0]) {
                    this.varList = this.constantArr.filter(item => item.key.indexOf(matchText) > -1)
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
                        this.$nextTick(() => {
                            const { width: varListWidth, height: varListHeight } = this.$el.querySelector('.rf-select-list').getBoundingClientRect()
                            let right = inputWidth - varListWidth - previousDomLeft - previousDomWidth - focusValueWidth
                            right = right > 0 ? right : 0
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
            updateInputValue () {
                // 获取行内纯文本
                const divInputDom = this.$el.querySelector('.div-input')
                let inputValue = divInputDom.textContent
                inputValue.replace(' ', ' ')
                if (divInputDom.childNodes.length) {
                    inputValue = Array.from(divInputDom.childNodes).map(item => {
                        return item.type === 'button'
                            ? item.value
                            : item.textContent.trim() === ''
                                ? ' '
                                : item.textContent
                    }).join('')
                }
                inputValue = inputValue.replace(/\u00A0/g, ' ')
                this.input.value = inputValue
            },
            // 文本框失焦
            handleInputBlur  (e) {
                this.$emit('blur', this.input.value)
                this.input.focus = false
                // 更新文本框结构，生成tag标签
                this.updateInputHtml()
                // 向上更新表单
                this.updateForm(this.input.value)
            },
            // 更新文本框结构，生成tag标签
            updateInputHtml () {
                // 如果表单项开启了变量免渲染，不以tag展示
                if (!this.render) return
                // 支持所有变量（系统变量，内置变量，自定义变量）
                const varRegexp = /\${([^${}]+)}/g
                // 获取行内纯文本
                const divInputDom = this.$el.querySelector('.div-input')
                let domValue = divInputDom.textContent
                if (divInputDom.childNodes.length) {
                    domValue = Array.from(divInputDom.childNodes).map(item => {
                        return item.type === 'button' ? item.value : item.textContent
                    }).join('')
                }
                // 将html标签拆成文本形式
                domValue = domValue.replace(/(<|>)/g, ($0, $1) => `<span>${$1}</span>`)
                // 用户手动输入的实体字符渲染时需要切开展示
                domValue = domValue.replace(/&(nbsp|ensp|emsp|thinsp|zwnj|zwj|quot|apos|lt|gt|amp|cent|pound|yen|euro|sect|copy|reg|trade|times|divide);/g, ($0, $1) => {
                    return `<span>&</span><span>${$1}</span><span>;</span>`
                })

                const innerHtml = domValue.replace(varRegexp, (match, $0) => {
                    let isExistVar = false
                    if ($0) {
                        isExistVar = this.constantArr.some(item => {
                            const varText = item.key.slice(2, -1)
                            if ($0.indexOf(varText) > -1) {
                                const regexp = new RegExp(`^(.*\\W|\\W)?${varText}(\\W|\\W.*)?$`)
                                return regexp.test($0)
                            }
                        })
                    }
                    if (isExistVar) {
                        const randomId = Math.random().toString().slice(-6)
                        // 将装转的尖括号恢复原样
                        let value = match.replace(/<span>(<|>)<\/span>/g, ($0, $1) => $1)
                        // 将双引号转为实体字符
                        value = value.replace(/"/g, '&quot;')
                        return `<input type="button" class="var-tag" id="${randomId}" value="${value}" />`
                    }
                    return match
                })
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
                    let curIndex = this.varList.findIndex(item => item.key === this.hoverKey)
                    curIndex = event.code === 'ArrowDown' ? curIndex + 1 : curIndex - 1
                    curIndex = curIndex > len - 1 ? 0 : (curIndex < 0 ? len - 1 : curIndex)
                    const option = this.varList[curIndex]
                    if (option) {
                        this.hoverKey = option.key
                        const selectDom = this.$el.querySelector('.rf-select-content')
                        const hoverItemDom = selectDom.querySelector('.is-hover')
                        if (hoverItemDom) {
                            selectDom.scrollTo({
                                top: 32 * (curIndex < 3 ? 0 : curIndex - 2)
                            })
                        }
                    }
                }
            },
            handleBlur () {
                this.emit_event(this.tagCode, 'blur', this.value)
                this.$emit('blur', this.value)
            },
            async handlePaste (e) {
                event.preventDefault()
                let text = ''
                const clp = (e.originalEvent || e).clipboardData
                if (clp === undefined || clp === null) {
                    text = window.clipboardData.getData('text') || ''
                    text = text.replace(/(\n|\r|\r\n)/g, ' ')
                    if (text !== '') {
                        if (window.getSelection) {
                            const newNode = document.createElement('span')
                            newNode.innerHTML = text
                            window.getSelection().getRangeAt(0).insertNode(newNode)
                        } else {
                            document.selection.createRange().pasteHTML(text)
                        }
                    }
                } else {
                    text = clp.getData('text/plain') || ''
                    text = text.replace(/(\n|\r|\r\n)/g, ' ')
                    this.pasteIng = true
                    await this.insertTextAsync(text)
                    this.pasteIng = false
                    this.handleInputChange(e)
                }
            },
            async insertTextAsync (text) {
                const chunkSize = 1000
                for (let i = 0; i < text.length; i += chunkSize) {
                    const part = text.slice(i, i + chunkSize)
                    // 创建一个Promise用于管理setTimeout的异步行为
                    await new Promise((resolve) => setTimeout(() => {
                        document.execCommand('insertText', false, part)
                        resolve()
                    }, 0))
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
            max-width: 600px;
            background: #ffffff;
            border: 1px solid #dcdee5;
            border-radius: 2px;
            box-shadow: 0 3px 9px 0 rgba(0,0,0,.1);
            overflow-y: hidden;
            z-index: 100;
            .name {
                color: #c4c6cc;
                margin-left: 16px;
            }
        }
        .rf-select-content {
            max-height: 100px;
            padding: 2px 0;
            overflow: auto;
            @include scrollbar;
        }
        .rf-select-item {
            display: flex;
            align-items: center;
            padding: 0 10px;
            line-height: 32px;
            font-size: 12px;
            cursor: pointer;
            > span {
                flex-shrink: 0;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
            }
            .name {
                max-width: 250px;
            }
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
        white-space: pre;
        overflow: hidden;
        /deep/.var-tag {
            margin-right: 1px;
            padding: 0px 4px;
            background: #f0f1f5;
            cursor: pointer;
            border: none;
            user-select: auto;
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
