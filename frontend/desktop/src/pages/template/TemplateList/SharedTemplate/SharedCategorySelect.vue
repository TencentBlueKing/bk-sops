<template>
    <bk-select
        ref="categorySelect"
        :disabled="formData.type === 'update'"
        v-model="formData.category"
        :loading="loading"
        :show-empty="!categoryList.length"
        searchable
        :remote-method="onCategorySearch"
        @toggle="handleSelectToggle">
        <div
            slot="trigger"
            class="bk-select-name category-select"
            :data-placeholder="categorySelectPath ? '' : $t('请选择场景分类')">
            {{ categorySelectPath }}
            <i class="bk-select-angle bk-icon icon-angle-down"></i>
        </div>
        <template v-if="searchVal">
            <bk-option
                v-for="option in searchList"
                :key="option.id"
                :id="option.id"
                :name="option.name">
            </bk-option>
            <p v-if="!searchList.length" class="search-empty-info">{{ $t('搜索结果为空') }}</p>
        </template>
        <bk-big-tree
            v-else
            ref="categoryTree"
            :data="categoryList"
            selectable
            :show-link-line="false"
            :show-icon="false"
            :options="{ idKey: 'code_path' }"
            :default-expanded-nodes="defaultExpandedNodes"
            :default-selected-node="formData.category"
            :before-select="(node) => !node.children.length"
            @select-change="onCategorySelect">
        </bk-big-tree>
    </bk-select>
</template>
<script>
    export default {
        props: {
            categoryList: {
                type: Array,
                default: () => ([])
            },
            loading: {
                type: Boolean,
                default: false
            },
            formData: {
                type: Object,
                default: () => ({})
            }
        },
        data () {
            return {
                searchVal: '',
                searchList: []
            }
        },
        computed: {
            categorySelectPath () {
                return this.findPathByCodePath(this.categoryList, this.formData.category)
            },
            defaultExpandedNodes () {
                return this.categoryList.map(item => item.code_path)
            },
            categoryFlattenList () {
                return this.handleFlattenList(this.categoryList)
            }
        },
        methods: {
            onCategorySearch (val) {
                this.searchVal = val
                this.searchList = val
                    ? this.categoryFlattenList.filter(item => item.name.toLowerCase().indexOf(val.toLowerCase()) > -1)
                    : []
            },
            onCategorySelect (node) {
                this.formData.category = node.id
                this.$refs.categorySelect.close()
            },
            handleFlattenList (data, parentPath = '') {
                let result = []

                data.forEach(item => {
                    const currentPath = parentPath ? `${parentPath}-${item.name}` : item.name

                    if (item.children && item.children.length > 0) {
                        result = result.concat(this.handleFlattenList(item.children, currentPath))
                    } else {
                        result.push({ id: item.code_path, name: currentPath })
                    }
                })

                return result
            },
            findPathByCodePath (categoryList, targetCodePath) {
                const traverse = (node, path) => {
                    const currentPath = [...path, node.name]
                    if (node.code_path === targetCodePath) {
                        return currentPath
                    }

                    for (const child of node.children || []) {
                        const result = traverse(child, currentPath)
                        if (result) {
                            return result
                        }
                    }

                    return null
                }

                for (const rootNode of categoryList) {
                    const result = traverse(rootNode, [])
                    if (result) {
                        return result.join('-')
                    }
                }

                return null
            },
            handleSelectToggle () {
                this.searchVal = ''
                this.searchList = []
            }
        }
    }
</script>
<style lang="scss" scoped>
    
    .category-select::before {
        position: absolute;
        content: attr(data-placeholder);
        color: #c4c6cc;
    }
    .search-empty-info {
        margin: 15px 0;
        text-align: center;
    }
</style>
