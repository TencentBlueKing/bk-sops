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
        :is-show="isModalShow"
        :width="600"
        :has-header="false"
        :has-footer="false"
        :quick-close="false">
        <div slot="content">
            <div class="login-wrapper">
                <iframe
                    name="login_frame"
                    id="login_frame"
                    width="100%"
                    height="100%"
                    frameborder="0"
                    allowtransparency="yes"
                    :src="src">
                </iframe>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapMutations} from 'vuex'
export default {
    name: 'UserLoginModal',
    data () {
        return {
            isModalShow: false,
            src: ''
        }
    },
    methods: {
        show (src) {
            this.isModalShow = true
            this.src = src
        }
    }
}
</script>
<style lang="scss" scoped>
    .login-wrapper {
        width: 560px;
        height:440px;
    }
</style>

