<template>
    <base-title>
        <div class="title-area">
            <span class="title">{{ title }}</span>
            <span
                v-if="num > 0"
                :class="['number', { 'active': showDetail }]"
                @click="toggleDetail">
                {{ num }}
            </span>
            <notify-info
                class="tpl-update-message"
                :show.sync="showDetail"
                :content="content">
                <template class="buttons" v-slot:buttons>
                    <bk-button :text="true" size="small" @click="onViewClick">{{ i18n.view }}</bk-button>
                    <bk-button :text="true" size="small" @click="showDetail = false">{{ i18n.hide }}</bk-button>
                </template>
            </notify-info>
        </div>
    </base-title>
</template>
<script>
    import '@/utils/i18n.js'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import NotifyInfo from '@/components/common/NotifyInfo.vue'

    export default {
        name: 'ListPageTipsTitle',
        components: {
            BaseTitle,
            NotifyInfo
        },
        props: {
            title: {
                type: String,
                required: true
            },
            num: {
                type: Number,
                default: 0
            }
        },
        data () {
            return {
                showDetail: false,
                i18n: {
                    view: gettext('查看需要更新的流程'),
                    hide: gettext('收起')
                }
            }
        },
        computed: {
            content () {
                return gettext('建议及时处理子流程更新，') + gettext('涉及') + this.num + gettext('条流程')
            }
        },
        methods: {
            toggleDetail () {
                this.showDetail = !this.showDetail
            },
            onViewClick () {
                this.$emit('viewClick')
            }
        }
    }
</script>
<style lang="scss" scoped>
    .title {
        margin-left: 12px;
        line-height: 60px;
        font-size: 14px;
        font-weight:600;
        color: #313238;
        &:before {
            content: '';
            position: absolute;
            left: 0;
            top: 21px;
            width: 0;
            height: 20px;
            border-left: 2px solid #a3c5fd;
        }
    }
    .number {
        display: inline-block;
        padding: 0 1px;
        min-width: 18px;
        height: 18px;
        line-height: 18px;
        font-size: 12px;
        border-radius: 9px;
        text-align: center;
        vertical-align: middle;
        color: #ffffff;
        background: #ea3636;
        cursor: pointer;
        transition: background-color .5s;
        &.active {
            background: #979ba5;
        }
    }
    .tpl-update-message {
        margin-bottom: 10px;
    }
</style>
