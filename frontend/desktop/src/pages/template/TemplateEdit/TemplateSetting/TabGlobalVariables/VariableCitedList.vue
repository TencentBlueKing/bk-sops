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
    <div class="variable-cited-wrap">
        <div class="variable-cited-list">
            <p class="num">{{$t('引用变量的节点')}}{{$t('（')}}{{list.length}}{{$t('）')}}</p>
            <div
                v-for="item in list"
                :key="item.id"
                class="variable-cited-item">
                <span
                    :class="['cited-name', { 'name-error': !item.name }]"
                    :title="item.name"
                    @click.stop="onCitedNodeClick(item.id)">
                    {{ item.name }}
                </span>
            </div>
        </div>
    </div>
</template>
<script>
    import { mapState } from 'vuex'
    export default {
        name: 'VariableCitedList',
        props: {
            citedList: Array
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
.num {
    margin: 0 0 10px;
}
.variable-cited-list {
    position: relative;
    margin: 10px 30px;
    padding: 16px;
    background: #f0f1f5;
    border: 1px solid #dcdee5;
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
        border-color: #dcdee5 #dcdee5 transparent transparent;
        transform: rotate(-45deg);
        border-radius: 1px;
    }
    .variable-cited-item {
        position: relative;
        padding: 0 18px;
        height: 24px;
        line-height: 24px;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
        &::before {
            content: '';
            position: absolute;
            top: 9px;
            left: 0;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #b6b6b6;
        }
        .cited-name {
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
        }
    }
}
</style>
