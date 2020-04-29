/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import os from 'os'
import path from 'path'

import config from './config'

const isProd = process.env.NODE_ENV === 'production'

export function resolve (dir) {
    return path.join(__dirname, '..', dir)
}

export function assetsPath (_path) {
    const assetsSubDirectory = isProd ? config.build.assetsSubDirectory : config.dev.assetsSubDirectory
    return path.posix.join(assetsSubDirectory, _path)
}

export function getIP () {
    const ifaces = os.networkInterfaces()
    const defultAddress = '127.0.0.1'
    let ip = defultAddress

    /* eslint-disable fecs-use-for-of, no-loop-func */
    for (const dev in ifaces) {
        if (ifaces.hasOwnProperty(dev)) {
            /* jshint loopfunc: true */
            ifaces[dev].forEach(details => {
                if (ip === defultAddress && details.family === 'IPv4') {
                    ip = details.address
                }
            })
        }
    }
    /* eslint-enable fecs-use-for-of, no-loop-func */
    return ip
}
