/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
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
import './config/login.js'
import './api/index.js'
import i18n from './config/i18n/index.js'
import App from './App.vue'
import bkMagicVue, { locale, lang } from 'bk-magic-vue'
import 'bk-magic-vue/dist/bk-magic-vue.min.css'
import { Input, InputNumber, Select, Radio, RadioGroup, RadioButton, Checkbox,
    CheckboxGroup, Button, Option, OptionGroup, Table, TableColumn,
    DatePicker, TimePicker, TimeSelect, Upload, Tree, Loading,
    Container, Row, Col, Pagination, Tooltip, Cascader } from 'element-ui'
import enLocale from 'element-ui/lib/locale/lang/en'
import zhLocale from 'element-ui/lib/locale/lang/zh-CN'
import locales from 'element-ui/lib/locale'
import { STRING_LENGTH } from '@/constants/index.js'
import cron from '@/assets/js/node-cron-valid/node-cron-vaild.js'
Vue.use(VeeValidate)

Vue.use(bkMagicVue)

Vue.use(Input)
Vue.use(InputNumber)
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
Vue.use(Tooltip)
Vue.use(Cascader)

if (store.state.lang === 'en') {
    locale.use(lang.enUS)
    locales.use(enLocale)
} else {
    locales.use(zhLocale)
}

$.atoms = {} // hack atom config load
$.context = {}

const InvalidNameChar = '\'‘"”$&<>'
Validator.extend('cronRlue', {
    getMessage: (field, args) => {
        return args + i18n.t('输入定时表达式非法，请校验')
    },
    validate: value => cron.validate(value).status
})
Validator.extend('integer', {
    getMessage: (field, args) => {
        return args + i18n.t('间隔时间必须是正整数')
    },
    validate: value => Number(value) >= 1 && Number(value) % 1 === 0
})
Validator.localize({
    en: {
        messages: {
            required: i18n.t('必填项')
        },
        custom: {
            templateName: {
                required: i18n.t('流程名称不能为空'),
                regex: i18n.t('流程名称不能包含') + InvalidNameChar + i18n.t('非法字符'),
                max: i18n.t('流程名称长度不能超过') + STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH + i18n.t('个字符')
            },
            nodeName: {
                required: i18n.t('节点名称不能为空'),
                regex: i18n.t('节点名称不能包含') + InvalidNameChar + i18n.t('非法字符'),
                max: i18n.t('节点名称长度不能超过') + STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH + i18n.t('个字符')
            },
            stageName: {
                regex: i18n.t('步骤名称不能包含') + InvalidNameChar + i18n.t('非法字符'),
                max: i18n.t('步骤名称不能超过') + STRING_LENGTH.STAGE_NAME_MAX_LENGTH + i18n.t('个字符')
            },
            variableName: {
                required: i18n.t('变量名称不能为空'),
                regex: i18n.t('变量名称不能包含') + InvalidNameChar + i18n.t('非法字符'),
                max: i18n.t('变量名称长度不能超过') + STRING_LENGTH.VARIABLE_NAME_MAX_LENGTH + i18n.t('个字符')
            },
            variableKey: {
                required: i18n.t('变量KEY值不能为空'),
                regex: i18n.t('变量KEY由英文字母、数字、下划线组成，且不能以数字开头'),
                max: i18n.t('变量KEY值长度不能超过') + STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH + i18n.t('个字符'),
                keyRepeat: i18n.t('变量KEY值已存在')
            },
            defaultValue: {
                required: i18n.t('变量隐藏时默认值不能为空'),
                customValueCheck: i18n.t('默认值不满足正则校验')
            },
            valueValidation: {
                validReg: i18n.t('正则校验不是合法的正则表达式')
            },
            taskName: {
                required: i18n.t('任务名称不能为空'),
                regex: i18n.t('任务名称不能包含') + InvalidNameChar + i18n.t('非法字符'),
                max: i18n.t('任务名称不能超过') + STRING_LENGTH.TASK_NAME_MAX_LENGTH + i18n.t('个字符')
            },
            schemeName: {
                required: i18n.t('方案名称不能为空'),
                regex: i18n.t('方案名称不能包含') + InvalidNameChar + i18n.t('非法字符'),
                max: i18n.t('方案名称不能超过') + STRING_LENGTH.SCHEME_NAME_MAX_LENGTH + i18n.t('个字符')
            },
            appTemplate: {
                required: i18n.t('流程模板不能为空')
            },
            appName: {
                required: i18n.t('应用名称不能为空'),
                regex: i18n.t('应用名称不能包含') + InvalidNameChar + i18n.t('非法字符'),
                max: i18n.t('应用名称不能超过') + STRING_LENGTH.APP_NAME_MAX_LENGTH + i18n.t('个字符')
            },
            appDesc: {
                max: i18n.t('应用简介不能超过') + STRING_LENGTH.APP_DESCRIPTION_MAX_LENGTH + i18n.t('个字符')
            },
            periodicName: {
                required: i18n.t('定时流程名称不能为空'),
                regex: i18n.t('定时流程名称包含') + InvalidNameChar + i18n.t('非法字符'),
                max: i18n.t('定时流程名称不能超过') + STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH + i18n.t('个字符')
            },
            projectName: {
                required: i18n.t('项目名称不能为空'),
                regex: i18n.t('项目名称包含') + InvalidNameChar + i18n.t('非法字符'),
                max: i18n.t('项目名称不能超过') + STRING_LENGTH.PROJECT_NAME_MAX_LENGTH + i18n.t('个字符')
            },
            projectDesc: {
                max: i18n.t('项目描述不能超过') + STRING_LENGTH.PROJECT_DESC_LENGTH + i18n.t('个字符')
            },
            periodicCron: {
                required: i18n.t('定时表达式不能为空'),
                regex: i18n.t('输入定时表达式非法，请校验')
            },
            interval: {
                required: i18n.t('间隔时间不能为空'),
                regex: i18n.t('间隔时间必须是正整数')
            },
            draftName: {
                required: i18n.t('本地缓存名称不能为空'),
                regex: i18n.t('本地缓存名称包含') + InvalidNameChar + i18n.t('非法字符'),
                max: i18n.t('本地缓存名称不能超过') + STRING_LENGTH.DRAFT_NAME_MAX_LENGTH + i18n.t('个字符')
            },
            packageName: {
                regex: i18n.t('名称由英文字母、数字、下划线组成，且不能以数字开头'),
                max: i18n.t('名称长度不能超过') + STRING_LENGTH.SOURCE_NAME_MAX_LENGTH + i18n.t('个字符')
            },
            moduleName: {
                regex: i18n.t('名称由英文字母、数字、下划线组成，且不能以数字开头'),
                max: i18n.t('名称长度不能超过') + STRING_LENGTH.SOURCE_NAME_MAX_LENGTH + i18n.t('个字符')
            },
            cacheName: {
                regex: i18n.t('名称由英文字母、数字、下划线组成，且不能以数字开头'),
                max: i18n.t('名称长度不能超过') + STRING_LENGTH.SOURCE_NAME_MAX_LENGTH + i18n.t('个字符')
            },
            minRule: {
                required: i18n.t('开始分钟数不能为空'),
                regex: i18n.t('请输入 0 - 59 之间的数')
            },
            hourRule: {
                required: i18n.t('开始小时数不能为空'),
                regex: i18n.t('请输入 0 - 23 之间的数')
            },
            weekRule: {
                required: i18n.t('开始周数不能为空'),
                regex: i18n.t('请输入 0 - 6 之间的数')
            },
            dayRule: {
                required: i18n.t('开始天数不能为空'),
                regex: i18n.t('请输入 1 - 31 之间的数')
            },
            monthRule: {
                required: i18n.t('开始月数不能为空'),
                regex: i18n.t('请输入 1 - 12 之间的数')
            },
            testName: {
                required: i18n.t('test不能为空'),
                regex: i18n.t('请输入 test 之间的数')
            }
        }
    }
})

new Vue({
    i18n,
    router,
    store,
    render: h => h(App)
}).$mount('#root')
