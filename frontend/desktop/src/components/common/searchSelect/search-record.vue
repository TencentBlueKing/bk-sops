<template>
    <dl class="recent-search-list" v-if="recordsData.length">
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
</template>
<script>
    import { mapState } from 'vuex'
    export default {
        props: {
            id: {
                type: String,
                default: ''
            },
            searchList: {
                type: Array,
                default: () => {
                    return []
                }
            },
            searchValue: {
                type: Array,
                default: () => {
                    return []
                }
            }
        },
        data () {
            return {
                records: []
            }
        },
        computed: {
            ...mapState({
                lang: state => state.lang,
                username: state => state.username
            }),
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
        mounted () {
            this.records = this.getSearchRecords()
        },
        methods: {
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
                const selectInfo = this.searchValue.find(item => item.id === data.id)
                if (selectInfo) {
                    this.$emit('updateSelectTag', { ...selectInfo, values: data.values })
                } else {
                    this.$emit('update', data)
                }
            },
            // 删除搜索数据
            onDeleteRecord (record) {
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
</style>
