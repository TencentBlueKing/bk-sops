                    
<template>
    <section class="sort-header">
        <p v-bk-overflow-tips class="label-text">{{ name }}</p>
        <span class="caret-wrapper" @click="handleSort()" v-if="orderShow">
            <i
                class="bk-table-sort-caret ascending"
                :class="{ 'active': sortOrder === 'ascending' }"
                @click.stop="handleSort('ascending')">
            </i>
            <i
                class="bk-table-sort-caret descending"
                :class="{ 'active': sortOrder === 'descending' }"
                @click.stop="handleSort('descending')">
            </i>
        </span>
        <bk-popover
            v-if="filterConfig.show"
            placement="bottom"
            theme="light"
            trigger="click"
            :distance="6"
            :arrow="false"
            :ext-cls="`table-header-filter-popover ${filterConfig.extCls}`"
            :on-hide="() => isFilterOpen = false">
            <i
                class="bk-table-column-filter-trigger bk-icon icon-funnel"
                :class="{ 'is-selected': isSelected, 'is-open': isFilterOpen }"
                @click="isFilterOpen = !isFilterOpen">
            </i>
            <div slot="content">
                <template v-if="filterConfig.list.length">
                    <ul class="option-list">
                        <li
                            v-for="item in filterConfig.list"
                            :key="item.id"
                            :class="['option-item', { 'is-checked': judgeOptionSelected(item) }]"
                            @click="handleFilter(item)">
                            <span
                                v-if="item.color"
                                class="label-name"
                                :style="{ background: item.color, color: item.textColor }">
                                {{ item.name }}
                            </span>
                            <span v-else>{{ item.name }}</span>
                            <i class="check-icon bk-icon icon-check-line"></i>
                        </li>
                    </ul>
                    <p v-if="filterConfig.multiple" class="clear-checked" @click="handleClearFilter">{{ $t('清空筛选') }}</p>
                </template>
                <p v-else class="no-search-data">{{ $t('查询无数据') }}</p>
            </div>
        </bk-popover>
        <bk-date-picker
            v-if="dateFilterShow"
            :value="dateTimeRange"
            :open="isFilterOpen"
            :shortcuts="shortcuts"
            :type="'datetimerange'"
            :transfer="true"
            ext-popover-cls="date-time-range-popover"
            @open-change="handleDateOpenChange"
            @change="handleChange"
            @clear="handleClear"
            @pick-success="handlePickSuccess">
            <i
                slot="trigger"
                class="bk-table-column-filter-trigger bk-icon icon-funnel"
                :class="{ 'is-filtered': isFiltered, 'is-open': isFilterOpen }"
                @click.stop="isFilterOpen = !isFilterOpen">
            </i>
        </bk-date-picker>
    </section>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    export default {
        name: 'TableRenderHeader',
        props: {
            name: {
                type: String,
                default: ''
            },
            orderShow: {
                type: Boolean,
                default: true
            },
            dateFilterShow: {
                type: Boolean,
                default: true
            },
            property: {
                type: String,
                default: ''
            },
            sortConfig: {
                type: Object,
                default: () => ({})
            },
            dateValue: {
                type: Array,
                default: () => ([])
            },
            filterConfig: {
                type: Object,
                default: () => {
                    return {
                        show: false,
                        list: [],
                        values: [],
                        multiple: false,
                        extCls: ''
                    }
                }
            }
        },
        data () {
            return {
                sortOrder: '',
                dateTimeRange: [],
                isFilterOpen: false,
                shortcuts: [
                    {
                        text: i18n.t('今天'),
                        value () {
                            const end = new Date()
                            const start = new Date(end.getFullYear(), end.getMonth(), end.getDate())
                            return [start, end]
                        },
                        onClick: picker => {
                            console.log(picker)
                        }
                    },
                    {
                        text: i18n.t('近7天'),
                        value () {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
                            return [start, end]
                        }
                    },
                    {
                        text: i18n.t('近15天'),
                        value () {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 15)
                            return [start, end]
                        }
                    },
                    {
                        text: i18n.t('近30天'),
                        value () {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
                            return [start, end]
                        }
                    }
                ]
            }
        },
        computed: {
            isFiltered () {
                return this.dateValue.length
                    ? this.dateValue.every(date => date)
                    : false
            },
            isSelected () {
                return this.filterConfig.values.length
            }
        },
        watch: {
            sortConfig: {
                handler (val) {
                    this.sortOrder = val.prop === this.property ? val.order : ''
                },
                deep: true,
                immediate: true
            },
            dateValue: {
                handler (val) {
                    this.dateTimeRange = val
                },
                deep: true,
                immediate: true
            }
        },
        methods: {
            handleSort (order) {
                if (order) {
                    this.sortOrder = order
                } else {
                    this.sortOrder = this.sortOrder === 'ascending'
                        ? ''
                        : this.sortOrder === ''
                            ? 'descending'
                            : this.sortOrder === 'descending'
                                ? 'ascending' : ''
                }
                this.$emit('sortChange', { prop: this.property, order: this.sortOrder })
            },
            handleDateOpenChange (state) {
                this.isFilterOpen = state
                if (state) {
                    this.dateTimeRange = [...this.dateValue]
                }
            },
            handleChange (date) {
                this.dateTimeRange = date
            },
            handleClear () {
                this.dateTimeRange = []
                this.$emit('dateChange', [])
            },
            handlePickSuccess () {
                this.$emit('dateChange', this.dateTimeRange)
            },
            judgeOptionSelected (data) {
                return this.filterConfig.values.find(item => item.id === data.id)
            },
            handleFilter (data) {
                let values = this.filterConfig.values
                const index = values.findIndex(item => item.id === data.id)
                if (index > -1) {
                    values.splice(index, 1)
                } else {
                    if (this.filterConfig.multiple) {
                        values.push(data)
                    } else {
                        values = [data]
                    }
                }
                this.$emit('filterChange', values)
            },
            handleClearFilter () {
                if (this.filterConfig.values.length) {
                    this.filterConfig.values = []
                    this.$emit('filterChange', [])
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    .sort-header {
        position: relative;
        display: inline-flex;
        align-items: center;
        justify-content: left;
        min-width: 90px;
        height: 42px;
        width: 100%;
        .caret-wrapper {
            flex-shrink: 0;
            height: 20px;
            vertical-align: middle;
            cursor: pointer;
            position: relative;
            margin: 0 10px;
            .bk-table-sort-caret {
                width: 0;
                height: 0;
                border: solid 5px transparent;
                position: absolute;
                &.ascending {
                    border-bottom-color: #c0c4cc;
                    top: -1px;
                    &.active {
                        border-bottom-color: #3a84ff;
                    }
                }
                &.descending {
                    border-top-color: #c0c4cc;
                    bottom: -1px;
                    &.active {
                        border-top-color: #3a84ff;
                    }
                }
            }
        }
        .bk-table-column-filter-trigger {
            font-size: 14px;
            text-align: center;
            cursor: pointer;
            color: #c4c6cc;
            &.is-open {
                color: #63656e;
            }
            &.is-selected,
            &.is-filtered {
                color: #3a84ff;
            }
        }
        .bk-date-picker {
            flex-shrink: 0;
            width: 14px;
            margin-left: 5px;
        }
    }
</style>
<style lang="scss">
    @import '@/scss/mixins/scrollbar.scss';
    .date-time-range-popover {
        .bk-picker-panel-body {
            .bk-picker-confirm {
                font-size: 12px;
                a:nth-child(2) {
                    color: #3a84ff;
                }
                .confirm {
                    display: inline-block;
                    width: 56px;
                    height: 26px;
                    text-align: center;
                    line-height: 26px;
                    color: #fff;
                    background: #3A84FF;
                    border-radius: 2px;
                    margin-left: 16px;
                }
            }
        }
        .bk-picker-panel-sidebar {
            color: #63656e;
            font-size: 12px;
            .bk-picker-panel-shortcut {
                height: 32px;
                line-height: 32px;
                padding: 0 21px;
                &:hover {
                    color: #3a84ff;
                }
            }
        }
    }
    .table-header-filter-popover {
        .tippy-tooltip {
            padding: 4px 0 0 0;
            .tippy-content {
                background: #fff;
            }
        }
        .option-list {
            width: 200px;
            max-height: 350px;
            overflow: auto;
            @include scrollbar;
            margin-bottom: 15px;
            .option-item {
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 15px;
                color: #63656e;
                cursor: pointer;
                .label-name {
                    padding: 2px 6px;
                    font-size: 12px;
                    color: #63656e;
                    border-radius: 8px;
                }
                .check-icon {
                    display: none;
                    font-size: 18px;
                    color: #3a84ff;
                }
                &:hover {
                    background: #f5f7fa;
                }
            }
            .is-checked {
                background: #e1ecff !important;
                .check-icon {
                    display: inline-block;
                }
            }
        }
        .clear-checked {
            text-align: right;
            margin: 0 16px;
            padding: 16px 0;
            color: #3a84ff;
            cursor: pointer;
            border-top: 1px solid #dedee5;
        }
        .no-search-data {
            width: 200px;
            line-height: 32px;
            text-align: center;
            color: #63656e;
        }
    }
</style>
