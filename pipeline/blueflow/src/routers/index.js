/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '@/store/index.js'
import { setAtomConfigApiUrls } from '@/config/setting.js'
import NotFoundComponent from '@/components/layout/NotFoundComponent.vue'
import Home from '@/pages/home/index.vue'
import Template from '@/pages/template/index.vue'
import TemplateEdit from '@/pages/template/TemplateEdit/index.vue'
import TemplateList from '@/pages/template/TemplateList/index.vue'
import Task from '@/pages/task/index.vue'
import ConfigPage from '@/pages/config/index.vue'
import AppMaker from '@/pages/appmaker/index.vue'
import AppMakerTaskHome from '@/pages/appmaker/AppTaskHome/index.vue'
import TaskList from '@/pages/task/TaskList/index.vue'
import TaskCreate from '@/pages/task/TaskCreate/index.vue'
import TaskExecute from '@/pages/task/TaskExecute/index.vue'
import ErrorPage from '@/pages/error/index.vue'
import AnalysisTemplate from '@/pages/analysis/Template/index.vue'
import AnalysisInstance from '@/pages/analysis/Instance/index.vue'
import AnalysisAtom from '@/pages/analysis/Atom/index.vue'
import AnalysisAppmaker from '@/pages/analysis/Appmaker/index.vue'
import FunctionHome from '@/pages/function/index.vue'
import AuditHome from '@/pages/audit/index.vue'

Vue.use(VueRouter)

const routers = new VueRouter({
    base: SITE_URL,
    mode: 'history',
    routes: [
        {
            path: '/',
            redirect: to => {
                return `/business/home/${store.state.cc_id}`
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
            children: [{
                path: 'home/:cc_id/',
                component: TemplateList,
                props: (route) => ({
                    cc_id: route.params.cc_id
                })
            },
            {
                path: 'edit/:cc_id/',
                component: TemplateEdit,
                props: (route) => ({
                    cc_id: route.params.cc_id,
                    template_id: route.query.template_id,
                    type: 'edit'
                })
            },
            {
                path: 'new/:cc_id/',
                component: TemplateEdit,
                props: (route) => ({
                    cc_id: route.params.cc_id,
                    type: 'new'
                })
            },
            {
                path: 'clone/:cc_id/',
                component: TemplateEdit,
                props: (route) => ({
                    cc_id: route.params.cc_id,
                    template_id: route.query.template_id,
                    type: 'clone'
                })
            },
            {
                path: 'newtask/:cc_id/:step/',
                component: TaskCreate,
                props: (route) => ({
                    cc_id: route.params.cc_id,
                    step: route.params.step,
                    template_id: route.query.template_id
                })
            }]
        },
        {
            path: '/taskflow',
            component: Task,
            children: [{
                path: 'home/:cc_id/',
                component: TaskList,
                props: (route) => ({
                    cc_id: route.params.cc_id
                })
            },
            {
                path: 'execute/:cc_id/',
                component: TaskExecute,
                props: (route) => ({
                    cc_id: route.params.cc_id,
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
            path: '/analysis/atom/',
            component: AnalysisAtom,
            name: 'analysisAtom'
        },
        {
            path: '/analysis/template/',
            component: AnalysisTemplate,
            name: 'analysisTemplate'
        },
        {
            path: '/analysis/instance/',
            component: AnalysisInstance,
            name: 'analysisInstance'
        },
        {
            path: '/analysis/appmaker/',
            component: AnalysisAppmaker,
            name: 'analysisAppmaker'
        },
        {
            path: '/function/home/',
            component: FunctionHome,
            name: 'functionHome'
        },
        {
            path: '/audit/home/',
            component: AuditHome,
            name: 'auditHome'
        },
        {
            path: '*',
            name: 'notFoundPage',
            component: NotFoundComponent
        }
    ]
})

const oldPages = [
]

routers.beforeEach ((to, from, next) => {
    // is jump to 404 page
    if (process.env.NODE_ENV === "production" && to.name === 'notFoundPage') {
        store.commit('setNotFoundPage', true)
    } else {
        store.commit('setNotFoundPage', false)
    }

    if (to.params.cc_id) {
        store.commit('setBizId', to.params.cc_id)
        setAtomConfigApiUrls(store.state.site_url, store.state.cc_id)
    }
    const isPathShouldReload = oldPages.some(item => {
        const reg = new RegExp('^' + item)
        return reg.test(to.fullPath)
    })
    if (process.env.NODE_ENV === "production" && isPathShouldReload && !store.state.firstEnterApp) {
        let prefix_url = SITE_URL.replace(/\/?$/, '')
        let redirectPath = prefix_url + to.fullPath
        if (store.state.hideHeader) {
            if (Object.keys(to.query).length) {
                redirectPath += '&hide_header=1'
            } else {
                redirectPath += '?hide_header=1'
            }
        }
        window.location.href = redirectPath
    } else {
        // hack spa page goto Django page
        if (store.state.firstEnterApp) {
            store.commit('markFirstEnter')
        }
        next()
    }
})


export default routers
