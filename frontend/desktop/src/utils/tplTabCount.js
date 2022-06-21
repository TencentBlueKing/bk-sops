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

const tplTabCount = {
    getStorage () {
        const storageData = localStorage.getItem('tplTabStorage')
        const data = JSON.parse(storageData)
        return data || {}
    },
    setStorage (data) {
        try {
            localStorage.setItem('tplTabStorage', JSON.stringify(data))
        } catch (e) {
            localStorage.removeItem('tplTabStorage')
        }
    },
    setTab (data, type) {
        const { user, id, tpl } = data
        const tabDict = this.getStorage()
        if (type === 'add') {
            if (!(user in tabDict)) {
                tabDict[user] = {}
            }
            if (!(id in tabDict[user])) {
                tabDict[user][id] = {}
            }
            if (!(tpl in tabDict[user][id])) {
                tabDict[user][id][tpl] = 0
            }
            tabDict[user][id][tpl] += 1
        } else if (type === 'del') {
            if (tabDict[user] && tabDict[user][id]) {
                if (tabDict[user][id][tpl] > 0) {
                    tabDict[user][id][tpl] -= 1
                }
                if (tabDict[user][id][tpl] === 0) {
                    delete tabDict[user][id][tpl]
                }
            }
        }
        this.setStorage(tabDict)
    },
    getCount (query) {
        const { user, id, tpl } = query
        const tabDict = this.getStorage()
        if (tabDict[user] && tabDict[user][id]) {
            return tabDict[user][id][tpl]
        }
        return 0
    }
}

export default tplTabCount
