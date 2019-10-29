<template>
    <div class="permisson-apply">
        <div class="apply-content">
            <div class="lock-img">
                <img :src="lock" alt="permission-lock" />
            </div>
            <h3>{{permissionTitle}}</h3>
            <p>{{i18n.resourceContent}}</p>
            <div class="operation-btns">
                <bk-button
                    theme="primary"
                    @click="applyBtnClick">
                    {{i18n.apply}}
                </bk-button>
                <!-- <bk-button
                    theme="default"
                    v-if="permissionData.type === 'project' && viewMode !== 'appmaker'"
                    v-cursor="{ active: !hasProjectPermission }"
                    :class="{
                        'btn-permission-disable': !hasProjectPermission
                    }"
                    @click="goToCreateProject">
                    {{i18n.create}}
                </bk-button> -->
            </div>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapMutations, mapActions, mapState, mapGetters } from 'vuex'
    import permission from '@/mixins/permission.js'
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'PermissionApply',
        mixins: [permission],
        props: {
            permissionData: {
                type: Object,
                default () {
                    return {
                        type: 'project', // 无权限类型: project、other
                        permission: []
                    }
                }
            }
        },
        data () {
            return {
                url: '',
                authActions: [],
                lock: require('../../assets/images/lock-radius.svg'),
                i18n: {
                    resourceTitle: gettext('无权限访问'),
                    projectTitle: gettext('无权限访问项目'),
                    resourceContent: gettext('你没有相应资源的访问权限，请申请权限或联系管理员授权'),
                    // projectContent: gettext('你可以申请已有项目的权限'),
                    apply: gettext('去申请'),
                    create: gettext('新建项目')
                }
            }
        },
        computed: {
            ...mapState({
                'viewMode': state => state.view_mode
            }),
            ...mapState('project', {
                'projectList': state => state.projectList,
                'authResource': state => state.authResource,
                'authOperations': state => state.authOperations
            }),
            ...mapGetters('project', [
                'userCanViewProjects'
            ]),
            permissionTitle () {
                return this.permissionData.type === 'project' ? this.i18n.projectTitle : this.i18n.resourceTitle
            },
            // permissionContent () {
            //     return this.permissionData.type === 'project' ? this.i18n.projectContent : this.i18n.resourceContent
            // },
            hasProjectPermission () {
                return this.hasPermission(['create'], this.authActions, this.authOperations)
            }
        },
        watch: {
            'permissionData': {
                deep: true,
                handler (val) {
                    if (val.permission.length > 0) {
                        this.loadPermissionUrl()
                    }
                }
            }
        },
        created () {
            if (this.permissionData.type === 'project' && this.viewMode !== 'appmaker') {
                this.queryProjectCreatePerm()
            }
            if (this.permissionData.permission.length > 0) {
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
                if (this.permissionData.type === 'project') {
                    const isProjectValid = this.permissionData.permission.every(perm => {
                        return perm.resources.every(resource => {
                            return resource.every(item => {
                                return this.projectList.find(project => {
                                    return project.id === item.resource_id
                                })
                            })
                        })
                    })
                    if (isProjectValid) {
                        this.goToAuthCenter()
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
                
                if (self === top) {
                    window.open(this.url, '__blank')
                } else {
                    window.PAAS_API.open_other_app('bk_iam_app', this.url)
                }
            },
            goToCreateProject () {
                if (!this.hasPermission(['create'], this.authActions, this.authOperations)) {
                    this.goToApply('create')
                } else {
                    this.$router.push('/project/home/')
                }
            },
            goToApply (perm) {
                const resourceData = {
                    name,
                    auth_actions: this.authActions
                }
                this.applyForPermission([perm], resourceData, this.authOperations, this.authResource)
            },
            getResource (permission) {
                return permission.resources.map(res => {
                    return res.map(item => item.resource_name).join(',')
                }).join(',')
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
        position: absolute;
        top: 35%;
        left: 0;
        width: 100%;
        text-align: center;
        .lock-img {
            margin: 0 auto 20px;
            width: 56px;
            height: 58px;
            box-shadow: 0 8px 3px -5px rgba(90, 90, 90, 0.7);
        }
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
