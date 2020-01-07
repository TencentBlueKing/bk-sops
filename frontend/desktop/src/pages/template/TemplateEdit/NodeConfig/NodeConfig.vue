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
    <div class="node-config-wrapper">
        <section class="config-section">
            <h3>{{i18n.basicInfo}}</h3>
            <basic-info
                :node-id="nodeId"
                :atom-list="atomList"
                :subflow-list="subflowList">
            </basic-info>
        </section>
        <section class="config-section">
            <h3>{{i18n.inputParams}}</h3>
            <input-params></input-params>
        </section>
        <section class="config-section">
            <h3>{{i18n.outputParams}}</h3>
            <output-params></output-params>
        </section>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    // import { mapActions, mapState, mapMutations } from 'vuex'
    // import { errorHandler } from '@/utils/errorHandler.js'
    import BasicInfo from './BasicInfo.vue'
    import InputParams from './InputParams.vue'
    import outputParams from './outputParams.vue'

    export default {
        name: 'NodeConfig',
        components: {
            BasicInfo,
            InputParams,
            outputParams
        },
        props: {
            nodeId: {
                type: String,
                default: ''
            },
            atomList: {
                type: Array,
                default () {
                    return []
                }
            },
            subflowList: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                i18n: {
                    basicInfo: gettext('基础信息'),
                    inputParams: gettext('输入参数'),
                    outputParams: gettext('输出参数')
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .node-config-wrapper {
        float: left;
        padding: 15px 20px;
        width: 694px;
        height: 100%;
        background: #ffffff;
        border-left: 1px solid #dddddd;
        box-shadow: -4px 0 6px -4px rgba(0, 0, 0, .15);
    }
    .config-section {
        margin-bottom: 50px;
        & > h3 {
            margin: 0 0 20px 0;
            padding-bottom: 14px;
            font-size: 14px;
            font-weight: bold;
            line-height: 1;
            color: #313238;
            border-bottom: 1px solid #cacecb;
        }

    }
</style>
