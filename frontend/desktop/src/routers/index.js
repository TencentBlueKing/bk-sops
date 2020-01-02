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
import { setAtomConfigApiUrls } from '@/config/setting.js'

const NotFoundComponent = () => import('@/components/layout/NotFoundComponent.vue')

const Home = () => import('@/pages/home/index.vue')

const Template = () => import('@/pages/template/index.vue')
const TemplateEdit = () => import('@/pages/template/TemplateEdit/index.vue')
const TemplateList = () => import('@/pages/template/TemplateList/index.vue')

const Task = () => import('@/pages/task/index.vue')
const TaskList = () => import('@/pages/task/TaskList/index.vue')
const TaskCreate = () => import('@/pages/task/TaskCreate/index.vue')
const TaskExecute = () => import('@/pages/task/TaskExecute/index.vue')

const ConfigPage = () => import('@/pages/config/index.vue')

const AppMaker = () => import('@/pages/appmaker/index.vue')
const AppMakerTaskHome = () => import('@/pages/appmaker/AppTaskHome/index.vue')

const ErrorPage = () => import('@/pages/error/index.vue')

const Admin = () => import('@/pages/admin/index.vue')
const Statistics = () => import('@/pages/admin/statistics/index.vue')
const StatisticsTemplate = () => import('@/pages/admin/statistics/Template/index.vue')
const StatisticsInstance = () => import('@/pages/admin/statistics/Instance/index.vue')
const StatisticsAtom = () => import('@/pages/admin/statistics/Atom/index.vue')
const StatisticsAppmaker = () => import('@/pages/admin/statistics/Appmaker/index.vue')
const CommonTemplate = () => import('@/pages/admin/common/template.vue')
const Manage = () => import('@/pages/admin/manage/index.vue')
const SourceManage = () => import('@/pages/admin/manage/SourceManage/index.vue')
const SourceEdit = () => import('@/pages/admin/manage/SourceEdit/index.vue')
const PackageEdit = () => import('@/pages/admin/manage/SourceEdit/PackageEdit.vue')
const CacheEdit = () => import('@/pages/admin/manage/SourceEdit/CacheEdit.vue')
const SourceSync = () => import('@/pages/admin/manage/SourceSync/index.vue')

const FunctionHome = () => import('@/pages/functor/index.vue')

const AuditHome = () => import('@/pages/audit/index.vue')

const periodic = () => import('@/pages/periodic/index.vue')
const periodicTemplateList = () => import('@/pages/periodic/PeriodicList/index.vue')

Vue.use(VueRouter)

const routers = new VueRouter({
    base: SITE_URL,
    mode: 'history',
    routes: [
        {
            path: '/',
            redirect: to => {
                return `/business/home/${store.state.cc_id}/`
            }
        },
        {
            path: '/business/home/:cc_id',
            component: Home,
            props: (route) => ({
                cc_id: route.params.cc_id
            })
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
                    path: 'home/:cc_id/',
                    component: TemplateList,
                    props: (route) => ({
                        cc_id: route.params.cc_id,
                        common: route.query.common,
                        common_template: route.query.common_template
                    })
                },
                {
                    path: 'common/:cc_id/',
                    component: TemplateList,
                    props: (route) => ({
                        cc_id: route.params.cc_id,
                        common: 1,
                        common_template: 'common'
                    })
                },
                {
                    path: 'edit/:cc_id?/',
                    component: TemplateEdit,
                    props: (route) => ({
                        cc_id: route.params.cc_id,
                        template_id: route.query.template_id,
                        type: 'edit',
                        common: route.query.common
                    })
                },
                {
                    path: 'new/:cc_id/',
                    component: TemplateEdit,
                    props: (route) => ({
                        cc_id: route.params.cc_id,
                        type: 'new',
                        common: route.query.common
                    })
                },
                {
                    path: 'clone/:cc_id/',
                    component: TemplateEdit,
                    props: (route) => ({
                        cc_id: route.params.cc_id,
                        template_id: route.query.template_id,
                        type: 'clone',
                        common: route.query.common
                    })
                },
                {
                    path: 'newtask/:cc_id/:step/',
                    component: TaskCreate,
                    name: 'templateStep',
                    props: (route) => ({
                        cc_id: route.params.cc_id,
                        step: route.params.step,
                        template_id: route.query.template_id,
                        common: route.query.common,
                        entrance: route.query.entrance
                    })
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
                    path: 'home/:cc_id/',
                    component: TaskList,
                    name: 'taskList',
                    props: (route) => ({
                        cc_id: route.params.cc_id,
                        common: route.query.common,
                        create_method: route.query.create_method
                    })
                },
                {
                    path: 'execute/:cc_id/',
                    component: TaskExecute,
                    props: (route) => ({
                        cc_id: route.params.cc_id,
                        common: route.query.common,
                        instance_id: route.query.instance_id
                    })
                }]
        },
        {
            path: '/config/home/:cc_id/',
            component: ConfigPage,
            props: (route) => ({
                cc_id: route.params.cc_id
            })
        },
        {
            path: '/appmaker/home/:cc_id/',
            component: AppMaker,
            props: (route) => ({
                cc_id: route.params.cc_id
            })
        },
        {
            path: '/appmaker/:app_id/newtask/:cc_id/:step',
            name: 'appmakerTaskCreate',
            component: TaskCreate,
            props: (route) => ({
                cc_id: route.params.cc_id,
                step: route.params.step,
                template_id: route.query.template_id
            })
        },
        {
            path: '/appmaker/:app_id/execute/:cc_id/',
            name: 'appmakerTaskExecute',
            component: TaskExecute,
            props: (route) => ({
                cc_id: route.params.cc_id,
                instance_id: route.query.instance_id
            })
        },
        {
            path: '/appmaker/:app_id/task_home/:cc_id/',
            name: 'appmakerTaskHome',
            component: AppMakerTaskHome,
            props: (route) => ({
                cc_id: route.params.cc_id,
                app_id: route.params.app_id
            })
        },
        {
            path: '/error/:code(401|403|405|406|500)/',
            component: ErrorPage,
            name: 'errorPage',
            props: (route) => ({
                code: route.params.code
            })
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
                            component: StatisticsTemplate
                        },
                        {
                            path: 'instance/',
                            name: 'statisticsInstance',
                            component: StatisticsInstance
                        },
                        {
                            path: 'atom/',
                            name: 'statisticsAtom',
                            component: StatisticsAtom
                        },
                        {
                            path: 'appmaker/',
                            name: 'statisticsAppmaker',
                            component: StatisticsAppmaker
                        }
                    ]
                },
                {
                    path: 'common/template',
                    component: CommonTemplate
                },
                {
                    path: 'template/',
                    component: Template,
                    children: [
                        {
                            path: '',
                            component: NotFoundComponent
                        },

                        {
                            path: 'edit/:cc_id?/',
                            component: TemplateEdit,
                            props: (route) => ({
                                cc_id: route.params.cc_id,
                                template_id: route.query.template_id,
                                type: 'edit',
                                common: '1'
                            })
                        },
                        {
                            path: 'new/:cc_id/',
                            component: TemplateEdit,
                            props: (route) => ({
                                cc_id: route.params.cc_id,
                                type: 'new',
                                common: '1'
                            })
                        },
                        {
                            path: 'clone/:cc_id/',
                            component: TemplateEdit,
                            props: (route) => ({
                                cc_id: route.params.cc_id,
                                template_id: route.query.template_id,
                                type: 'clone',
                                common: '1'
                            })
                        }]
                },
                {
                    path: 'manage/',
                    component: Manage,
                    children: [
                        {
                            path: 'source_manage/',
                            name: 'sourceManage',
                            component: SourceManage
                        },
                        {
                            path: 'source_edit/',
                            component: SourceEdit,
                            children: [
                                {
                                    path: 'package_edit/',
                                    name: 'packageEdit',
                                    component: PackageEdit
                                },
                                {
                                    path: 'cache_edit/',
                                    name: 'cacheEdit',
                                    component: CacheEdit
                                }
                            ]
                        },
                        {
                            path: 'source_sync/',
                            name: 'sourceSync',
                            component: SourceSync
                        }
                    ]
                }
            ]
        },

        {
            path: '/function/home/',
            name: 'functionHome',
            component: FunctionHome
        },
        {
            path: '/audit/home/',
            name: 'auditHome',
            component: AuditHome
        },
        {
            path: '/periodic',
            component: periodic,
            children: [{
                path: 'home/:cc_id/',
                component: periodicTemplateList,
                name: 'periodicTemplate',
                props: (route) => ({
                    cc_id: route.params.cc_id
                })
            }]
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
    if (to.params.cc_id) {
        store.commit('setBizId', to.params.cc_id)
        setAtomConfigApiUrls(store.state.site_url, to.params.cc_id)
    }
    next()
})

export default routers
