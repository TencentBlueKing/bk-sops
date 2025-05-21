<template>
    <div class="render-input-wrap">
        <div
            ref="input"
            class="div-input"
            contenteditable="plaintext-only"
            @focus="handleInputFocus"
            @blur="handleInputBlur"
            @input="handleInputChange"
            @keydown="handleInputKeyup">
        </div>
        <p v-if="isShowPlaceholder" class="data-placeholder">
            {{ placeholder }}
        </p>
        <div class="input-icons">
            <span
                v-if="isShowClearIcon"
                class="bk-icon icon-close-circle-shape"
                @click="handleClear">
            </span>
            <span
                v-else
                :class="['bk-icon icon-search', { 'is-focus': focused }]"
                @click="handleKeyEnter">
            </span>
        </div>
    </div>
</template>
<script>

    const Symbol = {
        label: '：',
        multiple: ' | '
    }

    export default {
        name: '',
        props: {
            searchValue: {
                type: Array,
                default: () => ([])
            },
            searchList: {
                type: Array,
                default: () => ([])
            },
            placeholder: {
                type: String,
                default: ''
            },
            focused: {
                type: Boolean,
                default: false
            },
            menuOptionList: {
                type: Array,
                default: () => ([])
            },
            selectedOption: {
                type: Object,
                default: () => ({})
            },
            selectedOptionValue: {
                type: Array,
                default: () => ([])
            }
        },
        data () {
            return {
                localValue: '',
                hoverId: ''
            }
        },
        computed: {
            isShowPlaceholder () {
                return !this.searchValue.length
                    && !this.selectedOption.id
                    && !this.localValue
            },
            isShowClearIcon () {
                return this.searchValue.length || this.localValue || this.selectedOption.id
            }
        },
        watch: {
            selectedOption (val) {
                const text = val.id ? `${val.name}${Symbol.label}` : ''
                this.setInputValue(text)
            },
            localValue (val) {
                this.$emit('input', val)
            },
            selectedOptionValue (val) {
                //  非多选时，选中值后直接保存
                if (!this.selectedOption.multiple && val.length === 1) {
                    this.$emit('update', {
                        ...this.selectedOption,
                        values: [val[0]]
                    })
                    // 初始化数据
                    this.init()
                } else {
                    const { id, name } = this.selectedOption
                    const valueText = val.map(item => item.name).join(Symbol.multiple)
                    const text = id ? `${name}${Symbol.label}${valueText}` : ''
                    this.setInputValue(text)
                }
            },
            hoverId (val) {
                this.$emit('updateHoverId', val)
            }
        },
        mounted () {
            
        },
        methods: {
            init () {
                this.hoverId = ''
                this.localValue = ''
                this.setInputValue('')
            },
            focus () {
                this.$refs.input.focus()
            },
            blur () {
                this.$refs.input.blur()
            },
            setInputValue (val) {
                this.$refs.input.innerText = val
                // 更新localValue
                this.setLocalValue(val)
                // 获取焦点
                this.focus()
                // 设置文本框焦点显示位置
                this.setSelection()
            },
            setSelection () {
                const input = this.$refs.input
                let selection = null
                if (window.getSelection) {
                    selection = window.getSelection()
                    selection.selectAllChildren(input)
                    selection.collapseToEnd()
                } else if (document.onselectionchange) {
                    selection = document.onselectionchange.createRange()
                    selection.moveToElementText(input)
                    selection.collapse(false)
                    selection.select()
                }
            },
            handleInputFocus () {
                this.$emit('update:focused', true)
            },
            handleInputBlur () {
                this.hoverId = ''
                this.$emit('update:focused', false)
            },
            getInputLabelRegex (name) {
                return new RegExp(`^${name}${Symbol.label}`)
            },
            setLocalValue (text) {
                const regex = this.getInputLabelRegex(this.selectedOption.name)
                this.localValue = regex.test(text)
                    ? text.slice(text.indexOf(Symbol.label) + 1)
                    : text.trim()
            },
            handleInputChange (e) {
                const text = e.target.innerText

                if (this.selectedOption.id) {
                    this.setLocalValue(text)
                    return
                }

                this.localValue = text.trim()
            },
            handleInputKeyup (e) {
                switch (e.code) {
                    case 'Enter':
                    case 'NumpadEnter':
                        this.handleKeyEnter(e)
                        break
                    case 'Backspace':
                        this.handleKeyBackspace(e)
                        break
                    case 'ArrowDown':
                    case 'ArrowUp':
                        e.preventDefault()
                        this.handleDocumentKeydown(e)
                        break
                    default:
                        // 如果选择了值则禁止键盘默认事件
                        if (this.selectedOptionValue.length) {
                            e.preventDefault()
                        }
                        return false
                }
            },
            handleKeyEnter (e) {
                e.preventDefault()
                // setTimeout用在使用中文输入法不空格直接回车时，生成的tag和input.value会同时存在
                setTimeout(() => {
                    const { id: optionId, children, isUser } = this.selectedOption

                    // 选择上下键选中的选项
                    if (this.hoverId) {
                        this.handleHoverSelection()
                        return
                    }

                    if (!this.localValue) return

                    if (optionId) {
                        const index = this.searchValue.findIndex(item => item.id === optionId)
                        // 如果该选项已被选中，则更新对应tag
                        if (index > -1) {
                            const searchContent = this.searchValue[index]
                            const isMatch = searchContent.values.some(item => item === this.localValue)
                            isMatch && searchContent.values.push(this.localValue)
                        } else {
                            // 当包含子项时，输入值不存在匹配项是禁止回车
                            if (children || (isUser && window.ENABLE_MULTI_TENANT_MODE)) {
                                const isMatch = this.menuOptionList.some(item => item.name === this.localValue)
                                if (!isMatch) return
                            }

                            this.$emit('update', {
                                ...this.selectedOption,
                                values: [this.localValue]
                            })
                        }
                    } else {
                        // 检查是否存在默认选项且未被选中
                        const defaultOption = this.searchList.find(item => item.isDefaultOption)
                        if (defaultOption) {
                            const isMatch = this.searchValue.some(item => item.isDefaultOption)
                            !isMatch && this.$emit('update', {
                                ...defaultOption,
                                values: [this.localValue]
                            })
                        } else {
                            return
                        }
                    }
                    // 回车成功，初始化数据
                    this.init()
                }, 100)
            },
            handleHoverSelection () {
                const { id: optionId, multiple } = this.selectedOption
                const option = this.menuOptionList.find(item => item.id === this.hoverId)
                if (!option) return

                if (!multiple) this.hoverId = '' // 多选需要选中、取消选中

                // 已选择条件选项
                if (optionId) {
                    this.$emit('switchOption', option) // 新增或移除选项值
                } else if (this.localValue) {
                    // 如果有值直接创建tag
                    this.$emit('update', {
                        ...option,
                        values: [this.localValue]
                    })
                } else {
                    // 选择条件选项
                    this.$emit('update:selectedOption', option)
                }
            },
            handleKeyBackspace (e) {
                const text = e.target.innerText

                const { id, name, multiple } = this.selectedOption
                // 多选时回退则删除最后一个选项
                if (multiple && this.selectedOptionValue.length) {
                    e.preventDefault()
                    this.$emit('update:selectedOptionValue', this.selectedOptionValue.slice(0, -1))
                } else if (!text && this.searchValue.length) {
                    // 空值时回退如果已存在搜索值则删除最后一个搜索条件
                    this.$emit('update:searchValue', this.searchValue.slice(0, -1))
                } else if (text && id) {
                    // 回退时如果不存在 `name：` 结构时则取消选中选项
                    const regex = this.getInputLabelRegex(name)
                    if (!regex.test(text)) {
                        this.$emit('update:selectedOption', {})
                        this.localValue = text
                    }
                }
            },
            handleDocumentKeydown (e) {
                const len = this.menuOptionList.length
                if (len) {
                    e.preventDefault()
                    e.stopPropagation()
                    let curIndex = this.menuOptionList.findIndex(set => set.id === this.hoverId)
                    curIndex = e.code === 'ArrowDown' ? curIndex + 1 : curIndex - 1
                    curIndex = curIndex > len - 1 ? 0 : (curIndex < 0 ? len - 1 : curIndex)
                    const option = this.menuOptionList[curIndex]
                    if (option) {
                        this.hoverId = option.id
                    }
                }
            },
            handleClear () {
                this.init()
                this.$emit('clear')
            }
        }
    }
</script>
<style lang="scss" scoped>
    .div-input {
        width: 100%;
        line-height: 22px;
        word-break: break-all;
        position: relative;
        border: none;
        cursor: text;
        &:focus {
            outline: none;
        }
    }
    .data-placeholder {
        position: absolute;
        top: 3px;
        left: 2px;
        z-index: -1;
        color: #c4c6cc;
    }
    .input-icons {
        .bk-icon {
            position: absolute;
            top: 4px;
            right: -25px;
            font-size: 16px;
            color: #c4c6cc;
            display: inline-block;
            cursor: pointer;
            &.is-focus {
                color: #3a84ff;
            }
        }
        .icon-close-circle-shape {
            font-size: 14px;
            &:hover {
                color: #979ba5;
            }
        }
    }
</style>
