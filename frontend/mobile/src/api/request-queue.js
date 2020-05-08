/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
export default class RequestQueue {
    constructor () {
        this.queue = []
    }

    /**
     * 根据 id 获取请求对象，如果不传入 id，则获取整个地列
     *
     * @param {string?} id id
     *
     * @return {Array|Object} 队列集合或队列对象
     */
    get (id) {
        if (typeof id === 'undefined') {
            return this.queue
        }
        return this.queue.filter(request => request.requestId === id)
    }

    /**
     * 设置新的请求对象到请求队列中
     *
     * @param {Object} newRequest 请求对象
     */
    set (newRequest) {
        this.queue.push(newRequest)
        // if (!this.queue.some(request => request.requestId === newRequest.requestId)) {
        //     this.queue.push(newRequest)
        // }
    }

    /**
     * 根据 id 删除请求对象
     *
     * @param {string} id id
     */
    delete (id) {
        // const target = this.queue.filter(request => request.requestId === id)[0]
        // if (target) {
        //     const index = this.queue.indexOf(target)
        //     this.queue.splice(index, 1)
        // }
        this.queue = [...this.queue.filter(request => request.requestId !== id)]
    }

    /**
     * cancel 请求队列中的请求
     *
     * @param {string|Array?} requestIds 要 cancel 的请求 id，如果不传，则 cancel 所有请求
     * @param {string?} msg cancel 时的信息
     *
     * @return {Promise} promise 对象
     */
    cancel (requestIds, msg = 'request canceled') {
        let cancelQueue = []
        if (typeof requestIds === 'undefined') {
            cancelQueue = [...this.queue]
        } else if (requestIds instanceof Array) {
            requestIds.forEach(requestId => {
                const cancelRequest = this.get(requestId)
                if (cancelRequest) {
                    cancelQueue = [...cancelQueue, ...cancelRequest]
                }
            })
        } else {
            const cancelRequest = this.get(requestIds)
            if (cancelRequest) {
                cancelQueue = [...cancelQueue, ...cancelRequest]
            }
        }

        try {
            cancelQueue.forEach(request => {
                const requestId = request.requestId
                this.delete(requestId)
                request.cancelExcutor(`${msg}: ${requestId}`)
            })
            return Promise.resolve(requestIds)
        } catch (error) {
            return Promise.reject(error)
        }
    }
}
