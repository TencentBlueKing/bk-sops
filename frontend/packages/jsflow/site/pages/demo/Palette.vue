<template>
  <ul>
    <li><div class="entry-item start" data-type="startpoint">start</div></li>
    <li><div class="entry-item end" data-type="endpoint">end</div></li>
    <li><div class="entry-item tasknode" data-type="tasknode">task</div></li>
    <li><div class="entry-item subnode" data-type="subflow">sub</div></li>
  </ul>
</template>
<script>
export default {
  name: 'Palette'
}
</script>
<style lang="scss" scoped>
ul {
  margin: 0;
  padding: 0;
  list-style: none;
  li {
    text-align: center;
  }
  .entry-item {
    display: inline-block;
    margin: 10px 0;
    width: 40px;
    height: 30px;
    line-height: 30px;
    border: 1px solid #cccccc;
    text-align: center;
    user-select: none;
    cursor: move;
    &:hover {
      background: #aaaaaa;
    }
  }
  .start,
  .end {
    width: 40px;
    height: 40px;
    line-height: 40px;
    border-radius: 50%;
    border: 1px solid #cccccc;
    text-align: center;
  }
}
</style>


