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
    <bk-tag-input
        v-model="setValue"
        :list="memberlist"
        :placeholder="placeholder"
        :has-delete-icon="hasDeleteIcon"
        :max-data="maxData"
        :max-result="maxResult"
        save-key="username"
        search-key="username"
        display-key="username"
        @change="change"
        @select="select"
        @remove="remove">
    </bk-tag-input>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapActions, mapMutations } from 'vuex'
    export default {
        name: 'MemberSelect',
        model: {
            prop: 'value',
            event: 'change'
        },
        props: {
            /**
             * type
             * @description
             * all -人员和邮件组
             * user -人员
             * email -邮件组
             */
            type: {
                type: String,
                default: 'user'
            },
            value: {
                type: Array,
                default: () => ([])
            },
            placeholder: {
                type: String,
                default: ''
            },
            disabled: {
                type: Boolean,
                default: false
            },
            hasDeleteIcon: {
                type: Boolean,
                default: true
            },
            maxData: {
                type: Number,
                default: -1
            },
            maxResult: {
                type: Number,
                default: 5
            }
        },
        computed: {
            ...mapState({
                'memberlist': state => state.member.memberlist
            }),
            setValue: {
                get () {
                    return this.value
                },
                set (val) {
                    this.$emit('change', val)
                }
            }
        },
        created () {
            this.initData()
        },
        methods: {
            ...mapActions('member/', [
                'loadMemberList'
            ]),
            ...mapMutations('member/', [
                'setMemberList'
            ]),
            initData () {
                switch (this.type) {
                    case 'email':
                        this.getEmailData()
                        break
                    case 'all':
                        this.getAllData()
                        break
                    default:
                        this.getUserData()
                }
            },
            change (tags) {
                this.$emit('change', tags)
            },
            select (tag) {
                this.$emit('select', tag)
            },
            remove (tag) {
                this.$emit('remove', tag)
            },
            async getUserData () {
                if (this.memberlist && this.memberlist.length === 0) {
                    const result = await this.loadMemberList()
                    this.setMemberList(result.data)
                }
            },
            // 暂未支持邮件组
            getEmailData () {
                
            },
            // 暂未支持邮件组 + 人员列表
            getAllData () {

            }
        }
    }
</script>
