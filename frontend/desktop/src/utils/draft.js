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
import '@/utils/i18n.js'
import moment from 'moment'
const draft = {
    // 添加本地缓存
    addDraft (username, ccId, templateId, templateData, message = gettext('自动保存')) {
        // 防止无法进行存储本地缓存 大约96KB左右的多余空间
        const minDraftLength = 100000
        // 本地缓存剩余大小
        let remainingLocalStorageSize = 1024 * 1024 * 5 - unescape(encodeURIComponent(JSON.stringify(localStorage))).length
        let index = 0
        while (remainingLocalStorageSize < minDraftLength) {
            // 大小不足96KB时清除一部分本地缓存 从最早创建的本地缓存开始删除
            const key = localStorage.key(index++)
            const keyArray = key.split('_')
            if (keyArray.length !== 4) {
                continue
            }
            localStorage.removeItem(key)
            remainingLocalStorageSize = 1024 * 1024 * 5 - unescape(encodeURIComponent(JSON.stringify(localStorage))).length
        }
        // 当前时间戳
        const timestamp = new Date().getTime()
        // 当前年月日时分秒时间
        const localTime = moment.unix(timestamp / 1000).format('YYYY-MM-DD HH:mm:ss')
        // 数据
        const descriptionData = { 'time': localTime, 'message': message }
        // 存储数据
        const key = [username, ccId, templateId, timestamp].join('_')
        // 超过50个本地缓存需要进行删除
        let draftNumber = 0
        const localStorageLength = localStorage.length
        const regex = this.getKeyRegex(username, ccId, templateId)
        for (let index = localStorageLength - 1; index >= 0; index--) {
            const key = localStorage.key(index)
            // 获取key字段的所有切割信息
            if (regex.test(key)) {
                draftNumber++
                if (draftNumber >= 50) {
                    this.deleteDraft(key)
                }
            }
        }
        try {
            localStorage[key] = JSON.stringify({ 'template': templateData, 'description': descriptionData })
        } catch (e) {
            // 用户浏览器不支持localStorage
        }
    },
    // 删除本地缓存
    deleteDraft (key) {
        try {
            localStorage.removeItem(key)
            return true
        } catch (e) {
            return false
        }
    },
    // 用于替换第一次创建模板id为 uuid 的id
    draftReplace (username, ccId, templateId, templateUUID) {
        const regex = this.getKeyRegex(username, ccId, templateUUID)
        for (const key in localStorage) {
            // 获取key字段的所有切割信息
            const keyArray = key.split('_')
            // 切割完的长度应该为4且原先的模板id uuid 时才需要使用
            // username重复的几率比较大放置最后判断
            if (regex.test(key)) {
                // 原先的模板数据
                const draftData = localStorage[key]
                // 将原先信息删除
                localStorage.removeItem(key)
                keyArray[2] = templateId
                // 重新创建key值
                const newKey = keyArray.join('_')
                localStorage[newKey] = draftData
            }
        }
    },
    // 获取当前本地缓存
    getDraftArray (username, ccId, templateId) {
        const regex = this.getKeyRegex(username, ccId, templateId)
        const draftArray = []
        const localStorageLength = localStorage.length
        for (let index = localStorageLength - 1; index >= 0; index--) {
            const key = localStorage.key(index)
            if (regex.test(key)) {
                draftArray.push({ 'key': key, 'data': JSON.parse(localStorage[key]) })
            }
        }
        draftArray.sort(function (a, b) {
            const t1 = new Date(a.data.description.time).getTime()
            const t2 = new Date(b.data.description.time).getTime()
            return t2 - t1
        })
        return draftArray
    },
    // 删除没有template_id 的模板
    deleteAllDraftByUUID (username, ccId, uuid) {
        const regex = this.getKeyRegex(username, ccId, uuid)
        const localStorageLength = localStorage.length
        for (let index = localStorageLength - 1; index >= 0; index--) {
            const key = localStorage.key(index)
            // uuid 需要加上""变为字符串
            if (regex.test(key)) {
                localStorage.removeItem(key)
            }
        }
    },
    // 复制并替换本地缓存（模板克隆时使用）
    copyAndReplaceDraft (username, ccId, templateId, uuid) {
        const regex = this.getKeyRegex(username, ccId, templateId)
        for (const key in localStorage) {
            // 获取key字段的所有切割信息
            const keyArray = key.split('_')
            if (regex.test(key)) {
                // 原先的模板数据
                const draftData = localStorage[key]
                keyArray[2] = uuid
                // 重新创建key值并进行创建
                const newKey = keyArray.join('_')
                localStorage[newKey] = draftData
            }
        }
    },
    // 获取最近的一个本地缓存
    getLastDraft (username, ccId, templateId) {
        const localStorageLength = localStorage.length
        // 动态生成正则表达式
        const regex = this.getKeyRegex(username, ccId, templateId)
        let lastTime = 0
        let lastKey = ''
        for (let index = localStorageLength - 1; index >= 0; index--) {
            const key = localStorage.key(index)
            if (regex.test(key)) {
                const time = new Date(JSON.parse(localStorage[key]).description.time).getTime()
                if (time > lastTime) {
                    lastTime = time
                    lastKey = key
                }
            }
        }
        return localStorage[lastKey]
    },
    // 获得正则表达式
    getKeyRegex (username, ccId, templateId) {
        return new RegExp('^' + username + '_' + ccId + '_' + templateId + '_')
    }
}

export default draft
