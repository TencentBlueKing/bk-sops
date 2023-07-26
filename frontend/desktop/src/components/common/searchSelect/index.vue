<template>
    <section ref="wrap" class="search-select" :class="{ 'is-focus': input.focus }" @click="handleWrapClick">
        <div
            class="search-input"
            :style="{ maxHeight: (shrink ? (input.focus ? maxHeight : minHeight) : maxHeight) + 'px' }">
            <template v-if="searchSelectValue.length">
                <!-- 已经选中的tag列表 -->
                <select-tag
                    v-for="tagInfo in searchSelectValue"
                    :key="tagInfo.id"
                    :list="list"
                    :tag-info="tagInfo"
                    @handleTagClear="handleTagClear"
                    @handleSelectTagConfirm="handleSelectTagConfirm"
                    @handleSelectTagCancel="initInputFocus"
                    @updateSelectTag="setSearchSelectValue">
                </select-tag>
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
                                <template v-if="optionList.length">
                                    <li
                                        v-for="(option, index) in optionList"
                                        :key="index"
                                        class="menu-item search-menu-item"
                                        :class="{ 'default-menu-item': option.isDefaultOption, 'is-hover': hoverId === option.id }"
                                        @click="handleResultOptionSelect(option)">
                                        <span class="search-menu-label">{{ option.name + '：' }}</span>
                                        <span class="value-text" v-bk-overflow-tips>{{ input.value }}</span>
                                    </li>
                                </template>
                                <li v-else class="menu-item no-search-data">{{ '查询无数据' }}</li>
                            </ul>
                        </template>
                        <!-- 默认列表 -->
                        <template v-else-if="optionList.length">
                            <ul class="search-list-menu">
                                <template v-for="option in optionList">
                                    <li
                                        :key="option.id"
                                        class="menu-item"
                                        :class="{ 'is-hover': hoverId === option.id }"
                                        @click="handleOptionSelect(option)">
                                        {{ option.name }}
                                        <i class="bk-icon icon-check-1" v-if="selectInfo.multiable && judgeOptionActive(option)"></i>
                                    </li>
                                </template>
                            </ul>
                            <div class="popover-footer" v-show="selectInfo.children && selectInfo.multiable">
                                <span class="footer-btn" @click="selectOptionConfirm">{{ $t('确定') }}</span>
                                <span class="footer-btn" @click="selectOptionCancel">{{ $t('取消') }}</span>
                            </div>
                        </template>
                        <p v-else class="no-search-data">{{ '查询无数据' }}</p>
                        <!-- 最近搜索 -->
                        <dl class="recent-search-list" v-if="!selectInfo.children && recordsData.length">
                            <dt>
                                <span class="label">{{ $t('最近搜索') }}</span>
                                <span class="clear" @click="onEmptyRecord">{{ $t('清空') }}</span>
                            </dt>
                            <dd
                                class="search-item"
                                v-for="(record, index) in recordsData" :key="index"
                                @click="setSearchSelectValue(record)">
                                <span class="search-item-label">{{ record.name + $t('：') + (lang === 'en' ? '&nbsp;' : '') }}</span>
                                <span class="search-item-text" v-bk-overflow-tips>{{ record.text_value }}</span>
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
    import selectTag from './selectTag.vue'
    export default {
        components: {
            selectTag
        },
        model: {
            prop: 'values',
            event: 'change'
        },
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
            values: {
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
                list: [],
                selectInfo: {},
                input: {
                    value: '',
                    focus: false
                },
                searchText: '',
                searchSelectValue: [],
                selectTagList: [],
                isVisible: false, // 输入框是否获取焦点
                records: [],
                hoverId: ''
            }
        },
        computed: {
            ...mapState({
                lang: state => state.lang,
                username: state => state.username
            }),
            isShowPlaceholder () {
                return !this.searchSelectValue.length
                    && !this.input.value.length
                    && !Object.keys(this.selectInfo).length
            },
            optionList () {
                const list = this.list.filter(option => {
                    if (option.multiable) return true
                    return !this.searchSelectValue.some(item => item.id === option.id)
                })
                const { id, children, multiable } = this.selectInfo
                if (id) {
                    if (multiable) {
                        return children
                    } else if (children) {
                        const text = this.input.value
                        if (text) {
                            return children.filter(item => item.name.indexOf(text) > -1)
                        } else {
                            return children
                        }
                    } else {
                        return list
                    }
                } else if (this.input.value) {
                    const inputOptions = this.list.filter(item => !item.children) || []
                
                    return inputOptions.filter(option => {
                        const isMatch = this.searchSelectValue.some(item => item.id === option.id)
                        return !isMatch
                    }) || []
                } else {
                    return list
                }
            },
            isOptionShowAll () {
                if (this.input.value && !this.selectInfo.id) {
                    return !this.optionList.length
                }
                const isMultiable = this.optionList.some(item => item.multiable)
                if (isMultiable) {
                    return false
                }
                return !this.optionList.length
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
                    const nameMap = this.searchList.reduce((acc, cur) => {
                        acc[cur.id] = cur.name
                        return acc
                    }, {})
                    list = this.records.map(recordItem => {
                        if (Array.isArray(recordItem.values)) {
                            const values = recordItem.values.map(item => item.name || item)
                            recordItem.text_value = values.join(recordItem.type === 'dateRange' ? ' - ' : ',')
                        } else {
                            recordItem.text_value = recordItem.values
                        }
                        recordItem.name = nameMap[recordItem.id] || this.$t(recordItem.name)
                        return recordItem
                    })
                }
                return list
            }
        },
        watch: {
            values: {
                handler (val) {
                    if (!tools.isDataEqual(val, this.searchSelectValue)) {
                        this.searchSelectValue = [...val]
                    }
                },
                deep: true,
                immediate: true
            },
            searchList: {
                handler (val) {
                    this.list = tools.deepClone(val)
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
            judgeOptionActive (option) {
                return this.selectTagList.find(tag => tag.id === option.id)
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
            // 确定修改已生成的tag
            handleSelectTagConfirm (id, selectValues) {
                const index = this.searchSelectValue.findIndex(item => item.id === id)
                const selectContent = this.searchSelectValue[index]
                selectContent.values = selectValues
                if (!selectContent.values.length) {
                    this.searchSelectValue.splice(index, 1)
                }
                // 添加搜索记录
                this.addSearchRecord(selectContent)
                this.initInputFocus()
            },
            // 输入框focus&打开searchPopover
            initInputFocus () {
                this.setInputFocus()
                this.isVisible = true
            },
            // 修改已生成的tag
            handleTagClear (id) {
                const index = this.searchSelectValue.findIndex(item => item.id === id)
                this.searchSelectValue.splice(index, 1)
                this.initInputFocus()
            },
            handleSearchPopHidden () {
                this.isVisible = false
            },
            // 确认按钮
            selectOptionConfirm () {
                const searchContent = this.searchSelectValue.find(item => item.id === this.selectInfo.id)
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
                        ...this.selectInfo,
                        values
                    })
                }
                // 添加搜索记录
                this.addSearchRecord({ ...this.selectInfo, values })
                this.resetPopover()
            },
            // 取消按钮
            selectOptionCancel () {
                this.isVisible = false
                this.selectTagList = []
                this.input.value = ''
                this.$refs.input.innerText = this.selectInfo.name + '：'
                this.setInputFocus()
            },
            // 选择搜索结果匹配下拉项
            handleResultOptionSelect (option) {
                const selectInfo = {
                    ...option,
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
                    if (this.selectInfo.multiable) {
                        let text = this.selectTagList.map(item => item.name).join(' | ')
                        this.input.value = text
                        text = this.selectInfo.name + '：' + text
                        this.$refs.input.innerText = text
                    } else {
                        this.selectOptionConfirm()
                    }
                } else {
                    this.selectInfo = tools.deepClone(val)
                    const inputDom = this.$refs.input
                    inputDom.innerText = val.name + '：'
                    this.input.value = this.selectInfo.id ? '' : val.name + '：'
                    // 输入框获取焦点
                    inputDom.focus()
                    if (val.children) {
                        this.selectTagList = []
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
                if (!this.selectInfo.id || this.selectInfo.children) {
                    this.isVisible = true
                }
            },
            handleInputCut () {
                console.log('cut')
            },
            // 文本框内容改变
            handleInputChange (e) {
                const text = e.target.innerText
                this.input.value = this.selectInfo.id ? text.slice(text.indexOf('：') + 1) : text.trim()
                this.hoverId = ''
                if (this.selectInfo.id) {
                    // 不包含：标识符默认为自定义搜索条件
                    if (text.indexOf('：') === -1) {
                        this.selectInfo = {}
                    }
                } else {
                    this.selectInfo = {}
                }
                if (!text && !this.searchSelectValue.length) { // 没有自定义搜索条件和已选中条件，重置searchPopover
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
                        this.handleDocumentKeydown(e)
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
                    if (this.hoverId) {
                        const option = this.optionList.find(item => item.id === this.hoverId)
                        if (!this.selectInfo.multiable) {
                            this.hoverId = ''
                        }
                        if (this.selectInfo.id) {
                            this.handleOptionSelect(option)
                        } else {
                            this.handleResultOptionSelect(option)
                        }
                        this.handleInputFocus()
                        return
                    }
                    if (!this.input.value) {
                        return
                    }
                    let info = {}
                    const { id, children } = this.selectInfo
                    if (id) {
                        const index = this.searchSelectValue.findIndex(item => item.id === id)
                        if (index > -1) { // 多选
                            const selectContent = this.searchSelectValue[index]
                            const isMatch = selectContent.values.some(item => item === this.input.value)
                            if (!isMatch) {
                                selectContent.values.push(this.input.value)
                            }
                        } else {
                            if (children && !this.optionList.length) return // 当包含子项时，如果输入匹配列表为空时，回车禁止选中
                            info = {
                                ...this.selectInfo,
                                values: [this.input.value]
                            }
                            this.searchSelectValue.push(info)
                        }
                    } else {
                        const isMatch = this.searchSelectValue.some(item => item.isDefaultOption)
                        if (!isMatch) {
                            const defaultOption = this.list.find(item => item.isDefaultOption) || {}
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

                    this.hoverId = ''
                    this.input.value = ''
                    this.$refs.input.innerText = ''
                    this.selectInfo = {}
                    this.isVisible = true
                }, 100)
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
                const cid = random4()
                if (list.length) {
                    const match = list.every(item => item.id !== data.id || !tools.isDataEqual(item.values, data.values))
                    if (match) {
                        list.unshift({ ...data, cid })
                    }
                    records[this.username][this.id] = list.splice(0, 10)
                } else {
                    records[this.username][this.id] = [{ ...data, cid }]
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
            setSearchSelectValue (data) {
                this.setInputFocus()
                const selectInfo = this.searchSelectValue.find(item => item.id === data.id)
                if (selectInfo) {
                    selectInfo.values = data.values
                } else {
                    this.searchSelectValue.push(data)
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
            },
            handleDocumentKeydown (e) {
                const len = this.optionList.filter(option => {
                    return this.judgeOptionShow(option)
                }).length
                if (len) {
                    e.preventDefault()
                    e.stopPropagation()
                    this.setInputFocus()
                    let curIndex = this.optionList.findIndex(set => set.id === this.hoverId)
                    curIndex = e.code === 'ArrowDown' ? curIndex + 1 : curIndex - 1
                    curIndex = curIndex > len - 1 ? 0 : (curIndex < 0 ? len - 1 : curIndex)
                    const option = this.optionList[curIndex]
                    if (option) {
                        this.hoverId = option.id
                    }
                }
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
        min-height: 30px;
        transition: max-height .3s cubic-bezier(0.4, 0, 0.2, 1);

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
                line-height: 30px;
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
            .tippy-content {
                padding: 0;
            }
        }
        .option-none {
            .search-list-menu {
                padding: 0;
            }
            .recent-search-list {
                margin-top: 0;
                &::before {
                    width: 100%;
                    left: 0;
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
            .icon-check-1 {
                font-size: 22px;
                color: #3a84ff;
            }
            &:hover,
            &.is-hover {
                background: #eaf3ff;
                color: #3a84ff;
            }
        }
        .search-menu-item {
            .search-menu-label {
                min-width: 60px;
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
        .no-search-data {
            height: 46px;
            width: 238px !important;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #63656e;
            cursor: default;
            &:hover {
                color: #63656e;
                background: none;
            }
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
