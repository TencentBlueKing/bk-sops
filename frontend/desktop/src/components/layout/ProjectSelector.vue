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
            v-model="crtProject"
            :disabled="disabled"
            :search-with-pinyin="true"
            :clearable="false"
            :searchable="true"
            @selected="onProjectChange">
            <bk-option-group
                v-for="(group, index) in projects"
                :name="group.name"
                :key="index">
                <bk-option
                    class="project-item"
                    v-for="option in group.children"
                    :class="{ 'btn-permission-disable': !option.is_user_project }"
                    v-cursor="{ active: !option.is_user_project }"
                    :key="option.id"
                    :id="option.id"
                    :name="option.from_cmdb ? `[${option.bk_biz_id}] ${option.name}` : `[${option.id}] ${option.name}`">
                    <div>{{ option.from_cmdb ? `[${option.bk_biz_id}] ${option.name}` : `[${option.id}] ${option.name}` }}</div>
                    <div
                        v-bk-tooltips="option.is_fav ? $t('取消收藏') : $t('添加收藏')"
                        style="padding: 0 5px"
                        :class="['commonicon-icon', option.is_fav ? 'common-icon-favorite' : 'common-icon-rate', option.is_user_project ? 'favorite' : 'no-permission']"
                        @click.stop="changeFavorite(option)"></div>
                </bk-option>
            </bk-option-group>
            <div slot="extension" @click="jumpToOther">
                <i class="bk-icon icon-plus-circle"></i>
                {{ $t('申请业务权限') }}
            </div>
        </bk-select>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'
    import openOtherApp from '@/utils/openOtherApp.js'
    import permission from '@/mixins/permission.js'

    export default {
        name: 'ProjectSelector',
        mixins: [permission],
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
                        // 后台排序
                        projects.push(group)
                    }
                })

                return projects
            }
        },
        methods: {
            ...mapActions([
                'projectFavorite',
                'projectuCancelFavorite'
            ]),
            ...mapActions('project', [
                'loadUserProjectList'
            ]),
            async onProjectChange (id) {
                const project = this.projectList.find(item => item.id === id)
                if (!project.is_user_project) {
                    const resourceData = {
                        project: [{
                            id: project.id,
                            name: project.name
                        }]
                    }
                    this.applyForPermission(['project_view'], project.auth_actions, resourceData)
                    this.crtProject = Number(this.$store.state.project.project_id)
                    return false
                }
                if (this.project_id === id) {
                    return false
                }
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
                if (key && this.$route.name !== redirectMap[key].name) {
                    this.$router.push(redirectMap[key])
                } else {
                    this.$router.push({
                        name: this.$route.name,
                        params: { project_id: id }
                    })
                    this.$nextTick(() => {
                        this.$emit('reloadHome')
                    })
                }
            },
            // 这里统一直接用后端提供的 host 跳转
            jumpToOther () {
                openOtherApp(window.BK_IAM_APP_CODE, window.BK_IAM_APPLY_URL)
            },
            async changeFavorite (option) {
                const { is_fav, id } = option
                const res = await is_fav ? this.projectuCancelFavorite({ id }) : this.projectFavorite({ id })
                if (res.data && res.data.result) {
                    this.loadUserProjectList()
                    this.$bkMessage({ message: is_fav ? i18n.t('取消收藏成功！') : i18n.t('添加收藏成功！'), theme: 'success' })
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
                display: flex;
                justify-content: space-between;
                align-items: center;
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
                .no-permission {
                    display: none;
                }
                .favorite {
                    display: none;
                }
                &:hover {
                    .favorite {
                        display: block;
                    }
                }
            }
        }
        .bk-select-extension {
            text-align: center;
            cursor: pointer;
            padding: 0;
            .project-create {
                display: flex;
                .project {
                    flex: 1;
                }
            }
        }
    }
</style>
