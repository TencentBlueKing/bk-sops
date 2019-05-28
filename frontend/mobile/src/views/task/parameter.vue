/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="page-view">
        <!-- 输入参数 -->
        <section class="bk-block">
            <VueJsonPretty :data="parameters" class="parameter-info" />
        </section>
    </div>
</template>
<script>
    import VueJsonPretty from 'vue-json-pretty'
    import { mapActions } from 'vuex'

    export default {
        name: 'task_node_parameter',
        components: {
            VueJsonPretty
        },
        // props: { taskId: String, parameters: Object },
        data () {
            return {
                parameters: {}
            }
        },
        mounted () {
            this.loadData()
        },
        methods: {
            ...mapActions('task', [
                'getTask'
            ]),

            loadData () {
                this.parameters = JSON.parse(this.$route.params.parameters)
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '../../../static/style/app.scss';
    .parameter-info{
        background: #313238;
        min-height: calc(100vh - 60px);
        color: $white;
        font-size: $fs-14;
        padding: 15px 25px;
    }
</style>
