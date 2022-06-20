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
            :value="crtProject"
            :disabled="disabled"
            :clearable="false"
            :searchable="true"
            @selected="onProjectChange">
            <bk-option-group
                v-for="(group, index) in projects"
                :name="group.name"
                :key="index">
                <bk-option
                    class="project-item"
                    v-for="(option, i) in group.children"
                    :key="i"
                    :id="option.id"
                    :name="option.from_cmdb ? `[${option.bk_biz_id}] ${option.name}` : `[${option.id}] ${option.name}`">
                </bk-option>
            </bk-option-group>
        </bk-select>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import bus from '@/utils/bus.js'
    import { mapState } from 'vuex'

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
            }
        },
        data () {
            const id = Number(this.$store.state.project.project_id)
            return {
                crtProject: isNaN(id) ? '' : id,
                showList: false,
                searchStr: ''
            }
        },
        computed: {
            ...mapState('project', {
                projectList: state => state.userProjectList,
                project_id: state => state.project_id,
                projectName: state => state.projectName
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
        created () {
            bus.$on('resetProjectChange', (id) => {
                this.crtProject = id
            })
        },
        methods: {
            async onProjectChange (id) {
                if (this.crtProject === id) {
                    return false
                }
                this.crtProject = id
                const redirectMap = {
                    '/template': {
                        name: 'processHome',
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
                } else { // 默认跳转到项目流程页面
                    this.$router.push(redirectMap['/template'])
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    .project-wrapper {
        position: relative;
        margin-right: 10px;
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
                width: 100%;
                color: #979ba5;
                font-size: 14px;
                text-align: right;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
            }
        }
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
