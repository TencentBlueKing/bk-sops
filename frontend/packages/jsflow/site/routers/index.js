import VueRouter from 'vue-router'

import Home from '../pages/home'
import Demo from '../pages/demo'

const router = new VueRouter({
    mode: 'history',
    routes: [
        {
            path: '/',
            component: Home,
            name: 'Home'
        },
        {
            path: '/demo',
            component: Demo,
            name: 'Demo'
        }
    ]
})

export default router
