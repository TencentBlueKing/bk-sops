<template>
    <content-loader
        :width="1366"
        :height="700"
        :speed="loadingConf.speed"
        :primary-color="loadingConf.primaryColor"
        :secondary-color="loadingConf.secondaryColor">
        <path d="M 20 20 h 128 v 32 H 20 z" />
        <path d="M 857 26 h 80 v 20 h -80 z" />
        <path d="M 984 20 h 360 v 32 H 984 z" />
        <rect x="20" y="72" rx="2" ry="2" width="320" height="184" />
        <rect x="355" y="72" rx="2" ry="2" width="320" height="184" />
        <rect x="690" y="72" rx="2" ry="2" width="320" height="184" />
        <rect x="1024" y="72" rx="2" ry="2" width="320" height="184" />
        <rect x="20" y="276" rx="2" ry="2" width="320" height="184" />
        <rect x="355" y="276" rx="2" ry="2" width="320" height="184" />
        <rect x="690" y="276" rx="2" ry="2" width="320" height="184" />
        <rect x="1024" y="276" rx="2" ry="2" width="320" height="184" />
        <rect x="20" y="480" rx="2" ry="2" width="320" height="184" />
        <rect x="355" y="479" rx="2" ry="2" width="320" height="184" />
        <rect x="690" y="479" rx="2" ry="2" width="320" height="184" />
        <rect x="1024" y="479" rx="2" ry="2" width="320" height="184" />
    </content-loader>
</template>

<script>
    import { ContentLoader } from 'vue-content-loader'
    export default {
        name: 'appmakerList',
        components: {
            ContentLoader
        },
        props: {
            loadingConf: {
                type: Object,
                default () {
                    return {
                        primaryColor: '#ebecf3',
                        secondaryColor: '#f6f7fb'
                    }
                }
            }
        }
    }
</script>
