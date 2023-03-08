                    
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
        <bk-date-picker
            :value="dateTimeRange"
            :open="isDateOpen"
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
                :class="{ 'is-filtered': isFiltered, 'is-open': isDateOpen }"
                @click.stop="isDateOpen = !isDateOpen">
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
            }
        },
        data () {
            return {
                sortOrder: '',
                dateTimeRange: [],
                isDateOpen: false,
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
                this.isDateOpen = state
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
            display: inline-flex;
            flex-shrink: 0;
            flex-direction: column;
            align-items: center;
            height: 20px;
            flex: 20px 0 0;
            vertical-align: middle;
            cursor: pointer;
            position: relative;
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
</style>
