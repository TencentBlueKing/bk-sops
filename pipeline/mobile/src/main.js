import Vue from 'vue'

import App from './App'
import router from './router'
import store from './store'
import Exception from './components/exception'
import { bus } from './common/bus'

Vue.component('app-exception', Exception)

global.bus = bus
global.mainComponent = new Vue({
    el: '#app',
    router,
    store,
    components: { App },
    template: '<App/>'
})
