<template>
    <div class="project-scope-select-wrapper">
        <bk-select class="project-select"
            ref="projectSelectRef"
            :searchable="true"
            :clearable="true"
            :multiple="true"
            :display-tag="true"
            :auto-height="false"
            :ext-cls="extCls"
            :disabled="disabled"
            :readonly="readonly"
            :remote-method="handleRemoteSearch"
            :search-placeholder="$t('输入关键词搜索,批量搜索使用逗号分隔')"
            @change="handleChange"
            v-model="localValue">
            <bk-option-group
                v-for="(group, index) in filteredProjects"
                :name="group.name"
                :key="index"
                :show-select-all="true">
                <bk-option v-for="item in group.children"
                    :key="item.id"
                    :id="item.id"
                    :name="item.name">
                </bk-option>
            </bk-option-group>
        </bk-select>
        <ScopeCopyPaste
            :show-copy-paste="showCopyPaste"
            :is-view-mode="isViewMode"
            :scope-data="scopeData"
            :all-project-ids="allProjectIds"
            :is-in-common-list="isInCommonList"
            @paste="$emit('paste', $event)" />
    </div>
</template>

<script>
    import { mapState } from 'vuex'
    import i18n from '@/config/i18n/index.js'
    import ScopeCopyPaste from '../ScopeCopyPaste.vue'

    export default {
        name: 'ProjectScopeSelect',
        components: {
            ScopeCopyPaste
        },
        props: {
            value: {
                type: Array,
                default: () => []
            },
            // 用于置顶的已选项目列表
            projectScopeList: {
                type: Array,
                default: () => []
            },
            disabled: {
                type: Boolean,
                default: false
            },
            readonly: {
                type: Boolean,
                default: false
            },
            isViewMode: {
                type: Boolean,
                default: false
            },
            showCopyPaste: {
                type: Boolean,
                default: true
            },
            isInCommonList: {
                type: Boolean,
                default: false
            },
            extCls: {
                type: String,
                default: ''
            },
            scopeData: {
                type: Object,
                default: () => ({})
            }
        },
        data () {
            return {
                localValue: [...this.value],
                projects: [],
                filteredProjects: [],
                isDropdownOpen: false,
                isFirstOpen: true
            }
        },
        computed: {
            ...mapState('project', {
                projectList: state => state.userProjectList
            }),
            allProjectIds () {
                const allIds = []
                this.projects.forEach((group) => {
                    group.children.forEach((item) => {
                        allIds.push(item.id)
                    })
                })
                return allIds
            }
        },
        watch: {
            value (val) {
                this.localValue = [...val]
            },
            projectList: {
                handler (val) {
                    if (val && val.length) {
                        this.initProjects()
                    }
                },
                immediate: true
            },
            isDropdownOpen: {
                handler (val) {
                    if (!val && this.localValue.length > 0) {
                        this.processingProjectsToTop(this.localValue, this.projects)
                    }
                }
            }
        },
        mounted () {
            document.addEventListener('click', this.handleClickOutside)
        },
        beforeDestroy () {
            document.removeEventListener('click', this.handleClickOutside)
        },
        methods: {
            processingProjectsToTop (val, projects) {
                val.forEach((item) => {
                    const id = typeof item === 'number' ? item : Number(item)
                    projects.forEach((group) => {
                        group.children.forEach((project, index) => {
                            if (project.id === id) {
                                const tempItem = group.children.splice(index, 1)[0]
                                group.children.unshift(tempItem)
                            }
                        })
                    })
                })
                return projects
            },
            buildGroupedProjects (list) {
                const projectsGroup = [
                    { name: i18n.t('业务'), id: 1, children: [] },
                    { name: i18n.t('项目'), id: 2, children: [] }
                ]
                list.forEach(item => {
                    if (item.from_cmdb) {
                        projectsGroup[0].children.push(item)
                    } else {
                        projectsGroup[1].children.push(item)
                    }
                })
                const projects = projectsGroup.filter(group => group.children.length)
                if (this.projectScopeList.length > 0 && !this.projectScopeList.includes('*')) {
                    return this.processingProjectsToTop(this.projectScopeList, projects)
                }
                return projects
            },
            handleRemoteSearch (keyword) {
                if (!keyword) {
                    this.filteredProjects = this.projects
                }
                // 支持逗号（中英文）分隔
                const keywords = keyword.split(/[,|\uff0c]/).map(k => k.trim()).filter(k => k)
                console.log('keywords', keywords)
                const searchList = this.projectList.filter(project => {
                    if (!project.name) return false
                    return keywords.some(kw => project.name.toLowerCase().includes(kw.toLowerCase()))
                })
                this.filteredProjects = this.buildGroupedProjects(searchList)
                console.log('filteredProjects', this.filteredProjects)
            },
            initProjects () {
                if (!this.projectList) {
                    return
                }
                const projects = this.buildGroupedProjects(this.projectList)
                this.projects = projects
                this.filteredProjects = projects
            },
            handleChange (val) {
                this.localValue = [...new Set(val)]
                this.$emit('change', this.localValue)
            },
            handleClickOutside (event) {
                const isHaveSomeClassName = event.target.classList.contains('bk-option-name')
                    || event.target.classList.contains('bk-group-options')
                    || event.target.classList.contains('bk-option-content-default')
                if (!isHaveSomeClassName) {
                    if (this.$refs.projectSelectRef && this.$refs.projectSelectRef.$el.contains(event.target)) {
                        if (this.isFirstOpen) {
                            this.isDropdownOpen = true
                            this.isFirstOpen = false
                        } else {
                            this.isDropdownOpen = false
                            this.isFirstOpen = true
                        }
                    } else {
                        this.isDropdownOpen = false
                        this.isFirstOpen = true
                    }
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    ::v-deep .common-scope-select {
        width: 300px;
        .bk-select-dropdown {
            .bk-tooltip-ref {
                width: 250px !important;
            }
        }
    }
</style>
