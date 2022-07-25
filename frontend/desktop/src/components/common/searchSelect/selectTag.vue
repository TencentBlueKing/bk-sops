<template>
    <div class="select-tag" :class="{ 'is-edit': isEditing }" @click.stop="handleTagClick">
        <span class="tag-label">{{ tagInfo.name + '：' }}</span>
        <bk-popover
            ref="selectPopover"
            placement="bottom"
            ext-cls="select-list-popover"
            trigger="manual"
            theme="light"
            :disabled="!tagInfo.children"
            :allow="false">
            <template v-if="!isEditing">
                <span class="tag-value" @click="toggleEditMode">
                    {{ localValue }}
                </span>
                <i @click="handleTagClear" class="bk-icon icon-close"></i>
            </template>
            <template v-else>
                <div class="hidden-value">{{ localValue }}</div>
                <textarea
                    ref="textarea"
                    class="tag-value-edit"
                    spellcheck="false"
                    :value="localValue"
                    v-bk-clickoutside="handleInputOutSide"
                    @click="showPopover"
                    @keydown="handleKeydown"
                    @input="handleTagInput" />
                <bk-date-picker
                    v-if="tagInfo.type === 'dateRange'"
                    :value="dateTimeRange"
                    :open="isDateOpen"
                    :type="'datetimerange'"
                    :transfer="true"
                    ext-popover-cls="date-time-range-popover"
                    @change="handleChange"
                    @clear="handleDateClear"
                    @pick-success="handleDatePickSuccess">
                    <div slot="trigger" class="hidden-value">{{ localValue }}</div>
                </bk-date-picker>
            </template>
            
            <div slot="content">
                <template v-if="menuList.length">
                    <ul class="select-list-menu">
                        <li
                            v-for="menu in menuList"
                            :key="menu.id"
                            class="menu-item"
                            :class="{ 'is-hover': hoverId === menu.id }"
                            @click="handleMenuClick(menu.id)">
                            {{ menu.name }}
                            <i class="bk-icon icon-check-1" v-if="checkedIdList.includes(menu.id)"></i>
                        </li>
                    </ul>
                    <div class="popover-footer" v-if="tagInfo.multiable">
                        <span class="footer-btn" @click="handleSelectTagConfirm">{{ $t('确定') }}</span>
                        <span class="footer-btn" @click="handleSelectTagCancel">{{ $t('取消') }}</span>
                    </div>
                </template>
                <p v-else class="option-none no-search-data">{{ '查询无数据' }}</p>
            </div>
        </bk-popover>
        
    </div>
</template>

<script>
    import tools from '@/utils/tools.js'
    import dom from '@/utils/dom.js'
    export default {
        props: {
            tagInfo: {
                type: Object,
                default: () => ({})
            },
            list: {
                type: Array,
                default: () => ([])
            }
        },
        data () {
            return {
                initValue: '',
                localValue: '',
                checkedIdList: [],
                isEditing: false,
                hoverId: '',
                dateTimeRange: [],
                isDateOpen: false
            }
        },
        computed: {
            menuList () {
                const { children, multiable } = this.tagInfo
                if (!children) return []
                const list = tools.deepClone(children)
                if (!multiable && this.localValue) {
                    const textArr = this.localValue.split(' | ')
                    return list.filter(item => textArr.includes(item.name))
                }
                return list
            }
        },
        watch: {
            tagInfo: {
                handler (val) {
                    const { type, values, children } = this.tagInfo
                    const symbol = type === 'dateRange' ? ' ~ ' : ' | '
                    const value = values.map(item => children ? item.name : item).join(symbol)
                    this.initValue = value
                    this.localValue = value
                },
                deep: true,
                immediate: true
            }
        },
        methods: {
            showPopover () {
                const instance = this.$refs.selectPopover.instance
                instance.show()
            },
            hidePopover () {
                const instance = this.$refs.selectPopover.instance
                instance.hide()
            },
            judgeMenuChecked (menu) {
                return this.tagInfo.children.find(tag => tag.id === menu.id)
            },
            handleTagClick () {
                this.$parent.input.focus = true
            },
            handleTagClear () {
                this.$emit('handleTagClear', this.tagInfo.id)
            },
            toggleEditMode () {
                if (this.tagInfo.type === 'dateRange') {
                    this.dateTimeRange = this.localValue.split(' ~ ')
                    this.isDateOpen = true
                } else {
                    this.checkedIdList = this.tagInfo.values.map(item => item.id)
                }
                this.isEditing = true
                setTimeout(() => {
                    this.$refs.textarea.focus()
                    this.$refs.textarea.selectionStart = 0
                    this.$refs.textarea.selectionEnd = this.localValue.length
                })
                if (this.tagInfo.children) {
                    this.showPopover()
                }
            },
            handleKeydown (event) {
                switch (event.code) {
                    case 'Enter':
                    case 'NumpadEnter':
                        event.preventDefault()
                        this.handleKeyEnter()
                        break
                    case 'Backspace':
                        this.handleRemove(event)
                        break
                    case 'ArrowDown':
                    case 'ArrowUp':
                        event.preventDefault()
                        this.handleDocumentKeydown(event)
                        break
                    default:
                        if (this.tagInfo.multiable) {
                            event.preventDefault()
                            return false
                        }
                        return false
                }
            },
            handleKeyEnter () {
                const isEqual = tools.isDataEqual(this.initValue, this.localValue)
                const { children, multiable } = this.tagInfo
                if (isEqual) {
                    this.isEditing = false
                    this.isDateOpen = false
                } else if (this.hoverId !== '') {
                    if (multiable) {
                        this.handleMenuClick(this.hoverId)
                        return
                    } else {
                        const menuItem = this.menuList.find(item => item.id === this.hoverId)
                        this.$emit('updateSelectTag', { ...this.tagInfo, values: [menuItem] })
                        this.hoverId = ''
                    }
                } else if (this.localValue === '') {
                    return
                } else if (children) {
                    if (multiable) {
                        const values = this.menuList.filter(item => this.checkedIdList.includes(item.id))
                        this.$emit('updateSelectTag', { ...this.tagInfo, values })
                        return
                    }
                    const child = children.find(item => item.name === this.localValue)
                    if (child) {
                        this.$emit('updateSelectTag', { ...this.tagInfo, values: [child] })
                    } else {
                        return
                    }
                } else {
                    this.$emit('updateSelectTag', { ...this.tagInfo, values: [this.localValue] })
                }
                this.isEditing = false
                this.isDateOpen = false
                this.hidePopover()
            },
            handleRemove (event) {
                if (!this.localValue) {
                    event.preventDefault()
                    this.handleTagClear()
                } else if (this.tagInfo.multiable) {
                    event.preventDefault()
                    const idLength = this.checkedIdList.length
                    const lastId = this.checkedIdList[idLength - 1]
                    this.handleMenuClick(lastId)
                }
            },
            handleDocumentKeydown (event) {
                const len = this.menuList.length
                if (len) {
                    event.preventDefault()
                    event.stopPropagation()
                    let curIndex = this.menuList.findIndex(set => set.id === this.hoverId)
                    curIndex = event.code === 'ArrowDown' ? curIndex + 1 : curIndex - 1
                    curIndex = curIndex > len - 1 ? 0 : (curIndex < 0 ? len - 1 : curIndex)
                    const option = this.menuList[curIndex]
                    if (option) {
                        this.hoverId = option.id
                    }
                }
            },
            handleTagInput (event) {
                this.localValue = event.target.value.replace(/\n/, '')
                const { children, multiable, type } = this.tagInfo
                if (children) {
                    if (!this.localValue) {
                        this.checkedIdList = []
                        return
                    }
                    const textArr = this.localValue.split(' | ')
                    this.checkedIdList = children.reduce((acc, cur) => {
                        if (textArr.includes(cur.name)) {
                            acc.push(cur.id)
                        }
                        return acc
                    }, [])
                } else if (type === 'dateRange' && !this.localValue) {
                    // 当时间被清空后导致输入框换行时更新date选择器
                    this.isDateOpen = false
                    this.dateTimeRange = []
                    this.$nextTick(() => {
                        this.isDateOpen = true
                    })
                }
                if (!multiable) {
                    this.hoverId = ''
                }
            },
            handleInputOutSide (e) {
                if (dom.parentClsContains('select-list-popover', e.target) || dom.parentClsContains('date-time-range-popover', e.target)) {
                    this.handleTagClick()
                    return
                }
                this.localValue = this.initValue
                this.isEditing = false
                this.isDateOpen = false
            },
            handleMenuClick (id) {
                const index = this.checkedIdList.findIndex(item => item === id)
                if (index > -1) {
                    this.checkedIdList.splice(index, 1)
                } else {
                    this.checkedIdList.push(id)
                }
                this.localValue = this.menuList.reduce((acc, cur) => {
                    if (this.checkedIdList.includes(cur.id)) {
                        acc.push(cur.name)
                    }
                    return acc
                }, []).join(' | ')
                this.$refs.textarea.focus()
            },
            handleSelectTagConfirm () {
                const checkedList = this.menuList.filter(menu => this.checkedIdList.includes(menu.id))
                const isEqual = tools.isDataEqual(this.tagInfo.values, checkedList)
                if (!isEqual) {
                    this.$emit('handleSelectTagConfirm', this.tagInfo.id, checkedList)
                }
                this.isEditing = false
                this.hidePopover()
            },
            handleSelectTagCancel () {
                this.$emit('handleSelectTagCancel')
                this.isEditing = false
                this.localValue = this.initValue
                this.hidePopover()
            },
            handleChange (date) {
                this.dateTimeRange = date
            },
            handleDateClear () {
                this.dateTimeRange = []
                this.isEditing = false
                this.isDateOpen = false
                this.handleTagClear()
            },
            handleDatePickSuccess () {
                this.isEditing = false
                this.isDateOpen = false
                this.$emit('updateSelectTag', { ...this.tagInfo, values: this.dateTimeRange })
            }
        }
    }
</script>

<style lang="scss" scoped>
    .select-tag {
        position: relative;
        display: flex;
        margin: 4px 0 4px 5px;
        padding: 0 5px;
        min-height: 22px;
        line-height: 22px;
        background: #f0f1f5;
        border-radius: 2px;
        color: #63656e;
        cursor: pointer;
        .tag-label {
            flex-shrink: 0;
            align-self: start;
        }
        .bk-tooltip {
            display: inherit;
        }
        .tag-value {
            display: inline-block;
            line-height: 22px;
            margin-right: 22px;
        }
        .icon-close {
            position: absolute;
            top: 5px;
            right: 0;
            color: #979ba5;
            font-size: 14px;
            font-weight: 700;
        }
        .hidden-value {
            min-height: 22px;
            margin-right: 22px;
            white-space: normal;
            word-break: break-all;
            visibility: hidden;
        }
        .bk-date-picker {
            position: absolute;
            top: 0;
            z-index: 1;
            width: 100%;
            visibility: hidden;
            .bk-date-picker-rel {
                display: inline-block;
            }
        }
        .tag-value-edit {
            position: absolute;
            top: 0;
            z-index: 2;
            width: 100%;
            height: 100%;
            padding: 0;
            font-size: inherit;
            line-height: 22px;
            color: inherit;
            background: transparent;
            border: none;
            outline: none;
            resize: none;
            &::selection {
                background: #e1ecff;
            }
        }
        &:hover {
            background: #dcdee4;
        }
        &.is-edit {
            background: #fff;
            &:hover {
                background: #fff;
            }
        }
    }
</style>
