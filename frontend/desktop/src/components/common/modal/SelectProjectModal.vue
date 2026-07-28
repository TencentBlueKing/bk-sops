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
                    <template v-if="isSetProjectVisible">
                        <ProjectScopeSelect
                            :value="localProjectScopeList"
                            :project-scope-list="projectScopeList"
                            :disabled="isOutermostAllProjectScope"
                            :show-copy-paste="!isOutermostAllProjectScope"
                            :scope-data="currentScopeData"
                            :is-in-common-list="true"
                            ext-cls="common-scope-select"
                            @change="handleProjectVisibleChange"
                            @paste="onPasteSuccess" />
                    </template>
                    <bk-select v-else
                        class="project-select"
                        :clearable="false"
                        :searchable="true"
                        :value="id"
                        @change="handleProjectSelect">
                        <bk-option-group
                            v-for="(group, index) in groupedProjectList"
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
    import ProjectScopeSelect from './ProjectScopeSelect.vue'

    export default {
        name: 'SelectProjectModal',
        components: {
            ProjectScopeSelect
        },
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
                isOutermostAllProjectScope: false
            }
        },
        computed: {
            ...mapState('project', {
                projectList: state => state.userProjectList
            }),
            groupedProjectList () {
                if (!this.projectList) return []
                const groups = [
                    { name: this.$t('业务'), id: 1, children: [] },
                    { name: this.$t('项目'), id: 2, children: [] }
                ]
                this.projectList.forEach(item => {
                    groups[item.from_cmdb ? 0 : 1].children.push(item)
                })
                return groups.filter(g => g.children.length)
            },
            allProjectIds () {
                if (!this.projectList) return []
                return this.projectList.map(item => item.id)
            },
            currentScopeData () {
                return {
                    isAllScope: this.isOutermostAllProjectScope,
                    projectIds: this.localProjectScopeList.slice()
                }
            }
        },
        watch: {
            project (val) {
                this.id = val
            },
            projectScopeList: {
                handler (val) {
                    if (val.includes('*')) {
                        this.isOutermostAllProjectScope = true
                        this.localProjectScopeList = this.allProjectIds
                    } else {
                        this.localProjectScopeList = val.map(id => typeof id === 'string' ? Number(id) : id)
                        this.isOutermostAllProjectScope = false
                    }
                },
                immediate: true
            }
        },
        methods: {
            onPasteSuccess (result) {
                if (result.isAllScope) {
                    this.handleSelectAllProjectScope(true)
                } else {
                    this.isOutermostAllProjectScope = false
                    const numericIds = result.projectIds.map(id => typeof id === 'string' ? Number(id) : id)
                    this.localProjectScopeList = [...new Set(numericIds)]
                    this.$emit('onVisibleChange', { project_scope: this.localProjectScopeList, isSelectAllProjectScope: false })
                }
            },
            handleProjectVisibleChange (row) {
                this.localProjectScopeList = [...new Set(row)]
                this.$emit('onVisibleChange', { project_scope: this.localProjectScopeList })
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
                    this.$emit('onVisibleConfirm', { isSelectAllProjectScope: this.isOutermostAllProjectScope })
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
        }
    }
</script>
<style lang="scss" scoped>
    .select-wrapper {
        padding: 30px;
    }
    .project-select {
        width: 300px;
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
