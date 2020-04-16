/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div
        :class="[
            'project-wrapper',
            { 'disabled': disabled },
            { 'read-only': readOnly }
        ]">
        <div v-if="readOnly" :title="projectName" class="project-name">
            {{ projectName }}
        </div>
        <bk-select
            v-else
            class="project-select"
            ext-popover-cls="project-select-comp-list"
            v-model="currentProject"
            :disabled="disabled || isLoading"
            :clearable="false"
            :searchable="true">
            <bk-option-group
                v-for="(group, index) in projects"
                :name="group.name"
                :key="index">
                <bk-option
                    class="project-item"
                    v-for="(option, i) in group.children"
                    :key="i"
                    :id="option.id"
                    :name="option.name">
                </bk-option>
            </bk-option-group>
        </bk-select>
        <div v-if="isLoading" class="local-loading">
            <i class="common-icon-loading-ring"></i>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapMutations, mapActions, mapGetters } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'ProjectSelector',
        props: {
            readOnly: {
                type: Boolean,
                default: false
            },
            disabled: {
                type: Boolean,
                default: false
            },
            // 切换项目后是否重定向
            redirect: {
                type: Boolean,
                default: true
            }
        },
        data () {
            return {
                showList: false,
                isLoading: false,
                searchStr: '',
                i18n: {
                    biz: gettext('业务'),
                    proj: gettext('项目'),
                    placeholder: gettext('请选择')
                }
            }
        },
        computed: {
            ...mapState({
                site_url: state => state.site_url,
                viewMode: state => state.view_mode
                
            }),
            ...mapState('project', {
                project_id: state => state.project_id,
                projectName: state => state.projectName
            }),
            ...mapGetters('project', {
                projectList: 'userCanViewProjects'
            }),
            projects () {
                const projects = []
                const projectsGroup = [
                    {
                        name: this.i18n.biz,
                        id: 1,
                        children: []
                    },
                    {
                        id: 2,
                        name: this.i18n.proj,
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
            },
            currentProject: {
                get () {
                    const num = Number(this.project_id)
                    return isNaN(num) ? '' : num
                },
                set (id) {
                    this.onProjectChange(id)
                }
            }
        },
        methods: {
            ...mapMutations('project', [
                'setProjectId',
                'setTimeZone',
                'setProjectName',
                'setProjectActions'
            ]),
            ...mapActions('project', [
                'changeDefaultProject',
                'loadProjectDetail'
            ]),
            async onProjectChange (id) {
                if (this.project_id === id) {
                    return false
                }
                try {
                    this.isLoading = true
                    this.$emit('loading', true)

                    this.setProjectId(id)
                    await this.changeDefaultProject(id)
                    const timeZone = this.projectList.find(m => Number(m.id) === Number(id)).time_zone || 'Asia/Shanghai'
                    this.setTimeZone(timeZone)

                    const projectDetail = await this.loadProjectDetail(this.project_id)
                    this.setProjectName(projectDetail.name)
                    this.setProjectActions(projectDetail.auth_actions)
                    $.atoms = {} // notice: 清除标准插件配置项里的全局变量缓存
                    if (!this.redirect) {
                        this.isLoading = false
                        this.$emit('loading', false)
                        return
                    }
                    // switch project go back this home list
                    const redirectMap = {
                        '/template': {
                            name: 'process',
                            params: { project_id: id }
                        },
                        '/taskflow': {
                            name: 'taskList',
                            params: { project_id: id }
                        },
                        '/appmaker': {
                            name: 'appMakerList',
                            params: { project_id: id }
                        }
                    }
                    const key = Object.keys(redirectMap).find(path => this.$route.path.indexOf(path) === 0)
                    if (key) {
                        if (this.$route.name === redirectMap[key].name) {
                            this.$router.push(redirectMap[key])
                            this.$nextTick(() => {
                                this.$emit('reloadHome')
                            })
                        } else {
                            this.$router.push(redirectMap[key])
                        }
                    }
                    this.isLoading = false
                    this.$emit('loading', false)
                } catch (err) {
                    errorHandler(err, this)
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    .project-wrapper {
        float: left;
        position: relative;
        margin-top: 9px;
        width: 200px;
        color: #979ba5;
        font-size: 14px;
        &.disabled {
            background: #252f43;
        }
        &.read-only {
            margin-top: 0;
            width: auto;
            height: 50px;
            line-height: 50px;
            .project-name {
                width: 200px;
                color: #979ba5;
                font-size: 14px;
                text-align: center;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
            }
        }
    }
    .project-select {
        border-color: #445060;
        color: #c4c6cc;
    }
    .local-loading {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        text-align: center;
        cursor: not-allowed;
        .common-icon-loading-ring {
            display: inline-block;
            font-size: 34px;
            animation: loading 1.4s infinite linear;
        }
    }
    @keyframes loading {
        from {
            transform: rotate(0);
        }
        to {
            transform: rotate(360deg);
        }
    }
</style>
<style lang="scss">
    .project-select-comp-list {
        .project-item.bk-option {
            .bk-option-content {
                padding: 0;
                .bk-option-content-default {
                    padding: 0;
                    .bk-option-name {
                        width: 100%;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        white-space: nowrap;
                    }
                }
            }
        }
    }
</style>
