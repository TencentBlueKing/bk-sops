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
    <div class="local-cache">
        <table>
            <tbody>
                <tr>
                    <th class="cache-label">{{$t('名称')}}</th>
                    <td class="cache-content-item">{{value.name}}</td>
                </tr>
                <tr>
                    <th class="cache-label">{{$t('类型')}}</th>
                    <td class="cache-content-item">{{value.type}}</td>
                </tr>
                <tr>
                    <th class="cache-label">{{$t('描述')}}</th>
                    <td class="cache-content-item">{{value.desc}}</td>
                </tr>
                <tr>
                    <th class="cache-label">{{$t('详细信息')}}</th>
                    <td class="cache-content-item">
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
            </tbody>
        </table>
    </div>
</template>
<script>
    import { SOURCE_TYPE } from '@/constants/manage.js'

    export default {
        name: 'LocalCache',
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
            th {
                width: 25%;
            }
        }
    }
</style>
