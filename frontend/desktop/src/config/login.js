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
import isCrossOriginIFrame from '@/utils/isCrossOriginIFrame.js'

const isCrossOrigin = isCrossOriginIFrame()
const topWindow = isCrossOrigin ? window : window.top
const topDocument = topWindow.document

try {
    topWindow.BLUEKING.corefunc.open_login_dialog = openLoginDialog
    topWindow.BLUEKING.corefunc.close_login_dialog = closeLoginDialog
} catch (_) {
    topWindow.BLUEKING = {
        corefunc: {
            open_login_dialog: openLoginDialog,
            close_login_dialog: closeLoginDialog
        }
    }
}

function openLoginDialog (src, width = 460, height = 490, method = 'get') {
    if (!src) return
    const isWraperExit = topDocument.querySelector('#bk-gloabal-login-iframe')
    if (isWraperExit) return
    window.needReloadPage = method === 'get' // 是否需要刷新界面
    const closeIcon = topDocument.createElement('span')
    closeIcon.style.cssText = 'outline: 10px solid;outline-offset: -22px;transform: rotate(45deg);position: absolute;right: 0;cursor: pointer;color: #979ba5;width: 26px;height: 26px;border-radius: 50%;'
    closeIcon.id = 'bk-gloabal-login-close'
    topDocument.addEventListener('click', topWindow.BLUEKING.corefunc.close_login_dialog)

    const frame = topDocument.createElement('iframe')
    frame.setAttribute('src', src)
    frame.style.cssText = `border: 0;outline: 0;width:${width}px;height:${height}px;`

    const dialogDiv = topDocument.createElement('div')
    dialogDiv.style.cssText = 'position: absolute;left: 50%;top: 20%;transform: translateX(-50%);'
    dialogDiv.appendChild(closeIcon)
    dialogDiv.appendChild(frame)

    const wraper = topDocument.createElement('div')
    wraper.id = 'bk-gloabal-login-iframe'
    wraper.style.cssText = 'position: fixed;top: 0;bottom: 0;left: 0;right: 0;background-color: rgba(0,0,0,.6);height: 100%;z-index: 5000;'
    wraper.appendChild(dialogDiv)
    topDocument.body.appendChild(wraper)
}
function closeLoginDialog (e) {
    try {
        e.stopPropagation()
        const el = e.target
        const closeIcon = topDocument.querySelector('#bk-gloabal-login-close')
        if (closeIcon !== el) return
        topDocument.removeEventListener('click', topWindow.BLUEKING.corefunc.close_login_dialog)
        // if (el) {
        //     el.removeEventListener('click', topWindow.BLUEKING.corefunc.close_login_dialog)
        // }
        topDocument.body.removeChild(el.parentElement.parentElement)
    } catch (_) {
        topDocument.removeEventListener('click', topWindow.BLUEKING.corefunc.close_login_dialog)
        const wraper = topDocument.querySelector('#bk-gloabal-login-iframe')
        if (wraper) {
            topDocument.body.removeChild(wraper)
        }
    }
    window.needReloadPage && window.location.reload()
}
