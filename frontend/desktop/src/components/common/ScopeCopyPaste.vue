<template>
    <div :class="['scope-copy-paste', isInCommonList ? 'list-absolute-position' : 'basicinfo-absolute-position']"
        v-if="showCopyPaste">
        <div :title="$t('复制')" class="operate-icon" @click="handleCopy">
            <svg viewBox="0 0 72 72" version="1.1" xmlns="http://www.w3.org/2000/svg">
                <path fill="currentColor" fill-rule="evenodd" d="M54,0 C55.1045695,-2.02906125e-16 56,0.8954305 56,2 L56,47 C56,48.0543618 55.1841222,48.9181651 54.1492623,48.9945143 L54,49 L54,49 L43,49 L43,53 C43,54.1045695 42.1045695,55 41,55 L2,55 C0.8954305,55 1.3527075e-16,54.1045695 0,53 L0,14 C-1.3527075e-16,12.8954305 0.8954305,12 2,12 L12,12 L12,2 C12,0.8954305 12.8954305,0 14,0 L54,0 Z M24,21 L20,21 C19.4477153,21 19,21.4477153 19,22 L19,30 L11,30 C10.4477153,30 10,30.4477153 10,31 L10,35 C10,35.5522847 10.4477153,36 11,36 L19,36 L19,44 C19,44.5522847 19.4477153,45 20,45 L24,45 C24.5522847,45 25,44.5522847 25,44 L25,36 L33,36 C33.5522847,36 34,35.5522847 34,35 L34,31 C34,30.4477153 33.5522847,30 33,30 L25,30 L25,22 C25,21.4477153 24.5522847,21 24,21 Z M50,6 L18,6 L18,12 L41,12 C42.1045695,12 43,12.8954305 43,14 L43,43 L50,43 L50,6 Z" transform="translate(8 8)" />
            </svg>
        </div>
        <div :title="$t('粘贴')" class="operate-icon" v-if="!isViewMode && hasClipboardData" @click="handlePaste">
            <svg viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg">
                <path fill="currentColor" d="M928 547.2c0-9.6-3.2-17.6-9.6-24L651.2 254.4v-3.2V131.2c0-19.2-16-35.2-35.2-35.2H131.2C112 96 96 112 96 131.2v624c0 19.2 16 35.2 35.2 35.2h243.2v104c0 19.2 16 35.2 35.2 35.2h484.8c19.2 0 35.2-16 35.2-35.2V598.4v-35.2L928 547.2 928 547.2zM809.6 512h-158.4v-158.4L809.6 512zM200 164.8h347.2v68.8h-139.2-208V164.8zM859.2 598.4v259.2h-416V304h139.2v243.2c0 19.2 16 35.2 35.2 35.2h243.2V598.4z" />
            </svg>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'ScopeCopyPaste',
        props: {
            // 是否显示复制粘贴按钮
            showCopyPaste: {
                type: Boolean,
                default: true
            },
            // 是否为查看模式
            isViewMode: {
                type: Boolean,
                default: false
            },
            // 当前的项目范围数据
            scopeData: {
                type: Object,
                default: () => ({})
            },
            // 所有可用的项目ID列表
            allProjectIds: {
                type: Array,
                default: () => []
            },
            storageKey: {
                type: String,
                default: 'project_scope_clipboard'
            },
            isInCommonList: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                hasClipboardData: false
            }
        },
        created () {
            this.checkClipboardData()
        },
        methods: {
            handleCopy () {
                try {
                    const copyData = {
                        isAllScope: this.scopeData.projectIds.length === this.allProjectIds.length || this.scopeData.isAllScope,
                        projectIds: this.scopeData.projectIds.slice(),
                        timestamp: Date.now()
                    }
                    localStorage.setItem(this.storageKey, JSON.stringify(copyData))
                    this.hasClipboardData = true
                    this.$bkMessage({
                        message: this.$t('复制成功'),
                        theme: 'success'
                    })
                } catch (error) {
                    this.$bkMessage({
                        message: this.$t('复制失败'),
                        theme: 'error'
                    })
                }
            },
            handlePaste () {
                try {
                    const clipboardData = localStorage.getItem(this.storageKey)
                    if (!clipboardData) {
                        this.$bkMessage({
                            message: this.$t('剪贴板中没有数据'),
                            theme: 'warning'
                        })
                        return
                    }
                
                    const pasteData = JSON.parse(clipboardData)
                
                    // 过滤出当前项目列表中存在的项目ID
                    const validProjectIds = pasteData.projectIds.filter(id =>
                        this.allProjectIds.includes(Number(id))
                    )
                
                    if (validProjectIds.length === 0) {
                        this.$bkMessage({
                            message: this.$t('没有找到匹配的项目'),
                            theme: 'warning'
                        })
                        return
                    }
                
                    // 检查数据是否相同
                    const isSameData = this.isScopeDataSame(pasteData, validProjectIds)
                    if (isSameData) {
                        this.$bkMessage({
                            message: this.$t('粘贴数据与当前数据相同'),
                            theme: 'warning'
                        })
                        return
                    }
                
                    // 构造粘贴结果
                    const pasteResult = {
                        isAllScope: pasteData.isAllScope && validProjectIds.length === this.allProjectIds.length,
                        projectIds: validProjectIds.map(id => Number(id)),
                        originalData: pasteData,
                        filteredCount: pasteData.projectIds.length - validProjectIds.length
                    }
                
                    this.$emit('paste', pasteResult)
                
                    const successMsg = pasteResult.filteredCount === 0
                        ? this.$t('粘贴成功')
                        : this.$t('粘贴成功，部分项目因权限问题被过滤')
                
                    this.$bkMessage({
                        message: successMsg,
                        theme: 'success'
                    })
                } catch (error) {
                    this.$bkMessage({
                        message: this.$t('粘贴失败'),
                        theme: 'error'
                    })
                }
            },
        
            // 检查剪贴板数据
            checkClipboardData () {
                try {
                    const clipboardData = localStorage.getItem(this.storageKey)
                    if (clipboardData) {
                        const parsedData = JSON.parse(clipboardData)
                        // 验证数据格式和有效性
                        if (parsedData
                            && typeof parsedData === 'object'
                            && Array.isArray(parsedData.projectIds)
                            && typeof parsedData.isAllScope === 'boolean') {
                            // 定期一周过期
                            const isExpired = parsedData.timestamp
                                && (Date.now() - parsedData.timestamp > 7 * 24 * 60 * 60 * 1000)
                            if (isExpired) {
                                localStorage.removeItem(this.storageKey)
                                this.hasClipboardData = false
                                return
                            }
                            this.hasClipboardData = true
                            return
                        }
                    }
                    this.hasClipboardData = false
                } catch (error) {
                    console.error(error)
                    this.hasClipboardData = false
                    localStorage.removeItem(this.storageKey)
                }
            },
            // 检查粘贴数据是否与当前数据相同
            isScopeDataSame (pasteData, validProjectIds) {
                // 如果剪贴板数据是全选
                if (pasteData.isAllScope) {
                    // 当前也是全选，且有效项目ID包含所有项目，则认为相同
                    return this.scopeData.isAllScope
                        && validProjectIds.length === this.allProjectIds.length
                }
                // 如果当前是全选，但剪贴板不是全选，则不同
                if (this.scopeData.isAllScope) {
                    return false
                }
                const currentIds = [...this.scopeData.projectIds].sort((a, b) => a - b)
                const pasteIds = [...validProjectIds].map(id => Number(id)).sort((a, b) => a - b)
                if (currentIds.length !== pasteIds.length) {
                    return false
                }
                return currentIds.every((id, index) => id === pasteIds[index])
            }
        }

    }
</script>

<style lang="scss" scoped>
.scope-copy-paste {
    position: absolute;
    top: 38px;
    display: flex;
    .operate-icon {
        height: 16px;
        width: 16px;
        margin-right: 5px;
        color: #979ba5;
        cursor: pointer;
        display: flex;
        &:hover {
            color: #3a84ff;
            background-color: #f0f8ff;
        }
    }
}
.list-absolute-position {
    right: 110px;
}
.basicinfo-absolute-position {
    right: 20px;
}
</style>
