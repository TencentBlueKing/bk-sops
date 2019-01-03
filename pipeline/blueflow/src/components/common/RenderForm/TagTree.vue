/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="tag-form tag-tree" v-show="showForm">
        <div v-if="editable">
            <el-tree
                ref="tree"
                :data="items"
                :props="default_props"
                :show-checkbox="show_checkbox"
                :default-expand-all="default_expand_all"
                :default-checked-keys="value"
                :filter-node-method="filterNode"
                node-key="id"
                :check-on-click-node="true"
                :expand-on-click-node="false"
                @check="_handleBoxCheck"
                >
            </el-tree>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="view-value">{{(value === 'undefined' || value === '') ? '--' : value}}</span>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { getAtomFormMixins, getInitialProps } from './atomFormMixins.js'
const TreeAttrs = {
    value: {
        type: Array,
        required: false,
        default () {
            return []
        }
    },
    items: {
        type: Array,
        required: false,
        default () {
            return []
        },
        desc: "set tree data, which should be a multiple layers array"
    },
    show_checkbox: {
        type: Boolean,
        required: false,
        default () {
            return true
        },
        desc: "whether node is selectable"
    },
    default_expand_all: {
        type: Boolean,
        required: false,
        default () {
            return true
        },
        desc: "whether to expand all nodes by default"
    },
    remote: {
        type: Boolean,
        required: false,
        default () {
            return false
        },
        desc: "use remote data or not"
    },
    remote_url: {
        type: String,
        required: false,
        default () {
            return ""
        },
        desc: "remote url when remote is true"
    },
    remote_data_init: {
        type: Function,
        required: false,
        default () {
            return function (data) {
                return data
            }
        },
        desc: "how to process data after getting remote data"
    }
}
export default {
    name: 'TagTree',
    mixins: [getAtomFormMixins(TreeAttrs, this)],
    props: getInitialProps(TreeAttrs),
    data () {
        return {
            default_props: {
                label: 'label',
                children: 'children'
            },
            loading: false,
            remote_cache: null
        }
    },
    mounted () {
        this.remoteMethod(this.remote_url)
    },
    methods: {
        handleCheckChange: function (data, checked, indeterminate) {
            return true
        },
        filterNode: function (value, data) {
            return true
        },
        handleBoxCheck: function (data) {
            return true
        },
        _handleBoxCheck: function (data) {
            if (this.handleBoxCheck(data)) {
                this.value = this.$refs.tree.getCheckedKeys(true)
                this.onChange()
            }
        },
        remoteMethod (query) {
            var $this = this
            if (!$this.editable) return

            var remote_url = typeof this.remote_url === 'function' ? this.remote_url() : this.remote_url
            if (!remote_url) return

            this.loading = true

            // 请求远程数据
            if (this.remote_cache === null && remote_url) {
                $.ajax({
                    url: remote_url,
                    method: "GET",
                    success: function (res) {
                        var data = $this.remote_data_init(res)
                        $this.remote_cache = data

                        if ($this.remote_cache !== null) {
                            $this.items = $this.remote_cache
                            $this.$refs.tree.setCheckedKeys($this.value)
                        } else {
                            $this.items = []
                        }

                        $this.loading = false
                    },
                    error: function () {
                        $this.empty_text = gettext("请求数据失败")
                        $this.loading = false
                    }
                })
            } else {
                $this.items = $this.remote_cache
                $this.$refs.tree.setCheckedKeys($this.value)
                $this.loading = false
            }
        }
    }
}
</script>
<style lang="scss" scoped>

</style>
