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
    <div class="variable-cited-wrap">
        <ul class="variable-cited-list">
            <li
                v-for="item in citedList"
                :key="item.id"
                class="variable-cited-item">
                <span class="cited-name"
                    @click.stop="onCitedNodeClick(item.id)">
                    {{ item.name }}
                </span>
            </li>
        </ul>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState } from 'vuex'
    export default {
        name: 'VariableCitedList',
        props: ['constant'],
        computed: {
            ...mapState({
                'constantsCited': state => state.template.constantsCited,
                'activities': state => state.template.activities
            }),
            citedList () {
                const list = []
                for (const node in this.constantsCited) {
                    const codes = this.constantsCited[node]
                    for (const code in codes) {
                        console.log(code, this.constant.key, 'sss')
                        if (code === this.constant.key) {
                            list.push({
                                name: this.activities[node].name,
                                id: node
                            })
                        }
                    }
                }
                return list
            }
        },
        methods: {
            // 引用节点点击
            onCitedNodeClick (nodeId) {
                this.$emit('onCitedNodeClick', nodeId)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.variable-cited-list {
    .variable-cited-item {
        padding-left: 50px;
        width: 100%;
        height: 42px;
        line-height: 42px;
        color: #3a84ff;
        background: #fafbfd;
        border-top: 1px solid #ebebeb;
        .cited-name {
            cursor: pointer;
        }
    }
}
</style>
