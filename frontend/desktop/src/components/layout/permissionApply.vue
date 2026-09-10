<template>
    <div class="permisson-apply">
        <div class="apply-content">
            <div class="lock-img">
                <img :src="lock" alt="permission-lock" />
            </div>
            <h3>{{permissionTitle}}</h3>
            <p>{{$t('你没有相应资源的访问权限，请申请权限或联系管理员授权')}}</p>
            <p v-if="errorMessage" class="permission-error">{{errorMessage}}</p>
            <div class="operation-btns">
                <bk-button
                    theme="primary"
                    :loading="loading"
                    :disabled="hasAbnormalReturn"
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
                hasAbnormalReturn: false,
                errorMessage: '',
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
                } else if (/^https?:\/\//.test(this.url)) {
                    this.hasClicked = true
                    window.open(this.url, '_blank', 'noopener')
                } else {
                    this.hasAbnormalReturn = true
                    this.errorMessage = this.$t('权限申请链接无效，请联系管理员')
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
                const permission = this.permissionData.permission
                if (!permission || !Array.isArray(permission.actions) || permission.actions.length === 0) {
                    this.hasAbnormalReturn = true
                    this.errorMessage = this.$t('权限数据无效，请联系管理员')
                    return
                }
                this.hasAbnormalReturn = false
                this.errorMessage = ''
                this.url = ''
                try {
                    this.loading = true
                    const res = await this.getIamUrl(permission)
                    if (res.result && /^https?:\/\//.test(res.data && res.data.url)) {
                        this.url = res.data.url
                    } else {
                        this.hasAbnormalReturn = true
                        this.errorMessage = (res.message || this.$t('获取权限申请链接失败'))
                            + (res.request_id ? ` (trace-id: ${res.request_id})` : '')
                    }
                } catch (e) {
                    this.hasAbnormalReturn = true
                    const traceId = e && e.data && (e.data.request_id || e.data.trace_id)
                    this.errorMessage = this.$t('获取权限申请链接失败')
                        + (traceId ? ` (trace-id: ${traceId})` : '')
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
        .permission-error {
            color: #ea3636;
        }
    }
</style>
