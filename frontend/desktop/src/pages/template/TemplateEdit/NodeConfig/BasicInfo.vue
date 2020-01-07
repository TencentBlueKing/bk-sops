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
    <div class="basic-info">
        <bk-form v-if="nodeInfo.type === 'ServiceActivity'" :label-width="130">
            <bk-form-item :label="i18n.plugin" :required="true">
                <bk-select v-model="plugin">
                    <bk-options
                        v-for="atom in atomList"
                        :key="atom.code"
                        :id="atom.code"
                        :name="`${atom.type}-${atom.name}`">
                    </bk-options>
                </bk-select>
            </bk-form-item>
            <bk-form-item :label="i18n.version" :required="true">
                <bk-select v-model="version"></bk-select>
            </bk-form-item>
            <bk-form-item :label="i18n.name" :required="true">
                <bk-input v-model="nodeName"></bk-input>
            </bk-form-item>
            <bk-form-item :label="i18n.step">
                <bk-input v-model="stepName"></bk-input>
            </bk-form-item>
            <bk-form-item :label="i18n.errorHandle">
                <bk-checkbox-group>
                    <bk-checkbox>
                        <i class="common-icon-dark-circle-i"></i>
                        {{ i18n.ignorable }}
                    </bk-checkbox>
                    <bk-checkbox>
                        <i class="common-icon-dark-circle-s"></i>
                        {{ i18n.skip }}
                    </bk-checkbox>
                    <bk-checkbox>
                        <i class="common-icon-dark-circle-r"></i>
                        {{ i18n.retry }}
                    </bk-checkbox>
                </bk-checkbox-group>
            </bk-form-item>
            <bk-form-item :label="i18n.selectable">
                <bk-switcher v-model="optional" size="small"></bk-switcher>
            </bk-form-item>
        </bk-form>
        <bk-form v-else :label-width="130">
            <bk-form-item :label="i18n.tpl" :required="true">
                <bk-select v-model="tpl"></bk-select>
            </bk-form-item>
            <bk-form-item :label="i18n.name" :required="true">
                <bk-input v-model="nodeName"></bk-input>
            </bk-form-item>
            <bk-form-item :label="i18n.step">
                <bk-input v-model="stepName"></bk-input>
            </bk-form-item>
            <bk-form-item :label="i18n.selectable">
                <bk-switcher v-model="optional" size="small"></bk-switcher>
            </bk-form-item>
        </bk-form>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState } from 'vuex'

    export default {
        name: 'BasicInfo',
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
                plugin: '',
                tpl: '',
                version: '',
                nodeName: '',
                stepName: '',
                optional: false,
                i18n: {
                    plugin: gettext('标准插件'),
                    version: gettext('插件版本'),
                    name: gettext('节点名称'),
                    step: gettext('步骤名称'),
                    errorHandle: gettext('失败处理'),
                    selectable: gettext('是否可选'),
                    ignorable: gettext('自动忽略'),
                    skip: gettext('手动跳过'),
                    retry: gettext('手动重试'),
                    tpl: gettext('流程模板')
                }
            }
        },
        computed: {
            ...mapState({
                'singleAtom': state => state.atomList.singleAtom,
                'subAtom': state => state.atomList.subAtom,
                'activities': state => state.template.activities
            }),
            nodeInfo () {
                return this.activities[this.nodeId]
            }
        }
    }
</script>
<style lang="scss" scoped>
    .basic-info {
        padding-right: 30px;
    }
    /deep/ .bk-form {
        .bk-label {
            font-size: 12px;
        }
        .bk-checkbox-text {
            font-size: 12px;
            color: #63656e;
        }
    }
</style>
