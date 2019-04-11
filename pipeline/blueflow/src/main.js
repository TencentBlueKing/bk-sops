/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
import Vue from 'vue'
import VeeValidate, { Validator } from 'vee-validate'
import router from './routers/index.js'
import store from './store/index.js'
import './directives/index.js'
import App from './App.vue'
import './api/index.js'
import bkMagic, { locale, langPkg } from './assets/bk-magic/bk-magic-vue.min.js'
import './assets/bk-magic/bk-magic-vue.min.css'
import { Input, Select, Radio, RadioGroup, RadioButton, Checkbox,
    CheckboxGroup, Button, Option, OptionGroup, Table, TableColumn,
    DatePicker, TimePicker, TimeSelect, Upload, Tree, Loading,
    Container, Row, Col, Pagination } from 'element-ui'
import enLocale from 'element-ui/lib/locale/lang/en'
import zhLocale from 'element-ui/lib/locale/lang/zh-CN'
import locales from 'element-ui/lib/locale'
import { JSEncrypt } from 'jsencrypt'
import { STRING_LENGTH } from '@/constants/index.js'

Vue.use(VeeValidate)

Vue.use(bkMagic)

Vue.use(Input)
Vue.use(Select)
Vue.use(Radio)
Vue.use(RadioGroup)
Vue.use(RadioButton)
Vue.use(Checkbox)
Vue.use(CheckboxGroup)
Vue.use(Button)
Vue.use(Option)
Vue.use(OptionGroup)
Vue.use(Table)
Vue.use(TableColumn)
Vue.use(DatePicker)
Vue.use(TimeSelect)
Vue.use(TimePicker)
Vue.use(Upload)
Vue.use(Tree)
Vue.use(Loading.directive)
Vue.use(Container)
Vue.use(Row)
Vue.use(Col)
Vue.use(Pagination)


if (store.state.lang === 'en') {
    locale.use(langPkg.enUS)
    locales.use(enLocale)
} else {
    locales.use(zhLocale)
}

$.atoms = {} // hack atom config load

const InvalidNameChar = '\'‘"”$&<>'

Validator.localize({
    en: {
        messages: {
            required: gettext('必填项')
        },
        custom: {
            templateName: {
                required: gettext('流程名称不能为空'),
                regex: gettext('流程名称不能包含') + InvalidNameChar + gettext('非法字符'),
                max: gettext('流程名称长度不能超过') + STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH + gettext('个字符')
            },
            nodeName: {
                required: gettext('节点名称不能为空'),
                regex: gettext('节点名称不能包含') + InvalidNameChar + gettext('非法字符'),
                max: gettext('节点名称长度不能超过') + STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH + gettext('个字符')
            },
            stageName: {
                regex: gettext('步骤名称不能包含') + InvalidNameChar + gettext('非法字符'),
                max: gettext('步骤名称不能超过') + STRING_LENGTH.STAGE_NAME_MAX_LENGTH + gettext('个字符')
            },
            variableName: {
                required: gettext('变量名称不能为空'),
                regex: gettext('变量名称不能包含') + InvalidNameChar + gettext('非法字符'),
                max: gettext('变量名称长度不能超过') + STRING_LENGTH.VARIABLE_NAME_MAX_LENGTH + gettext('个字符')
            },
            variableKey: {
                required: gettext('变量KEY值不能为空'),
                regex: gettext('变量KEY由英文字母、数字、下划线组成，且不能以数字开头'),
                max: gettext('变量KEY值长度不能超过') + STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH + gettext('个字符'),
                keyRepeat: gettext('变量KEY值已存在')
            },
            defaultValue: {
                required: gettext('变量隐藏时默认值不能为空'),
                customValueCheck: gettext('默认值不满足正则校验')
            },
            valueValidation: {
                validReg: gettext('正则校验不是合法的正则表达式')
            },
            taskName: {
                required: gettext('任务名称不能为空'),
                regex: gettext('任务名称不能包含') + InvalidNameChar + gettext('非法字符'),
                max: gettext('任务名称不能超过') + STRING_LENGTH.TASK_NAME_MAX_LENGTH + gettext('个字符')
            },
            schemeName: {
                required: gettext('方案名称不能为空'),
                regex: gettext('方案名称不能包含') + InvalidNameChar + gettext('非法字符'),
                max: gettext('方案名称不能超过') + STRING_LENGTH.SCHEME_NAME_MAX_LENGTH + gettext('个字符')
            },
            appTemplate: {
                required: gettext('流程模板不能为空')
            },
            appName: {
                required: gettext('应用名称不能为空'),
                regex: gettext('应用名称不能包含') + InvalidNameChar + gettext('非法字符'),
                max: gettext('应用名称不能超过') + STRING_LENGTH.APP_NAME_MAX_LENGTH + gettext('个字符')
            },
            appDesc: {
                max: gettext('应用简介不能超过') + STRING_LENGTH.APP_DESCRIPTION_MAX_LENGTH + gettext('个字符')
            },
            periodicName: {
                required: gettext('定时流程名称不能为空'),
                regex: gettext('定时流程名称包含') + InvalidNameChar + gettext('非法字符'),
                max: gettext('定时流程名称不能超过') + STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH + gettext('个字符')
            },
            periodicCron: {
                required: gettext('定时表达式不能为空'),
                regex: gettext('输入定时表达式非法，请校验')
            },
            draftName: {
                required: gettext('本地缓存名称不能为空'),
                regex: gettext('本地缓存名称包含') + InvalidNameChar + gettext('非法字符'),
                max: gettext('本地缓存名称不能超过') + STRING_LENGTH.DRAFT_NAME_MAX_LENGTH + gettext('个字符')
            }
        }
    }
})

new Vue({
    router,
    store,
    render: h => h(App)
}).$mount('#root')
