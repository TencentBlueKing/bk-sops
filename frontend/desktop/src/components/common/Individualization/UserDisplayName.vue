<template>
    <div class="user-display-name-container">
        <span v-if="!name">{{ '--' }}</span>
        <bk-user-display-name v-else-if="isMultiTenantMode" :user-id="name" />
        <span v-else>{{ displayName }}</span>
    </div>
</template>
<script>
    import { mapState } from 'vuex'
    export default {
        props: {
            name: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                displayName: this.name
            }
        },
        computed: {
            ...mapState({
                'isMultiTenantMode': state => state.isMultiTenantMode
            })
        },
        watch: {
            name: {
                immediate: true,
                handler (val) {
                    if (val && !this.isMultiTenantMode) {
                        this.displayName = val
                        this.fetchUserDisplayInfo()
                    }
                }
            }
        },
        methods: {
            async fetchUserDisplayInfo () {
                if (!this.name || this.isMultiTenantMode) {
                    return
                }
                try {
                    const resp = await fetch(`${window.BK_USER_WEB_APIGW_URL}/api/v3/open-web/tenant/users/${this.name}/display_info/`, {
                        headers: {
                            'x-bk-tenant-id': window.TENANT_ID
                        },
                        credentials: 'include'
                    })
                    const data = await resp.json()
                    if (data.data && data.data.display_name) {
                        this.displayName = data.data.display_name
                    } else {
                        this.displayName = this.name
                    }
                } catch (error) {
                    console.error(error)
                    this.displayName = this.name
                }
            }
        }
    }
</script>
