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
    <div class="card-wrapper">
        <div class="card-operation">
            <span class="operate-btn" @click.stop="onCardEdit">{{i18n.edit}}</span>
            <span class="operate-btn" @click.stop="onCardDelete">{{i18n.delete}}</span>
        </div>
        <div class="logo">
            <div v-if="isShowDefaultLogo" class="default-logo">
                <i  class="common-icon-blueking"></i>
            </div>
            <div v-else>
                <img class="logo-pic" :src="appData.logo_url" @error="useDefaultLogo"/>
            </div>
        </div>
        <div class="app-detail">
            <p v-if="appData.template_name" :title="appData.template_name">{{i18n.template}}{{appData.template_name}}</p>
            <p :title="appData.desc">{{i18n.appDesc}}{{appData.desc || '--'}}</p>
        </div>
        <a
            class="app-name"
            :title="appData.name"
            @click="onGotoAppMaker">
            {{appData.name}}
        </a>
    </div>
</template>
<script>
import '@/utils/i18n.js'
export default {
    name: 'AppCard',
    props: ['appData', 'cc_id'],
    data () {
        return {
            isShowDefaultLogo: false,
            i18n: {
                edit: gettext('编辑'),
                delete: gettext('删除'),
                template: gettext('流程模板：'),
                appDesc: gettext('应用简介：')
            }
        }
    },
    methods: {
        useDefaultLogo () {
            this.isShowDefaultLogo = true
        },
        onCardEdit () {
            this.$emit('onCardEdit', this.appData)
        },
        onCardDelete () {
            this.$emit('onCardDelete', this.appData)
        },
        onGotoAppMaker () {
            if (self === top) {
                this.$bkMessage({
                    'message': gettext('外链不支持打开轻应用，请在蓝鲸市场中打开此链接'),
                    'theme': 'warning'
                })
            }
            else {
                window.PAAS_API.open_other_app(this.appData.code, this.appData.link)
            }
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.card-wrapper {
    position: relative;
    padding: 20px 15px 15px;
    width: 285px;
    height: 200px;
    background: $whiteDefault;
    border: 1px solid $commonBorderColor;
    border-radius: 2px;
    &:hover {
        border: 1px solid $blueDefault;
        .card-operation {
            display: inline-block;
        }
    }
}
.card-operation {
    display: none;
    position: absolute;
    top: 15px;
    right: 15px;
    .operate-btn {
        display: inline-block;
        font-size: 14px;
        color: $blueDefault;
        cursor: pointer;
    }
}
.logo {
    width: 60px;
    height: 60px;
    margin: 0 auto;
    .logo-pic {
        width: 60px;
        height: 60px;
        border-radius: 6px;
    }
}
.default-logo {
    width: 100%;
    height: 100%;
    text-align: center;
    border: 1px dashed #1b7cef;
    border-radius: 6px;
    .common-icon-blueking {
        display: inline-block;
        margin-top: 10px;
        color: #1b7cef;
        font-size: 40px;
    }
}
.app-detail {
    display: table-cell;
    padding: 15px;
    width: 255px;
    height: 60px;
    font-size: 14px;
    vertical-align: middle;
    & > p {
        width: 220px;
        color: $greyDark;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
    }
}
.app-name {
    display: block;
    padding: 15px;
    font-size: 14px;
    font-weight: bold;
    color: $greyDefault;
    text-align: center;
    border-top: 1px solid $commonBorderColor;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    cursor: pointer;
    &:hover {
        color: $blueDefault;
    }
}
</style>


