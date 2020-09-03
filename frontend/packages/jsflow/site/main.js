import Vue from 'vue'
import VueRouter from 'vue-router'

import store from './store'
import router from './routers'
import App from './App.vue'

Vue.use(VueRouter)

/* eslint-disable no-new */
new Vue({
    el: '#app-main-page',
    store,
    router,
    render: h => h(App)
})
