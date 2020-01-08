/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
const tools = {

    timeTransform (time) {
        const val = Number(time)
        if (val > 0) {
            if (val < 60) {
                return val + window.gettext(' 秒')
            } else if (val < 3600) {
                return parseFloat(val / 60).toFixed(1) + window.gettext(' 分')
            } else if (val < 86400) {
                return parseFloat(val / 3600).toFixed(1) + window.gettext(' 小时')
            } else {
                return parseFloat(val / 86400).toFixed(1) + window.gettext(' 天')
            }
        } else {
            return '--'
        }
    }
}

export default tools
