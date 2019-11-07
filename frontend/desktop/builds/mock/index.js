/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/

const path = require('path')
const pathToRegexp = require('path-to-regexp')
const chokidar = require('chokidar')
let config = require('./config/')

module.exports = function (app) {
    const watcher = chokidar.watch(require.resolve('./config/index.js'), {
        persistent: true
    })
    
    watcher.on('all', (event, path) => {
        config = requireUncached(path)
    })
    
    function requireUncached(module){
        delete require.cache[require.resolve(module)]
        return require(module)
    }

    app.all('/*', (req, res, next) => {
        let pathKey = ''

        if (!config) {
            next()
        }

        Object.keys(config).some(item => {
            if (pathToRegexp(item).exec(req.path) && req.method === config[item].method) {
                pathKey = item
                return true
            }
        })
        if (pathKey) {
           const mock = config[pathKey]
            if (mock.type === 'file') {
                res.sendFile(path.resolve(__dirname, './config/', mock.data))
            } else {
                res.json(mock.data)
            }
        } else {
            next()
        }
    })
}