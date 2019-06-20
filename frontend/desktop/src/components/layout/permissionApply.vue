<template>
    <div class="permisson-apply">
        <div class="apply-content">
            <h3>{{permissionTitle}}</h3>
            <p>{{permissionContent}}</p>
            <div class="operation-btns">
                <bk-button type="primary" @click="goToAuthCenter">{{i18n.apply}}</bk-button>
                <bk-button type="default" v-if="type === 'project'">{{i18n.create}}</bk-button>
            </div>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'PermissionApply',
        props: {
            type: { // 权限申请类型
                type: String,
                default: 'project'
            }
        },
        data () {
            return {
                i18n: {
                    resourceTitle: gettext('无权限访问'),
                    projectTitle: gettext('无权限访问项目'),
                    resourceContent: gettext('你没有相应资源的访问权限，请申请权限或联系管理员授权'),
                    projectContent: gettext('你可以申请已有项目的权限，或新建项目'),
                    apply: gettext('去申请'),
                    create: gettext('创建项目')
                }
            }
        },
        computed: {
            permissionTitle () {
                return this.type === 'project' ? this.i18n.projectTitle : this.i18n.resourceTitle
            },
            permissionContent () {
                return this.type === 'project' ? this.i18n.projectContent : this.i18n.resourceContent
            }
        },
        created () {
            if (this.type === 'project') {
                this.queryProjectCreatePerm()
            }
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            goToAuthCenter () {
            },
            async queryProjectCreatePerm () {
                try {
                    await this.queryUserPermission({
                        resource_type: 'project',
                        action_ids: ['create']
                    })
                } catch (err) {
                    errorHandler(err, this)
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .apply-content {
        margin-top: 240px;
        text-align: center;
        & > h3 {
            margin: 0 0 30px;
            color: #313238;
            font-size: 20px;
        }
        & > p {
            margin: 0 0 30px;
            color: #979ba5;
            font-size: 14px;
        }
        .bk-button {
            height: 32px;
            line-height: 30px;
        }
    }
</style>
