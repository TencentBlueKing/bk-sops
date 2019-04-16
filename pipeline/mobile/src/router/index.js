import Vue from 'vue'
import VueRouter from 'vue-router'
import VueCookies from 'vue-cookies'

import store from '@/store'
import http from '@/api'

Vue.use(VueRouter)
Vue.use(VueCookies)

const Home = () => import(/* webpackChunkName: 'home' */'../views/home')
const Template = () => import(/* webpackChunkName: 'home' */'../views/template/index')
const TaskList = () => import(/* webpackChunkName: 'home' */'../views/task/list')
const TaskCreate = () => import(/* webpackChunkName: 'home' */'../views/task/create')
const TaskReset = () => import(/* webpackChunkName: 'home' */'../views/task/reset')
const TaskDetail = () => import(/* webpackChunkName: 'home' */'../views/task/detail')
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
        path: '/template',
        name: 'template',
        title: '流程模板',
        isActionSheetShow: true,
        component: Template
    },
    {
        path: '/task/create',
        name: 'task_create',
        title: '任务信息',
        isActionSheetShow: true,
        component: TaskCreate
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
        path: '/task/detail',
        name: 'task_detal',
        component: TaskDetail
    },
    // 404
    {
        path: '*',
        name: '404',
        component: NotFound
    }
]

const router = new VueRouter({
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
    if (bizId) {
        store.commit('setBizId', bizId)
        store.commit('setActionSheetShow', true)
        // cookies记录用户第一次选择的biz_id,如果为空，则跳转至选择业务页面
        VueCookies.set('biz_id', store.state.bizId)
        if (to.name === 'home') {
            next({ path: '/template', query: { bizId: bizId } })
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
