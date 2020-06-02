/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
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
                    <bk-select
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
    import { mapGetters } from 'vuex'
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
            }
        },
        data () {
            return {
                id: this.project,
                hasError: false
            }
        },
        computed: {
            ...mapGetters('project', {
                projectList: 'userCanViewProjects'
            }),
            projects () {
                const projects = []
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

                return projects
            }
        },
        watch: {
            project (val) {
                this.id = val
            }
        },
        methods: {
            handleProjectSelect (id) {
                this.id = id
                this.hasError = false
                const project = this.projectList.find(item => item.id === this.id)
                this.$emit('onChange', project)
            },
            handleConfirm () {
                if (typeof this.id === 'number') {
                    const project = this.projectList.find(item => item.id === this.id)
                    this.$emit('onConfirm', project)
                } else {
                    this.hasError = true
                }
            },
            handleCancel () {
                this.id = ''
                this.hasError = false
                this.$emit('onCancel')
            }
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
</style>
