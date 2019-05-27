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
    <div class="package-edit">
        <div class="source-centent">
            <h3 class="edit-title">step1.{{ i18n.setting + i18n.package }}</h3>
            <package-form></package-form>
            <package-form></package-form>
        </div>
        <div class="operate-area">
            <router-link to="/admin/manage/source_edit/cache_edit/" class="bk-button bk-success">{{ i18n.nextStep }}</router-link>
            <router-link to="/admin/manage/source_manage/" class="bk-button bk-default">{{ i18n.cancel }}</router-link>
        </div>
    </div>
</template>
<script>
    import PackageForm from './PackageForm.vue'

    export default {
        name: 'PackageEdit',
        components: {
            PackageForm
        },
        data () {
            return {
                i18n: {
                    setting: gettext('配置'),
                    package: gettext('主包源'),
                    nextStep: gettext('下一步'),
                    cancel: gettext('取消')
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .package-edit {
        height: calc(100% - 60px);
        background: #ffffff;
    }
    .source-centent {
        padding: 30px 60px 60px;
        min-height: 100%;
    }
    .edit-title {
        margin: 0 0 30px;
        font-size: 20px;
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
        }
    }
</style>
