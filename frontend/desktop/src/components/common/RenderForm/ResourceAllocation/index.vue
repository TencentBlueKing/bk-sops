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
    <div class="resource-allocation">
        <resource-list
            v-show="!showFilter"
            :show-filter.sync="showFilter"
            :cols="tbCols"
            :config="localConfig"
            :value="localValue"
            @update="updateValue">
        </resource-list>
        <resource-filter
            v-if="showFilter"
            :show-filter.sync="showFilter"
            :config="localConfig"
            @update="updateConfig">
        </resource-filter>
    </div>
</template>
<script>
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import ResourceList from './ResourceList.vue'
    import ResourceFilter from './ResourceFilter.vue'

    export default {
        name: 'ResourceAllocation',
        components: {
            ResourceList,
            ResourceFilter
        },
        props: {
            config: {
                type: Object,
                default () {
                    return {
                        set_template_id: '',
                        host_resources: [],
                        set_count: 0,
                        module_detail: []
                    }
                }
            },
            value: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                showFilter: false,
                localConfig: this.config,
                localValue: this.value,
                colsLoading: false,
                originalCols: [], // 表格列原始配置项
                tbCols: [] // 增加模块列后的表格配置项
            }
        },
        mounted () {
            this.getColsConfig()
        },
        methods: {
            ...mapActions([
                'getCCSearchColAttrSet'
            ]),
            async getColsConfig () {
                try {
                    this.colsLoading = true
                    const resp = await this.getCCSearchColAttrSet()
                    if (resp.result) {
                        this.originalCols = resp.data
                        this.joinCols()
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.colsLoading = false
                }
            },
            // 将模块列拼接到表格中，从第二列开始
            joinCols () {
                const modulesConfig = []
                const originalConfig = this.originalCols.map(item => {
                    return {
                        width: 100,
                        config: item
                    }
                })
                this.localConfig.module_detail.forEach(item => {
                    modulesConfig.push({
                        width: 120,
                        config: {
                            tag_code: item.name,
                            type: 'textarea',
                            attrs: {
                                name: gettext('模块:') + item.name + '(' + item.host_count + ')',
                                editable: true,
                                validation: [{ type: 'required' }]
                            }
                        }
                    })
                })
                const cols = [...originalConfig.slice(0, 1), ...modulesConfig, ...originalConfig.slice(1)]
                cols.push({
                    width: 100,
                    config: {
                        tag_code: 'tb_btns',
                        attrs: {
                            name: gettext('操作')
                        }
                    }
                })
                this.tbCols = cols
            },
            updateConfig (val) {
                this.localConfig = val
                this.joinCols()
                this.updateValue()
            },
            updateValue (val) {
                this.localValue = val
            }
        }
    }
</script>
<style style="scss" scoped>
    .resource-allocation {
        width: 800px;
        background: #ffffff;
    }
</style>
