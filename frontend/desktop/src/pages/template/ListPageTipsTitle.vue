<template>
    <div class="title-area">
        <notify-info
            v-if="num > 0"
            class="tpl-update-message"
            :show.sync="showDetail"
            theme="warning"
            :content="content">
            {{ content }}
            <span class="view-btn" data-test-id="process_form_viewUpdateProcess" @click="onViewClick">{{$t('立即查看')}}</span>
            <template name="buttons" v-slot:buttons>
                <bk-button
                    :text="true"
                    size="small"
                    ext-cls="close-notify-btn"
                    @click="showDetail = false">
                    <i class="common-icon common-icon-close"></i>
                </bk-button>
            </template>
        </notify-info>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import NotifyInfo from '@/components/common/NotifyInfo.vue'

    export default {
        name: 'ListPageTipsTitle',
        components: {
            NotifyInfo
        },
        props: {
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
    .tpl-update-message {
        margin-bottom: 20px;
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
