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
                    {{ hasClicked ? $t('已申请') : $t('去申请') }}
                </bk-button>
            </div>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapMutations, mapActions, mapState } from 'vuex'
    import permission from '@/mixins/permission.js'
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
                hasClicked: false,
                authActions: [],
                lock: require('../../assets/images/lock-radius.svg')
            }
        },
        computed: {
            ...mapState({
                'viewMode': state => state.view_mode
            }),
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
                if (this.loading) {
                    return
                }
                if (this.hasClicked) {
                    window.location.reload()
                } else {
                    this.hasClicked = true
                    let url = this.url
                    if (this.permissionData.type === 'project' & !this.url) {
                        url = window.BK_IAM_SAAS_HOST + '/perm-apply'
                    }
                    openOtherApp(window.BK_IAM_APP_CODE, url)
                }
            },
            async queryProjectCreatePerm () {
                try {
                    const res = await this.queryUserPermission({
                        action: 'project_create'
                    })
    
                    if (res.data.is_allow) {
                        this.authActions.push('project_create')
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            async loadPermissionUrl () {
                try {
                    this.loading = true
                    const res = await this.getIamUrl(this.permissionData.permission)
                    if (res.result) {
                        this.url = res.data.url
                    }
                } catch (e) {
                    console.log(e)
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
