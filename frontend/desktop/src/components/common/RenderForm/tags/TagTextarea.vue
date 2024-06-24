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
    <div class="tag-textarea">
        <div class="rf-form-wrapper">
            <template v-if="formMode">
                <div class="rf-form-wrap" :class="{ 'input-focus': input.focus, 'input-disable': isDisabled }">
                    <div
                        ref="input"
                        class="div-input"
                        :class="{
                            'input-before': !input.value && !pasteIng
                        }"
                        :contenteditable="!isDisabled"
                        :data-placeholder="placeholder"
                        data-test-name="formTag_textarea_divInput"
                        v-bk-clickoutside="handleClickOutSide"
                        @mouseup="handleInputMouseUp"
                        @focus="handleInputFocus"
                        @keydown="handleInputKeyDown"
                        @input="handleInputChange"
                        @blur="handleBlur">
                    </div>
                </div>
                <transition>
                    <div
                        class="rf-select-list"
                        :style="`${varListPosition}`"
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
        <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import i18n from '@/config/i18n/index.js'
    import { mapState } from 'vuex'
    import dom from '@/utils/dom.js'
    import { getFormMixins } from '../formMixins.js'

    export const attrs = {
        value: {
            type: [String, Object],
            required: false,
            default: ''
        },
        disabled: {
            type: Boolean,
            required: false,
            default: false,
            desc: i18n.t('禁用组件')
        },
        placeholder: {
            type: String,
            required: false,
            default: '',
            desc: 'placeholder'
        },
        showVarList: {
            type: Boolean,
            default: false,
            inner: true
        }
    }
    export default {
        name: 'TagTextarea',
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
                lastEditRange: null,
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
            viewValue () {
                if (this.value === '' || this.value === undefined) {
                    return '--'
                }
                return this.value
            },
            isDisabled () {
                return !this.editable || !this.formMode || this.disable || this.scheme.attrs?.disabled
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
            }
        },
        created () {
            window.addEventListener('click', this.handleListShow, false)
        },
        mounted () {
            const divInputDom = this.$el.querySelector('.div-input')
            if (divInputDom) {
                const value = typeof this.value === 'string' ? this.value : JSON.stringify(this.value)
                divInputDom.innerText = value
                if (this.render && value) {
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
                        return Array.from(node.childNodes).some(child => {
                            if (child.id === e.target.id) {
                                node.replaceChild(varTextNode, child)
                                return true
                            }
                        })
                    })
                    const selection = window.getSelection()
                    const range = document.createRange()
                    range.selectNodeContents(varTextNode)
                    range.setStart(varTextNode, varTextNode.length)
                    range.collapse(true)
                    selection.removeAllRanges()
                    selection.addRange(range)
                } else if (this.input.value) {
                    this.handleInputChange(e, false)
                }
            },
            // 文本框获取焦点
            handleInputFocus (e) {
                this.input.focus = true
            },
            // 文本框输入
            handleInputChange (e, updateForm = true) {
                if (this.pasteIng) return
                if (updateForm) {
                    // 实时更新
                    this.updateInputValue()
                }
                const range = window.getSelection().getRangeAt(0)
                this.lastEditRange = range
                const { startContainer: textNode, startOffset } = range
                const textValue = textNode.textContent
                // 如果光标所在元素没有内容则不进行后续操作
                if (!textValue) return
                let previousText
                if (textNode.nodeName === '#text') {
                    previousText = textValue.slice(0, startOffset)
                } else if (textNode.nodeName === 'DIV') {
                    const lastNode = textNode.childNodes[startOffset - 1]
                    previousText = lastNode.textContent
                }
                // 如果不包含$则不进行后续计算、 如果是完整全局变量则不进行后续操作
                if (previousText.indexOf('$') === -1 || /\${[a-zA-Z_][\w|.]*}/.test(previousText)) {
                    this.isListOpen = false
                    return
                }
                const matchText = previousText.replace(/(.*)(\$[^\}]*)/, ($0, $1, $2) => $2)
                // 判断是否为变量格式
                if (matchText === '$' || /^\${[a-zA-Z_]*[\w|.]*/.test(matchText)) {
                    this.varList = this.constantArr.filter(item => item.key.indexOf(matchText) > -1)
                    // 计算变量下拉列表的坐标
                    this.isListOpen = false
                    if (this.varList.length) {
                        const { top: textNodeTop, width } = textNode.parentNode.getBoundingClientRect()
                        const { width: inputWidth, top: inputTop } = this.$el.querySelector('.rf-form-wrap').getBoundingClientRect()
                        let previousDomWidth = 0
                        let previousDomLeft = 0
                        const { previousSibling, previousElementSibling } = textNode
                        if (previousSibling) {
                            if (previousSibling.nodeName === '#text') {
                                previousText = previousSibling.textContent + previousText
                                if (previousElementSibling && previousElementSibling.nodeName !== '#text') {
                                    previousDomWidth = previousElementSibling.offsetWidth || 0
                                    previousDomLeft = previousElementSibling.offsetLeft || 0
                                }
                            } else {
                                previousDomWidth = previousElementSibling.offsetWidth || 0
                                previousDomLeft = previousElementSibling.offsetLeft || 0
                            }
                        }
                        const newDom = document.createElement('span')
                        newDom.style.maxWidth = `${width}px`
                        newDom.style.lineHeight = '18px'
                        newDom.style.display = 'inline-block'
                        newDom.innerHTML = previousText
                        this.$el.appendChild(newDom)
                        const focusValueWidth = newDom.offsetWidth || 0
                        const focusValueHeight = newDom.offsetHeight || 0
                        this.$el.removeChild(newDom)
                        this.$nextTick(() => {
                            const { height: varListHeight, width: varListWidth } = this.$el.querySelector('.rf-select-list').getBoundingClientRect()
                            let popLeft = previousDomLeft + previousDomWidth + focusValueWidth
                            if (popLeft > inputWidth - varListWidth) {
                                popLeft = inputWidth - varListWidth
                            }
                            let popTop = textNodeTop - inputTop + focusValueHeight + 2 // 2px是为了使光标和联想列表隔开
                            if (window.innerHeight < textNodeTop + focusValueHeight + varListHeight + 50) {
                                popTop = textNodeTop - inputTop - varListHeight - 2
                            }
                            this.varListPosition = `left: ${popLeft}px; top: ${popTop}px`
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
                    return ['tag-textarea', 'tippy-tooltip', 'tippy-content', 'rf-select-list'].includes(key)
                }))
                if (unFocus && e.target.className !== 'var-tag') {
                    this.handleInputBlur()
                }
            },
            updateInputValue () {
                const divInputDom = this.$el.querySelector('.div-input')
                const childNodes = Array.from(divInputDom.childNodes).filter(item => item.nodeName !== 'TEXT')
                const inputValue = childNodes.map(dom => {
                    // 获取行内纯文本
                    let domValue = dom.textContent
                    if (dom.childNodes.length) {
                        domValue = Array.from(dom.childNodes).map(item => {
                            return item.type === 'button'
                                ? item.value
                                : item.nodeName === 'BR'
                                    ? ''
                                    : item.textContent
                        }).join('')
                    }
                    return domValue.replace(/\u00A0/g, ' ')
                }).join('\n')
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
                const divInputDom = this.$el.querySelector('.div-input')
                const childNodes = Array.from(divInputDom.childNodes).filter(item => item.nodeName !== 'TEXT')
                const deleteMap = {} // 需要删除的br下标
                childNodes.forEach((dom, index) => {
                    // 删除多余的br标签
                    if (deleteMap[index]) {
                        divInputDom.removeChild(dom)
                        return
                    }
                    // 获取行内纯文本
                    let domValue = dom.textContent
                    if (dom.childNodes.length) {
                        domValue = Array.from(dom.childNodes).map(item => {
                            return item.type === 'button' ? item.value : item.textContent
                        }).join('')
                    }
                    // 将html标签拆成文本形式
                    domValue = domValue.replace(/(<|>)/g, ($0, $1) => `<span>${$1}</span>`)
                    // 用户手动输入的实体字符渲染时需要切开展示
                    domValue = domValue.replace(/&(nbsp|ensp|emsp|thinsp|zwnj|zwj|quot|apos|lt|gt|amp|cent|pound|yen|euro|sect|copy|reg|trade|times|divide);/g, ($0, $1) => {
                        return `<span>&</span><span>${$1}</span><span>;</span>`
                    })

                    // 初始化时是通过innerText进行复制的，如果有多个连续空格则只会显示一个，所以需手动将转为&nbsp;
                    domValue = domValue.replace(/( )/g, '&nbsp;')
                    // 支持匹配变量内运算
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
                            return `<input type="button" class="var-tag" id="tag_${randomId}" value="${value}" />`
                        }
                        return match
                    })
                    // 初始化时\n会转化为【独占一行】的<br>标签，导致渲染异常。当我们手动把text标签转为div标签时需要删除【紧挨】着的<br>标签
                    if (dom.nodeName === '#text') {
                        // 记录需要被删除的br标签下标
                        if (dom.nextSibling?.nodeName === 'BR') {
                            deleteMap[index + 1] = true
                        }
                        const newDom = document.createElement('div')
                        newDom.innerHTML = innerHtml
                        divInputDom.replaceChild(newDom, dom)
                    } else if (dom.nodeName === 'DIV' && innerHtml) {
                        dom.innerHTML = innerHtml
                    } else if (dom.nodeName === 'BR') {
                        // br标签实际上是初始化时\n转化的，\n表示当前行换行了，那么br标签必定会有下一行!!!
                        if (!dom.nextSibling) {
                            const appendDom = document.createElement('div')
                            appendDom.innerHTML = '<br>'
                            divInputDom.appendChild(appendDom)
                        }
                        const newDom = document.createElement('div')
                        newDom.innerHTML = '<br>'
                        divInputDom.replaceChild(newDom, dom)
                    }
                })
            },
            // 文本框按键事件
            handleInputKeyDown (e) {
                switch (e.code) {
                    case 'Enter':
                    case 'NumpadEnter':
                        if (this.isListOpen) {
                            e.preventDefault()
                            this.handleKeyEnter()
                        }
                        break
                    case 'ArrowDown':
                    case 'ArrowUp':
                        if (this.isListOpen) {
                            e.preventDefault()
                            this.handleDocumentKeydown(e)
                        }
                        break
                    case 'Backspace':
                        this.handleDocumentBackspace(e)
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
            handleDocumentBackspace (event) {

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
                    text = text.replace(/(\r|\r\n)/g, '')
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
                    text = text.replace(/(\r|\r\n)/g, '')
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
.tag-textarea {
    .rf-form-wrapper {
        position: relative;
        .rf-select-list {
            position: absolute;
            top: 40px;
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
        padding: 5px 10px;
        border: 1px solid #c4c6cc;
        border-radius: 2px;
        &.input-focus {
            border-color: #3a84ff;
        }
        &.input-disable {
            cursor: not-allowed;
            background-color: #fafbfd;
            border-color: #dcdee5;
            /deep/.var-tag {
                cursor: not-allowed;
            }
        }
    }
    .div-input {
        min-height: 36px;
        max-height: 300px;
        line-height: 18px;
        color: #63656e;
        outline: 0;
        word-wrap: break-word;
        overflow-x: hidden;
        overflow-y: auto;
        /deep/.var-tag {
            padding: 0px 4px;
            margin-right: 1px;
            background: #f0f1f5;
            cursor: pointer;
            white-space: nowrap;
            border: none;
            user-select: auto;
            &:hover {
                background: #eaebf0;
            }
        }
        /deep/div {
            word-break: break-all;
        }
        &.input-before::before {
            content: attr(data-placeholder);
            color: #c4c6cc;
        }
    }
    /deep/.div-input {
        >div {
            width: 100%;
        }
    }
}
</style>
