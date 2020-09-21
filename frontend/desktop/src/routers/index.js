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
*/
import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '@/store/index.js'
// import bus from '@/utils/bus.js'

const NotFoundComponent = () => import('@/components/layout/NotFoundComponent.vue')

const Home = () => import('@/pages/home/index.vue')

const Template = () => import('@/pages/template/index.vue')
const TemplateList = () => import('@/pages/template/TemplateList/index.vue')

const CommonTemplate = () => import('@/pages/template/common/index.vue')
const TemplatePanel = () => import('@/pages/template/TemplateEdit/index.vue')
const CommonTemplateList = () => import('@/pages/template/common/CommonTemplateList.vue')

const Task = () => import('@/pages/task/index.vue')
const TaskManage = () => import('@/pages/task/TaskManage.vue')
const TaskList = () => import('@/pages/task/TaskList/index.vue')
const TaskCreate = () => import('@/pages/task/TaskCreate/index.vue')
const TaskExecute = () => import('@/pages/task/TaskExecute/index.vue')

const AppMaker = () => import('@/pages/appmaker/index.vue')
const AppMakerTaskHome = () => import('@/pages/appmaker/AppTaskHome/index.vue')

const ProjectHome = () => import('@/pages/project/index.vue')

const ErrorPage = () => import('@/pages/error/index.vue')

const Admin = () => import('@/pages/admin/index.vue')
const Statistics = () => import('@/pages/admin/statistics/index.vue')
const StatisticsTemplate = () => import('@/pages/admin/statistics/Template.vue')
const StatisticsInstance = () => import('@/pages/admin/statistics/Instance.vue')
const StatisticsAtom = () => import('@/pages/admin/statistics/Atom.vue')
const StatisticsAppmaker = () => import('@/pages/admin/statistics/Appmaker.vue')
const Manage = () => import('@/pages/admin/manage/index.vue')
const AdminSearch = () => import('@/pages/admin/manage/AdminSearch/index.vue')
const AdminPeriodic = () => import('@/pages/admin/manage/AdminPeriodic.vue')
const SourceManage = () => import('@/pages/admin/manage/SourceManage/index.vue')
const SourceEdit = () => import('@/pages/admin/manage/SourceEdit/index.vue')
const PackageEdit = () => import('@/pages/admin/manage/SourceEdit/PackageEdit.vue')
const CacheEdit = () => import('@/pages/admin/manage/SourceEdit/CacheEdit.vue')
const SourceSync = () => import('@/pages/admin/manage/SourceSync/index.vue')

const FunctionHome = () => import('@/pages/functor/FunctionList.vue')
const Functor = () => import('@/pages/functor/index.vue')

const AuditHome = () => import('@/pages/audit/AuditList.vue')
const Audit = () => import('@/pages/audit/index.vue')

const periodicTemplateList = () => import('@/pages/task/PeriodicList/index.vue')

const AtomDev = () => import('@/pages/atomdev/index.vue')

Vue.use(VueRouter)

const APPMAKER = {
    getIndex () {
        return `/appmaker/${store.state.app_id}/task_home/${store.state.project.project_id}/`
    },
    routes: ['appmakerTaskCreate', 'appmakerTaskExecute', 'appmakerTaskHome']
}

const routers = new VueRouter({
    base: SITE_URL,
    mode: 'history',
    routes: [
        {
            path: '/',
            redirect: function () {
                const viewMode = store.state.view_mode
                return viewMode === 'appmaker'
                    ? `/appmaker/${store.state.app_id}/task_home/${store.state.project.project_id}/`
                    : '/home/'
            }
        },
        {
            path: '/home/',
            name: 'home',
            pathToRegexpOptions: { strict: true },
            component: Home,
            props: (route) => ({
                project_id: route.params.project_id
            })
        },
        {
            path: '/common',
            component: CommonTemplate,
            children: [
                {
                    path: '',
                    component: NotFoundComponent
                },
                {
                    path: 'home/',
                    name: 'commonProcessList',
                    pathToRegexpOptions: { strict: true },
                    component: CommonTemplateList,
                    props: (route) => ({
                        common: '1',
                        page: route.query.page
                    })
                },
                {
                    path: ':type(new|edit|clone)/',
                    component: TemplatePanel,
                    name: 'commonTemplatePanel',
                    pathToRegexpOptions: { strict: true },
                    props: (route) => ({
                        template_id: route.query.template_id,
                        type: route.params.type,
                        common: '1'
                    }),
                    meta: { project: false }
                }
            ]
        },
        {
            path: '/template',
            component: Template,
            children: [
                {
                    path: '',
                    component: NotFoundComponent
                },
                {
                    path: 'home/:project_id/',
                    name: 'process',
                    pathToRegexpOptions: { strict: true },
                    component: TemplateList,
                    props: (route) => ({
                        project_id: route.params.project_id,
                        common: route.query.common,
                        common_template: route.query.common_template,
                        page: route.query.page
                    }),
                    meta: { project: true }
                },
                {
                    path: ':type(new|edit|clone)/:project_id/',
                    component: TemplatePanel,
                    name: 'templatePanel',
                    pathToRegexpOptions: { strict: true },
                    props: (route) => ({
                        project_id: route.params.project_id,
                        template_id: route.query.template_id,
                        type: route.params.type,
                        common: route.query.common
                    }),
                    meta: { project: true }
                }]
        },
        {
            path: '/taskflow',
            component: Task,
            children: [
                {
                    path: '',
                    component: NotFoundComponent
                },
                {
                    path: 'home/',
                    component: TaskManage,
                    name: 'taskHome',
                    children: [
                        {
                            path: 'list/:project_id/',
                            component: TaskList,
                            name: 'taskList',
                            pathToRegexpOptions: { strict: true },
                            props: (route) => ({
                                project_id: route.params.project_id,
                                template_source: route.query.template_source,
                                create_method: route.query.create_method,
                                create_info: route.query.create_info
                            }),
                            meta: { project: true }
                        },
                        {
                            path: 'periodic/:project_id/',
                            pathToRegexpOptions: { strict: true },
                            component: periodicTemplateList,
                            name: 'periodicTemplate',
                            props: (route) => ({
                                project_id: route.params.project_id
                            }),
                            meta: { project: true }
                        }
                    ],
                    meta: { project: true }
                },
                {
                    path: 'newtask/:project_id/:step/',
                    component: TaskCreate,
                    name: 'taskStep',
                    pathToRegexpOptions: { strict: true },
                    props: (route) => ({
                        project_id: route.params.project_id,
                        step: route.params.step,
                        template_id: route.query.template_id,
                        common: route.query.common,
                        entrance: route.query.entrance
                    }),
                    meta: { project: true }
                },
                {
                    path: 'execute/:project_id/',
                    component: TaskExecute,
                    name: 'taskExecute',
                    pathToRegexpOptions: { strict: true },
                    props: (route) => ({
                        project_id: route.params.project_id,
                        common: route.query.common,
                        instance_id: route.query.instance_id
                    }),
                    meta: { project: true }
                }]
        },
        {
            path: '/appmaker/home/:project_id/',
            component: AppMaker,
            name: 'appMakerList',
            pathToRegexpOptions: { strict: true },
            props: (route) => ({
                project_id: route.params.project_id
            }),
            meta: { project: true }
        },
        {
            path: '/appmaker/:app_id/newtask/:project_id/:step/',
            name: 'appmakerTaskCreate',
            pathToRegexpOptions: { strict: true },
            component: TaskCreate,
            props: (route) => ({
                project_id: route.params.project_id,
                step: route.params.step,
                template_id: route.query.template_id
            }),
            meta: { project: true }
        },
        {
            path: '/appmaker/:app_id/execute/:project_id/',
            name: 'appmakerTaskExecute',
            pathToRegexpOptions: { strict: true },
            component: TaskExecute,
            props: (route) => ({
                project_id: route.params.project_id,
                instance_id: route.query.instance_id
            }),
            meta: { project: true }
        },
        {
            path: '/appmaker/:app_id/task_home/:project_id/',
            name: 'appmakerTaskHome',
            pathToRegexpOptions: { strict: true },
            component: AppMakerTaskHome,
            props: (route) => ({
                project_id: route.params.project_id,
                app_id: route.params.app_id
            }),
            meta: { project: true }
        },
        {
            path: '/project/home/',
            name: 'projectHome',
            pathToRegexpOptions: { strict: true },
            component: ProjectHome
        },
        {
            path: '/function',
            component: Functor,
            children: [
                {
                    path: '',
                    component: NotFoundComponent
                },
                {
                    path: 'home/',
                    name: 'functionHome',
                    pathToRegexpOptions: { strict: true },
                    component: FunctionHome
                },
                {
                    path: 'newtask/:project_id/:step/',
                    component: TaskCreate,
                    name: 'functionTemplateStep',
                    pathToRegexpOptions: { strict: true },
                    props: (route) => ({
                        project_id: route.params.project_id,
                        step: route.params.step,
                        template_id: route.query.template_id,
                        common: route.query.common,
                        entrance: route.query.entrance
                    }),
                    meta: { project: true }
                },
                {
                    path: 'execute/:project_id/',
                    component: TaskExecute,
                    name: 'functionTaskExecute',
                    pathToRegexpOptions: { strict: true },
                    props: (route) => ({
                        project_id: route.params.project_id,
                        common: route.query.common,
                        instance_id: route.query.instance_id
                    }),
                    meta: { project: true }
                }
            ]
        },
        {
            path: '/audit',
            component: Audit,
            children: [
                {
                    path: '',
                    component: NotFoundComponent
                },
                {
                    path: 'home/',
                    name: 'auditHome',
                    pathToRegexpOptions: { strict: true },
                    component: AuditHome
                },
                {
                    path: 'execute/:project_id/',
                    component: TaskExecute,
                    name: 'auditTaskExecute',
                    pathToRegexpOptions: { strict: true },
                    props: (route) => ({
                        project_id: route.params.project_id,
                        common: route.query.common,
                        instance_id: route.query.instance_id
                    }),
                    meta: { project: true }
                }
            ]
        },
        {
            path: '/admin',
            component: Admin,
            children: [
                {
                    path: 'statistics/',
                    component: Statistics,
                    children: [
                        {
                            path: '',
                            component: NotFoundComponent
                        },
                        {
                            path: 'template/',
                            name: 'statisticsTemplate',
                            pathToRegexpOptions: { strict: true },
                            component: StatisticsTemplate
                        },
                        {
                            path: 'instance/',
                            name: 'statisticsInstance',
                            pathToRegexpOptions: { strict: true },
                            component: StatisticsInstance
                        },
                        {
                            path: 'atom/',
                            name: 'statisticsAtom',
                            pathToRegexpOptions: { strict: true },
                            component: StatisticsAtom
                        },
                        {
                            path: 'appmaker/',
                            name: 'statisticsAppmaker',
                            pathToRegexpOptions: { strict: true },
                            component: StatisticsAppmaker
                        }
                    ]
                },
                {
                    path: 'manage/',
                    component: Manage,
                    children: [
                        {
                            path: 'search/',
                            name: 'adminSearch',
                            pathToRegexpOptions: { strict: true },
                            component: AdminSearch
                        },
                        {
                            path: 'periodic/',
                            name: 'adminPeriodic',
                            pathToRegexpOptions: { strict: true },
                            component: AdminPeriodic
                        },
                        {
                            path: 'source_manage/',
                            name: 'sourceManage',
                            pathToRegexpOptions: { strict: true },
                            component: SourceManage
                        },
                        {
                            path: 'source_edit/',
                            component: SourceEdit,
                            children: [
                                {
                                    path: 'package_edit/',
                                    name: 'packageEdit',
                                    pathToRegexpOptions: { strict: true },
                                    component: PackageEdit
                                },
                                {
                                    path: 'cache_edit/',
                                    name: 'cacheEdit',
                                    pathToRegexpOptions: { strict: true },
                                    component: CacheEdit
                                }
                            ]
                        },
                        {
                            path: 'source_sync/',
                            name: 'sourceSync',
                            pathToRegexpOptions: { strict: true },
                            component: SourceSync
                        }
                    ]
                },
                {
                    path: 'atomdev/',
                    name: 'atomDev',
                    pathToRegexpOptions: { strict: true },
                    component: AtomDev
                }
            ]
        },
        {
            path: '/error/:code(401|403|405|406|500)/',
            component: ErrorPage,
            name: 'errorPage',
            pathToRegexpOptions: { strict: true },
            props: (route) => ({
                code: route.params.code
            })
        },
        {
            path: '*',
            name: 'notFoundPage',
            component: NotFoundComponent
        }
    ]
})

routers.beforeEach((to, from, next) => {
    // 生产环境 404 页面头部导航跳转统一设置为首页
    if (process.env.NODE_ENV === 'production' && to.name === 'notFoundPage') {
        store.commit('setNotFoundPage', true)
    } else {
        store.commit('setNotFoundPage', false)
    }
    // 设置全局 project_id
    if (to.params.project_id) {
        store.commit('project/setProjectId', to.params.project_id)
    }
    if (store.state.viewMode === 'appmaker' && !APPMAKER.routes.includes(to.name)) {
        next(APPMAKER.getIndex())
    } else {
        next()
    }
})

export default routers
