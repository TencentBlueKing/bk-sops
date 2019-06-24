<template>
    <div class="permisson-apply">
        <div class="apply-content">
            <h3>{{permissionTitle}}</h3>
            <p>{{permissionContent}}</p>
            <div class="operation-btns">
                <bk-button
                    type="primary"
                    v-cursor="{
                        active: permissionData.toProject && !hasProjectPermission
                    }"
                    :class="{
                        'btn-permission-disable': !hasProjectPermission
                    }"
                    @click="applyBtnClick">
                    {{i18n.apply}}
                </bk-button>
                <bk-button
                    type="default"
                    v-if="type === 'project'"
                    v-cursor="{ active: !hasProjectPermission }"
                    :class="{
                        'btn-permission-disable': !hasProjectPermission
                    }"
                    @click="goToCreateProject">
                    {{i18n.create}}
                </bk-button>
            </div>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapMutations, mapActions, mapState } from 'vuex'
    import permission from '@/mixins/permission.js'
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'PermissionApply',
        mixins: [permission],
        props: {
            type: { // 权限申请类型
                type: String,
                default: 'project'
            },
            permissionData: {
                type: Object,
                default () {
                    return {
                        type: 'project', // 无权限类型: project、other
                        permission: [],
                        toProject: false
                    }
                }
            }
        },
        data () {
            return {
                url: '',
                authActions: [],
                i18n: {
                    resourceTitle: gettext('无权限访问'),
                    projectTitle: gettext('无权限访问项目'),
                    resourceContent: gettext('你没有相应资源的访问权限，请申请权限或联系管理员授权'),
                    projectContent: gettext('你可以申请已有项目的权限，或新建项目'),
                    apply: gettext('去申请'),
                    create: gettext('新建项目')
                }
            }
        },
        computed: {
            ...mapState('project', {
                'authResource': state => state.authResource,
                'authOperations': state => state.authOperations
            }),
            permissionTitle () {
                return this.permissionData.type === 'project' ? this.i18n.projectTitle : this.i18n.resourceTitle
            },
            permissionContent () {
                return this.permissionData.type === 'project' ? this.i18n.projectContent : this.i18n.resourceContent
            },
            hasProjectPermission () {
                return this.hasPermission(['create'], this.authActions, this.authOperations)
            }
        },
        created () {
            if (this.permissionData.type === 'project') {
                this.queryProjectCreatePerm()
            }
            if (!this.toProject) {
                this.loadPermissionUrl()
            }
        },
        methods: {
            ...mapActions([
                'queryUserPermission',
                'getPermissionUrl'
            ]),
            ...mapMutations('project', [
                'setProjectActions'
            ]),
            applyBtnClick () {
                if (this.permissionData.toProject) {
                    if (!this.hasPermission(['create'], this.authActions, this.authOperations)) {
                        this.goToApply()
                    } else {
                        this.$router.push('/project/home/')
                    }
                } else {
                    this.goToAuthCenter()
                }
            },
            goToAuthCenter () {
                if (this.urlLoading || !this.url) {
                    return
                }
                window.open(this.url, '__blank')
            },
            goToCreateProject () {
                if (!this.hasPermission(['create'], this.authActions, this.authOperations)) {
                    this.goToApply()
                } else {
                    this.$router.push('/project/home/')
                }
            },
            goToApply () {
                const resourceData = {
                    name: gettext('项目'),
                    auth_actions: this.authActions
                }
                this.applyForPermission(['create'], resourceData, this.authOperations, this.authResource)
            },
            async queryProjectCreatePerm () {
                try {
                    const res = await this.queryUserPermission({
                        resource_type: 'project',
                        action_ids: JSON.stringify(['create'])
                    })
    
                    const hasCreatePerm = !!res.data.details.find(item => {
                        return item.action_id === 'create' && item.is_pass
                    })
                    if (hasCreatePerm) {
                        this.authActions.push('create')
                    }
                } catch (err) {
                    errorHandler(err, this)
                }
            },
            async loadPermissionUrl () {
                try {
                    this.loading = true
                    const res = await this.getPermissionUrl(JSON.stringify(this.permissionData.permission))
                    this.url = res.data.url
                } catch (err) {
                    errorHandler(err, this)
                } finally {
                    this.loading = false
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
