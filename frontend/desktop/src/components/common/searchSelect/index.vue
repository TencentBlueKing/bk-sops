<template>
    <section
        ref="wrap"
        :class="['search-select', { 'is-focus': focused }]"
        v-bk-clickoutside="handleClickOutSide"
        @click="handleWrapClick">
        <!-- 已经选中的tag列表 -->
        <template v-if="searchValue.length">
            <RenderTag
                v-for="tagInfo in searchValue"
                :key="tagInfo.id"
                :tag-info="tagInfo"
                @focus="focused = $event"
                @handleTagClear="handleTagClear"
                @updateSelectTag="updateSelectTag">
            </RenderTag>
        </template>
        <div class="search-input-wrap">
            <bk-popover
                ref="searchPopover"
                placement="bottom-start"
                theme="light"
                trigger="manual"
                :allow="false"
                :distance="5"
                ext-cls="search-list-popover"
                :on-hide="handlePopHidden">
                <RenderInput
                    ref="renderInput"
                    :search-value.sync="searchValue"
                    :search-list="searchList"
                    :placeholder="placeholder"
                    :focused.sync="focused"
                    :selected-option.sync="selectedOption"
                    :menu-option-list="menuOptionList"
                    :selected-option-value.sync="selectedOptionValue"
                    @input="inputValue = $event"
                    @clear="handleClear"
                    @update="updateSearchValue"
                    @updateHoverId="hoverOptionId = $event"
                    @switchOption="handleOptionSelect" />
                <div slot="content" class="search-list-content">
                    <RenderMenu
                        :search-value="searchValue"
                        :search-list="searchList"
                        :input-value="inputValue"
                        :hover-id="hoverOptionId"
                        :selected-option.sync="selectedOption"
                        :selected-option-value.sync="selectedOptionValue"
                        @update="updateSearchValue"
                        @switchOption="handleOptionSelect"
                        @cancelOption="handleOptionCancel"
                        @updateOptionList="menuOptionList = $event" />
                    <!-- 最近搜索 -->
                    <searchRecord
                        v-if="!selectedOption.id"
                        :id="id"
                        :search-list="searchList"
                        :search-value.sync="searchValue"
                        @update="updateSearchValue"
                        @updateSelectTag="updateSelectTag" />
                </div>
            </bk-popover>
        </div>
    </section>
</template>
<script>
    import RenderInput from './render-input.vue'
    import RenderMenu from './render-menu.vue'
    import RenderTag from './render-tag.vue'
    import searchRecord from './search-record.vue'
    import { random4 } from '@/utils/uuid.js'
    import tools from '@/utils/tools.js'
    import { mapState } from 'vuex'

    export default {
        name: '',
        components: {
            RenderInput,
            RenderMenu,
            RenderTag,
            searchRecord
        },
        model: {
            prop: 'values',
            event: 'change'
        },
        props: {
            id: {
                type: String,
                default: ''
            },
            values: {
                type: Array,
                default: () => ([])
            },
            searchList: {
                type: Array,
                default: () => {
                    return []
                }
            },
            placeholder: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                focused: false,
                inputValue: '',
                searchValue: [],
                selectedOption: {}, // 选中的搜索选项
                menuOptionList: [], // 选项面板列表
                selectedOptionValue: [], // 搜索选项选中的值
                hoverOptionId: '',
                isVisible: false
            }
        },
        computed: {
            ...mapState({
                username: state => state.username
            })
        },
        watch: {
            values: {
                handler (val) {
                    if (!tools.isDataEqual(val, this.searchValue)) {
                        this.searchValue = [...val]
                    }
                },
                deep: true,
                immediate: true
            },
            isVisible (val) {
                if (val) {
                    this.showPopover()
                } else {
                    this.hidePopover()
                }
            },
            searchValue: {
                handler (val) {
                    this.$emit('change', val)
                },
                deep: true
            }
        },
        methods: {
            showPopover () {
                const instance = this.$refs.searchPopover
                instance.showHandler()
            },
            hidePopover () {
                const instance = this.$refs.searchPopover
                instance.hideHandler()
            },
            setInputFocus () {
                this.$refs.renderInput.focus()
                this.showPopover()
            },
            handlePopHidden () {
                this.isVisible = false
            },
            handleWrapClick () {
                this.focused = true
                this.setInputFocus()
                this.isVisible = true
            },
            handleClickOutSide () {
                if (!this.isVisible) this.focused = false
            },
            updateSearchValue (data) {
                this.searchValue.push(data)
                this.selectedOption = {}
                this.selectedOptionValue = []
                this.isVisible = true

                // 添加搜索记录
                this.addSearchRecord(data)
            },
            handleClear () {
                this.searchValue = []
                this.selectedOption = {}
                this.selectedOptionValue = []
                this.isVisible = true
            },
            handleOptionSelect (option) {
                console.log(option)
                // 选择条件选项值
                if (this.selectedOption.id) {
                    const valIndex = this.selectedOptionValue.findIndex(item => item.id === this.inputValue)
                    // 新增或移除
                    if (valIndex > -1) {
                        this.selectedOptionValue.splice(valIndex, 1)
                    } else {
                        this.selectedOptionValue.push(option)
                    }
                } else if (this.inputValue) {
                    // 直接创建tag
                    this.updateSearchValue({
                        ...option,
                        values: [this.inputValue]
                    })
                    this.selectedOption = {}
                } else {
                    // 选择条件选项
                    this.selectedOption = option
                    this.isVisible = !!option.children
                }
            },
            handleOptionCancel () {
                this.isVisible = false
                this.selectedOptionValue = []
            },
            handleTagClear (id) {
                const index = this.searchValue.findIndex(item => item.id === id)
                this.searchValue.splice(index, 1)
                this.setInputFocus()
            },
            updateSelectTag (data) {
                const index = this.searchValue.findIndex(item => item.id === data.id)
                this.searchValue.splice(index, 1, data)
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
            }
        }
    }
</script>
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
        .menu-content {
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
        .option-item {
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
            &:hover {
                background: #eaf3ff;
                color: #3a84ff;
            }
        }
        .search-option {
            .option-name {
                min-width: 72px;
                text-align: right;
                padding-left: 12px !important;
                font-weight: 700;
                white-space: nowrap;
            }
            .search-text {
                flex: 1;
                text-align: left;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
        }
        .default-option {
            background: #eaf3ff;
            color: #3a84ff;
        }
        .hover-option {
            background: #eaf3ff;
            color: #3a84ff;
        }
        .no-data {
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
    }
</style>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    .search-select {
        position: absolute;
        right: 0;
        z-index: 666;
        background: #fff;
        display: flex;
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
            height: max-content;
            border-color: #3a84ff;
        }
    }
    .search-input-wrap {
        position: relative;
        padding: 0 8px;
        color: #63656e;
        flex: 1 1 auto;
        border: none;
        min-width: 40px;
        display: flex;
        align-items: center;
        /deep/ .bk-tooltip {
            width: 100%;
            .bk-tooltip-ref {
                width: 100%;
            }
        }
    }
</style>
