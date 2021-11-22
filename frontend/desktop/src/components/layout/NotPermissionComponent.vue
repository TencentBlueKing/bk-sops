<template>
    <div class="project-guide-page">
        <div class="guide-item">
            <p class="title">{{ $t('获取权限') }}</p>
            <img class="desc-img" :src="notPermissionUrl" alt="">
            <p>{{ $t('已有业务，但尚未获取资源') }}</p>
            <p>{{ $t('前往权限中心申请相关的业务权限') }}</p>
            <bk-button @click="jumpToOther('bk_iam')">{{ $t('申请业务权限') }}</bk-button>
        </div>
        <div class="guide-item">
            <p class="title">{{ $t('新接入业务') }}</p>
            <img class="desc-img" :src="addBizUrl" alt="">
            <p>{{ $t('还没有接入新的业务') }}</p>
            <p>{{ $t('需要前往配置平台新建业务') }}</p>
            <bk-button @click="jumpToOther('bk_cmdb')">{{ $t('创建新业务') }}</bk-button>
        </div>
    </div>
</template>

<script>
    import openOtherApp from '@/utils/openOtherApp.js'
    export default {
        data () {
            return {
                notPermissionUrl: require('@/assets/images/not-permission.png'),
                addBizUrl: require('@/assets/images/add-biz.png')
            }
        },
        methods: {
            // 这里统一直接用后端提供的 host 跳转
            jumpToOther (name) {
                const code = name === 'bk_iam' ? window.BK_IAM_APP_CODE : name
                const HOST_MAP = {
                    'bk_iam': window.BK_IAM_SAAS_HOST,
                    'bk_cmdb': window.BK_CC_HOST
                }
                openOtherApp(code, HOST_MAP[name])
            }
        }
    }
</script>

<style lang="scss" scoped>
    .project-guide-page {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        background: #f5f7fa;
        .guide-item {
            width: 280px;
            height: 400px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #ffffff;
            border-radius: 2px;
            box-shadow: 0px 2px 4px 0px rgba(25,25,41,0.05);
            p {
                font-size: 12px;
                color: #979ba5;
                line-height: 20px;
            }
            .title {
                font-size: 16px;
                color: #63656e;
                margin-bottom: 12px;
            }
            img {
                width: 180px;
                height: 200px;
                margin-bottom: 8px;
            }
            .bk-button {
                width: 180px;
                margin-top: 20px;
            }
            &:first-child {
                margin-right: 32px;
            }
        }
    }
</style>
