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
    <div class="error-page">
        <div class="pic-wrapper">
            <img :src="errorPic" class="error-pic" alt="error-pic">
        </div>
        <component :is="errorModal"></component>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import ErrorCode401 from '@/components/common/modal/ErrorCode401.vue'
import ErrorCode403 from '@/components/common/modal/ErrorCode403.vue'
import ErrorCode405 from '@/components/common/modal/ErrorCode405.vue'
import ErrorCode406 from '@/components/common/modal/ErrorCode406.vue'
import ErrorCode500 from '@/components/common/modal/ErrorCode500.vue'
export default {
    name: 'ErrorPage',
    components: {
        ErrorCode401,
        ErrorCode403,
        ErrorCode405,
        ErrorCode406,
        ErrorCode500
    },
    props: ['code'],
    data () {
        return {
            errorModal: `ErrorCode${this.code}`,
            expPic401: require('@/assets/images/expre_401.png'),
            expPic403: require('@/assets/images/expre_403.png'),
            expPic500: require('@/assets/images/expre_500.png')
        }
    },
    computed: {
        errorPic () {
            if (this.code === '500') {
                return this.expPic500
            } else if (this.code === '401') {
                return this.expPic401
            }
            return this.expPic403
        }
    }
}
</script>
<style lang="scss" scoped>
.error-page {
    padding-top: 150px;
    .pic-wrapper {
        text-align: center;
        .error-pic {
            width: 360px;
            height: 168px;
        }
    }
    .content-wrapper {
        /deep/ .error-title {
            margin: 10px 0;
            font-weight: bold;
        }
        margin: 0 auto;
        width: 500px;
    }
}
</style>
