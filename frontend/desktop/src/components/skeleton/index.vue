<template lang="html">
    <div :class="[{ 'ag-loading-content': isLoaderShow, 'loading': localLoading, 'fadeout': !localLoading }]" :style="{ 'min-height': localLoading && height ? height + 'px' : '100%' }">
        <div :class="['loading-loader', { 'hide': !isLoaderShow }]" :style="{ 'background-color': backgroundColor }">
            <template v-if="loader">
                <component
                    :is="loader"
                    :style="{ 'padding-top': `${offsetTop}px`, 'margin-left': `${offsetLeft}px`, 'transform-origin': 'left top' }"
                    :base-width="baseWidth"
                    :content-width="contentWidth">
                </component>
            </template>
            <template v-else>
                <div class="bk-loading" style="position: absolute; z-index: 10; background-color: rgba(255, 255, 255, 0.9);">
                    <div class="bk-loading-wrapper">
                        <div class="bk-loading1 bk-colorful bk-size-large">
                            <div class="point point1"></div>
                            <div class="point point2"></div>
                            <div class="point point3"></div>
                            <div class="point point4"></div>
                        </div>
                    </div>
                </div>
            </template>
        </div>
        <slot></slot>
    </div>
</template>

<script>
    function registerLoaders () {
        const loaderComponents = {}
        const loaderFiles = require.context(
            './loaders/',
            false,
            /\w+\.vue$/
        )
        loaderFiles.keys().forEach(key => {
            const componentConfig = loaderFiles(key)
            const comp = componentConfig.default
            loaderComponents[comp.name] = comp
        })

        return loaderComponents
    }

    export default {
        components: {},
        props: {
            loading: {
                type: Boolean,
                default: true
            },
            loader: {
                type: String
            },
            offsetTop: {
                type: Number,
                default: 0
            },
            offsetLeft: {
                type: Number,
                default: 0
            },
            width: {
                type: Number
            },
            height: {
                type: Number
            },
            delay: {
                type: Number,
                default: 300
            },
            backgroundColor: {
                type: String,
                default: '#f4f7fa'
            }
        },
        data () {
            return {
                localLoading: this.loading,
                isLoaderShow: this.loading,
                baseWidth: 1615,
                contentWidth: 1280
            }
        },
        watch: {
            loading (newVal, oldVal) {
                // true转false时，让loading动画再运行一段时间，防止过快而闪烁
                if (oldVal && !newVal) {
                    setTimeout(() => {
                        this.localLoading = this.loading
                        setTimeout(() => {
                            this.isLoaderShow = this.loading
                        }, 200)
                    }, this.delay)
                } else {
                    this.localLoading = this.loading
                    this.isLoaderShow = this.loading
                }
            }
        },
        mounted () {
            this.initContentWidth()

            window.onresize = () => {
                this.initContentWidth()
            }
        },
        beforeCreate () {
            const loaderComponents = registerLoaders()
            console.log(loaderComponents)
            Object.keys(loaderComponents).forEach(name => {
                this.$options.components[name] = loaderComponents[name]
            })
        },
        methods: {
            initContentWidth () {
                if (this.width) {
                    this.contentWidth = this.width
                } else {
                    const winWidth = window.innerWidth
                    const PADDING_WIDTH = 25
                    const MENU_WIDTH = 60
                    this.contentWidth = winWidth - MENU_WIDTH - PADDING_WIDTH * 2
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    .ag-loading-content {
        position: relative;
        overflow: hidden;

        &.loading {
            * {
                opacity: 0 !important;
            }
        }

        &.fadeout {
            .loading-loader {
                opacity: 0 !important;
            }
        }

        .loading-loader {
            opacity: 1 !important;
            position: absolute;
            width: 100%;
            height: 100%;
            left: 0;
            right: 0;
            top: 0;
            bottom: 0;
            z-index: 100;
            transition: opacity ease 0.5s;

            &.hide {
                z-index: -1;
            }

            svg {
                width: 1615px;
            }

            * {
                opacity: 1 !important;
            }
        }
    }
    .hide {
        display: none;
    }
</style>
