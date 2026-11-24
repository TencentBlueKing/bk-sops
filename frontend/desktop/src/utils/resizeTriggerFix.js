/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
/**
 * 绕过 bk-magic-vue resize 监听的缺陷
 *
 * bk-magic-vue 添加 resize 监听时用 addEventListener('scroll', handler, true)，移除时漏了 capture 参数，
 * 监听器实际没被移除，只把元素的 __resizeTrigger__ 置为 false。之后该元素内任何滚动都会报
 * "Cannot read properties of undefined (reading 'firstElementChild')"（如 bk-resize-layout 销毁后、DOM 还在时）。
 *
 * 在 document 的捕获阶段（先于这些元素上的监听器）把这类元素恢复成 bk-magic-vue 自己创建的结构，残留监听器照常运行，
 * 此时元素已没有 resize 回调，不会产生其他效果。
 */
let installed = false

function restoreTrigger (el) {
    const trigger = document.createElement('div')
    trigger.className = 'resize-triggers'
    trigger.innerHTML = '<div class="expand-trigger"><div></div></div><div class="contract-trigger"></div>'
    el.appendChild(trigger)
    el.__resizeTrigger__ = trigger
}

export default function installResizeTriggerFix () {
    if (installed) return
    installed = true
    document.addEventListener('scroll', (event) => {
        event.composedPath().forEach(el => {
            if (el.__resizeTrigger__ === false) restoreTrigger(el)
        })
    }, true)
}
