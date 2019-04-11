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
import cloneDeepWith from 'lodash/cloneDeepWith'
import { checkDataType } from './checkDataType.js'

const tools = {
    /**
     * 防抖函数
     * @param {Function} fn 回调函数
     * @param {Number} delay 延迟时间
     */
    debounce (fn, delay) {
        let timer

        return function () {
            let context = this
            let args = arguments

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
     * 对象比较
     * @param {Object} a 对象 a
     * @param {Object} b 对象 b
     */
    isObjEqual (a, b) {
        let p, t
        for (p in a) {
            if (typeof b[p] === 'undefined') {
                return false
            }
            if (b[p] && !a[p]) {
                return false
            }
            t = typeof a[p]
            if (t === 'object' && !this.isObjEqual(a[p], b[p])) {
                return false
            }
            if (t === 'function' && (typeof b[p] === 'undefined' || a[p].toString() !== b[p].toString())) {
                return false
            }
            if (a[p] !== b[p]) {
                return false
            }
        }
        for (p in b) {
            if (typeof a[p] === 'undefined') {
                return false
            }
        }
        return true
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
        if (val > 0) {
            if (val < 60) {
                return val + gettext(' 秒')
            } else if (val < 3600) {
                return parseFloat(val / 60).toFixed(1) + gettext(' 分')
            } else if (val < 86400) {
                return parseFloat(val / 3600).toFixed(1) + gettext(' 小时')
            } else {
                return parseFloat(val / 86400).toFixed(1) + gettext(' 天')
            }
        } else {
            return '--'
        }
    }
}

export default tools
