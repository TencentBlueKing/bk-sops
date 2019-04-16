import Vue from 'vue'

import App from './App'
import router from './router'
import store from './store'
import Exception from './components/exception'
import { bus } from './common/bus'
import {
    NavBar,
    Button,
    Search,
    Cell,
    CellGroup,
    Icon,
    Tag,
    Tabbar,
    TabbarItem,
    Field,
    List,
    Dialog,
    Popup,
    Locale,
    Picker,
    Actionsheet
} from 'vant'
import enUS from 'vant/lib/locale/lang/en-US'
import zhCN from 'vant/lib/locale/lang/zh-CN'
import 'amfe-flexible'

Vue.use(NavBar)
    .use(Search)
    .use(Button)
    .use(Cell)
    .use(CellGroup)
    .use(Icon)
    .use(Tag)
    .use(Tabbar)
    .use(TabbarItem)
    .use(Field)
    .use(List)
    .use(Dialog)
    .use(Popup)
    .use(Picker)
    .use(Actionsheet)

Vue.component('app-exception', Exception)
Vue.config.devtools = false

global.bus = bus
global.mainComponent = new Vue({
    el: '#app',
    router,
    store,
    components: { App },
    template: '<App/>'
})

if (store.state.lang === 'en') {
    Locale.use('en-US', enUS)
} else {
    Locale.use('zh-CN', zhCN)
}

if (typeof (window.gettext) !== 'function') {
    window.gettext = function gettext (string) {
        return string
    }
}
