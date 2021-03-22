<template>
    <content-loader
        :width="1280"
        :height="600"
        :style="{ 'transform': `scale(${1280 / baseWidth})` }"
        :speed="loadingConf.speed"
        :primary-color="loadingConf.primaryColor"
        :secondary-color="loadingConf.secondaryColor">
        <rect x="0" y="60" rx="0" ry="0" width="120" height="32" />
        <rect x="130" y="60" rx="0" ry="0" width="68" height="32" />
        <rect x="206" y="60" rx="0" ry="0" width="68" height="32" />
        <rect x="0" y="114" rx="0" ry="0" width="1920" height="28" />
        <rect x="0" y="157" rx="0" ry="0" width="1920" height="28" />
        <rect x="0" y="200" rx="0" ry="0" width="1920" height="28" />
        <rect x="0" y="242" rx="0" ry="0" width="1920" height="28" />
        <rect x="0" y="285" rx="0" ry="0" width="1920" height="28" />
        <rect x="0" y="328" rx="0" ry="0" width="1920" height="28" />
        <rect x="0" y="372" rx="0" ry="0" width="1920" height="28" />
        <rect x="0" y="414" rx="0" ry="0" width="1920" height="28" />
        <rect x="0" y="458" rx="0" ry="0" width="1920" height="28" />
    </content-loader>
</template>

<script>
    import { ContentLoader } from 'vue-content-loader'
    export default {
        name: 'home',
        components: {
            ContentLoader
        },
        props: {
            baseWidth: {
                type: Number,
                default: 1613
            },
            contentWidth: {
                type: Number,
                default: 1180
            },
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
