/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
export default class CachedPromise {
    constructor () {
        this.cache = {}
    }

    /**
     * 根据 id 获取缓存对象，如果不传 id，则获取所有缓存
     *
     * @param {string?} id id
     *
     * @return {Array|Promise} 缓存集合或promise 缓存对象
     */
    get (id) {
        if (typeof id === 'undefined') {
            return Object.keys(this.cache).map(requestId => this.cache[requestId])
        }
        return this.cache[id]
    }

    /**
     * 设置 promise 缓存对象
     *
     * @param {string} id id
     * @param {Promise} promise 要缓存的 promise 对象
     *
     * @return {Promise} promise 对象
     */
    set (id, promise) {
        Object.assign(this.cache, { [id]: promise })
    }

    /**
     * 删除 promise 缓存对象
     *
     * @param {string|Array?} deleteIds 要删除的缓存对象的 id，如果不传则删除所有
     *
     * @return {Promise} 以成功的状态返回 Promise 对象
     */
    delete (deleteIds) {
        let requestIds = []
        if (typeof deleteIds === 'undefined') {
            requestIds = Object.keys(this.cache)
        } else if (deleteIds instanceof Array) {
            deleteIds.forEach(id => {
                if (this.get(id)) {
                    requestIds.push(id)
                }
            })
        } else if (this.get(deleteIds)) {
            requestIds.push(deleteIds)
        }

        requestIds.forEach(requestId => {
            delete this.cache[requestId]
        })

        return Promise.resolve(deleteIds)
    }
}
