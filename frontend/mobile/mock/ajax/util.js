/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
export function randomInt (n, m) {
    return Math.floor(Math.random() * (m - n + 1) + n)
}

/**
 * sleep 函数
 *
 * @param {number} ms 毫秒数
 */
export function sleep (ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * sleep 函数，慎用，这会阻止一切 js 线程
 *
 * @param {number} delay 毫秒数
 */
export function sleep1 (delay) {
    const start = +new Date()
    while (+new Date().getTime() < start + delay) {}
}
