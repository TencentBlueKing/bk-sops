<template>
    <div class="permisson-apply">
        <div class="apply-content">
            <div class="lock-img">
                <img :src="lock" alt="permission-lock" />
            </div>
            <h3>{{permissionTitle}}</h3>
            <p>{{$t('你没有相应资源的访问权限，请申请权限或联系管理员授权')}}</p>
            <div class="operation-btns">
                <bk-button
                    theme="primary"
                    :loading="loading"
                    @click="applyBtnClick">
                    {{$t('去申请')}}
                </bk-button>
            </div>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapMutations, mapActions, mapState, mapGetters } from 'vuex'
    import permission from '@/mixins/permission.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import openOtherApp from '@/utils/openOtherApp.js'

    export default {
        name: 'PermissionApply',
        mixins: [permission],
        props: {
            permissionData: {
                type: Object,
                default () {
                    return {
                        type: 'project', // 无权限类型: project、other
                        permission: null
                    }
                }
            }
        },
        data () {
            return {
                url: '',
                loading: false,
                authActions: [],
                lock: require('../../assets/images/lock-radius.svg')
            }
        },
        computed: {
            ...mapState({
                'viewMode': state => state.view_mode
            }),
            ...mapState('project', {
                'projectList': state => state.projectList
            }),
            ...mapGetters('project', [
                'userCanViewProjects'
            ]),
            permissionTitle () {
                return this.permissionData.type === 'project' ? i18n.t('无权限访问项目') : i18n.t('无权限访问')
            }
        },
        watch: {
            'permissionData': {
                deep: true,
                handler (val) {
                    if (val.permission) {
                        this.loadPermissionUrl()
                    }
                }
            }
        },
        created () {
            if (this.permissionData.type === 'project' && this.viewMode !== 'appmaker') {
                this.queryProjectCreatePerm()
            }
            if (this.permissionData.permission) {
                this.loadPermissionUrl()
            }
        },
        methods: {
            ...mapActions([
                'queryUserPermission',
                'getIamUrl'
            ]),
            ...mapMutations('project', [
                'setProjectActions'
            ]),
            applyBtnClick () {
                if (this.permissionData.type === 'project') {
                    const isProjectValid = this.permissionData.permission.length && this.permissionData.permission.every(perm => {
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
                        this.$router.push({ name: 'projectHome' })
                    }
                } else {
                    this.goToAuthCenter()
                }
            },
            goToAuthCenter () {
                if (this.loading || !this.url) {
                    return
                }
                
                openOtherApp(window.BK_IAM_APP_CODE, this.url)
            },
            goToCreateProject () {
                if (!this.hasPermission(['project_create'], this.authActions)) {
                    this.goToApply()
                } else {
                    this.$router.push({ name: 'projectHome' })
                }
            },
            goToApply () {
                this.applyForPermission(['project_create'])
            },
            async queryProjectCreatePerm () {
                try {
                    const res = await this.queryUserPermission({
                        action: 'project_create'
                    })
    
                    if (res.data.is_allow) {
                        this.authActions.push('project_create')
                    }
                } catch (err) {
                    errorHandler(err, this)
                }
            },
            async loadPermissionUrl () {
                try {
                    this.loading = true
                    const res = await this.getIamUrl(this.permissionData.permission)
                    if (res.result) {
                        this.url = res.data.url
                    } else {
                        errorHandler(res, this)
                    }
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
