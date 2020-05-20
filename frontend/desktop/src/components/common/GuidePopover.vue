/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="guide-popover">
        <div class="guide-content">
            <div v-if="config.img" class="guide-map" :style="{ height: config.img.height + 'px' }">
                <img class="guide-img" :src="config.img.url" alt="guide-img">
            </div>
            <div class="guide-info">
                <span
                    v-for="(item,index) in config.text"
                    :key="index"
                    :class="item.type">
                    {{ item.val }}
                </span>
            </div>
        </div>
    </div>
</template>
<script>
    export default {
        name: 'GuidePopover',
        props: {
            config: {
                type: Object,
                default: () => ({})
            }
        },
        data () {
            return {
            }
        }
    }
</script>
<style lang="scss" scoped>
.guide-content {
    width: 100%;
    background: #444d62;
    z-index: 999;
    font-size: 12px;
    &::before {
        position: absolute;
    }
    .guide-map {
        width: 100%;
        height: 155px;
        .guide-img {
            width: 100%;
            height: 100%;
        }
    }
    .guide-info {
        width: 100%;
        line-height: 17px;
        padding: 14px 22px 14px 20px;
        .name {
            color: #ffffff;
        }
        .text {
            color: #d2d5dd;
        }
    }
}
</style>
