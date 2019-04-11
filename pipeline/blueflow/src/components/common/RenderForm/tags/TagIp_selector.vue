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
    <div class="tag-ip-selector" v-bkloading="{isLoading: loading, opacity: 1}">
        <div v-if="formMode" class="tag-ip-selector-wrap">
            <ip-selector
                ref="ipSelector"
                :editable="editable"
                :isMultiple="isMultiple"
                :staticIpList="staticIpList"
                :dynamicIpList="dynamicIpList"
                :topoModelList="topoModelList"
                v-model="ipValue">
            </ip-selector>
        </div>
        <span v-else class="rf-view-value">{{viewValue}}</span>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import {mapActions} from 'vuex'
import { getFormMixins } from '../formMixins.js'
import { errorHandler } from '@/utils/errorHandler.js'
import IpSelector from '../IpSelector/index.vue'

const intAttrs = {
    isMultiple: {
        type: Boolean,
        required: false,
        default: true,
        desc: 'checkbox or radio'
    },
    value: {
        type: [Object],
        required: false,
        default () {
            return {
                selectors: [],
                ip: [],
                topo: [],
                filters: [],
                excludes: []
            }
        }
    }
}
export default {
    name: 'TagIp_selector',
    components: {
        IpSelector
    },
    mixins: [getFormMixins(intAttrs)],
    data () {
        return {
            loading: true,
            staticIpList: [],
            dynamicIpList: [],
            topoModelList: []
        }
    },
    computed: {
        ipValue: {
            get () {
                return this.value
            },
            set (val) {
                this.updateForm(val)
            }
        },
        viewValue () {
            let val = ''
            this.ipValue.selectors.forEach(selector => {
                if (selector === 'ip') {
                    val += this.ipValue[selector].map(item => item.bk_host_innerip).join('; ')
                }
                if (selector === 'topo') {
                    val += this.ipValue[selector].map(item => item.bk_inst_id).join('; ')
                }
            })
            return val || '--'
        }
    },
    created () {
        this.getData()
    },
    methods: {
        ...mapActions([
            'getHostInCC',
            'getTopoTreeInCC',
            'getTopoModelInCC'
        ]),
        getData () {
            this.loading = true
            const staticIpExtraFields = ['agent']

            Promise.all([
                this.getHostInCC(staticIpExtraFields),
                this.getTopoTreeInCC(),
                this.getTopoModelInCC()
            ]).then(values => {
                if (Array.isArray(values)) {
                    this.staticIpList = (values[0] && values[0].data) || []
                    this.dynamicIpList = (values[1] && values[1].data) || []
                    this.topoModelList = (values[2] && values[2].data) || []
                }
                this.loading = false
            }).catch(e => {
                this.loading = false
                errorHandler(e, this)
            })
        },
        customValidate () {
            return this.$refs.ipSelector.validate()
        }
    }
}
</script>
<style lang="scss" scoped>
.tag-ip-selector-wrap {
    padding: 0 10px 10px;
    background: #fafbfd;
}
</style>
