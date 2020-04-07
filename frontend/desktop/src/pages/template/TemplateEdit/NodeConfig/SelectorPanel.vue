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
    <div class="selector-panel">
        <div class="search-area">
            <bk-search-select
                class="search-input"
                :data="groupList"
                :show-condition="false"
                :show-popover-tag-change="false"
                v-model="value"
                @change="handleSelectChange">
            </bk-search-select>
        </div>
        <div class="list-wrapper">
            <template v-if="listInPanel.length > 0">
                <!-- 全部插件类表 -->
                <template v-if="value.length === 0">
                    <bk-collapse ext-cls="group-collapse" v-for="group in listInPanel" :key="group.type">
                        <bk-collapse-item :name="group.group_name">
                            <div class="group-header">
                                <img v-if="group.group_icon" class="group-icon-img" :src="group.group_icon" />
                                <i v-else :class="['group-icon-font', getIconCls(group.type)]"></i>
                                <span class="header-title">{{group.group_name}}
                                    <span class="header-atom">
                                        ({{group.list.length}})
                                    </span>
                                </span>
                            </div>
                            <ul slot="content" class="list-item-wrap">
                                <li class="list-item"
                                    v-for="(item, index) in group.list"
                                    :key="index">
                                    <span class="node-name">{{ item.name }}</span>
                                    <span class="opt-btns">
                                        <span v-if="getSelectedStatus(item)" class="opt-item selected">{{ i18n.selected }}</span>
                                        <span v-else class="opt-item" @click="onSelect(item)">{{ i18n.choose }}</span>
                                        <span v-if="isSubflow" class="opt-item" @click.stop="onViewSubflow(item)">{{ i18n.view }}</span>
                                    </span>
                                </li>
                                <div class="node-empty" v-if="group.list.length === 0">
                                    <no-data></no-data>
                                </div>
                            </ul>
                        </bk-collapse-item>
                    </bk-collapse>
                </template>
                <!-- 搜索结果插件列表 -->
                <template v-else>
                    <ul slot="content" class="list-item-wrap">
                        <li class="list-item"
                            v-for="(item, index) in searchResult"
                            :key="index">
                            <span class="node-name">{{ item.name }}</span>
                            <span class="opt-btns">
                                <span v-if="getSelectedStatus(item)" class="opt-item selected">{{ i18n.selected }}</span>
                                <span v-else class="opt-item" @click.stop="onSelect(item)">{{ i18n.choose }}</span>
                                <span v-if="isSubflow" class="opt-item" @click.stop="onViewSubflow(item)">{{ i18n.view }}</span>
                            </span>
                        </li>
                        <div class="node-empty" v-if="searchResult.length === 0">
                            <no-data></no-data>
                        </div>
                    </ul>
                </template>
            </template>
            <no-data v-else></no-data>
        </div>
    </div>
</template>

<script>
    import '@/utils/i18n.js'
    import NoData from '@/components/common/base/NoData.vue'
    import { SYSTEM_GROUP_ICON } from '@/constants/index.js'

    export default {
        name: 'SelectorPanel',
        components: {
            NoData
        },
        props: {
            atomTypeList: {
                type: Object
            },
            isSubflow: {
                type: Boolean,
                default: false
            },
            basicInfo: {
                type: Object
            }
        },
        data () {
            return {
                i18n: {
                    choose: gettext('选择'),
                    selected: gettext('已选'),
                    view: gettext('查看'),
                    placeholder: gettext('请输入名称')
                },
                value: [],
                searchResult: []
            }
        },
        computed: {
            listData () {
                return this.isSubflow ? this.atomTypeList.subflow : this.atomTypeList.tasknode
            },
            listInPanel () {
                return this.value.length === 0 ? this.listData : this.searchResult
            },
            groupList () {
                if (this.value.length > 0 && this.value.some(item => item.values && item.values.length > 0)) {
                    return []
                }
                const list = [{
                    name: gettext('分组'),
                    id: 'group',
                    children: []
                }]
                this.listData.forEach(item => {
                    list[0].children.push({
                        name: item.group_name,
                        id: item.type
                    })
                })
                return list
            }
        },
        methods: {
            handleSelectChange (val) {
                if (val.length === 0) {
                    return
                }

                let searchStr = ''
                let group = []
                let list = this.listData
                const result = []
                val.forEach(item => {
                    if (item.values && item.values.length > 0) {
                        group = item.values.map(v => v.id)
                    } else {
                        searchStr += item.id
                    }
                })

                if (group.length > 0) {
                    list = this.listData.filter(item => group.includes(item.type))
                }
                list.forEach(group => {
                    if (group.list.length > 0) {
                        group.list.forEach(item => {
                            if (item.name.indexOf(searchStr) > -1) {
                                result.push(item)
                            }
                        })
                    }
                })
                this.searchResult = result
            },
            getIconCls (type) {
                const systemType = SYSTEM_GROUP_ICON.find(item => new RegExp(item).test(type))
                if (this.activeNodeListType === 'subflow') {
                    return 'common-icon-subflow-mark'
                }
                if (systemType) {
                    return `common-icon-sys-${systemType.toLowerCase()}`
                }
                return 'common-icon-sys-default'
            },
            /**
             * 选择插件/子流程
             */
            onSelect (val) {
                this.$emit('select', val)
            },
            /**
             * 插件/子流程选中状态
             */
            getSelectedStatus (item) {
                if (this.isSubflow) {
                    return item.id === this.basicInfo.tpl
                }
                return item.code === this.basicInfo.plugin
            },
            // 查看子流程
            onViewSubflow (tpl) {
                const { href } = this.$router.resolve({
                    name: 'templatePanel',
                    params: {
                        type: 'edit',
                        project_id: tpl.project.id
                    },
                    query: {
                        template_id: tpl.id
                    }
                })
                window.open(href, '_blank')
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.selector-panel {
    position: relative;
}
.search-area {
    float: right;
    margin: 16px;
    width: 450px;
}
.list-wrapper {
    clear: both;
    height: calc(100vh - 232px);
    overflow: scroll;
    @include scrollbar;
    .group-collapse {
        /deep/ {
            .bk-collapse-item-header {
                width: 100%;
                background: #fafbfd;
                border-top: 1px solid #e2e4ed;
            }
            .bk-collapse-item-content {
                padding: 0;
            }
        }
    }
}
.group-header {
    height: 42px;
    overflow: hidden;
    .group-icon-font {
        float: left;
        margin-top: 13px;
        font-size: 16px;
        color: #52699d;
        &.common-icon-subflow-mark {
            font-size: 18px;
        }
    }
    .group-icon-img {
        float: left;
        margin-top: 13px;
        width: 16px;
        height: 16px;
    }
    .header-title {
        display: inline-block;
        margin-left: 10px;
        width: 210px;
        font-size: 14px;
        overflow: hidden;
        .header-atom {
            color: #a9b2bd;
            font-size: 12px;
        }
    }
}
.list-item-wrap {
    .list-item {
        clear: both;
        height: 42px;
        line-height: 42px;
        border-top: 1px solid #e2e4ed;
    }
    .node-name {
        margin-left: 38px;
        color: #63656e;
        font-size: 12px;
    }
    .opt-btns {
        float: right;
        margin-right: 30px;
        .opt-item {
            margin-left: 10px;
            color: #3a84ff;
            font-size: 12px;
            cursor: pointer;
            &.selected {
                color: #c4c6cc;
            }
        }
    }
}
</style>
