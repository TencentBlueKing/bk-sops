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
    <div class="cache-edit">
        <div class="cache-content">
            <cache-form
                v-for="(item, index) in list"
                :key="index"
                :value="item"
                @updateCache="updateCache"
                @deleteCache="deleteCache">
            </cache-form>
            <div v-if="list.length === 0" class="add-cache" @click="onCreateCache">{{i18n.addCache}}</div>
        </div>
        <div class="operate-area">
            <router-link to="/admin/manage/source_edit/package_edit/" class="bk-button bk-default">{{ i18n.prevStep }}</router-link>
            <bk-button
                theme="success"
                class="save-btn"
                :loading="pending"
                @click="onSaveSetting">
                {{ i18n.save }}
            </bk-button>
            <router-link to="/admin/manage/source_manage/" class="bk-button bk-default">{{ i18n.cancel }}</router-link>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
    import CacheForm from './CacheForm.vue'

    export default {
        name: 'CacheEdit',
        components: {
            CacheForm
        },
        props: {
            cacheList: {
                type: Array,
                default () {
                    return []
                }
            },
            pending: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                list: tools.deepClone(this.cacheList),
                i18n: {
                    prevStep: gettext('上一步'),
                    save: gettext('完成'),
                    cancel: gettext('取消'),
                    addCache: gettext('添加本地缓存')
                }
            }
        },
        computed: {
            isEditing () {
                return this.cacheList.length > 0 && typeof this.cacheList[0].id === 'number'
            }
        },
        watch: {
            cacheList (val) {
                this.list = tools.deepClone(val)
            }
        },
        methods: {
            onCreateCache () {
                this.list.push({
                    id: undefined,
                    name: '',
                    type: 's3',
                    desc: '',
                    details: {
                        access_key: '',
                        bucket: '',
                        secret_key: '',
                        service_address: ''
                    }
                })
            },
            updateCache (value) {
                const val = tools.deepClone(value)
                this.list.splice(0, 1, val)
                this.$emit('updateList', 'cacheList', this.list)
            },
            deleteCache () {
                this.list = []
                this.$emit('updateList', 'cacheList', [])
            },
            onSaveSetting () {
                const packageComps = this.$children.filter(item => item.$options.name === 'CacheForm')
                const packageValidations = packageComps.map(comp => {
                    return comp.validate()
                })
                Promise.all(packageValidations).then(results => {
                    if (results.every(item => item)) {
                        this.$emit('saveSetting')
                    }
                })
            }
        }
    }
</script>
<style lang="scss" scoped>
    .cache-edit {
        height: calc(100% - 40px);
        background: #ffffff;
    }
    .cache-content {
        min-height: 100%;
        padding: 30px 60px 60px;
    }
    .add-cache {
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
        .save-btn {
            width: 140px;
        }
    }
</style>
