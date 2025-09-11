<!--
  Componente HeaderLogo
  Muestra el logo de la aplicación en el encabezado.
  Permite navegar a la página de inicio.
  Incluye soporte para tema oscuro y responsive.
-->
<template>
  <router-link to="/" class="lg:hidden">
    <img :src="logo" alt="Logo" width="150" height="40" />
  </router-link>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import logo from '@/assets/images/Logo-LIME-NoFondo.png'
</script>