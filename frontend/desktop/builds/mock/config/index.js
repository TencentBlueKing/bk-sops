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

/**
 * @descrition 接口 mock 配置文件，导出一个配置对象
 * 对象的 key 为需要 mock 接口的 path，支持模糊匹配(参考path-to-regexp文档)
 * 对象的 value 为 mock 数据配置对象，包含 type、method、data 三个属性
 * type 取值为 'json' 或者 'file'，分别表示模拟数据为 json 或文件类型
 * method 表示接口的请求方法
 * data 为 mock 数据，当 type 取值为 'json' 时，直接返回实际的 mock 数据对象，当 type 取值为 'file' 时，返回文件的相对路径(相对于 config 文件夹)
 */

 const permission = require('./permission.js')

module.exports = {
    // demo 参考：
    // '/t/bk_sops/api/v3/template/': {
    //     type: 'json',
    //     method: 'GET',
    //     data: {
    //         meta: {
    //             limit: 15,
    //             next: null,
    //             offset: 0,
    //             previous: null,
    //             total_count: 1
    //         },
    //         objects: [
    //             {
    //                 category: "MonitorAfdfdsflarm",
    //                 category_name: "监控告警",
    //                 create_time: "2019-10-10 10:05:31 +0800",
    //                 creator_name: "admin",
    //                 edit_time: "2019-10-10 10:05:31 +0800",
    //                 editor_name: "fgdfg",
    //                 has_subprocess: false,
    //                 id: 9,
    //                 is_add: 0,
    //                 is_deleted: false,
    //                 name: "new20191010020512",
    //                 notify_receivers: "{'receiver_group':[],'more_receiver':''}",
    //                 notify_type: "[]",
    //                 pipeline_template: "",
    //                 resource_uri: "/t/bk_sops/weixin/api/v3/template/9/",
    //                 subprocess_has_update: false,
    //                 template_id: 9,
    //                 time_out: 20,
    //                 version: "56dbcc8e7a72cd57c1aaa8d23e11ae31",
    //             }
    //         ]
    //     }
    // },
    // '/t/bk_sops/static/components/atoms/job/job_fast_execute_script.js': {
    //     type: 'file',
    //     method: 'GET',
    //     data: './data.js'
    // }
    '/o/bk_sops/iam/api/meta/': {
        type: 'json',
        method: 'GET',
        data: permission
    }
}
