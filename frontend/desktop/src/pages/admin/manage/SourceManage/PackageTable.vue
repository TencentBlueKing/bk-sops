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
<template>
    <div class="package-table">
        <table>
            <tbody>
                <tr>
                    <th class="source-label">{{$t('名称')}}</th>
                    <td class="source-content-item">{{value.name}}</td>
                </tr>
                <tr>
                    <th class="source-label">{{$t('类型')}}</th>
                    <td class="source-content-item">{{packageName}}</td>
                </tr>
                <tr>
                    <th class="source-label">{{$t('描述')}}</th>
                    <td class="source-content-item">{{value.desc}}</td>
                </tr>
                <tr>
                    <th class="source-label">{{$t('详细信息')}}</th>
                    <td class="source-content-item">
                        <table class="detail-table">
                            <tbody>
                                <tr v-for="field in detailFields" :key="field.id">
                                    <th>{{field.name}}</th>
                                    <td>{{value.details[field.id]}}</td>
                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
                <tr>
                    <th class="source-label">{{$t('模块配置')}}</th>
                    <td class="source-content-item">
                        <table class="content-item-table">
                            <thead>
                                <tr>
                                    <th>{{$t('根模块')}}</th>
                                    <th>{{$t('版本')}}</th>
                                    <th>{{$t('导入模块')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(item, key) in value.packages" :key="key">
                                    <td>{{key}}</td>
                                    <td>{{item.version}}</td>
                                    <td>
                                        <p v-for="(m, i) in item.modules" :key="i">{{ m }}</p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
                <tr>
                    <th class="source-label">{{$t('已导入插件')}}</th>
                    <td class="source-content-item">
                        <table class="content-item-table">
                            <thead>
                                <tr>
                                    <th>{{$t('插件名')}}</th>
                                    <th>{{$t('类名')}}</th>
                                    <th>{{$t('所属模块')}}</th>
                                </tr>
                            </thead>
                            <tbody v-if="value.imported_plugins.length">
                                <tr v-for="(item, key) in value.imported_plugins" :key="key">
                                    <td>{{item.group_name}}-{{item.name}}</td>
                                    <td>{{item.class_name}}</td>
                                    <td>{{item.module}}</td>
                                </tr>
                            </tbody>
                        </table>
                        <NoData class="local-no-data" v-if="!value.imported_plugins.length" />
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
<script>
    import { SOURCE_TYPE } from '@/constants/manage.js'
    import NoData from '@/components/common/base/NoData'
    export default {
        name: 'PackageTable',
        components: {
            NoData
        },
        props: {
            value: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            const detailFields = this.getSourceKeys(this.value.type)
            return {
                detailFields
            }
        },
        computed: {
            packageName () {
                return SOURCE_TYPE.filter(m => m.type === this.value.type)[0].name
            }
        },
        methods: {
            getSourceKeys (type) {
                const detailFields = []

                const source = SOURCE_TYPE.find(item => item.type === type)
                for (const key in source.keys) {
                    detailFields.push({
                        id: key,
                        name: source.keys[key].name
                    })
                }
                
                return detailFields
            }
        }
    }
</script>
<style lang="scss" scoped>
    .local-no-data {
        border: 1px solid #dde4eb;
        border-top: none;
        /deep/ .no-data {
            padding: 20px 0px;
        }
    }
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
