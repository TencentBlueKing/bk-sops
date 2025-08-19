<template>
    <div class="select-tag" :class="{ 'is-edit': isEditMode }" @click.stop="handleTagClick">
        <span class="tag-label">{{ tagInfo.name + '：' }}</span>
        <bk-popover
            ref="selectPopover"
            placement="bottom"
            ext-cls="select-list-popover"
            trigger="manual"
            theme="light"
            :allow="false">
            <template v-if="!isEditMode">
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
                    @blur="handleBlur"
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
                    @clear="handleTagClear"
                    @pick-success="handleDatePickSuccess">
                    <div slot="trigger" class="hidden-value">{{ localValue }}</div>
                </bk-date-picker>
            </template>
            
            <div slot="content">
                <template v-if="renderList.length">
                    <ul class="menu-content">
                        <li
                            v-for="option in renderList"
                            :key="option.id"
                            :class="[
                                'option-item',
                                { 'hover-option': hoverId === option.id }
                            ]"
                            @click="handleMenuClick(option.id)">
                            <span class="option-name">{{ option.name }}</span>
                            <i class="bk-icon icon-check-1" v-if="checkedIdList.includes(option.id)"></i>
                        </li>
                    </ul>
                    <div class="popover-footer" v-if="tagInfo.multiple">
                        <span class="footer-btn" @click="handleSelectTagConfirm">{{ $t('确定') }}</span>
                        <span class="footer-btn" @click="handleSelectTagCancel">{{ $t('取消') }}</span>
                    </div>
                </template>
                <p v-else-if="tagInfo.children" class="no-data">{{ '查询无数据' }}</p>
            </div>
        </bk-popover>
        
    </div>
</template>

<script>
    import tools from '@/utils/tools.js'
    export default {
        props: {
            tagInfo: {
                type: Object,
                default: () => ({})
            }
        },
        data () {
            return {
                initValue: '',
                localValue: '',
                checkedIdList: [],
                isEditMode: false,
                hoverId: '',
                dateTimeRange: [],
                isDateOpen: false,
                renderList: []
            }
        },
        watch: {
            localValue: {
                handler (val) {
                    this.handleInputChange(val)
                }
            },
            tagInfo: {
                handler (val) {
                    const { type, values, children, isUser } = this.tagInfo
                    const symbol = type === 'dateRange' ? ' ~ ' : ' | '
                    const value = values.map(value => {
                        return typeof value === 'string' ? value : value.name
                    }).join(symbol)
                    this.initValue = value
                    this.localValue = value
                    this.renderList = children || []

                    // 多租户人员选择器特殊处理
                    if (isUser && typeof values[0] === 'string') {
                        this.getUserDisplayInfo()
                    }
                },
                deep: true,
                immediate: true
            }
        },
        methods: {
            async getUserDisplayInfo () {
                try {
                    const { values } = this.tagInfo
                    const resp = await fetch(`${window.BK_USER_WEB_APIGW_URL}/api/v3/open-web/tenant/users/${values[0]}/display_info/`, {
                        headers: {
                            'x-bk-tenant-id': window.TENANT_ID
                        },
                        credentials: 'include'
                    })
                    if (!resp.ok) return
    
                    const data = await resp.json()
                    const { display_name: name } = data.data
                    this.updateSelectTag([{ id: values[0], name }])
                } catch (error) {
                    console.warn(error)
                }
            },
            async handleInputChange (val) {
                try {
                    const { children, multiple, remoteMethod, isUser } = this.tagInfo
                    let renderList = children || []
                    if (val) {
                        if (!multiple && children) {
                            renderList = children.filter(item => item.name.indexOf(val) > -1)
                        } else if (remoteMethod && typeof remoteMethod === 'function') {
                            renderList = await remoteMethod(val)
                        } else if (isUser && window.ENABLE_MULTI_TENANT_MODE) { // 多租户人员选择器特殊处理
                            const resp = await fetch(`${window.BK_USER_WEB_APIGW_URL}/api/v3/open-web/tenant/users/-/search/?keyword=${val}`, {
                                headers: {
                                    'x-bk-tenant-id': window.TENANT_ID
                                },
                                credentials: 'include'
                            })
                            if (!resp.ok) return

                            const data = await resp.json()
                            renderList = data.data.map(item => ({ id: item.bk_username, name: item.display_name }))
                        }
                    }

                    this.renderList = renderList
                } catch (error) {
                    console.warn(error)
                }
            },
            showPopover () {
                const instance = this.$refs.selectPopover.instance
                instance.show()
            },
            hidePopover () {
                const instance = this.$refs.selectPopover.instance
                instance.hide()
            },
            handleTagClick () {
                this.$emit('focus', true)
            },
            handleTagClear () {
                this.hidePopover()
                this.isDateOpen = false
                this.$emit('handleTagClear', this.tagInfo.id)
            },
            updateSelectTag (values) {
                this.hoverId = ''
                this.hidePopover()
                this.exitEditMode()
                this.$emit('updateSelectTag', { ...this.tagInfo, values })
            },
            exitEditMode () {
                this.isEditMode = false
                this.isDateOpen = false
            },
            toggleEditMode () {
                if (this.tagInfo.type === 'dateRange') {
                    this.dateTimeRange = this.localValue.split(' ~ ')
                    this.isDateOpen = true
                } else {
                    this.checkedIdList = this.tagInfo.values.map(item => item.id)
                }
                this.isEditMode = true
                setTimeout(() => {
                    this.$refs.textarea.focus()
                })
                this.showPopover()
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
                        if (this.tagInfo.multiple) {
                            event.preventDefault()
                            return false
                        }
                        return false
                }
            },
            handleKeyEnter () {
                const isEqual = tools.isDataEqual(this.initValue, this.localValue)

                if (isEqual) {
                    this.exitEditMode()
                    return
                }
    
                if (this.hoverId) {
                    this.handleHoverSelection()
                    return
                }
    
                if (this.localValue) {
                    this.handleSelection()
                }
            },
            handleHoverSelection () {
                if (this.tagInfo.multiple) {
                    this.handleMenuClick(this.hoverId)
                } else {
                    this.selectRenderListItem(item => item.id === this.hoverId)
                }
            },
            handleSelection () {
                const { children, isUser } = this.tagInfo

                if (children) {
                    this.handleChildrenSelection()
                    return
                }

                if (isUser && window.ENABLE_MULTI_TENANT_MODE) {
                    this.selectRenderListItem(item => item.name.indexOf(this.localValue) > -1)
                    return
                }

                this.updateSelectTag([this.localValue])
            },
            handleChildrenSelection () {
                if (this.tagInfo.multiple) {
                    const values = this.renderList.filter(item => this.checkedIdList.includes(item.id))
                    this.updateSelectTag(values)
                } else {
                    this.selectRenderListItem(item => item.name === this.localValue)
                }
            },
            selectRenderListItem (predicate) {
                const item = this.renderList.find(predicate)
                if (item) {
                    this.updateSelectTag([item])
                }
            },
            handleRemove (event) {
                // 清除tag
                if (!this.localValue) {
                    event.preventDefault()
                    this.handleTagClear()
                    return
                }
                // 清除多选选项
                if (this.tagInfo.multiple) {
                    event.preventDefault()
                    if (this.checkedIdList.length > 0) {
                        const lastId = this.checkedIdList[this.checkedIdList.length - 1]
                        this.handleMenuClick(lastId)
                    }
                }
            },
            handleDocumentKeydown (event) {
                if (!this.renderList.length) return

                event.preventDefault()
                event.stopPropagation()

                const direction = event.code === 'ArrowDown' ? 1 : -1
                const currentIndex = this.renderList.findIndex(item => item.id === this.hoverId)
                const nextIndex = this.calculateNextIndex(currentIndex, direction)

                const option = this.renderList[nextIndex]
                if (option) {
                    this.hoverId = option.id
                }
            },
            calculateNextIndex (currentIndex, direction) {
                const lastIndex = this.renderList.length - 1
    
                if (direction > 0) {
                    return currentIndex < lastIndex ? currentIndex + 1 : 0
                } else {
                    return currentIndex > 0 ? currentIndex - 1 : lastIndex
                }
            },
            handleTagInput (event) {
                this.localValue = event.target.value.replace(/\n/, '')
                const { children, multiple, type } = this.tagInfo

                if (children) {
                    this.handleChildrenInput()
                } else if (type === 'dateRange' && !this.localValue) {
                    // 当时间被清空后导致输入框换行时更新date选择器
                    this.isDateOpen = false
                    this.dateTimeRange = []
                    this.$nextTick(() => {
                        this.isDateOpen = true
                    })
                }
                if (!multiple) this.hoverId = ''
            },
            handleChildrenInput () {
                if (!this.localValue) {
                    this.checkedIdList = []
                    return
                }
    
                // 根据输入值命中选项
                const textArr = this.localValue.split(' | ')
                this.checkedIdList = textArr.reduce((acc, cur) => {
                    const child = this.tagInfo.children.find(item => item.name === cur)
                    if (child) {
                        acc.push(child.name)
                    }
                    return acc
                }, [])
            },
            handleBlur (e) {
                this.exitEditMode()
                this.localValue = this.initValue
            },
            handleMenuClick (id) {
                // 单选
                if (!this.tagInfo.multiple) {
                    const menuItem = this.renderList.filter(menu => menu.id === id)
                    this.updateSelectTag([menuItem])
                    return
                }
                // 多选
                const index = this.checkedIdList.findIndex(item => item === id)
                if (index > -1) {
                    this.checkedIdList.splice(index, 1)
                } else {
                    this.checkedIdList.push(id)
                }
                this.localValue = this.renderList.reduce((acc, cur) => {
                    if (this.checkedIdList.includes(cur.id)) {
                        acc.push(cur.name)
                    }
                    return acc
                }, []).join(' | ')
                this.$refs.textarea.focus()
            },
            handleSelectTagConfirm () {
                if (!this.checkedIdList.length) {
                    this.handleTagClear()
                    return
                }
                const checkedList = this.renderList.filter(menu => this.checkedIdList.includes(menu.id))
                const isEqual = tools.isDataEqual(this.tagInfo.values, checkedList)
                if (!isEqual) {
                    this.updateSelectTag(checkedList)
                }
            },
            handleSelectTagCancel () {
                this.$emit('handleSelectTagCancel')
                this.isEditMode = false
                this.localValue = this.initValue
                this.hidePopover()
            },
            handleChange (date) {
                this.dateTimeRange = date
            },
            handleDatePickSuccess () {
                this.updateSelectTag(this.dateTimeRange)
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
