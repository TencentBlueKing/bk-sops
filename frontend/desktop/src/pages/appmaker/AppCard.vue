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
    <div class="card-wrapper">
        <div class="card-basic">
            <div class="logo" @click="onGotoAppMaker">
                <div v-if="isShowDefaultLogo" class="default-logo">
                    <i class="common-icon-blueking"></i>
                </div>
                <div v-else>
                    <img class="logo-pic" :src="appData.logo_url" @error="useDefaultLogo" />
                </div>
            </div>
            <div class="app-name-wrap">
                <a
                    class="app-name"
                    :title="appData.name"
                    @click.self="onGotoAppMaker">
                    {{appData.name}}
                </a>
            </div>
            <div class="card-operation">
                <span
                    class="common-icon-box-pen operate-btn"
                    :title="i18n.modifier"
                    @click.stop="onCardEdit">
                </span>
                <span
                    class="common-icon-black-figure operate-btn"
                    :title="i18n.jurisdiction"
                    @click.stop="onOpenPermissions">
                </span>
                <span
                    class="common-icon-gray-edit operate-btn"
                    @mouseenter="onShowOperation"
                    @mouseleave="onHideOperation">
                </span>
            </div>
            <div
                class="edit-box-wrapper"
                v-if="isShowEdit"
                @mouseenter="onShowOperation"
                @mouseleave="onHideOperation">
                <ul class="edit-box">
                    <li class="executive-record edit-operation">
                        <router-link :to="getExecuteHistoryUrl(appData.template_id)">{{i18n.executive}}</router-link>
                    </li>
                    <li class="edit-delete edit-operation" @click.stop="onCardDelete">{{i18n.delete}}</li>
                </ul>
            </div>
        </div>
        <div class="card-particular">
            <div class="app-detail">
                <div class="app-template">{{i18n.template}}
                    <p>{{appData.template_name}}</p>
                </div>
                <div class="editor-name">{{i18n.editor}}
                    <p>{{appData.editor_name}}</p>
                </div>
                <div class="edit-time">{{i18n.editTime}}
                    <p>{{appData.edit_time}}</p>
                </div>
            </div>
            <div class="app-synopsis">{{i18n.appDesc}}
                <p class="synopsis-content">{{appData.desc || '--'}}</p>
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
                    executive: gettext('执行历史'),
                    modifier: gettext('修改轻应用'),
                    jurisdiction: gettext('使用权限')
                }
            }
        },
        methods: {
            useDefaultLogo () {
                this.isShowDefaultLogo = true
            },
            onShowOperation () {
                this.isShowEdit = true
            },
            onHideOperation () {
                this.isShowEdit = false
            },
            onCardEdit () {
                this.$emit('onCardEdit', this.appData)
            },
            onOpenPermissions (id) {
                this.$emit('onOpenPermissions', this.appData)
            },
            onCardDelete () {
                this.$emit('onCardDelete', this.appData)
            },
            onGotoAppMaker () {
                if (self === top) {
                    window.open(this.appData.link, '_blank')
                } else {
                    window.PAAS_API.open_other_app(this.appData.code, this.appData.link)
                }
            },
            // 查询执行记录
            getExecuteHistoryUrl (id) {
                return `/taskflow/home/${this.cc_id}/?template_id=${id}&create_method=app_maker`
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/multiLineEllipsis.scss';
.card-wrapper {
    position: relative;
    min-width: 345px;
    height: 184px;
    color: #63656e;
    background: $whiteDefault;
    border: 1px solid $commonBorderColor;
    border-radius: 2px;
}
.card-operation {
    position: relative;
    font-size: 24px;
    color: #979ba5;
    text-align: center;
    transform: translateY(130%);
    transition-duration: 0.25s;
    .operate-btn {
        cursor: pointer;
        &:hover {
            color: #63656e;
        }
    }
}
.edit-box-wrapper {
    position: absolute;
    left: 30%;
    top: 140px;
    z-index: 10;
    padding-left: 12px;
    width: 102px;
    cursor: pointer;
}
.card-basic {
    float: left;
    width: 40%;
    height: 100%;
    padding: 20px 15px;
    overflow: hidden;
    border-right: 1px solid $commonBorderColor;
    .logo {
        width: 60px;
        height: 60px;
        margin: 0 auto;
        cursor: pointer;
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
    .app-name-wrap {
        margin: 10px 0;
        height: 40px;
        .app-name {
            display: block;
            font-size: 14px;
            font-weight: bold;
            color: #63656e;
            word-break: break-all;
            cursor: pointer;
            @include multiLineEllipsis(1.2em, 2);
            text-align: center;
            &:hover {
                color: $blueDefault;
            }
        }
    }
    &:hover {
        .card-operation {
            transform: translateY(-10%);
            transition-duration: 0.25s;
            z-index: 1;
        }
    }
}
.edit-box {
        width: 96px;
        height: 84px;
        background: #fff;
        box-shadow: 0px 2px 4px 0px rgba(0,0,0,0.2);
        border-radius: 2px;
        &:hover {
            z-index: 10;
        }
        .edit-operation {
            width: 96px;
            height: 42px;
            color: #fff;
            font-size: 12px;
            font-weight: 400;
            line-height: 42px;
            text-align: center;
            background: #979ba5;
            &:hover {
                background: #63656e;
            }
        }
}
.edit-box>li>a {
    display: block;
    color: #fff;
    height: 42px;
    &:hover {
        background: #63656e;
    }
}
.card-particular {
    float: left;
    width: 60%;
    height: 100%;
    background: #f7f9fa;
    .app-detail {
        padding: 20px;
        font-size: 12px;
        & > p {
            width: 220px;
            color: $greyDark;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }
    }
    .app-template, .editor-name, .edit-time {
        margin-bottom: 10px;
        font-weight: bold;
        p {
            margin-top: 3px;
            font-weight: 400;
        }
    }
    &:hover {
        .app-synopsis {
            display: block;
        }
    }
    .app-synopsis {
        display: none;
        position: absolute;
        bottom: 0px;
        height: 100%;
        width: 60%;
        background: #f7f9fa;
        font-weight: bold;
        font-size: 12px;
        padding: 20px;
        p {
            margin-top: 3px;
            font-weight: 400;
        }
    }
    .synopsis-content {
        height: 130px;
        width: 100%;
        white-space: pre-line;
        word-wrap:break-word;
        overflow-y: auto;
    }
}
</style>
