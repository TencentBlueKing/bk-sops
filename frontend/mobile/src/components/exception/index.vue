/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="bk-exception bk-exception-center" v-show="show">
        <img :src="image">
        <template v-if="$slots.message">
            <slot name="message"></slot>
        </template>
        <template v-else>
            <h2 class="exception-text">{{message}}</h2>
        </template>
    </div>
</template>

<script>
    /**
     *  app-exception
     *  @desc 异常页面
     *  @param type {String} - 异常类型，有：404（找不到）、403（权限不足）、500（服务器问题）、building（建设中）
     *  @param delay {Number} - 延时显示
     *  @param text {String} - 显示的文案，默认：有：404（页面找不到了！）、403（Sorry，您的权限不足）、500（）、building(功能正在建设中···)
     *  @example1 <app-exception type="404"></app-exception>
     */
    import img403 from '@/images/403.png'
    import img404 from '@/images/404.png'
    import img500 from '@/images/500.png'
    import imgBuilding from '@/images/building.png'

    export default {
        name: 'app-exception',
        props: {
            type: {
                type: String,
                default: '404'
            },
            delay: {
                type: Number,
                default: 0
            },
            text: {
                type: String,
                default: ''
            }
        },
        data () {
            let message = ''
            let image = ''

            switch (this.type) {
                case '403':
                    image = img403
                    message = 'Sorry，您的权限不足！'
                    break

                case '404':
                    image = img404
                    message = '页面找不到了！'
                    break

                case '500':
                    image = img500
                    message = '服务器维护中，请稍后重试!'
                    break

                case 'building':
                    image = imgBuilding
                    message = '功能正在建设中···'
                    break
            }

            if (this.text) {
                message = this.text
            }

            return {
                show: false,
                message: message,
                image: image
            }
        },
        created () {
            setTimeout(() => {
                this.show = true
            }, this.delay)
        }
    }
</script>
