/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="dynamic-group">
        <div class="dynamic-group-select">
            <div class="group-wrapper">
                <ip-search-input
                    class="ip-search-wrap"
                    :editable="editable"
                    :placeholder="$t('搜索分组')"
                    @search="onGroupSearch">
                </ip-search-input>
                <div class="group-list">
                    <template v-if="groupList.length > 0">
                        <div :class="['group-item', { 'disabled': !editable }]" v-for="group in groupList" :key="group.id">
                            <bk-checkbox
                                class="group-checkbox"
                                :disabled="!editable"
                                :value="isChecked(group.id)"
                                @change="onGroupSelectChange(group)">
                            </bk-checkbox>
                            <span class="group-name" :title="group.name">{{ group.name }}</span>
                        </div>
                    </template>
                    <no-data v-else></no-data>
                </div>
            </div>
            <div class="selected-group">
                <div class="group-num">{{$t('已选择')}}
                    <span>{{selectedGroups.length}}</span>
                    {{$t('个动态分组')}}
                </div>
                <div class="selected-list">
                    <div
                        :class="['selected-item', { 'disabled': !editable }]"
                        v-for="item in selectedGroups"
                        :key="item.id">
                        {{ item.name }}
                        <i v-if="editable" class="common-icon-dark-circle-close" @click="onGroupSelectChange(item)"></i>
                    </div>
                </div>
            </div>
        </div>
        <span v-show="dataError" class="common-error-tip error-info">{{$t('必填项')}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js' // ip选择器兼容标准运维国际化

    import IpSearchInput from './IpSearchInput.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'DynamicGroup',
        components: {
            IpSearchInput,
            NoData
        },
        props: {
            editable: Boolean,
            dynamicGroupList: Array,
            dynamicGroups: Array
        },
        data () {
            return {
                groupList: this.dynamicGroupList,
                selectedGroups: this.dynamicGroups.slice(0),
                dataError: false
            }
        },
        watch: {
            dynamicGroupList (val) {
                this.groupList = val
            },
            dynamicGroups (val) {
                this.selectedGroups = val.slice(0)
            }
        },
        methods: {
            isChecked (id) {
                return this.selectedGroups.findIndex(item => item.id === id) > -1
            },
            onGroupSearch (keyword) {
                if (keyword) {
                    this.groupList = this.dynamicGroupList.filter(item => item.name.includes(keyword))
                } else {
                    this.groupList = this.dynamicGroupList
                }
            },
            onGroupSelectChange (group) {
                if (!this.editable) return
                const index = this.selectedGroups.findIndex(item => item.id === group.id)
                if (index === -1) {
                    this.selectedGroups.push(group)
                } else {
                    this.selectedGroups.splice(index, 1)
                }
                this.$emit('change', this.selectedGroups.slice(0))
                this.validate()
            },
            validate () {
                if (this.selectedGroups.length > 0) {
                    this.dataError = false
                    return true
                } else {
                    this.dataError = true
                    return false
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
.dynamic-group-select {
    border: 1px solid #ddebe4;
    overflow: hidden;
}
.group-wrapper {
    float: left;
    padding: 8px;
    width: 50%;
    border-right: 1px solid #ddebe4;
    .group-item {
        display: flex;
        align-items: center;
        padding: 0 6px;
        height: 30px;
        line-height: 30px;
        color: #606266;
        &.disabled {
            color: #ccc;
            cursor: not-allowed;
            /deep/.bk-checkbox:hover {
                border-color: #dcdfe6;
            }
        }
    }
    .group-checkbox {
        flex-shrink: 0;
        margin-right: 8px;
        /deep/ .bk-checkbox {
            border: 1px solid #dcdfe6;
            &:hover {
                border-color: #409eff;
            }
        }
    }
    .group-name {
        display: inline-block;
        width: 250px;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }
}
.selected-group {
    float: left;
    padding: 8px 0;
    width: 50%;
    .group-num {
        margin: 8px 0 12px;
        padding: 0 8px;
        font-size: 12px;
        color: #313238;
        & > span {
            color: #3a84ff;
        }
    }
    .selected-item {
        position: relative;
        padding: 0 28px 0 8px;
        line-height: 32px;
        &.disabled {
            color: #ccc;
            cursor: not-allowed;
            i {
                cursor: not-allowed;
                &:hover {
                    color: #dcdee6;
                }
            }
        }
    }
    .common-icon-dark-circle-close {
        position: absolute;
        right: 12px;
        top: 10px;
        font-size: 12px;
        color: #dcdee6;
        cursor: pointer;
        &:hover {
            color: #3a84ff;
        }
    }
}
.ip-search-wrap {
    position: relative;
    margin-bottom: 10px;
    width: 100%;
    /deep/ .search-input {
        width: 100%;
    }
}
.group-list,
.selected-list {
    height: 360px;
    overflow: auto;
    &::-webkit-scrollbar {
        width: 4px;
        height: 4px;
        &-thumb {
            border-radius: 20px;
            background: #a5a5a5;
            box-shadow: inset 0 0 6px hsla(0,0%,80%,.3);
        }
    }
}
</style>
