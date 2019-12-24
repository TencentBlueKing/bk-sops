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
    <div class="home-page">
        <common-used></common-used>
        <my-collection></my-collection>
        <my-dynamic></my-dynamic>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import CommonUsed from './CommonlyUsed.vue'
    import MyCollection from './MyCollection.vue'
    import MyDynamic from './MyDynamic.vue'
    export default {
        name: 'HomePage',
        components: {
            CommonUsed,
            MyCollection,
            MyDynamic
        },
        data () {
            return {
            }
        },
        created () {
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.home-page {
    padding: 0px 60px 0 60px;
    min-width: 1320px;
}
</style>
