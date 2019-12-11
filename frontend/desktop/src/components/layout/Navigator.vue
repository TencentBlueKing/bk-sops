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
                <ProjectSelector
                    :disabled="isProjectDisabled"
                    @reloadHome="reloadHome">
                </ProjectSelector>
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
    import { errorHandler } from '@/utils/errorHandler.js'
    import ProjectSelector from './ProjectSelector.vue'
    import bus from '@/utils/bus.js'

    const ROUTE_LIST = [
        {
            routerName: 'commonProcessList',
            name: gettext('公共流程'),
            path: '/common'
        },
        {
            routerName: 'process',
            name: gettext('业务流程'),
            path: '/template/',
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
            path: '/function/',
            name: gettext('职能化')
        },
        {
            routerName: 'auditHome',
            path: '/audit/',
            name: gettext('操作审计')
        },
        {
            routerName: 'projectHome',
            path: '/project/',
            name: gettext('项目管理')
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
                hasAdminPerm: false // 管理员入口权限
            }
        },
        computed: {
            ...mapState({
                view_mode: state => state.view_mode,
                username: state => state.username,
                app_id: state => state.app_id,
                notFoundPage: state => state.notFoundPage,
                userRights: state => state.userRights
            }),
            ...mapGetters('project', {
                projectList: 'userCanViewProjects'
            }),
            ...mapState('appmaker', {
                appmakerTemplateId: state => state.appmakerTemplateId
            }),
            ...mapState('project', {
                project_id: state => state.project_id,
                authResource: state => state.authResource
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
            ...mapActions('project', [
                'loadProjectList'
            ]),
            ...mapMutations('project', [
                'setProjectPerm'
            ]),
            ...mapMutations([
                'setUserRights',
                'setAdminPerm'
            ]),
            onLogoClick () {
                if (this.view_mode !== 'app') {
                    return false
                }
                if (this.$route.name === 'home') {
                    return this.reload()
                }
                this.$router.push({ name: 'home' })
            },
            async initNavgator () {
                if (this.view_mode !== 'appmaker') {
                    const res = await this.loadProjectList({ limit: 0 })
                    this.setProjectPerm(res.meta)
                    // 是否展示管理员入口
                    const hasAdminPerm = await this.getActionPerm('admin_operate', ['view'])
                    this.hasAdminPerm = hasAdminPerm
                    this.setAdminPerm(hasAdminPerm)
                    this.checkRouterPerm()
                }
            },
            /**
             * 校验路由权限
             * @param {String} routerName
             */
            async checkRouterPerm (routerName) {
                const functionRouterMap = ['functionHome', 'functionTemplateStep', 'functionTaskExecute']
                const auditRouterMap = ['auditHome', 'auditTaskExecute']
                const name = routerName || this.$route.name
                const { function: hasFunction, audit: hasAudit } = this.userRights
                if (functionRouterMap.includes(name) && !hasFunction) {
                    const result = await this.getActionPerm('function_center', ['view'])
                    this.setUserRights({ type: 'function', val: result })
                    if (!result) {
                        this.togglePermissionApplyPage(
                            {
                                type: 'function_center',
                                name: gettext('职能化中心')
                            },
                            {
                                id: 'view',
                                name: gettext('查看')
                            }
                        )
                    }
                } else if (auditRouterMap.includes(name) && !hasAudit) {
                    const result = await this.getActionPerm('audit_center', ['view'])
                    this.setUserRights({ type: 'audit', val: result })
                    if (!result) {
                        this.togglePermissionApplyPage(
                            {
                                type: 'audit_center',
                                name: gettext('审计中心')
                            },
                            {
                                id: 'view',
                                name: gettext('查看')
                            }
                        )
                    }
                }
            },
            /**
             * 切换到权限申请页
             */
            togglePermissionApplyPage (resource, action) {
                const permissions = []
                const res = []
                const { scope_id, scope_name, scope_type, scope_type_name, system_id, system_name } = this.authResource
                res.push([{
                    resource_type: resource.type,
                    resource_type_name: resource.name
                }])
                permissions.push({
                    scope_id,
                    scope_name,
                    scope_type_name,
                    resource_type: resource.type,
                    resource_type_name: resource.name,
                    scope_type,
                    system_id,
                    system_name,
                    resources: res,
                    action_id: action.id,
                    action_name: action.name
                })
                bus.$emit('togglePermissionApplyPage', true, 'function_center', permissions)
            },
            /**
             * 获取单个类型的权限
             * @param {String} type 类型
             * @param {Array} actions 具体操作类型
             */
            async getActionPerm (type, actions) {
                try {
                    const res = await this.queryUserPermission({
                        resource_type: type,
                        action_ids: JSON.stringify(actions)
                    })
                    return actions.every(action => {
                        return res.data.details.some(m => m.action_id === action && m.is_pass)
                    })
                } catch (err) {
                    errorHandler(err, this)
                }
            },
            /**
             * 导航跳转
             * @param {Object} route 路由信息
             */
            onGoToPath (route) {
                if (this.$route.name === route.routerName) {
                    return this.reload()
                }
                /** 404 页面时，导航统一跳转到首页 */
                if (this.notFoundPage && this.view_mode === 'app') {
                    return this.$router.push({ name: 'home' })
                }
                this.checkRouterPerm(route.routerName)
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
            },
            reloadHome () {
                this.reload()
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
