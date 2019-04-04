import Vue from 'vue'

import App from './App'
import router from './router'
import store from './store'
import Exception from './components/exception'
import { bus } from './common/bus'
import { Button, Search, Cell, CellGroup, Icon, Tag, Tabbar, TabbarItem, Field, List, Dialog, Locale } from 'vant'
import enUS from 'vant/lib/locale/lang/en-US'
import zhCN from 'vant/lib/locale/lang/zh-CN'

Vue.use(Button)
    .use(Search)
    .use(Cell)
    .use(CellGroup)
    .use(Icon)
    .use(Tag)
    .use(Tabbar)
    .use(TabbarItem)
    .use(Field)
    .use(List)
    .use(Dialog)

Vue.component('app-exception', Exception)

global.bus = bus
global.mainComponent = new Vue({
    el: '#app',
    router,
    store,
    components: { App },
    template: '<App/>'
})

if (store.state.lang === 'en') {
    Locale.use('en', enUS)
} else {
    Locale.use('zhCHS', zhCN)
}

if (typeof (window.gettext) !== 'function') {
    window.gettext = function gettext (string) {
        return string
    }
}
