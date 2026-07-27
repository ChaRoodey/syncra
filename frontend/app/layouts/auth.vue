<script setup lang="ts">

</script>

<template>
  <div class="auth-layout">
    <slot />
  </div>
</template>


<style scoped>
.auth-layout {
  min-height: 100vh;

  display: flex;
  justify-content: center;
  align-items: center;

  padding: 24px;
}
</style>