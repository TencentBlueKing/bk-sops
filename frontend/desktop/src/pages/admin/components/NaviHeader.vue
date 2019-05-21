<template>
    <div class="header-wrapper">
        <div class="nav-content clearfix">
            <div class="nav-title">
                <h3>{{title}}</h3>
            </div>
            <div class="router-wrapper">
                <router-link
                    v-for="router in routers"
                    :key="router.name"
                    :class="['router-item', { 'active': $route.name === router.name }]"
                    :to="router.path">
                    {{router.text}}
                </router-link>
            </div>
        </div>
    </div>
</template>
<script>
    export default {
        name: 'NaviHeader',
        props: {
            title: {
                type: String,
                default: 'header title'
            },
            routers: {
                type: Array,
                default () {
                    return []
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .header-wrapper {
        margin-bottom: 20px;
        border-bottom: 1px solid #dde4eb;
    }
    .nav-content {
        .nav-title {
            float: left;
            display: flex;
            align-items: center;
            height: 60px;
            h3 {
                margin: 0 25px 0 0;
                padding: 0 25px 0 10px;
                border-right: 1px solid #c4c6cc;
                border-left: 2px solid #a3c5fd;
                font-size: 14px;
                font-weight: bold;
                color: #313238;
            }
        }
        .router-wrapper {
            float: left;
            .router-item {
                display: inline-block;
                margin-right: 34px;
                height: 60px;
                line-height: 60px;
                font-size: 14px;
                color: #313238;
                cursor: pointer;
                &:hover {
                    color: #3a84ff;
                }
                &.active {
                    color: #3a84ff;
                    border-bottom: 2px solid #3a84ff;
                }
            }
        }
    }
</style>
