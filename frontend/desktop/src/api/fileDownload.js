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
export function fileDownload (data, filename) {
    const blob = new Blob([data], { type: 'application/octet-stream' })
    if (typeof window.navigator.msSaveBlob !== 'undefined') {
        // hack old IE
        window.navigator.msSaveBlob(blob, filename)
    } else {
        const eleLink = document.createElement('a')
        const blobURL = window.URL.createObjectURL(blob)
        eleLink.style.display = 'none'
        eleLink.href = blobURL
        eleLink.setAttribute('download', filename)

        // hack HTML5 download attribute
        if (typeof eleLink.download === 'undefined') {
            eleLink.setAttribute('target', '_blank')
        }
        document.body.appendChild(eleLink)
        eleLink.click()
        document.body.removeChild(eleLink)
        window.URL.revokeObjectURL(blobURL)
    }
}
