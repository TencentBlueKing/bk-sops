/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
const dom = {
    nodeContains (root, el) {
        if (root.compareDocumentPosition) {
            return root === el || !!(root.compareDocumentPosition(el) & 16)
        }
        if (root.contains && el.nodeType === 1) {
            return root.contains(el) && root !== el
        }
        let node = el.parentNode
        while (node) {
            if (node === root) return true
            node = node.parentNode
        }
        return false
    },
    parentClsContains (cls, el) {
        if (el.classList.contains(cls)) {
            return true
        }
        let node = el.parentNode
        while (node) {
            if (node.classList && node.classList.contains(cls)) return true
            node = node.parentNode
        }
        return false
    },
    setPageTabIcon (path) {
        const link = document.querySelector("link[rel*='icon']") || document.createElement('link')
        link.type = 'image/x-icon'
        link.rel = 'shortcut icon'
        link.href = path
        document.getElementsByTagName('head')[0].appendChild(link)
    }
}

export default dom
