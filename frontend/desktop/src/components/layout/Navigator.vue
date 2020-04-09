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
        <router-link :to="{ name: 'home' }" class="nav-logo" @click.native="onLogoClick">
            <img :src="logo" class="logo" />
            <span class="header-title">{{ i18n.title }}</span>
        </router-link>
        <ul class="nav-left" v-if="!appmakerDataLoading">
            <li
                v-for="(item, index) in showRouterList"
                :key="index"
                :class="['nav-item', { 'active': isNavActived(item) }]">
                <router-link :to="getNavPath(item)" :event="''" @click.native="onGoToPath(item)">
                    {{ item.name }}
                </router-link>
                <div
                    v-if="item.children"
                    class="sub-nav">
                    <router-link
                        v-for="(sub, subIndex) in item.children"
                        :key="subIndex"
                        :to="{ name: item.routerName }"
                        :class="['sub-nav-item', { 'active': isNavActived(sub) }]"
                        :event="''"
                        @click.native="onGoToPath(sub)">
                        {{ sub.name }}
                    </router-link>
                </div>
            </li>
        </ul>
        <!-- 右侧项目选择和其他信息 -->
        <ul class="nav-right">
            <li v-if="showProjectSelect" class="project-select">
                <ProjectSelector
                    :show="!isProjectHidden"
                    :read-only="isProjectReadOnly"
                    @reloadHome="reloadHome">
                </ProjectSelector>
            </li>
            <li class="right-icon help-doc">
                <a
                    class="common-icon-dark-circle-question"
                    href="https://bk.tencent.com/docs/document/5.1/3/22"
                    target="_blank">
                </a>
            </li>
            <li class="right-icon version-log"><i class="common-icon-info" @click="onOpenVersion"></i></li>
            <li class="right-icon user-avatar">
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
        <!-- 日志组件 -->
        <version-log
            ref="versionLog"
            :log-list="logList"
            :log-detail="logDetail"
            :loading="logListLoading || logDetailLoading"
            @active-change="handleVersionChange">
        </version-log>
    </header>
</template>
<script>
    import '@/utils/i18n.js'
    import bus from '@/utils/bus.js'
    import { mapState, mapGetters, mapActions, mapMutations } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import ProjectSelector from './ProjectSelector.vue'
    import VersionLog from './VersionLog.vue'

    const ROUTE_LIST = [
        {
            routerName: 'process',
            name: gettext('项目流程'),
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
            routerName: 'commonProcessList',
            name: gettext('公共流程'),
            path: '/common'
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
            routerName: 'adminSearch',
            path: '/admin',
            name: gettext('管理员入口'),
            children: [
                {
                    routerName: 'adminSearch',
                    path: '/admin/manage/',
                    name: gettext('后台管理')
                },
                {
                    routerName: 'statisticsTemplate',
                    path: '/admin/statistics/',
                    name: gettext('运营数据')
                }
            ]
        },
        {
            routerName: 'atomDev',
            path: '/atomdev',
            name: gettext('插件开发')
        }
    ]
    const APPMAKER_ROUTER_LIST = [
        {
            routerName: 'appmakerTaskCreate',
            path: 'appmakerTaskCreate',
            params: ['app_id', 'project_id'],
            name: gettext('新建任务')
        },
        {
            routerName: 'appmakerTaskHome',
            path: 'appmakerTaskHome',
            params: ['project_id'],
            name: gettext('任务记录')
        }
    ]
    export default {
        inject: ['reload'],
        name: 'Navigator',
        components: {
            ProjectSelector,
            VersionLog
        },
        props: ['appmakerDataLoading'],
        data () {
            return {
                logo: require('../../assets/images/logo/logo_icon.svg'),
                i18n: {
                    help: gettext('帮助文档'),
                    title: gettext('标准运维')
                },
                logList: [],
                logDetail: '',
                logListLoading: false,
                logDetailLoading: false,
                routerList: ROUTE_LIST,
                appmakerRouterList: APPMAKER_ROUTER_LIST,
                hasAdminPerm: false // 管理员入口权限
            }
        },
        computed: {
            ...mapState({
                site_url: state => state.site_url,
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
                if (this.view_mode === 'appmaker') {
                    return this.$route.name !== 'appmakerTaskHome'
                }
                return this.projectList.length > 0
            },
            isProjectHidden () {
                const route = this.$route
                const hiddenPathList = ['/home', '/common', '/admin', '/project', '/atomdev', '/audit', '/appmaker']
                const hiddenRouteNames = ['appmakerTaskHome', 'functionHome']
                return hiddenPathList.some(path => route.path.indexOf(path) === 0 || hiddenRouteNames.includes(route.name))
            },
            isProjectReadOnly () {
                const currPath = this.$route.path
                const readOnlyPathList = ['/appmaker', '/function']
                return readOnlyPathList.some(path => currPath.indexOf(path) === 0)
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
            ...mapActions([
                'queryUserPermission',
                'getVersionList',
                'getVersionDetail'
            ]),
            onLogoClick (e) {
                e.preventDefault()
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
                bus.$emit('togglePermissionApplyPage', true, resource.type, permissions)
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
            // 获取导航的链接，供右键点击跳转
            getNavPath (route) {
                const params = {}
                const query = {}
                route.params && route.params.forEach(m => {
                    params[m] = this[m] || undefined
                })
                route.query && route.query.forEach(m => {
                    query[m] = this[m] || undefined
                })
                if (route.routerName === 'appmakerTaskCreate') {
                    params['step'] = 'selectnode'
                    query['template_id'] = this.appmakerTemplateId
                }
                return {
                    name: route.routerName,
                    params,
                    query
                }
            },
            /**
             * 左键点击导航跳转
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
                const config = this.getNavPath(route)
                this.$router.push(config)
                this.checkRouterPerm(route.routerName)
            },
            /* 打开版本日志 */
            async onOpenVersion () {
                this.$refs.versionLog.show()
                try {
                    this.logListLoding = true
                    const res = await this.getVersionList()
                    this.logList = res.data
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.logListLoding = false
                }
            },
            async loadLogDetail (version) {
                try {
                    this.logDetailLoding = true
                    const res = await this.getVersionDetail({ version })
                    this.logDetail = res.data
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.logDetailLoding = false
                }
            },
            isNavActived (route) {
                if (this.view_mode === 'appmaker') {
                    return this.$route.name === route.path
                }
                return this.$route.path.indexOf(route.path) === 0
            },
            handleVersionChange (data) {
                const version = data[0]
                this.loadLogDetail(version)
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
                @media screen and (max-width: 1420px){
                    margin-left: 60px;
                }
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
        .right-icon {
            float: left;
            height: 50px;
            font-size: 16px;
            & > [class^='common-icon'] {
                margin-top: 17px;
                display: inline-block;
                color: #63656e;
                cursor: pointer;
                &:hover {
                    color: #616d7d;
                }
            }
        }
        .help-doc {
            margin-left: 18px;
        }
        .version-log {
            margin-left: 10px;
            & > .common-icon-info {
                font-size: 18px;
            }
        }
        .user-avatar {
            margin-left: 10px;
        }
        /deep/ .bk-select.is-disabled {
            background: none;
        }
    }
}
</style>
