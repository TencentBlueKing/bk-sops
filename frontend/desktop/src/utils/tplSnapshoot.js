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

const tplSnapshoot = {
    getSnapshootStorage () {
        const storageData = localStorage.getItem('snapshootStorage')
        const snapshootStorage = JSON.parse(storageData)
        return snapshootStorage ? snapshootStorage : {}
    },
    setSnapShootStorage (snapshootStorage) {
        try {
            localStorage.setItem('snapshootStorage', JSON.stringify(snapshootStorage))
        } catch (e) { // localstorage 单源域名下保存数据的大小有限制，不同浏览器可能会存在差异，这里通过捕获异常处理
            if (e.name === 'QuotaExceededError') {
                this.deleteTplSnapShoots()
            }
        }
    },
    /**
     * 创建快照
     * @param {String} username 用户名称
     * @param {String} id 项目 id 或者公共流程没有项目 id，使用 common 
     * @param {String} tpl 流程模板 id 或者流程新建、克隆没有生成 id 时，使用 uuid
     * @param {Object} data 需要保存的快照数据
     *  格式: {
     *      timeStamp: String, // unix 时间戳
     *      name: String, // 快照名称
     *      template: Object // 流程模板数据
     *  }
     */
    create (username, id, tpl, data) {
        const snapshootStorage = this.getSnapshootStorage()

        if (!snapshootStorage[username]) {
            snapshootStorage[username] = {}
        }
        if (!snapshootStorage[username][id]) {
            snapshootStorage[username][id] = {}
        }
        if (!snapshootStorage[username][id][tpl]) {
            snapshootStorage[username][id][tpl] = []
        }

        snapshootStorage[username][id][tpl].push(data)

        this.setSnapShootStorage (snapshootStorage)
    },
    /**
     * 更新快照，若快照不存在则新建
     * @param {String} username 用户名称
     * @param {String} id 项目 id 或者公共流程没有项目 id，使用 common 
     * @param {String} tpl 流程模板 id 或者流程新建、克隆没有生成 id 时，使用 uuid
     * @param {Object} data 需要保存的快照数据
     *  格式: {
     *      timeStamp: String, // unix 时间戳
     *      name: String, // 快照名称
     *      template: Object // 流程模板数据
     *  }
     */
    update (username, id, tpl, data) {
        const snapshootStorage = this.getSnapshootStorage()
        if (snapshootStorage[username]
             && snapshootStorage[username][id]
             && snapshootStorage[username][id][tpl]
        ) {
            const index = snapshootStorage[username][id][tpl].find(item => item.timeStamp === data.timeStamp)
            snapshootStorage[username][id][tpl].splice(index, 1, data)
            this.setSnapShootStorage(snapshootStorage)
        } else {
            this.create(username, id, tpl, data)
        }
    },
    /**
     * 获取流程模板下所有快照
     * @param {String} username 用户名称
     * @param {String} id 项目 id 或者公共流程没有项目 id，使用 common 
     * @param {String} tpl 流程模板 id 或者流程新建、克隆没有生成 id 时，使用 uuid
     */
    getTplSnapshoots (username, id, tpl) {
        const snapshootStorage = this.getSnapshootStorage()
        if (snapshootStorage[username]
             && snapshootStorage[username][id]
             && snapshootStorage[username][id][tpl]
        ) {
            return snapshootStorage[username][id][tpl]
        }

        return []
    },
    /**
     * 获取流程模板下某一快照，根据时间戳筛选
     * @param {String} username 用户名称
     * @param {String} id 项目 id 或者公共流程没有项目 id，使用 common 
     * @param {String} tpl 流程模板 id 或者流程新建、克隆没有生成 id 时，使用 uuid
     * @param {String} timeStamp unix 时间戳
     */
    getSnapshoot (username, id, tpl, timeStamp) {
        const tplSnapshoots = this.getTplSnapshoots(username, id, tpl)
        return tplSnapshoots.find(item => item.timeStamp === timeStamp)
    },
    /**
     * 删除流程模板下所有快照
     * @param {String} username 用户名称
     * @param {String} id 项目 id 或者公共流程没有项目 id，使用 common 
     * @param {String} tpl 流程模板 id 或者流程新建、克隆没有生成 id 时，使用 uuid
     */
    deleteTplSnapShoots (username, id, tpl) {
        const snapshootStorage = this.getSnapshootStorage()
        if (snapshootStorage[username]
            && snapshootStorage[username][id]
            && snapshootStorage[username][id][tpl].length > 0
        ) {
            snapshootStorage[username][id][tpl] = []
            this.setSnapShootStorage(snapshootStorage)
        }
    }
}

export default tplSnapshoot
