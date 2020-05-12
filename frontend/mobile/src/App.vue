/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="app-container">
        <Navbar></Navbar>
        <router-view></router-view>
    </div>
</template>
<script>
    import { mapGetters } from 'vuex'
    import Navbar from '@/components/navbar/Navbar.vue'

    export default {
        name: 'app',
        components: {
            Navbar
        },
        data () {
            return {
                routerKey: +new Date(),
                systemCls: 'mac'
            }
        },
        computed: {
            ...mapGetters(['mainContentLoading'])
        },
        watch: {
        },
        created () {
            const platform = window.navigator.platform.toLowerCase()
            if (platform.indexOf('win') === 0) {
                this.systemCls = 'win'
            }
        },
        mounted () {
            global.bus.$on('notify', ({ message, result = true }) => {
                this.$notify({
                    message: message,
                    background: result ? '#2fca55' : '#ea3636'
                })
            })
        },
        methods: {
            /**
             * router 跳转
             *
             * @param {string} idx 页面指示
             */
            goPage (idx) {
                this.$router.push({
                    name: idx
                })
            }
        }
    }
</script>

<style lang="scss">
    .app-container {
      font-family: 'PingFang SC', Helvetica, 'STHeiti STXihei', 'Microsoft YaHei', Tohoma, Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      color: #313238;
    }
</style>
