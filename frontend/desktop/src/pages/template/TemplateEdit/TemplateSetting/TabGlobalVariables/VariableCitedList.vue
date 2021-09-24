/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="variable-cited-wrap">
        <template v-for="group in list">
            <div v-if="group.data.length > 0" class="variable-cited-list" :key="group.key">
                <p class="group-title">{{$t('引用变量的')}}{{ $t(`${group.title}`) }}{{$t('（')}}{{group.data.length}}{{$t('）')}}</p>
                <div
                    v-for="item in group.data"
                    :key="item.id"
                    class="variable-cited-item">
                    <span
                        :class="['cited-name', { 'name-error': !item.name }]"
                        :title="item.name"
                        @click.stop="onCitedNodeClick(group.key, item.id)">
                        {{ item.name }}
                    </span>
                </div>
            </div>
        </template>
    </div>
</template>
<script>
    import { mapState } from 'vuex'
    export default {
        name: 'VariableCitedList',
        props: {
            citedList: Object
        },
        data () {
            return {
                groups: [
                    {
                        id: 'activities',
                        name: '任务节点'
                    },
                    {
                        id: 'conditions',
                        name: '分支条件'
                    },
                    {
                        id: 'constants',
                        name: '全局变量'
                    }
                ]
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'lines': state => state.template.line,
                'gateways': state => state.template.gateways,
                'constants': state => state.template.constants,
                'internalVariable': state => state.template.internalVariable
            }),
            variableList () {
                return { ...this.internalVariable, ...this.constants }
            },
            list () { // 变量被引用数据
                return this.groups.map(group => {
                    const key = group.id
                    const data = this.citedList[key].map(item => {
                        const id = item
                        let name = ''
                        if (key === 'activities') {
                            name = this.activities[item].name
                        } else if (key === 'conditions') {
                            const nodeId = this.lines.find(line => line.id === item).source.id
                            name = this.gateways[nodeId].conditions[id].name
                        } else {
                            name = this.variableList[item].name
                        }
                        return { id, name }
                    })
                    return { title: group.name, key, data }
                })
            }
        },
        methods: {
            // 引用详情点击
            onCitedNodeClick (group, id) {
                this.$emit('onCitedNodeClick', { group, id })
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.variable-cited-wrap {
    position: relative;
    margin: 10px 30px;
    padding: 0 16px 16px;
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
}
.group-title {
    margin: 16px 0 4px;
}
.variable-cited-list {
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
