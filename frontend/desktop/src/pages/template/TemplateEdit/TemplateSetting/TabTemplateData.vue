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
    <div class="template-data-panel">
        <div class="panel-title">
            <span>{{i18n.templateData}}</span>
        </div>
        <div class="code-wrapper">
            <code-editor :value="JSON.stringify(templateData, null, 4)" :options="{ readOnly: true }"></code-editor>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import CodeEditor from '@/components/common/CodeEditor.vue'
    import { mapState, mapGetters } from 'vuex'

    export default {
        name: 'TabTemplateData',
        components: {
            CodeEditor
        },
        data () {
            return {
                template: {},
                i18n: {
                    templateData: gettext('流程模板数据')
                }
            }
        },
        computed: {
            ...mapState('template/', {
                'activites': state => state.activities,
                'end_event': state => state.end_event,
                'flows': state => state.flows,
                'gateways': state => state.gateways,
                'line': state => state.line,
                'location': state => state.location,
                'outputs': state => state.outputs,
                'start_event': state => state.start_event,
                'constants': state => state.constants
            }),
            templateData () {
                const { activites, end_event, flows, gateways, line, location, outputs, start_event, constants } = this
                return {
                    activites,
                    constants,
                    end_event,
                    flows,
                    gateways,
                    line,
                    location,
                    outputs,
                    start_event
                }
            }
        },
        methods: {
            ...mapGetters('template/', [
                'getLocalTemplateData'
            ])
        }
    }
</script>
<style lang="scss" scoped>
    .template-data-panel {
        height: 100%;
        .panel-title {
            height: 35px;
            line-height: 35px;
            margin: 20px;
            border-bottom: 1px solid #cacecb;
            span {
                font-size: 14px;
                font-weight:600;
                color:#313238;
            }
        }
        .code-wrapper {
            margin: 0 10px;
            height: calc(100% - 100px);
        }
    }
</style>
