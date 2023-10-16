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
    margin-top: 6px;
    padding: 0 16px 12px;
    background: #fafbfd;
    border-radius: 2px;
    &::after {
        content: '';
        position: absolute;
        top: -5px;
        right: 54px;
        width: 8px;
        height: 8px;
        background: #fafbfd;
        transform: rotate(-45deg);
        border-radius: 1px;
    }
}
.group-title {
    width: 100%;
    margin: 12px 0 8px;
}
.variable-cited-list {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    .variable-cited-item {
        position: relative;
        height: 20px;
        min-width: 50%;
        display: flex;
        align-items: center;
        padding: 0 18px 0 14px;
        margin-bottom: 4px;
        &::before {
            content: '';
            position: absolute;
            top: 8px;
            left: 0;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #b6b6b6;
        }
        .cited-name {
            cursor: pointer;
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
        }
        &:hover {
            color: #3a84ff;
            &::before {
                background: #3a84ff;
            }
        }
    }
}
</style>
