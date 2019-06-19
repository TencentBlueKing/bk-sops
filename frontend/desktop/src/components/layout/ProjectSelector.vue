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
    <div class="project-wrapper">
        <bk-selector
            :has-children="true"
            :disabled="disabled"
            :searchable="true"
            :list="projects"
            :selected="currentProject"
            @item-selected="onProjectChange">
        </bk-selector>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import { setAtomConfigApiUrls } from '@/config/setting.js'
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'ProjectSelector',
        props: ['disabled'],
        data () {
            return {
                showList: false,
                searchStr: '',
                i18n: {
                    biz: gettext('业务'),
                    proj: gettext('项目')
                }
            }
        },
        computed: {
            ...mapState({
                site_url: state => state.site_url
            }),
            ...mapState('project', {
                project_id: state => state.project_id,
                projectList: state => state.projectList
            }),
            projects () {
                const projects = []
                const projectsGroup = [
                    {
                        name: this.i18n.biz,
                        children: []
                    },
                    {
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
                    return this.project_id
                },
                set (id) {
                    this.setProjectId(id)
                }
            }
        },
        methods: {
            ...mapMutations('project', [
                'setProjectId',
                'setTimeZone'
            ]),
            ...mapActions('project', [
                'changeDefaultProject'
            ]),
            async onProjectChange (id, project) {
                try {
                    this.setProjectId(id)
                    await this.changeDefaultProject(id)
                    const timeZone = project.time_zone || 'Asia/Shanghai'
                    this.setTimeZone(timeZone)
                    setAtomConfigApiUrls(this.site_url, id)
                    
                    $.atoms = {} // notice: 清除标准插件配置项里的全局变量缓存

                    this.$router.push({ path: `/project/home/${id}/` })
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
    }
    /deep/ .bk-selector-input {
        border: 1px solid #445060;
        color: #979ba5;
        background: transparent;
        &:not([disabled="disabled"]):hover {
            color: #ffffff;
            border-color: #616d7d;
            & + .bk-icon {
                color: #616d7d;
            }
        }
        &[disabled="disabled"] {
            color: #979ba5;
            background: transparent;
            cursor: not-allowed;
            &:hover {
                & + .bk-icon {
                    color: #616d7d;
                }
            }
        }
        &.active {
            color: #ffffff;
            border-color: #616d7d !important;
            & + .bk-icon {
                color: #616d7d;
            }
        }
    }
</style>
