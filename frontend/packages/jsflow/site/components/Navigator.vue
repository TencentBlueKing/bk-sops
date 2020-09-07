<template>
    <div class="navigator-wrap">
        <div class="container">
            <h3 class="page-title">JsFlow Vue Component <span class="beta">Beta</span></h3>
            <nav class="nav-item-wrapper">
                <router-link to="/">doc</router-link>
                <router-link to="/demo">demo</router-link>
            </nav>
        </div>
        
    </div>
</template>
<script>
    export default {
        name: 'Navigator'
    }
</script>
<style lang="scss">
    .navigator-wrap {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 40px;
        border-bottom: 1px solid #eee;
        background: #ffffff;
        z-index: 10;
        .container {
            margin: 0 auto;
        }
    }
    .page-title {
        float: left;
        margin: 0;
        padding: 0 20px;
        font-size: 16px;
        height: 40px;
        line-height: 40px;
        .beta {
            vertical-align: super;
            font-size: 12px;
            line-height: 1;
            color: #999;
        }
    }
    .nav-item-wrapper {
        margin-left: 400px;
        height: 40px;
        line-height: 40px;
        & > a {
            margin-right: 40px;
            font-size: 16px;
            color: #808080;
        }
        .router-link-exact-active {
            color: #4da6ff;
        }
    }
</style>



