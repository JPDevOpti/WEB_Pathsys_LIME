<template>
  <div class="p-6">
    <h1 class="text-xl font-semibold mb-4">Detalle de caso especial</h1>
    <p class="text-gray-600">ID: {{ id }}</p>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
const id = route.params.id as string
</script>


