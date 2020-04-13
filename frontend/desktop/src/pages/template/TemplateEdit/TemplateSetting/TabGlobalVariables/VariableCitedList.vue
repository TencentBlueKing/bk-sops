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
                v-for="item in list"
                :key="item.id"
                class="variable-cited-item">
                <span class="cited-name"
                    @click.stop="onCitedNodeClick(item.id)">
                    {{ item.name || i18n.notNamed }}
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
        props: {
            constant: Object,
            citedList: Array
        },
        data () {
            return {
                i18n: {
                    notNamed: gettext('未命名节点')
                }
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities
            }),
            list () {
                return this.citedList.map(id => {
                    return {
                        id,
                        name: this.activities[id].name
                    }
                })
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
    position: relative;
    margin: 10px 30px;
    background: #f0f1f5;
    border: 1px solid #ebebeb;
    border-radius: 2px;
    &::after {
        content: '';
        position: absolute;
        top: -5px;
        right: 100px;
        width: 8px;
        height: 8px;
        background: #f0f1f5;
        border-style: solid;
        border-width: 1px 1px 0 0;
        border-color: #ebebeb #ebebeb transparent transparent;
        transform: rotate(-45deg);
        border-radius: 1px;
    }
    .variable-cited-item {
        padding: 0 20px;
        height: 40px;
        line-height: 40px;
        color: #3a84ff;
        .cited-name {
            cursor: pointer;
        }
    }
}
</style>
