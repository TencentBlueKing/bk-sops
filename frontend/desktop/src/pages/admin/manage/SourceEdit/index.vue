<template>
    <div class="source-edit" v-bkloading="{ isLoading: loading }">
        <edit-header></edit-header>
        <router-view
            :origin-list="originList"
            :cache-list="cacheList"
            :pending="pending"
            @updateList="updateList"
            @saveSetting="saveSetting">
        </router-view>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import tools from '@/utils/tools.js'
    import EditHeader from './EditHeader.vue'

    export default {
        name: 'SourceEdit',
        components: {
            EditHeader
        },
        data () {
            return {
                emptyData: false,
                isCreating: false,
                originList: [],
                cacheList: [],
                loading: true,
                pending: false
            }
        },
        created () {
            this.loadData()
        },
        methods: {
            ...mapActions('manage', [
                'loadPackageSource',
                'createPackageSource',
                'updatePackageSource'
            ]),
            async loadData () {
                this.loading = true
                try {
                    const data = await this.loadPackageSource()
                    if (!data.objects.length) {
                        this.emptyData = true
                        this.isCreating = true
                    } else {
                        this.transformData(data.objects)
                    }
                } catch (err) {
                    errorHandler(err, this)
                } finally {
                    this.loading = false
                }
            },
            transformData (data) {
                const originList = []
                const cacheList = []
                data.forEach(item => {
                    if (item.category === 'origin') {
                        originList.push(item)
                    } else {
                        cacheList.push(item)
                    }
                })
                this.originList = originList
                this.cacheList = cacheList
            },
            updateList (type, value) {
                const val = tools.deepClone(value)
                if (type === 'originList') {
                    this.originList = val
                } else {
                    this.cacheList = val
                }
            },
            async saveSetting () {
                if (this.pending) {
                    return
                }
                this.pending = true

                const origins = this.originList.map(item => {
                    const { id, name, desc, type, packages, details } = item
                    return {
                        id,
                        name,
                        desc,
                        type,
                        packages,
                        details
                    }
                })
                const data = {
                    origins,
                    caches: this.cacheList
                }

                try {
                    if (this.isCreating) {
                        await this.createPackageSource(data)
                    } else {
                        await this.updatePackageSource(data)
                    }
                    this.$router.push('/admin/manage/source_manage/')
                } catch (err) {
                    errorHandler(err, this)
                } finally {
                    this.pending = false
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .source-edit {
        height: calc(100% - 80px);
    }
</style>
