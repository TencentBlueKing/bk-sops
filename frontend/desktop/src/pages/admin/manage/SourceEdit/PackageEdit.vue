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
    <div class="package-edit">
        <div class="source-centent">
            <template v-for="(item, index) in list">
                <package-form
                    :key="item.id"
                    :source-index="index"
                    :value="item"
                    @updateSource="updateSource"
                    @deleteSource="deleteSource(index)">
                </package-form>
            </template>
            <div class="add-package" @click="onCreateSource">{{i18n.addPackage}}</div>
        </div>
        <div class="operate-area">
            <bk-button
                theme="success"
                class="next-step"
                @click="onNextStepClick">
                {{ i18n.nextStep }}
            </bk-button>
            <router-link to="/admin/manage/source_manage/" class="bk-button bk-default">{{ i18n.cancel }}</router-link>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
    import PackageForm from './PackageForm.vue'

    export default {
        name: 'PackageEdit',
        components: {
            PackageForm
        },
        props: {
            originList: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                list: tools.deepClone(this.originList),
                i18n: {
                    nextStep: gettext('下一步'),
                    cancel: gettext('取消'),
                    addPackage: gettext('添加主包源')
                }
            }
        },
        watch: {
            originList (val) {
                this.list = tools.deepClone(val)
            }
        },
        methods: {
            onCreateSource () {
                this.list.push({
                    id: undefined,
                    name: '',
                    desc: '',
                    type: 'git',
                    packages: {},
                    details: {
                        repo_address: '',
                        repo_raw_address: '',
                        branch: ''
                    }
                })
            },
            onNextStepClick () {
                const packageComps = this.$children.filter(item => item.$options.name === 'PackageForm')
                const packageValidations = packageComps.map(comp => {
                    return comp.validate()
                })
                Promise.all(packageValidations).then(results => {
                    if (results.every(item => item)) {
                        this.$router.push('/admin/manage/source_edit/cache_edit/')
                    }
                })
            },
            deleteSource (index) {
                this.list.splice(index, 1)
                this.$emit('updateList', 'originList', this.list)
            },
            updateSource (key, value, index) {
                const val = tools.deepClone(value)
                const source = tools.deepClone(this.list[index])
                source[key] = val
                this.list.splice(index, 1, source)
                this.$emit('updateList', 'originList', this.list)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .package-edit {
        height: calc(100% - 40px);
        background: #ffffff;
    }
    .source-centent {
        padding: 30px 60px 60px;
        min-height: 100%;
        background: #ffffff;
    }
    .add-package {
        margin-bottom: 60px;
        height: 60px;
        line-height: 60px;
        color: #c4c6cc;
        font-size: 12px;
        text-align: center;
        border: 1px dashed #c4c6cc;
        border-radius: 2px;
        cursor: pointer;
        &:hover {
            color: #3a84ff;
            border-color: #a3c5fd;
        }
    }
    .operate-area {
        margin-top: -60px;
        padding: 0 60px;
        height: 60px;
        line-height: 60px;
        border-top: 1px solid #cacedb;
        .bk-button {
            height: 32px;
            line-height: 32px;
            &:not(:last-child) {
                margin-right: 6px;
            }
        }
        .next-step {
            width: 140px;
        }
    }
</style>
