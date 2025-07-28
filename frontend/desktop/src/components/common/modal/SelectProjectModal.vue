/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
<template>
    <bk-dialog
        width="600"
        render-directive="if"
        ext-cls="common-dialog"
        :title="title"
        :header-position="'left'"
        :mask-close="false"
        :auto-close="false"
        :value="show"
        @cancel="handleCancel">
        <div class="select-wrapper">
            <bk-form>
                <bk-form-item :label="$t('选择项目')">
                    <bk-checkbox
                        v-model="isOutermostAllProjectScope"
                        v-if="isSetProjectVisible"
                        @change="handleSelectAllProjectScope">
                        {{ $t('全选') }}
                    </bk-checkbox>
                    <bk-select class="project-select"
                        v-if="isSetProjectVisible"
                        ref="projectSelectRef"
                        :searchable="true"
                        :clearable="true"
                        :multiple="true"
                        :display-tag="true"
                        :auto-height="false"
                        :disabled="isOutermostAllProjectScope"
                        @change="handleProjectVisibleChange"
                        v-model="localProjectScopeList">
                        <bk-option-group
                            v-for="(group, index) in projects"
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
                    <bk-select v-else
                        class="project-select"
                        :clearable="false"
                        :searchable="true"
                        :value="id"
                        @change="handleProjectSelect">
                        <bk-option-group
                            v-for="(group, index) in projects"
                            :name="group.name"
                            :key="index">
                            <bk-option
                                class="project-item"
                                v-for="option in group.children"
                                :key="option.id"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-option-group>
                    </bk-select>
                    <div v-if="hasError" class="common-error-tip error-msg">{{ $t('请选择项目') }}</div>
                </bk-form-item>
            </bk-form>
        </div>
        <div class="dialog-footer" slot="footer">
            <bk-button
                theme="primary"
                :class="{ 'btn-permission-disable': confirmCursor }"
                :loading="confirmLoading"
                v-cursor="{ active: confirmCursor }"
                @click="handleConfirm">
                {{ $t('确定') }}
            </bk-button>
            <bk-button @click="handleCancel">{{ $t('取消') }}</bk-button>
        </div>
    </bk-dialog>
</template>
<script>
    import { mapState } from 'vuex'
    import i18n from '@/config/i18n/index.js'

    export default {
        name: 'SelectProjectModal',
        props: {
            title: String,
            show: Boolean,
            project: Number,
            confirmLoading: {
                type: Boolean,
                default: false
            },
            confirmCursor: {
                type: Boolean,
                default: false
            },
            isSetProjectVisible: {
                type: Boolean,
                default: false
            },
            projectScopeList: {
                type: Array,
                default: () => []
            }
        },
        data () {
            return {
                id: this.project,
                hasError: false,
                localProjectScopeList: [],
                isSelectAllProjectScope: false,
                isOutermostAllProjectScope: false,
                isDropdownOpen: false,
                isFirstOpen: true,
                projects: []
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
            project (val) {
                this.id = val
            },
            projectList: {
                handler (val) {
                    if (val && this.projectScopeList) {
                        this.initProjects()
                    }
                },
                immediate: true
            },
            projectScopeList: {
                handler (val) {
                    if (val.includes('*')) {
                        this.localProjectScopeList = this.allProjectIds
                        this.isOutermostAllProjectScope = true
                    } else {
                        this.localProjectScopeList = [...val]
                        this.isOutermostAllProjectScope = this.localProjectScopeList.length === this.allProjectIds.length
                    }
                    if (this.projectList && this.projectList.length && val) {
                        this.initProjects()
                    }
                },
                immediate: true
            },
            isDropdownOpen: {
                handler (val) {
                    if (!val) {
                        if (this.localProjectScopeList.length > 0) {
                            this.processingProjectsToTop(this.localProjectScopeList, this.projects)
                        }
                    }
                },
                immediate: true
            }

        },
        mounted () {
            document.addEventListener('click', this.handleClickOutside)
        },
        methods: {
            processingProjectsToTop (val, projects) {
                val.forEach((item) => {
                    projects.map((group) => {
                        group.children.map((project, index) => {
                            if (project.id === item) {
                                const tempItem = group.children.splice(index, 1)[0]
                                group.children.unshift(tempItem)
                            }
                        })
                    })
                })
                return projects
            },
            initProjects () {
                if (!this.projectList || !this.projectScopeList) {
                    return []
                }
                let projects = []
                const projectsGroup = [
                    {
                        name: i18n.t('业务'),
                        id: 1,
                        children: []
                    },
                    {
                        id: 2,
                        name: i18n.t('项目'),
                        children: []
                    }
                ]
                if (this.projectList) {
                    this.projectList.forEach(item => {
                        if (item.from_cmdb) {
                            projectsGroup[0].children.push(item)
                        } else {
                            projectsGroup[1].children.push(item)
                        }
                    })
                    projectsGroup.forEach(group => {
                        if (group.children.length) {
                            projects.push(group)
                        }
                    })
                    if (this.projectScopeList.length > 0 && !this.projectScopeList.includes('*')) {
                        projects = this.processingProjectsToTop(this.projectScopeList, projects)
                    }
                }
                this.projects = projects
            },
            handleClickOutside (event) {
                const isHaveSomeClassName = event.target.classList.contains('bk-option-name') || event.target.classList.contains('bk-group-options') || event.target.classList.contains('bk-option-content-default')
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
            },
            handleProjectVisibleChange (row) {
                this.localProjectScopeList = [...new Set(row)]
                this.$emit('onVisibleChange', { project_scope: this.localProjectScopeList, isSelectAllProjectScope: this.localProjectScopeList.length === this.allProjectIds.length })
            },
            handleSelectAllProjectScope (row) {
                if (row) {
                    this.localProjectScopeList = this.allProjectIds
                } else {
                    this.localProjectScopeList = []
                }
                this.$emit('onVisibleChange', { project_scope: this.localProjectScopeList, isSelectAllProjectScope: row })
            },
            handleProjectSelect (id) {
                this.id = id
                this.hasError = false
                const project = this.projectList.find(item => item.id === this.id)
                this.$emit('onChange', project)
            },
            handleConfirm () {
                if (this.isSetProjectVisible) {
                    this.$emit('onVisibleConfirm', { isSelectAllProjectScope: this.localProjectScopeList.length === this.allProjectIds.length })
                } else {
                    if (this.confirmLoading) {
                        return
                    }
                    if (typeof this.id === 'number') {
                        const project = this.projectList.find(item => item.id === this.id)
                        this.$emit('onConfirm', project)
                    } else {
                        this.hasError = true
                    }
                }
            },
            handleCancel () {
                if (this.isSetProjectVisible) {
                    this.$emit('onVisibleCancel')
                } else {
                    this.id = ''
                    this.hasError = false
                    this.$emit('onCancel')
                }
            }
        },
        unmounted () {
            document.removeEventListener('click', this.handleClickOutside)
        }
    }
</script>
<style lang="scss" scoped>
    .select-wrapper {
        padding: 30px;
    }
    .project-select {
        width: 260px;
    }
    .select-all-project-scope{
        margin: 0 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #dcdee5;
    }
    .select-all-project-scope-checkbox{
        margin-right: 14px;
    }
</style>
