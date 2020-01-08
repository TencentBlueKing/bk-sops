/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import Vue from 'vue'
import VueRouter from 'vue-router'
import VueCookies from 'vue-cookies'

import store from '@/store'
import http from '@/api'

Vue.use(VueRouter)
Vue.use(VueCookies)

const Home = () => import(/* webpackChunkName: 'home' */'../views/home')
const Template = () => import(/* webpackChunkName: 'home' */'../views/template/index')
const TemplatePreview = () => import(/* webpackChunkName: 'home' */'../views/template/preview')
const TaskList = () => import(/* webpackChunkName: 'home' */'../views/task/list')
const TaskCreate = () => import(/* webpackChunkName: 'home' */'../views/task/create')
const TaskReset = () => import(/* webpackChunkName: 'home' */'../views/task/reset')
const TaskEditTiming = () => import(/* webpackChunkName: 'home' */'../views/task/timing')
const TaskDetail = () => import(/* webpackChunkName: 'home' */'../views/task/detail')
const TaskNodes = () => import(/* webpackChunkName: 'home' */'../views/task/nodes')
const TaskCanvas = () => import(/* webpackChunkName: 'home' */'../views/task/canvas')
const NotFound = () => import(/* webpackChunkName: 'none' */'../views/404')

const routes = [
    {
        path: '/',
        name: 'home',
        title: '业务选择',
        isActionSheetShow: false,
        component: Home
    },
    {
        path: '/template/preview',
        name: 'template_preview',
        title: '预览',
        isActionSheetShow: true,
        component: TemplatePreview
    },
    {
        path: '/template/:bizId/',
        name: 'template',
        title: '流程模板',
        isActionSheetShow: true,
        component: Template,
        props: (route) => ({
            bizId: route.params.bizId
        })
    },
    {
        path: '/task/create/:templateId',
        name: 'task_create',
        title: '新建任务',
        isActionSheetShow: true,
        component: TaskCreate,
        props: (route) => ({
            templateId: route.params.templateId
        })
    },
    {
        path: '/task/list',
        name: 'task_list',
        title: '任务记录',
        isActionSheetShow: true,
        component: TaskList
    },
    {
        path: '/task/reset',
        name: 'task_reset',
        component: TaskReset
    },
    {
        path: '/task/timing',
        name: 'task_edit_timing',
        component: TaskEditTiming
    },
    {
        path: '/task/detail',
        name: 'task_detal',
        component: TaskDetail
    },
    {
        path: '/task/nodes',
        name: 'task_nodes',
        title: '执行详情',
        isActionSheetShow: true,
        component: TaskNodes
    },
    {
        path: '/task/canvas',
        name: 'task_canvas',
        title: '执行任务',
        component: TaskCanvas
    },
    // 404
    {
        path: '*',
        name: '404',
        component: NotFound
    }
]

const router = new VueRouter({
    base: global.SITE_URL + 'weixin/',
    mode: 'history',
    routes: routes
})

const routerConfig = getRouterConfig(routes)

function getRouterPageTitle ({ title = '', isActionSheetShow = true }) {
    return { title: title, isActionSheetShow: isActionSheetShow }
}

function getRouterConfig (routers) {
    const obj = {}
    routers.forEach((r) => {
        if (r.name) {
            obj[r.name] = getRouterPageTitle(r)
        }
    })
    return obj
}

const cancelRequest = async () => {
    const allRequest = http.queue.get()
    const requestQueue = allRequest.filter(request => request.cancelWhenRouteChange)
    await http.cancel(requestQueue.map(request => request.requestId))
}

let canceling = true
let pageMethodExecuting = true

router.beforeEach(async (to, from, next) => {
    canceling = true
    await cancelRequest()
    canceling = false
    const bizId = to.params.bizId || to.query.bizId || VueCookies.get('biz_id')
    if (to.name && routerConfig[to.name]) {
        ({ title: store.state.title, isActionSheetShow: store.state.isActionSheetShow } = routerConfig[to.name])
    }
    if (to.query.biz_selected) {
        store.commit('setActionSheetShow', true)
    }
    if (bizId) {
        store.commit('setBizId', bizId)
        store.commit('setActionSheetShow', true)
        // cookies记录用户第一次选择的biz_id,如果为空，则跳转至选择业务页面
        VueCookies.set('biz_id', store.state.bizId)
        VueCookies.set('isSelectedBiz', true)
        if (to.name === 'home' && !to.query.biz_selected) {
            next({ path: `/template/${bizId}` })
        } else {
            next()
        }
    } else {
        if (to.name !== 'home') {
            next({ path: '/' })
        } else {
            next()
        }
    }
})

router.afterEach(async (to, from) => {
    store.commit('setMainContentLoading', true)

    const pageDataMethods = []
    const routerList = to.matched
    routerList.forEach(r => {
        const fetchPageData = r.instances.default && r.instances.default.fetchPageData
        if (fetchPageData && typeof fetchPageData === 'function') {
            pageDataMethods.push(r.instances.default.fetchPageData())
        }
    })

    pageMethodExecuting = true
    await Promise.all(pageDataMethods)
    pageMethodExecuting = false

    if (!canceling && !pageMethodExecuting) {
        store.commit('setMainContentLoading', false)
    }
})

export default router
