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
/**
 * 画布引导 Popover 通用组件
 */

import GuidePopover from '@/components/common/GuidePopover.vue'
import Vue from 'vue'
import bus from './bus.js'
// 示例配置项
// const config = {
//     width: 325,
//     placement: 'bottom',
//     once: true,
//     delay: 0,
//     el: document.getElementById('#xxx'),
//     img: {
//         height: 145,
//         url: ''
//     },
//     text: [
//         {
//             type: 'name',
//             val: 'name'
//         },
//         {
//             type: 'text',
//             val: 'this is tips'
//         }
//     ]
// }

const Guide = function (config = {}) {
    this.config = config
    const GuideComponent = Vue.extend(GuidePopover)
    this.int = new GuideComponent()
    this.int.$props.config = config
    this.int.$mount()
    this.mount = (el) => {
        const { width, trigger, placement, delay, arrow, once } = this.config
        this.instance = this.instance || bus.$bkPopover(el, {
            width,
            arrow,
            placement,
            delay: delay || 0,
            duration: [0, 0],
            trigger: trigger || 'click',
            allowHTML: true,
            theme: 'guide',
            animation: 'shift-away',
            content: this.int.$el.innerHTML,
            onHidden: () => {
                if (once) {
                    this.instance.destroy()
                }
            }
        })
    }
}
export default Guide
