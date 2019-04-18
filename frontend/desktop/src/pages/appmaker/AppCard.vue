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
        <div class="card-left" @click="onGotoAppMaker">
            <div class="logo">
                <div v-if="isShowDefaultLogo" class="default-logo">
                    <i class="common-icon-blueking"></i>
                </div>
                <div v-else>
                    <img class="logo-pic" :src="appData.logo_url" @error="useDefaultLogo" />
                </div>
            </div>
            <a
                class="app-name"
                :title="appData.name">
                {{appData.name}}
            </a>
            <div class="card-operation">
                <span class="common-icon-box-pen operate-btn" :title="i18n.modifier" @click.stop="onCardEdit"></span>
                <span class="common-icon-black-figure operate-btn" :title="i18n.jurisdiction" @click.stop="onJurisdiction"></span>
                <span class="common-icon-gray-edit operate-btn" @mouseenter="onOperation" @mouseleave.stop="onWithdraw" @click.stop=""></span>
            </div>
            <div class="edit-box-background" v-if="isShowEdit" @mouseenter="onOperation" @mouseleave="onWithdraw">
                <ul class="edit-box">
                    <li class="executive-record edit-operation" @click.stop="">
                        <router-link :to="getExecuteHistoryUrl(appData.template_id)">{{i18n.executive}}</router-link>
                    </li>
                    <li class="edit-delete edit-operation" @click.stop="onCardDelete">{{i18n.delete}}</li>
                </ul>
            </div>
        </div>
        <div class="card-right">
            <div class="app-detail">
                <div class="app-template" v-if="appData.template_name" :title="appData.template_name">{{i18n.template}}
                    <p>{{appData.template_name}}</p>
                </div>
                <div class="editor-name" v-if="appData.editor_name" :title="appData.editor_name">{{i18n.editor}}
                    <p>{{appData.editor_name}}</p>
                </div>
                <div class="edit-time" v-if="appData.edit_time" :title="appData.edit_time">{{i18n.editTime}}
                    <p>{{appData.edit_time}}</p>
                </div>
            </div>
            <div class="app-synopsis">{{i18n.appDesc}}
                <p>{{appData.desc || '--'}}</p>
            </div>
        </div>
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
                isShowEdit: false,
                mouseAccess: true,
                i18n: {
                    edit: gettext('编辑'),
                    delete: gettext('删除'),
                    template: gettext('流程模板'),
                    appDesc: gettext('应用简介'),
                    editor: gettext('更新人'),
                    editTime: gettext('更新时间'),
                    executive: gettext('执行记录'),
                    modifier: gettext('修改轻应用'),
                    jurisdiction: gettext('使用权限')
                }
            }
        },
        methods: {
            useDefaultLogo () {
                this.isShowDefaultLogo = true
            },
            onOperation () {
                this.isShowEdit = true
            },
            onWithdraw () {
                this.isShowEdit = false
            },
            onCardEdit () {
                this.$emit('onCardEdit', this.appData)
            },
            onJurisdiction (id) {
                this.$emit('onJurisdiction', this.appData)
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
                } else {
                    window.PAAS_API.open_other_app(this.appData.code, this.appData.link)
                }
            },
            // 查询执行记录
            getExecuteHistoryUrl (id) {
                let url = `/taskflow/home/${this.cc_id}/?template_id=${id}`
                if (this.common || this.common_template) {
                    url += '&common=1'
                }
                return url
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.card-wrapper {
    position: relative;
    width: 345px;
    height: 184px;
    background: $whiteDefault;
    border: 1px solid $commonBorderColor;
    border-radius: 2px;
}
.card-operation{
    font-size: 24px;
    color: #979BA5;
    text-align: center;
    position: relative;
    transform: translateY(130%);
    transition-duration: 0.25s;
    bottom: -40px;
    .operate-btn{
        cursor: pointer;
        &:hover{
            color:#63656E;
        }
    }
}
.edit-box-background{
    width: 102px;
    cursor: pointer;
    position: absolute;
    left: 111px;
    top: 142px;
    z-index: 10;
    padding-left: 6px;
}
.card-left{
    float: left;
    width: 136px;
    height: 100%;
    padding: 20px;
    overflow: hidden;
    border-right: 1px solid $commonBorderColor;
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
    .app-name {
        display: block;
        height: 40px;
        overflow: hidden;
        margin: 10px 0;
        font-size: 14px;
        font-weight: bold;
        color: $greyDefault;
        text-align: center;
        text-overflow: ellipsis;
        cursor: pointer;
        &:hover {
            color: $blueDefault;
        }
    }
    &:hover {
        .card-operation{
            transform: translateY(-130%);
            transition-duration: 0.25s;
            z-index: 1;
        }
    }
}
.edit-box{
        width: 96px;
        height: 84px;
        background: rgba(255,255,255,1);
        box-shadow: 0px 2px 4px 0px rgba(0,0,0,0.2);
        border-radius: 2px;
        &:hover{
            z-index: 10;
        }
        .edit-operation{
            width: 96px;
            height: 42px;
            color: #63656E;
            font-size: 12px;
            font-weight: 400;
            line-height: 42px;
            text-align: center;
            background: rgba(255,255,255,1);
            &:hover{
                color: rgba(58,132,255,1);
                background: rgba(235,244,255,1);
            }
        }
}
.edit-box>li>a {
    color: #63656E;
    display: block;
    height: 42px;
    &:hover{
        color: rgba(58,132,255,1);
        background: rgba(235,244,255,1);
    }
}
.card-right{
    width: 207px;
    height: 100%;
    float: left;
    .app-detail {
        padding: 20px;
        font-size: 12px;
        .app-template,.editor-name,.edit-time{
            margin-bottom: 10px;
            font-weight:bold;
            p{
                margin-top: 3px;
                font-weight: 400;
            }
        }
        & > p {
            width: 220px;
            color: $greyDark;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }
    }
    &:hover{
        .app-synopsis{
            display: block;
        }
    }
    .app-synopsis{
        background: #f7f9fa;
        display: none;
        position: absolute;
        font-weight: bold;
        padding: 20px;
        font-size: 12px;
        height: 100%;
        width: 206px;
        bottom: 0px;
        p{
            margin-top: 3px;
            font-weight: 400;
        }
    }
}
</style>
