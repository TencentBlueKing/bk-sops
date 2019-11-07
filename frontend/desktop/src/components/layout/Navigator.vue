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
    <header>
        <router-link to="" class="nav-logo" @click.native="onLogoClick()">
            <img :src="logo" class="logo" />
            <span class="header-title">{{ i18n.title }}</span>
        </router-link>
        <ul class="nav-left" v-if="!appmakerDataLoading">
            <li
                v-for="(item, index) in showRouterList"
                :key="index"
                :class="['nav-item', { 'active': isNavActived(item) }]">
                <router-link to="" @click.native="onGoToPath(item)">
                    {{ item.name }}
                </router-link>
                <div
                    v-if="item.children"
                    class="sub-nav">
                    <router-link
                        v-for="(sub, subIndex) in item.children"
                        :key="subIndex"
                        to=""
                        :class="['sub-nav-item', { 'active': isNavActived(sub) }]"
                        @click.native="onGoToPath(sub)">
                        {{ sub.name }}
                    </router-link>
                </div>
            </li>
        </ul>
        <ul class="nav-right">
            <li v-if="showProjectSelect" class="project-select">
                <ProjectSelector :disabled="isProjectDisabled"></ProjectSelector>
            </li>
            <li class="help-doc">
                <a
                    class="common-icon-dark-circle-question"
                    href="http://docs.bk.tencent.com/product_white_paper/gcloud/"
                    target="_blank">
                </a>
            </li>
            <li class="user-avatar">
                <span
                    class="common-icon-dark-circle-avatar"
                    v-bk-tooltips="{
                        content: username,
                        placement: 'bottom-end',
                        theme: 'light',
                        zIndex: 1001
                    }">
                </span>
            </li>
        </ul>
    </header>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapGetters, mapActions, mapMutations } from 'vuex'
    import ProjectSelector from './ProjectSelector.vue'
    import { errorHandler } from '@/utils/errorHandler.js'

    const ROUTE_LIST = [
        {
            routerName: 'commonProcess',
            name: gettext('公共流程'),
            path: '/template/common'
        },
        {
            routerName: 'process',
            name: gettext('业务流程'),
            path: '/template/process',
            params: ['project_id']
        },
        {
            routerName: 'taskList',
            name: gettext('任务管理'),
            path: '/taskflow/',
            params: ['project_id']
        },
        {
            routerName: 'appMakerList',
            name: gettext('轻应用'),
            path: '/appmaker/',
            params: ['project_id']
        },
        {
            routerName: 'functionHome',
            path: '/function',
            name: gettext('职能化')
        },
        {
            routerName: 'auditHome',
            path: '/audit',
            name: gettext('操作中心')
        },
        {
            routerName: 'sourceManage',
            path: '/admin',
            name: gettext('管理员入口'),
            children: [
                {
                    routerName: 'sourceManage',
                    path: '/admin/manage',
                    name: gettext('后台管理')
                },
                {
                    routerName: 'statisticsTemplate',
                    path: '/admin/statistics/template',
                    name: gettext('运营数据')
                }
            ]
        }
    ]
    const APPMAKER_ROUTER_LIST = [
        {
            routerName: 'appmakerTaskCreate',
            path: 'appMakerList',
            params: ['app_id', 'project_id'],
            query: ['appmakerTemplateId'],
            name: gettext('新建任务')
        },
        {
            routerName: 'appmakerTaskList',
            path: 'appmakerTaskList',
            params: ['project_id'],
            name: gettext('任务记录')
        }
    ]
    export default {
        inject: ['reload'],
        name: 'Navigator',
        components: {
            ProjectSelector
        },
        props: ['appmakerDataLoading'],
        data () {
            return {
                logo: require('../../assets/images/logo/logo_icon.svg'),
                i18n: {
                    help: gettext('帮助文档'),
                    title: gettext('标准运维')
                },
                routerList: ROUTE_LIST,
                appmakerRouterList: APPMAKER_ROUTER_LIST,
                hasAdminPerm: false // 是否拥有管理员入口查看权限
            }
        },
        computed: {
            ...mapState({
                view_mode: state => state.view_mode,
                username: state => state.username,
                app_id: state => state.app_id,
                notFoundPage: state => state.notFoundPage
            }),
            ...mapGetters('project', {
                projectList: 'userCanViewProjects'
            }),
            ...mapState('appmaker', {
                appmakerTemplateId: state => state.appmakerTemplateId
            }),
            ...mapState('project', {
                project_id: state => state.project_id
            }),
            showProjectSelect () {
                return this.view_mode !== 'appmaker' && this.projectList.length > 0
            },
            isProjectDisabled () {
                const route = this.$route
                return route.path.indexOf('/admin/') === 0
            },
            showRouterList () {
                if (this.view_mode === 'appmaker') {
                    return this.appmakerRouterList
                }
                let list = this.routerList
                if (!this.hasAdminPerm) {
                    list = list.filter(item => item.path !== '/admin')
                }
                return list
            }
        },
        mounted () {
            this.initNavgator()
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            ...mapActions('project', [
                'loadProjectList'
            ]),
            ...mapMutations('project', [
                'setProjectPerm'
            ]),
            onLogoClick () {
                if (this.view_mode !== 'app') {
                    return false
                }
                this.$router.push('/')
            },
            async initNavgator () {
                if (this.view_mode !== 'appmaker') {
                    this.getAdminPerm()
                    const res = await this.loadProjectList({ limit: 0 })
                    this.setProjectPerm(res.meta)
                }
            },
            async getAdminPerm () {
                try {
                    const res = await this.queryUserPermission({
                        resource_type: 'admin_operate',
                        action_ids: JSON.stringify(['view'])
                    })
    
                    const hasCreatePerm = !!res.data.details.find(item => {
                        return item.action_id === 'view' && item.is_pass
                    })
                    if (hasCreatePerm) {
                        this.hasAdminPerm = true
                    }
                } catch (err) {
                    errorHandler(err, this)
                }
            },
            /**
             * 导航跳转
             * @param {Object} route 路由信息
             */
            onGoToPath (route) {
                /** 点击同一路由刷新当前页面 */
                if (this.$route.name === route.routerName) {
                    return this.reload()
                }
                /** 404 页面时，导航统一跳转到首页 */
                if (this.notFoundPage && this.view_mode === 'app') {
                    return this.$router.push('/')
                }
                const params = {}
                const query = {}
                route.params && route.params.forEach(m => {
                    params[m] = this[m] || undefined
                })
                route.query && route.query.forEach(m => {
                    query[m] = this[m] || undefined
                })
                this.$router.push({
                    name: route.routerName,
                    params,
                    query
                }).catch(err => {
                    errorHandler(err, this)
                })
            },
            isNavActived (route) {
                if (this.view_mode === 'appmaker') {
                    return this.$route.name === route.path
                }
                return this.$route.path.indexOf(route.path) > -1
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
header {
    min-width: 1334px;
    padding: 0 25px;
    height: 50px;
    font-size: 14px;
    background: #182131;
    .nav-logo {
            float: left;
            height: 100%;
            line-height: 50px;
            .logo,.header-title{
                display: inline-block;
                vertical-align: middle;
            }
            .logo {
                width: 28px;
                height: 28px;
            }
            .header-title{
                margin-left: 6px;
                font-size: 18px;
                color: #979ba5;
            }
        }
    .nav-left {
        float: left;
        .nav-item {
            position: relative;
            float: left;
            &:first-child {
                margin-left: 141px;
            }
            &:hover {
                color: $whiteDefault;
                .sub-nav {
                    display: block;
                }
            }
            &.active > a{
                color: $whiteDefault;
                background: $blackDefault;
            }
            > a {
                display: inline-block;
                padding: 0 17px;
                min-width: 90px;
                height: 50px;
                line-height: 50px;
                color: #979ba5;;
                text-align: center;
                border-radius: 2px;
                cursor: pointer;
                transition: all .5s linear;
                &:hover {
                    color: $whiteDefault;
                }
            }
            /*二级导航*/
            .sub-nav {
                display: none;
                position: absolute;
                top: 50px;
                left: 0;
                min-width: 100%;
                background: $whiteDefault;
                border: 1px solid #c4c6cc;
                border-radius: 2px;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.16);
                z-index: 1001;
                .sub-nav-item {
                    width: 100%;
                    display: block;
                    padding: 0 10px;
                    height: 35px;
                    line-height: 35px;
                    color: #63656E;
                    white-space: nowrap;
                    text-align: center;
                    &.selected {
                        color: #313238;
                        background: #f0f1f5;
                    }
                    &:hover {
                        color: #313238;
                        background: #f0f1f5;
                    }
                    &.active {
                        color: #313238;
                        background: #f0f1f5;
                    }
                }
            }
        }
    }
    .nav-right {
        float: right;
        .project-select {
            float: left;
        }
        .help-doc {
            float: left;
            margin-left: 25px;
            height: 50px;
            font-size: 16px;
            .common-icon-dark-circle-question {
                margin-top: 17px;
                display: inline-block;
                color: #63656e;
                &:hover {
                    color: #616d7d;
                }
            }
        }
        .user-avatar {
            float: left;
            margin-left: 25px;
            height: 50px;
            font-size: 16px;
            color: #63656e;
            .common-icon-dark-circle-avatar {
                display: inline-block;
                margin-top: 17px;
            }
        }
        /deep/ .bk-select.is-disabled {
            background: none;
        }
    }
}
</style>
