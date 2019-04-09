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
    ext-cls="error-content-dialog"
    :is-show="isModalShow"
    :title="` `"
    :width="'600'"
    padding="45px"
    :has-header="true"
    :has-footer="false"
    :quick-close="false"
    :close-icon="code !== 401"
    @cancel="onCloseDialog">
        <div slot="content" class="error-content">
            <div class="pic-wrapper">
                <img :src="errorPic" class="error-pic" alt="error-pic">
            </div>
            <ErrorCode401 v-if="code === 401"></ErrorCode401>
            <ErrorCode403 v-if="code === 403"></ErrorCode403>
            <ErrorCode405 v-if="code === 405" :responseText="responseText"></ErrorCode405>
            <ErrorCode406 v-if="code === 406"></ErrorCode406>
            <ErrorCode407 v-if="code === 407"></ErrorCode407>
            <ErrorCode500 v-if="code === 500" :responseText="responseText"></ErrorCode500>
        </div>
    </bk-dialog>
</template>
<script>
import '@/utils/i18n.js'
import ErrorCode401 from './ErrorCode401.vue'
import ErrorCode403 from './ErrorCode403.vue'
import ErrorCode405 from './ErrorCode405.vue'
import ErrorCode406 from './ErrorCode406.vue'
import ErrorCode407 from './ErrorCode407.vue'
import ErrorCode500 from './ErrorCode500.vue'
export default {
    name: 'ErrorCodeModal',
    components: {
        ErrorCode403,
        ErrorCode401,
        ErrorCode405,
        ErrorCode406,
        ErrorCode407,
        ErrorCode500
    },
    data () {
        return {
            isModalShow: false,
            code: '',
            responseText: '',
            expPic401: require('@/assets/images/expre_401.png'),
            expPic403: require('@/assets/images/expre_403.png'),
            expPic500: require('@/assets/images/expre_500.png')
        }
    },
    computed: {
        errorPic () {
            if (this.code === 500) {
                return this.expPic500
            } else if (this.code === 401) {
                return this.expPic401
            }
            return this.expPic403
        }
    },
    methods: {
        show (code, responseText) {
            this.code = code
            this.responseText = responseText
            this.isModalShow = true
        },
        onCloseDialog () {
            this.isModalShow = false
        }
    }
}
</script>
<style lang="scss" scoped>
.error-content-dialog {
    z-index: 1501;
    .error-content {
        padding-bottom: 40px;
        /deep/ .error-title {
            margin: 10px 0;
            font-weight: bold;
        }
        .pic-wrapper {
            text-align: center;
            .error-pic {
                width: 360px;
                height: 168px;
            }
        }

    }
}

</style>

