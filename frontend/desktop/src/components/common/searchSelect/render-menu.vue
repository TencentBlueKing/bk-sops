<template>
    <div class="render-menu-wrap">
        <template v-if="renderList.length">
            <ul class="menu-content">
                <li
                    v-for="option in renderList"
                    :key="option.id"
                    :class="[
                        'option-item',
                        {
                            'default-option': option.isDefaultOption && isShowSearchText,
                            'hover-option': hoverId === option.id,
                            'search-option': isShowSearchText
                        }
                    ]"
                    @click="handleOptionSelect(option)">
                    <span class="option-name">{{ option.name }}</span>
                    <span v-if="isShowSearchText" class="search-text">{{ '：' + inputValue }}</span>
                    <i
                        v-if="selectedOption.multiple && judgeOptionActive(option)"
                        class="bk-icon icon-check-1">
                    </i>
                </li>
            </ul>
            <div v-if="selectedOption.children && selectedOption.multiple" class="popover-footer">
                <span class="footer-btn" @click="selectOptionConfirm">{{ $t('确定') }}</span>
                <span class="footer-btn" @click="selectOptionCancel">{{ $t('取消') }}</span>
            </div>
        </template>
        <p v-else-if="selectedOption.children" class="no-data">{{ '查询无数据' }}</p>
    </div>
</template>
<script>
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
            inputValue: {
                type: String,
                default: ''
            },
            hoverId: {
                type: String,
                default: ''
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
                renderList: []
            }
        },
        computed: {
            isShowSearchText () {
                return !this.selectedOption.id && this.inputValue
            },
            baseRenderList () {
                // 过滤掉非多选的已选条件选项
                return this.searchList.filter(option => {
                    if (option.multiple) return true
                    return !this.searchValue.some(item => item.id === option.id)
                })
            }
            
        },
        watch: {
            searchValue: {
                handler () {
                    this.renderList = [...this.baseRenderList]
                },
                deep: true
            },
            selectedOption: {
                handler (val) {
                    let renderList = val.children || []
                    if (!val.id) {
                        renderList = [...this.baseRenderList]
                    }

                    this.renderList = renderList
                },
                immediate: true
            },
            inputValue: {
                handler (val) {
                    this.handleInputChange(val)
                }
            },
            renderList: {
                handler (val) {
                    this.$emit('updateOptionList', val)
                },
                immediate: true
            }
        },
        methods: {
            async handleInputChange (val) {
                try {
                    const { id, children, multiple, remoteMethod, isUser } = this.selectedOption
                    let renderList = children || []
                    if (id) {
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
                        return
                    }

                    this.renderList = [...this.baseRenderList]
                } catch (error) {
                    console.warn(error)
                }
            },
            judgeOptionActive (option) {
                return this.selectedOptionValue.some(tag => tag.id === option.id)
            },
            handleOptionSelect (option) {
                const { id, multiple } = this.selectedOption
                if (id) { // 选择子项
                    if (multiple) {
                        this.$emit('update:selectedOptionValue', option)
                    } else {
                        this.$emit('switchOption', option)
                    }
                } else if (this.inputValue) { // 选择搜索匹配项
                    this.$emit('update', {
                        ...option,
                        values: [this.inputValue]
                    })
                } else { // 选中条件选项
                    this.$emit('update:selectedOption', option)
                }
            },
            selectOptionConfirm () {
                const searchContent = this.searchValue.find(item => item.id === this.selectedOption.id)

                if (searchContent) {
                    const duplicateObj = {}
                    let values = searchContent.values.concat(this.selectedOptionValue)
                    values = values.reduce((acc, cur) => {
                        if (!duplicateObj[cur.id]) {
                            duplicateObj[cur.id] = true
                            acc.push(cur)
                        }
                        return acc
                    }, [])
                    searchContent.values = values
                    return
                }
                this.$emit('update', {
                    ...this.selectedOption,
                    values: [this.selectedOptionValue]
                })
            },
            selectOptionCancel () {
                this.$emit('cancelOption')
            }
        }
    }
</script>
