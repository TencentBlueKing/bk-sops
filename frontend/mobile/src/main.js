/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import './public-path.js'
import Vue from 'vue'
import $ from 'jquery'

import App from './App'
import router from './router'
import store from './store'
import Exception from './components/exception'
import VeeValidate, { Validator } from 'vee-validate'
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
    DatetimePicker,
    Actionsheet,
    Notify,
    Toast,
    Checkbox,
    CheckboxGroup,
    Radio,
    RadioGroup,
    Loading
} from 'vant'
import enUS from 'vant/lib/locale/lang/en-US'
import zhCN from 'vant/lib/locale/lang/zh-CN'
import 'amfe-flexible'
// import Vconsole from 'vconsole'

import '../static/style/app.scss'

// const vconsole = new Vconsole()
// console.log(vconsole)
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
    .use(DatetimePicker)
    .use(Actionsheet)
    .use(Notify)
    .use(Toast)
    .use(Checkbox)
    .use(CheckboxGroup)
    .use(Radio)
    .use(RadioGroup)
    .use(Loading)

Vue.use(VeeValidate)
Vue.component('app-exception', Exception)
Vue.config.devtools = true

global.$ = $
global.$.atoms = {}
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

Validator.localize({
    en: {
        messages: {
            required: window.gettext('必填项')
        },
        custom: {
            taskName: {
                required: window.gettext('任务名称不能为空'),
                regex: window.gettext('任务名称包含非法字符'),
                max: window.gettext('任务名称长度不能超过50个字符')
            },
            parameterInput: {
                regex: window.gettext('输入值不满足校验规则')
            }
        }
    }
})
