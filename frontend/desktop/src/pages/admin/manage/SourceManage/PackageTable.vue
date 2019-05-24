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
    <div class="package-table">
        <table>
            <tbody>
                <tr>
                    <th class="source-label">{{i18n.name}}</th>
                    <td class="source-content-item">main_source_1</td>
                </tr>
                <tr>
                    <th class="source-label">{{i18n.type}}</th>
                    <td class="source-content-item">Git</td>
                </tr>
                <tr>
                    <th class="source-label">{{i18n.desc}}</th>
                    <td class="source-content-item">我的主源包</td>
                </tr>
                <tr>
                    <th class="source-label">{{i18n.detail}}</th>
                    <td class="source-content-item">
                        <table class="detail-table">
                            <tbody>
                                <tr>
                                    <th>仓库地址</th>
                                    <td>http://radosgw-clouds.open.com</td>
                                </tr>
                                <tr>
                                    <th>仓库静态文件地址</th>
                                    <td>bucket-1</td>
                                </tr>
                                <tr>
                                    <th>分支</th>
                                    <td>d323dfa34fafsafsadf3423fasdf</td>
                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
                <tr>
                    <th class="source-label">{{i18n.module}}</th>
                    <td class="source-content-item">
                        <table class="content-item-table">
                            <thead>
                                <tr>
                                    <th>{{i18n.rootModule}}</th>
                                    <th>{{i18n.version}}</th>
                                    <th>{{i18n.importedModule}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>custom_plugins</td>
                                    <td>1.0</td>
                                    <td>custom_plugins.a.b.test</td>
                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
                <tr>
                    <th class="source-label">{{i18n.importedPlugin}}</th>
                    <td class="source-content-item">
                        <table class="content-item-table">
                            <thead>
                                <tr>
                                    <th>{{i18n.pluginName}}</th>
                                    <th>{{i18n.clsName}}</th>
                                    <th>{{i18n.moduleBelong}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>custom_plugins</td>
                                    <td>1.0</td>
                                    <td>custom_plugins.a.b.test</td>
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
                    module: gettext('模块配置'),
                    importedPlugin: gettext('已导入插件'),
                    rootModule: gettext('根模块'),
                    version: gettext('版本'),
                    importedModule: gettext('已导入模块'),
                    pluginName: gettext('插件名'),
                    clsName: gettext('类名'),
                    moduleBelong: gettext('所属模块')
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .package-table {
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
            .source-label {
                width: 11.1%;
                text-align: center;
            }
        }
        .detail-table {
            background: #fbfbfb;
            th {
                width: 25%;
            }
        }
        .content-item-table {
            background: #fbfbfb;
            th, td {
                text-align: center;
            }
        }
    }
</style>
