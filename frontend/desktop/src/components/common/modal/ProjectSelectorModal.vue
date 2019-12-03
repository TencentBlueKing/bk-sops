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
    <bk-dialog
        width="670"
        :title="i18n.new"
        :value="isModalShow"
        :header-position="'left'"
        :ext-cls="'common-dialog'"
        :has-header="false"
        :mask-close="false">
        <div class="select-wrapper">
            <label class="label-project" for="">{{ i18n.select }}</label>
            <project-selector
                :redirect="false">
            </project-selector>
        </div>
        <div slot="footer" class="common-wrapper-btn">
            <div class="bk-button-group">
                <bk-button style="margin-right:10px" theme="primary" @click="newTask">{{ i18n.newTask }}</bk-button>
                <bk-button theme="default" @click="cancel"> {{ i18n.cancel }} </bk-button>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
    import '@/utils/i18n.js'
    import ProjectSelector from '@/components/layout/ProjectSelector.vue'
    import { mapState } from 'vuex'
    export default {
        name: 'ProjectSelectorModal',
        components: {
            ProjectSelector
        },
        data () {
            return {
                i18n: {
                    new: gettext('新建任务'),
                    select: gettext('选择业务：'),
                    newTask: gettext('去新建'),
                    cancel: gettext('取消')
                },
                isModalShow: false,
                route: {}
            }
        },
        computed: {
            ...mapState('project', {
                project_id: state => state.project_id
            })
        },
        methods: {
            show (route) {
                this.isModalShow = true
                this.route = route
            },
            newTask () {
                this.$router.push(this.route)
            },
            cancel () {
                this.route = {}
                this.isModalShow = false
            }
        }
    }
</script>
<style lang="scss" scoped>
@import "@/scss/config.scss";
.select-wrapper {
    padding: 30px;
    overflow: hidden;
    .label-project {
        display: block;
        float: left;
        width: 180px;
        height: 30px;
        line-height: 30px;
        text-align: left;
    }
    /deep/ {
        .project-wrapper {
           margin-top: 0;
           width: 320px;
        }
        .project-select {
            border-color: #c4c6cc;
        }
    }
}
</style>
