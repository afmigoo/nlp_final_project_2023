<template>
  <v-app :theme="theme">
    <v-app-bar>
      <div class="d-flex justify-center align-center w-100">
        <h1 class="main-header">Dvach paste corpora</h1>
      </div>
    </v-app-bar>
    <v-main>
      <router-view></router-view>
    </v-main>
    <v-footer class="main-footer" border>
      2023. Affenmilchmann & oilgo
    </v-footer>
  </v-app>
</template>

<script>
import { ref } from "vue";

export default {
  name: 'App',
  data: () => ({
    theme: ref('dark')
  }),
}
</script>

<style>
.main-footer {
  max-height: 30px;
}
</style>
