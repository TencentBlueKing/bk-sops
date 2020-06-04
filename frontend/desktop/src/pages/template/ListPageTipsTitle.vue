<template>
    <base-title>
        <div class="title-area">
            <span class="title">{{ title }}</span>
            <notify-info
                v-if="num > 0"
                class="tpl-update-message"
                :show.sync="showDetail"
                theme="warning"
                :content="content">
                {{ content }}
                <span class="view-btn" @click="onViewClick">{{$t('立即查看')}}</span>
                <template name="buttons" v-slot:buttons>
                    <bk-button
                        :text="true"
                        size="small"
                        ext-cls="close-notify-btn"
                        @click="showDetail = false">
                        X
                    </bk-button>
                </template>
            </notify-info>
        </div>
    </base-title>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
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
                showDetail: true
            }
        },
        computed: {
            content () {
                return this.num + i18n.t(' 个流程涉及到子流程的更新，请及时处理。')
            }
        },
        methods: {
            onViewClick () {
                this.$emit('viewClick')
            }
        }
    }
</script>
<style lang="scss" scoped>
    .title {
        margin-left: 12px;
        height: 60px;
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
    .tpl-update-message {
        margin-bottom: 10px;
        .view-btn {
            color: #3a84ff;
            cursor: pointer;
        }
    }
    .close-notify-btn {
        color: #ffd89b;
        &:hover {
            color: #ff9c01;
        }
    }
</style>
