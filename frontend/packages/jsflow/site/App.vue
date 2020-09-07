<template>
    <div class="jsflow-site">
      <navigator></navigator>
      <div class="page-content">
        <router-view></router-view>
      </div>
    </div>
</template>
<script>
  import Navigator from './components/Navigator.vue'

  export default {
    name: 'App',
    components: {
      Navigator
    },
    data () {
      return {}
    }
  }
</script>
<style>
  body, html {
    margin: 0;
    height: 100%;
    font-size: 14px;
  }
  * {
    box-sizing: border-box;
  }
  .jsflow-site {
    height: 100%;
  }
  .page-content {
    margin: 0 auto;
    padding-top: 40px;
  }
</style>

