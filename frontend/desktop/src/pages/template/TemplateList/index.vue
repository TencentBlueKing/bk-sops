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
    <div class="tpl-list-page">
        <bk-tab
            :active="activeTab"
            type="unborder-card"
            :label-height="42"
            @tab-change="handleTabChange">
            <bk-tab-panel v-bind="{ name: 'processHome', label: $t('项目流程') }">
                <project-tpl-list v-if="activeTab === 'processHome'" :project_id="project_id"></project-tpl-list>
            </bk-tab-panel>
            <bk-tab-panel v-bind="{ name: 'processCommon', label: $t('公共流程') }">
                <common-tpl-list v-if="activeTab === 'processCommon'" :use-mode="true"></common-tpl-list>
            </bk-tab-panel>
        </bk-tab>
    </div>
</template>
<script>
    import ProjectTplList from './projectTplList.vue'
    import CommonTplList from './CommonTplList.vue'

    export default {
        name: 'TplListPage',
        components: {
            ProjectTplList,
            CommonTplList
        },
        props: {
            project_id: [String, Number],
            type: String
        },
        data () {
            return {
                activeTab: this.type || 'processHome'
            }
        },
        watch: {
            type (val) {
                this.activeTab = val || 'processHome'
            }
        },
        methods: {
            // 切换流程tab
            handleTabChange (val) {
                this.$router.push({ name: val, params: { project_id: this.project_id } })
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/mixins/scrollbar.scss';

.tpl-list-page {
    position: absolute;
    top: 51px;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 110;
    height: calc(100% - 52px);
    /deep/ .bk-tab {
        height: 100%;
        .bk-tab-header {
            background: #ffffff;
            box-shadow: 0px 3px 4px 0px rgba(64,112,203,0.06);
        }
        .bk-tab-section {
            padding: 0;
            height: calc(100% - 42px);
            overflow: auto;
            @include scrollbar;
        }
    }
}
</style>
