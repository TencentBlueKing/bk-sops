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
<template>
    <div class="local-cache">
        <table>
            <tbody>
                <tr>
                    <th class="cache-label">{{i18n.name}}</th>
                    <td class="cache-content-item">main_source_1</td>
                </tr>
                <tr>
                    <th class="cache-label">{{i18n.type}}</th>
                    <td class="cache-content-item">Git</td>
                </tr>
                <tr>
                    <th class="cache-label">{{i18n.desc}}</th>
                    <td class="cache-content-item">我的本地缓存</td>
                </tr>
                <tr>
                    <th class="cache-label">{{i18n.detail}}</th>
                    <td class="cache-content-item">
                        <table class="detail-table">
                            <tbody>
                                <tr>
                                    <th>{{i18n.serviceAddress}}</th>
                                    <td>http://radosgw-clouds.open.com</td>
                                </tr>
                                <tr>
                                    <th>bucket</th>
                                    <td>bucket-1</td>
                                </tr>
                                <tr>
                                    <th>access_key</th>
                                    <td>d323dfa34fafsafsadf3423fasdf</td>
                                </tr>
                                <tr>
                                    <th>secret_key</th>
                                    <td>aaafffffaffffff34fafsafsadf3423fasdf</td>
                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
<script>
    export default {
        name: 'PackageTable',
        data () {
            return {
                i18n: {
                    name: gettext('名称'),
                    type: gettext('类型'),
                    desc: gettext('描述'),
                    detail: gettext('详细信息'),
                    serviceAddress: gettext('服务地址')
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .local-cache {
        margin-top: 20px;
        table {
            width: 100%;
            border: 1px solid #dde4eb;
            font-size: 12px;
            border-collapse: collapse;
            background: #ffffff;
            th, td {
                padding: 12px 20px;
                border: 1px solid #dde4eb;
            }
            th {
                color: #313238;
            }
            td {
                color: #63656e;
            }
            .cache-label {
                width: 11.1%;
                text-align: center;
            }
        }
        .detail-table {
            background: #fbfbfb;
        }
    }
</style>
