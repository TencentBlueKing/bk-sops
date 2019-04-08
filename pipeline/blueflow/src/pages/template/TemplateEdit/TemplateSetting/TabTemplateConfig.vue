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
    <div class="config-wrapper" v-bkloading="{isLoading: businessInfoLoading, opacity: 1}">
        <div class="config-title">
            <span>{{i18n.basic_information}}</span>
        </div>
        <div class="common-form-item">
            <label>{{ i18n.type }}</label>
            <div class="common-form-content">
                <bk-selector
                    :list="taskCategories"
                    :selected.sync="category"
                    @item-selected="onChangeTaskCategories">
                </bk-selector>
                <span v-show="!isTemplateConfigValid" class="common-error-tip error-msg">{{ i18n.categoryTip}}</span>
            </div>
        </div>
        <div class="common-form-item">
            <label> {{i18n.notify_type}} </label>
            <div class="common-form-content">
                <el-checkbox-group v-model="notifyType">
                    <el-checkbox v-for="item in notifyTypeList" :key="item.id" :label="item.id">{{item.name}}</el-checkbox>
                </el-checkbox-group>
            </div>
        </div>
        <div class="common-form-item hide">
            <label>{{ i18n.timeout }}</label>
            <div class="common-form-content">
                <BaseInput :value="timeout" @input="onChangeTimeout"/>
            </div>
        </div>
        <div class="common-form-item">
            <label>{{ i18n.receiver_group }}</label>
            <div class="common-form-content">
                <el-checkbox-group v-model="receiverGroup">
                    <el-checkbox v-for="item in notifyGroup" :key="item.id" :label="item.id">{{item.name}}</el-checkbox>
                </el-checkbox-group>
            </div>
        </div>
    </div>
</template>

<script>
import '@/utils/i18n.js'
import { mapState, mapMutations } from 'vuex'
import BaseInput from '@/components/common/base/BaseInput.vue'
export default {
    name: 'TabTemplateConfig',
    components: {
        BaseInput
    },
    props: ['businessInfoLoading', 'isTemplateConfigValid'],
    data () {
        return {
            i18n: {
                basic_information: gettext('基础信息'),
                type: gettext('分类'),
                notify_type: gettext('通知方式'),
                timeout: gettext('超时时间(分钟)'),
                receiver_group: gettext('通知分组'),
                categoryTip: gettext('必填项')
            },
            selectedTaskCategory: ''
        }
    },
    computed: {
        ...mapState({
            'businessBaseInfo': state => state.template.businessBaseInfo,
            'timeout': state => state.template.time_out
        }),
        notifyGroup () {
            if (this.businessBaseInfo.notify_group) {
                return this.businessBaseInfo.notify_group.map(item => {
                    return {
                        id: item.value,
                        name: item.text
                    }
                })
            }
            return []
        },
        notifyTypeList () {
            if (this.businessBaseInfo.notify_type_list) {
                return this.businessBaseInfo.notify_type_list.map(item => {
                    return {
                        id: item.value,
                        name: item.name
                    }
                })
            }
            return []
        },
        taskCategories () {
            if (this.businessBaseInfo.task_categories) {
                return this.businessBaseInfo.task_categories.map(item => {
                    return {
                        id: item.value,
                        name: item.name
                    }
                })
            }
            return []
        },
        receiverGroup: {
            get () {
                return this.$store.state.template.notify_receivers.receiver_group
            },
            set (value) {
                this.setReceiversGroup(value)
            }
        },
        notifyType: {
            get () {
                return this.$store.state.template.notify_type
            },
            set (value) {
                this.setNotifyType(value)
            }
        },
        category: {
            get () {
                return this.$store.state.template.category
            },
            set (value) {
                this.setCategory(value)
                this.$emit('onSelectCategory', value)
            }
        }
    },
    methods: {
        ...mapMutations ('template/', [
            'setOutputs',
            'setReceiversGroup',
            'setNotifyType',
            'setOvertime',
            'setCategory'
        ]),
        onChangeTimeout (val) {
            this.setOvertime(val)
        },
        onChangeTaskCategories (id) {
            this.selectedTaskCategory = id
        }
    }
}
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.config-wrapper {
    height: 100%;
    background: none;
    border: none;
    .config-title {
        height: 35px;
        margin: 20px;
        border-bottom: 1px solid #cacecb;
        span {
            font-size: 14px;
            font-weight:600;
            color:#313238;
        }
    }
    .common-form-item {
       margin: 20px
    }
    .common-form-item > label {
        width: 70px;
        font-weight: normal;
    }
    .common-form-content {
        line-height: 32px;
        .base-input {
            height: 32px;
            line-height: 32px;
        }
    }
    .el-checkbox {
        min-width: 96px;
        margin-left: 0px;
        margin-right: 30px;
    }
    /deep/ .el-checkbox__input.is-checked + .el-checkbox__label {
        color: $greyDefault;
    }
    .bk-selector-input {
        height: 32px;
        line-height: 32px;
    }
    .hide {
        display: none;
    }
}
</style>
