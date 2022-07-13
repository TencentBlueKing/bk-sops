<template>
    <section ref="wrap" class="search-select" :class="{ 'is-focus': input.focus }" @click="handleWrapClick">
        <div
            class="search-input"
            :style="{ maxHeight: (shrink ? (input.focus ? maxHeight : minHeight) : maxHeight) + 'px' }">
            <template v-if="searchSelectValue.length">
                <div
                    v-for="(item, index) in searchSelectValue"
                    :key="index"
                    :class="['select-tags', { 'active': item.isSelect }]"
                    @click.stop="onClickSelectTag(item.id)">
                    <bk-popover
                        ref="selectPopover"
                        placement="bottom"
                        ext-cls="select-list-popover"
                        trigger="manual"
                        theme="light"
                        :disabled="item.id === 'dateRange' || !item.values"
                        :allow="false">
                        <span>{{ item.values ? item.name + '：' : item.name }}</span>
                        <span class="val-item" v-for="(val, idx) in item.values" :key="idx">
                            {{ val.name || val }}
                            <template v-if="idx !== item.values.length - 1">
                                <span class="wavy-line" v-if="item.id === 'dateRange'">~</span>
                                <span v-else class="separation-line">|</span>
                            </template>
                        </span>
                        <i @click.stop="onClearSelectTag(item.id)" class="bk-icon icon-close"></i>
                        <div slot="content">
                            <ul class="select-list-menu">
                                <li
                                    v-for="(val, valIndex) in selectValues"
                                    :key="valIndex"
                                    class="menu-item"
                                    @click="val.checked = !val.checked">
                                    {{ val.name }}
                                    <i class="bk-icon icon-check-1" v-if="val.checked"></i>
                                </li>
                            </ul>
                            <div class="popover-footer">
                                <span class="footer-btn" @click="handleConfirm(item.id)">确定</span>
                                <span class="footer-btn" @click="handleSelectPopHidden(item.id)">取消</span>
                            </div>
                        </div>
                    </bk-popover>
                </div>
            </template>
            <div class="search-input-input">
                <bk-popover
                    ref="searchPopover"
                    placement="bottom-start"
                    theme="light"
                    trigger="manual"
                    :allow="false"
                    :distance="5"
                    ext-cls="search-list-popover"
                    :on-hide="handleSearchPopHidden">
                    <div
                        ref="input"
                        class="div-input"
                        :class="{ 'input-before': isShowPlaceholder }"
                        contenteditable="plaintext-only"
                        :data-placeholder="placeholder"
                        v-bk-clickoutside="handleClickOutSide"
                        @focus="handleInputFocus"
                        @cut="handleInputCut"
                        @input="handleInputChange"
                        @keydown="handleInputKeyup">
                    </div>
                    <div slot="content" class="search-list-content" :class="{ 'option-none': isOptionShowAll }">
                        <!-- 搜索匹配列表 -->
                        <template v-if="input.value && !selectInfo.id">
                            <ul class="search-list-menu">
                                <template v-if="searchResultList.length">
                                    <li
                                        v-for="(item, index) in searchResultList"
                                        :key="index"
                                        class="menu-item search-menu-item"
                                        :class="{ 'default-menu-item': item.isDefaultOption }"
                                        @click="handleResultOptionSelect(item)">
                                        <span class="search-menu-label">{{ item.name + '：' }}</span>
                                        <span class="value-text" v-bk-overflow-tips>{{ input.value }}</span>
                                    </li>
                                </template>
                                <li v-else class="menu-item no-data">{{ '查询无数据' }}</li>
                            </ul>
                        </template>
                        <!-- 默认列表 -->
                        <template v-else>
                            <ul class="search-list-menu">
                                <template v-for="(item, index) in optionList">
                                    <li
                                        v-if="judgeOptionShow(item)"
                                        :key="index"
                                        class="menu-item"
                                        @click="handleOptionSelect(item)">
                                        {{ item.name }}
                                        <i class="bk-icon icon-check-1" v-if="selectInfo.multiable && item.isActive"></i>
                                    </li>
                                </template>
                            </ul>
                            <div class="popover-footer" v-show="selectInfo.children && selectInfo.multiable">
                                <span class="footer-btn" @click="selectOptionConfirm">确定</span>
                                <span class="footer-btn" @click="selectOptionCancel">取消</span>
                            </div>
                        </template>
                        <!-- 最近搜索 -->
                        <dl class="recent-search-list" v-if="!selectInfo.children && recordsData.length">
                            <dt>
                                <span class="label">最近搜索</span>
                                <span class="clear" @click="onEmptyRecord">清空</span>
                            </dt>
                            <dd
                                class="search-item"
                                v-for="(record, index) in recordsData" :key="index"
                                @click="setSearchSelectValue(record)">
                                <span class="search-item-label">{{ record.name + ' ：' }}</span>
                                <span class="search-item-text">{{ record.text_value }}</span>
                                <i class="bk-icon icon-delete" @click.stop="onDeleteRecord(record)"></i>
                            </dd>
                        </dl>
                    </div>
                </bk-popover>
            </div>
        </div>
        <span v-if="input.value || searchSelectValue.length" @click.stop="handleClear" class="bk-icon icon-close-circle-shape close-icon"></span>
        <span v-else @click.stop="handleKeyEnter" :class="['bk-icon icon-search search-icon', { 'is-focus': input.focus }]"></span>
    </section>
    
</template>

<script>
    import { mapState } from 'vuex'
    import tools from '@/utils/tools.js'
    import { random4 } from '@/utils/uuid.js'
    export default {
        props: {
            placeholder: {
                type: String,
                default: ''
            },
            searchList: {
                type: Array,
                default: () => {
                    return []
                }
            },
            value: {
                type: Array,
                default: () => []
            },
            maxHeight: {
                type: [String, Number],
                default: 120
            },
            minHeight: {
                type: [String, Number],
                default: 32
            },
            shrink: {
                type: Boolean,
                default: true
            },
            isSearch: {
                type: Boolean,
                default: true
            },
            id: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                isInit: false,
                optionList: [],
                selectInfo: {},
                input: {
                    value: '',
                    focus: false
                },
                searchText: '',
                selectValues: [],
                searchSelectValue: [],
                selectTagList: [],
                isVisible: false, // 输入框是否获取焦点
                records: []
            }
        },
        computed: {
            ...mapState({
                username: state => state.username
            }),
            isShowPlaceholder () {
                return !this.searchSelectValue.length
                    && !this.input.value.length
                    && !Object.keys(this.selectInfo).length
            },
            searchResultList () { // 搜索匹配列表
                const inputOptions = this.optionList.filter(item => !item.children) || []
                
                return inputOptions.filter(option => {
                    const isMatch = this.searchSelectValue.some(item => item.id === option.id)
                    return !isMatch
                }) || []
            },
            isOptionShowAll () {
                const isMultiable = this.optionList.some(item => item.multiable)
                if (isMultiable) {
                    return false
                }
                return this.optionList.every(item => {
                    return this.searchSelectValue.find(value => value.id === item.id)
                })
            },
            recordsData () {
                const isOld = this.records.some(item => item.id && item.form)
                let list = []
                if (isOld) {
                    // 清除旧数据
                    const records = JSON.parse(localStorage.getItem(`advanced_search_record`))
                    if (records && records[this.username] && records[this.username][this.id]) {
                        records[this.username][this.id] = []
                        localStorage.setItem(`advanced_search_record`, JSON.stringify(records))
                    }
                } else {
                    list = this.records.map(recordItem => {
                        if (Array.isArray(recordItem.values)) {
                            const values = recordItem.values.map(item => item.name || item)
                            recordItem.text_value = values.join(recordItem.id === 'dateRange' ? ' - ' : ',')
                        } else {
                            recordItem.text_value = recordItem.values
                        }
                        return recordItem
                    })
                }
                return list
            }
        },
        watch: {
            value: {
                handler (val) {
                    this.searchSelectValue = tools.deepClone(val)
                },
                deep: true,
                immediate: true
            },
            searchList: {
                handler (val) {
                    this.optionList = tools.deepClone(val)
                },
                deep: true,
                immediate: true
            },
            isVisible (val) {
                const popover = this.getPopoverInstance()
                if (val) {
                    popover.show()
                } else {
                    popover.hide()
                }
            },
            searchSelectValue: {
                handler (val) {
                    this.$emit('change', val)
                },
                deep: true
            }
        },
        mounted () {
            this.records = this.getSearchRecords()
        },
        methods: {
            judgeOptionShow (option) {
                if (option.multiable) return true
                return !this.searchSelectValue.some(item => item.id === option.id)
            },
            setInputFocus () {
                this.$refs.input.focus()
            },
            setInputBlur () {
                this.$refs.input.blur()
            },
            getPopoverInstance () {
                return this.$refs.searchPopover.instance
            },
            // 点击已生成的selectTag
            onClickSelectTag (id) {
                const index = this.searchSelectValue.findIndex(item => item.id === id)
                const popover = this.$refs.selectPopover[index].instance
                popover.show()
                const selectContent = this.searchSelectValue[index]
                this.selectValues = selectContent.values.map(item => {
                    if (item.id) {
                        return { ...item, checked: true }
                    }
                    return { name: item, checked: true }
                })
                this.input.focus = true
            },
            // 确定修改已生成的tag
            handleConfirm (id) {
                const index = this.searchSelectValue.findIndex(item => item.id === id)
                const selectContent = this.searchSelectValue[index]
                // 如果没有修改则不更新
                const selectValues = this.selectValues.reduce((acc, cur) => {
                    const { id, name, checked } = cur
                    if (checked) {
                        id ? acc.push({ id, name }) : acc.push(name)
                    }
                    return acc
                }, [])
                const isEqual = tools.isDataEqual(selectContent.values, selectValues)
                if (!isEqual) {
                    selectContent.values = selectValues
                    if (!selectContent.values.length) {
                        this.searchSelectValue.splice(index, 1)
                    }
                }
                // 添加搜索记录
                this.addSearchRecord(selectContent)
                // 关闭selectPopover，打开searchPopover
                this.selectValues = []
                const popover = this.$refs.selectPopover[index].instance
                popover.hide()
                this.setInputFocus()
                this.isVisible = true
            },
            // 已生成tag的popover消失事件
            handleSelectPopHidden (id) {
                const index = this.searchSelectValue.findIndex(item => item.id === id)
                const popover = this.$refs.selectPopover[index].instance
                popover.hide()
                this.setInputFocus()
                this.isVisible = true
            },
            // 修改已生成的tag
            onClearSelectTag (id) {
                const index = this.searchSelectValue.findIndex(item => item.id === id)
                this.searchSelectValue.splice(index, 1)
                // 关闭selectPopover，打开searchPopover
                const popover = this.$refs.selectPopover[index].instance
                popover.hide()
                this.setInputFocus()
                this.isVisible = true
            },
            handleSearchPopHidden () {
                this.isVisible = false
            },
            // 确认按钮
            selectOptionConfirm () {
                const { id, name, isDefaultOption } = this.selectInfo
                const searchContent = this.searchSelectValue.find(item => item.id === id)
                let values = []
                if (searchContent) {
                    const duplicateObj = {}
                    values = searchContent.values.concat(this.selectTagList)
                    values = values.reduce((acc, cur) => {
                        if (!duplicateObj[cur.id]) {
                            duplicateObj[cur.id] = true
                            acc.push(cur)
                        }
                        return acc
                    }, [])
                    searchContent.values = values
                } else {
                    values = [...this.selectTagList]
                    this.searchSelectValue.push({
                        id,
                        name,
                        values
                    })
                }
                this.resetPopover()
                // 添加搜索记录
                this.addSearchRecord({ id, name, values, isDefaultOption })
            },
            // 取消按钮
            selectOptionCancel () {
                this.isVisible = false
                this.selectTagList = []
                let text = this.$refs.input.innerText
                text = text.split('：')[0] + '：'
                this.input.value = text
                this.$refs.input.innerText = text
                this.setInputFocus()
            },
            // 选择搜索结果匹配下拉项
            handleResultOptionSelect (item) {
                const selectInfo = {
                    ...item,
                    values: [this.input.value]
                }
                this.searchSelectValue.push(selectInfo)
                // 添加搜索记录
                this.addSearchRecord(selectInfo)
                this.resetPopover()
            },
            // 选中标题类型
            handleOptionSelect (val) {
                if (this.selectInfo.id) {
                    const valIndex = this.selectTagList.findIndex(item => item.id === val.id)
                    if (valIndex > -1) {
                        this.selectTagList.splice(valIndex, 1)
                    } else {
                        this.selectTagList.push(tools.deepClone(val))
                    }
                    val.isActive = !val.isActive
                    if (this.selectInfo.multiable) {
                        let text = this.selectTagList.map(item => item.name).join(' | ')
                        text = this.selectInfo.name + '：' + text
                        this.$refs.input.innerText = text
                        this.input.value = text
                    } else {
                        this.selectOptionConfirm()
                        this.optionList = tools.deepClone(this.searchList)
                    }
                } else {
                    this.selectInfo = tools.deepClone(val)
                    const inputDom = this.$refs.input
                    inputDom.innerText = val.name + '：'
                    this.input.value = val.name + '：'
                    // 输入框获取焦点
                    inputDom.focus()
                    if (val.children) {
                        this.selectTagList = []
                        this.optionList = val.children
                    } else {
                        // 收起popover
                        const popover = this.getPopoverInstance()
                        popover.hide()
                    }
                }
            },
            // 点击到searchSelect外面
            handleClickOutSide (e) {
                const parent = e.target.offsetParent
                const classList = parent ? parent.classList : null
                const unFocus = !parent || (classList && !Array.from(classList.values()).some(key => {
                    return ['search-select', 'tippy-tooltip', 'tippy-content', 'menu-item', 'popover-footer', 'recent-search-list', 'search-item'].includes(key)
                }))
                if (unFocus) {
                    const popover = this.getPopoverInstance()
                    popover.hide()
                    this.input.focus = false
                }
            },
            // 文本框获取焦点
            handleInputFocus () {
                this.input.focus = true
                const input = this.$refs.input
                // 设置文本框焦点显示位置
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
            // searchSelect点击事件
            handleWrapClick () {
                if (this.shrink) {
                    this.setInputFocus()
                }
                this.isVisible = true
            },
            handleInputCut () {
                console.log('cut')
            },
            // 文本框内容改变
            handleInputChange (e) {
                const text = e.target.innerText
                this.input.value = this.selectInfo.id ? text.slice(text.indexOf('：') + 1) : text.trim()
                if (this.selectInfo.id) {
                    // 不包含：标识符默认为自定义搜索条件
                    if (text.indexOf('：') === -1) {
                        this.selectInfo = {}
                    }
                } else {
                    this.selectInfo = {}
                }
                if (!text && !this.searchSelectValue.length) { // 没有自定义搜索条件和已选中条件，重置searchPopover
                    this.optionList = tools.deepClone(this.searchList)
                    this.isVisible = true
                } else if (!this.input.value || this.selectInfo.children) { // 没有搜索值和搜索项包含子项时，显示searchPopover
                    this.isVisible = true
                }
            },
            // 文本框按键事件
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
                        break
                    default:
                        if (this.selectTagList.length) {
                            e.preventDefault()
                            return false
                        }
                        return false
                }
            },
            // 回车按键
            handleKeyEnter (e) {
                e.preventDefault()
                // setTimeout用在使用中文输入法不空格直接回车时，生成的tag和input.value会同时存在
                setTimeout(() => {
                    if (!this.input.value) return
                    let info = {}
                    if (this.selectInfo.id) {
                        const index = this.searchSelectValue.findIndex(item => item.id === this.selectInfo.id)
                        if (index > -1) {
                            const selectContent = this.searchSelectValue[index]
                            const isMatch = selectContent.values.some(item => item === this.input.value)
                            if (!isMatch) {
                                selectContent.values.push(this.input.value)
                            }
                        } else {
                            info = {
                                ...this.selectInfo,
                                values: [this.input.value]
                            }
                            this.searchSelectValue.push(info)
                        }
                    } else {
                        const isMatch = this.searchSelectValue.some(item => item.isDefaultOption)
                        if (!isMatch) {
                            const defaultOption = this.searchList.find(item => item.isDefaultOption) || {}
                            info = {
                                ...defaultOption,
                                values: [this.input.value]
                            }
                            this.searchSelectValue.push(info)
                        } else {
                            return
                        }
                    }
                    // 添加搜索记录
                    this.addSearchRecord(info)

                    this.input.value = ''
                    this.$refs.input.innerText = ''
                    this.selectInfo = {}
                    this.isVisible = true
                    this.optionList = tools.deepClone(this.searchList)
                }, 0)
            },
            // 清空按键
            handleKeyBackspace (e) {
                if (this.selectTagList.length && this.selectInfo.multiable) {
                    e.preventDefault()
                    this.selectTagList.pop()
                    let text = this.selectTagList.map(item => item.name).join(' | ')
                    text = this.selectInfo.name + '：' + text
                    this.$refs.input.innerText = text
                    this.input.value = text
                    this.handleInputFocus()
                } else if (!this.$refs.input.innerText && this.searchSelectValue.length) {
                    this.searchSelectValue.pop()
                } else if (this.selectInfo.id) {
                    const text = this.$refs.input.innerText
                    if (text !== this.selectInfo.name) {
                        this.optionList = tools.deepClone(this.searchList)
                    }
                }
            },
            // 快速清空
            handleClear () {
                this.$refs.input.innerText = ''
                this.setInputFocus()
                this.input.value = ''
                this.selectInfo = {}
                this.searchSelectValue = []
                this.isVisible = true
            },
            // 重置popover数据
            resetPopover () {
                this.selectTagList = []
                this.$refs.input.innerText = ''
                this.input.value = ''
                this.selectInfo = {}
                this.setInputFocus()
                this.optionList = tools.deepClone(this.searchList)
            },
            // 添加搜索记录
            addSearchRecord (data) {
                let records = JSON.parse(localStorage.getItem(`advanced_search_record`))
                if (records === null) {
                    records = {}
                }
                if (!records[this.username]) {
                    records[this.username] = {}
                }

                if (!records[this.username][this.id]) {
                    records[this.username][this.id] = []
                }

                const list = records[this.username][this.id]
                const { id, name, values, isDefaultOption } = data
                const cid = random4()
                if (list.length) {
                    const match = list.every(item => item.id !== id || !tools.isDataEqual(item.values, values))
                    if (match) {
                        const info = { id, name, values, cid }
                        if (isDefaultOption) {
                            info['isDefaultOption'] = true
                        }
                        list.unshift(info)
                    }
                    records[this.username][this.id] = list.splice(0, 7)
                } else {
                    const info = { id, name, values, cid }
                    if (isDefaultOption) {
                        info['isDefaultOption'] = true
                    }
                    records[this.username][this.id] = [info]
                }
                this.records = records[this.username][this.id]

                localStorage.setItem(`advanced_search_record`, JSON.stringify(records))
            },
            // 获取搜索记录
            getSearchRecords () {
                const records = JSON.parse(localStorage.getItem(`advanced_search_record`))
                if (records !== null && records[this.username] && records[this.username][this.id]) {
                    return records[this.username][this.id]
                }
                return []
            },
            // 清空搜索历史
            onEmptyRecord () {
                const records = JSON.parse(localStorage.getItem(`advanced_search_record`))
                records[this.username][this.id] = []
                this.records = []
                localStorage.setItem(`advanced_search_record`, JSON.stringify(records))
            },
            // 选中搜索数据
            setSearchSelectValue (record) {
                this.setInputFocus()
                const selectInfo = this.searchSelectValue.find(item => item.id === record.id)
                if (selectInfo) {
                    selectInfo.values = record.values
                } else {
                    this.searchSelectValue.push(record)
                }
            },
            // 删除搜索数据
            onDeleteRecord (record) {
                this.setInputFocus()
                const records = JSON.parse(localStorage.getItem(`advanced_search_record`))
                let list = records[this.username][this.id] || []
                list = list.filter(item => item.cid !== record.cid)
                records[this.username][this.id] = list
                localStorage.setItem(`advanced_search_record`, JSON.stringify(records))

                const index = this.records.findIndex(item => item.cid === record.cid)
                this.records.splice(index, 1)
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    .search-select {
        position: absolute;
        right: 0;
        z-index: 666;
        background: #fff;
        display: flex;
        flex-direction: row;
        align-items: center;
        width: 480px;
        font-size: 12px;
        min-height: 32px;
        box-sizing: border-box;
        border: 1px solid #c4c6cc;
        border-radius: 2px;
        outline: none;
        resize: none;
        transition: border 0.2s linear;
        overflow: auto;
        color: #63656e;
        flex-wrap: wrap;
        @include scrollbar;
        padding-right: 25px;
        &.is-focus {
            border-color: #3a84ff;
        }
        transition: all .5s;
    }
    .search-input {
        flex: 1;
        position: relative;
        text-align: left;
        overflow: visible;
        display: flex;
        flex-wrap: wrap;
        min-height: 32px;
        transition: max-height .3s cubic-bezier(0.4, 0, 0.2, 1);
        
        .select-tags {
            margin: 4px 0 5px 5px;
            padding: 0 5px;
            min-height: 22px;
            line-height: 22px;
            background: #f0f1f5;
            border-radius: 2pt;
            display: flex;
            align-items: center;
            color: #63656e;
            cursor: pointer;
            &.active, &:hover {
                background: #dcdee4;
            }
            .val-item {
                position: relative;
                .wavy-line,
                .separation-line {
                    margin: 0 7px;
                }
                &:nth-last-child(2) {
                    margin-right: 0;
                    &::after {
                        content: '';
                        display: none !important;
                    }
                }
            }
            .icon-close {
                color: #979ba5;
                font-size: 13px;
                margin: 0 4px;
                font-weight: 700;
            }
        }
        .search-input-input {
            position: relative;
            padding: 0 8px;
            color: #63656e;
            flex: 1 1 auto;
            border: none;
            min-width: 40px;
            display: flex;
            align-items: center;
            .div-input {
                width: 100%;
                line-height: 32px;
                word-break: break-all;
                position: relative;
                border: none;
                &:focus {
                    outline: none;
                }
            }
            .input-before {
                &:before {
                    content: attr(data-placeholder);
                    color: #c4c6cc;
                    padding-left: 2px;
                }
            }
            /deep/ .bk-tooltip {
                width: 100%;
                .bk-tooltip-ref {
                    width: 100%;
                }
            }
        }
    }
    
    .search-icon, .close-icon {
        position: absolute;
        top: 8px;
        right: 5px;
        font-size: 16px;
        color: #c4c6cc;
        display: inline-block;
        cursor: pointer;
        &.is-focus {
            color: #3a84ff;
        }
    }
    .close-icon {
        top: 9px;
        font-size: 14px;
        &:hover {
            color: #979ba5;
        }
    }
</style>
<style lang="scss">
    @import '@/scss/mixins/scrollbar.scss';
    
    .select-list-popover,
    .search-list-popover {
        padding-bottom: 0 !important;
        .tippy-tooltip {
            padding: 0 !important;
            border: 1px solid #dcdee5;
            .tippy-arrow {
                display: none;
            }
        }
        .option-none {
            .search-list-menu {
                padding: 0;
            }
            .recent-search-list {
                margin-top: 0;
                &::before {
                    display: none;
                }
            }
        }
        .search-list-menu,
        .select-list-menu {
            padding: 6px 0;
            max-height: 250px;
            overflow: auto;
            width: 238px !important;
            @include scrollbar;
            .data-null {
                text-align: center;
                padding: 90px 0;
                color: #979ba5;
            }
        }
        .menu-item {
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: #63656e;
            padding: 0 15px !important;
            cursor: pointer;
            font-size: 12px;
            &:hover {
                background: #f5f7fa;
            }
            .icon-check-1 {
                font-size: 22px;
                color: #3a84ff;
            }
            &.no-data {
                justify-content: center;
            }
        }
        .search-menu-item {
            .search-menu-label {
                width: 60px;
                text-align: right;
                padding-left: 12px !important;
                font-weight: 700;
                white-space: nowrap;
            }
            .value-text {
                flex: 1;
                text-align: left;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            &.default-menu-item {
                background: #eaf3ff;
                color: #3a84ff;
            }
        }
        .popover-footer {
            border: 1px solid #dcdee5;
        }
        .recent-search-list {
            position: relative;
            padding: 15px 0 4px;
            margin-top: 8px;
            color: #63656e;
            font-size: 12px;
            dt {
                height: 16px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 8px;
                padding: 0 12px;
                .label {
                    font-weight: 700;
                    color: #63656e;
                }
                .clear {
                    color: #3a84ff;
                    cursor: pointer;
                }
            }
            dd {
                height: 32px;
                position: relative;
                display: flex;
                align-items: center;
                padding: 0 12px;
                cursor: pointer;
                .search-item-text {
                    max-width: 130px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
                .icon-delete {
                    position: absolute;
                    top: 10px;
                    right: 12px;
                    display: none;
                    font-style: inherit;
                    &:hover {
                        color: #3a84ff;
                    }
                }
                &:hover {
                    background: #f5f7fa;
                    .icon-delete {
                        display: block;
                    }
                }
            }
            &::before {
                content: '';
                display: inline-block;
                width: 208px;
                height: 1px;
                position: absolute;
                top: 0;
                left: 16px;
                background: #dedee5;
            }
        }
        .popper__arrow {
            display: none !important;
        }
    }
    .popover-footer {
        display: flex;
        line-height: 32px;
        justify-content: space-around;
        align-items: center;
        font-size: 12px;
        border: none !important;
        border-top: 1px solid #dcdee5 !important;
        .footer-btn {
            flex: 1;
            text-align: center;
            cursor: pointer;
            &:first-child {
                border-right: 1px solid #dcdee5;
            }
            &:hover {
                background: #e1ecff;
                color: #3a84ff;
            }
        }
    }
    .search-tippy-popover {
        .tippy-tooltip {
            top:  5px !important;
            transform: translateY(0px) !important;
            padding: 7px 0;
        }
    }
</style>
