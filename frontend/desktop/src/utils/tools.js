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
import i18n from '@/config/i18n/index.js'
import cloneDeepWith from 'lodash/cloneDeepWith'
import isEqual from 'lodash/isEqual'
import escape from 'lodash/escape'
import assign from 'lodash/assign'
import { checkDataType } from './checkDataType.js'
import moment from 'moment'

const tools = {
    /**
     * 防抖函数
     * @param {Function} fn 回调函数
     * @param {Number} delay 延迟时间
     */
    debounce (fn, delay) {
        let timer

        return function () {
            const context = this
            const args = arguments

            clearTimeout(timer)

            timer = setTimeout(function () {
                fn.apply(context, args)
            }, delay)
        }
    },
    /**
     * 节流函数
     * @param {Function} fn 回调函数
     * @param {*} threshhold 时间间隔
     */
    throttle (fn, threshhold) {
        let last, timer

        threshhold || (threshhold = 250)

        return function () {
            const context = this
            const args = arguments
            const now = +new Date()

            if (last && now < last + threshhold) {
                clearTimeout(timer)

                timer = setTimeout(function () {
                    last = now
                    fn.apply(context, args)
                }, threshhold)
            } else {
                last = now
                fn.apply(context, args)
            }
        }
    },
    /**
     * 深拷贝函数
     * @param {Object}} obj copy 对象
     */
    deepClone (obj) {
        return cloneDeepWith(obj)
    },
    /**
     * 深比较函数
     */
    isDataEqual (a, b) {
        return isEqual(a, b)
    },
    /**
     * 转义特殊字符
     * @param {String} str 需要转义的字符
     */
    escapeStr (str = '') {
        return escape(str)
    },
    /**
     * 将源对象的属性分配到目标对象
     * @param {Object} target 目标对象
     * @param {Object} source 源对象
     */
    assign (target = {}, source = {}) {
        return assign(target, source)
    },
    /**
     * 判断传入值是否为空
     * @param {Any} value 值
     */
    isEmpty (value) {
        const dataType = checkDataType(value)
        let isEmpty
        switch (dataType) {
            case 'String':
                isEmpty = value === ''
                break
            case 'Array':
                isEmpty = !value.length
                break
            case 'Object':
                isEmpty = !Object.keys(value).length
                break
            default:
                isEmpty = false
        }
        return isEmpty
    },
    /**
     * 时间转化函数，毫秒转换为特定字符串格式
     * @param {String|Number} time 时间
     */
    timeTransform (time) {
        const val = Number(time)
        let timeStr = ''
        if (val >= 0) {
            if (val < 1) {
                timeStr += `${i18n.tc('小于')} ${i18n.tc('秒', 1)}`
            } else {
                const timeRange = moment.duration(val * 1000)
                const day = timeRange.days()
                const hour = timeRange.hours()
                const minute = timeRange.minutes()
                const second = timeRange.seconds()
                if (day > 0) {
                    timeStr += i18n.tc('天', day, { n: day })
                }
                if (hour > 0) {
                    timeStr += ` ${i18n.tc('小时', hour, { n: hour })}`
                }
                if (minute > 0) {
                    timeStr += ` ${i18n.tc('分钟', minute, { n: minute })}`
                }
                if (second >= 1) {
                    timeStr += ` ${i18n.tc('秒', second, { n: second })}`
                }
            }
        } else {
            timeStr = '--'
        }
        return timeStr
    }
}

export default tools
