<template>
    <div class="permisson-apply">
        <div class="apply-content">
            <h3>{{permissionTitle}}</h3>
            <p>{{permissionContent}}</p>
            <div class="operation-btns">
                <bk-button type="primary" @click="goToAuthCenter">{{i18n.apply}}</bk-button>
                <bk-button type="default" v-if="type === 'project'" @click="goToCreateProject">{{i18n.create}}</bk-button>
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
            permission: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                url: '',
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
                'authActions': state => state.authActions,
                'authResource': state => state.authResource,
                'authOperations': state => state.authOperations
            }),
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
            this.loadPermissionUrl()
        },
        methods: {
            ...mapActions([
                'queryUserPermission',
                'getPermissionUrl'
            ]),
            ...mapMutations('project', [
                'setProjectActions'
            ]),
            goToAuthCenter () {
                if (this.urlLoading || !this.url) {
                    return
                }
                window.open(this.url, '__blank')
            },
            goToCreateProject () {
                if (!this.hasPermission(['create'], this.authActions, this.authOperations)) {
                    let actions = []
                    this.authOperations.filter(item => {
                        return ['create'].includes(item.operate_id)
                    }).forEach(perm => {
                        actions = actions.concat(perm.actions)
                    })
                    
                    const { scope_id, scope_name, scope_type, system_id, system_name, resource } = this.authResource
                    const permissions = []
                    
                    actions.forEach(item => {
                        const res = []
                        res.push([{
                            resource_name: gettext('项目'),
                            resource_type: resource.resource_type,
                            resource_type_name: resource.resource_type_name
                        }])
                        permissions.push({
                            scope_id,
                            scope_name,
                            scope_type,
                            system_id,
                            system_name,
                            resource: res,
                            action_id: item.id,
                            action_name: item.name
                        })
                    })

                    this.triggerPermisionModal(permissions)
                } else {
                    this.$router.push('/project/home/')
                }
            },
            async queryProjectCreatePerm () {
                try {
                    const res = await this.queryUserPermission({
                        resource_type: 'project',
                        action_ids: JSON.stringify(['create'])
                    })
                    if (res.data.is_pass) {
                        const actions = this.authActions.slice(0).push('create')
                        this.setProjectActions(actions)
                    }
                } catch (err) {
                    errorHandler(err, this)
                }
            },
            async loadPermissionUrl () {
                try {
                    this.loading = true
                    const res = await this.getPermissionUrl(JSON.stringify(this.permission))
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
