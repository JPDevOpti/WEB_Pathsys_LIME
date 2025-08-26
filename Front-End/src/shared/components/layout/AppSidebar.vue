<!--
  AppSidebar Component
  Barra lateral de navegación principal.
  Incluye logo, menú de navegación y submenús.
-->
<template>
  <aside
    :class="[
      'fixed mt-16 flex flex-col lg:mt-0 top-0 px-0 left-0 bg-white text-gray-900 h-screen transition-all duration-500 ease-in-out z-99999 border-r border-gray-200',
      isExpanded || isMobileOpen || isHovered ? 'w-[290px] px-5' : 'w-[90px] px-2',
      isExpanded || isMobileOpen || isHovered ? 'sidebar-expanded' : 'sidebar-collapsed',
      'transition-[width,padding] duration-500 ease-in-out',
      // Hide on mobile unless open
      isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
    ]"
    @mouseenter="!isExpanded && !isMobileOpen && setIsHovered(true)"
    @mouseleave="setIsHovered(false)"
  >
    <div
      :class="[
        'py-8 flex transition-all duration-500',
        !isExpanded && !isHovered ? 'justify-center' : 'justify-start',
      ]"
    >
      <router-link to="/">
        <img
          v-if="isExpanded || isHovered || isMobileOpen"
          class="transition-all duration-500 ml-6"
          :src="logoExpanded"
          alt="Logo"
          width="150"
          height="40"
        />
        <img
          v-else
          class="transition-all duration-500"
          :src="logoCollapsed"
          alt="Logo"
          width="32"
          height="32"
        />
      </router-link>
    </div>
    <div
      class="flex flex-col overflow-y-auto duration-500 ease-in-out no-scrollbar"
    >
      <nav class="mb-6">
        <div class="flex flex-col gap-4">
          <div v-for="(menuGroup, groupIndex) in menuGroups" :key="groupIndex">
            <h2
              :class="[
                'mb-4 text-xs uppercase flex leading-[30px] text-gray-500 transition-all duration-500',
                !isExpanded && !isHovered ? 'justify-center' : 'justify-start',
                !isExpanded && !isHovered ? 'opacity-0 w-0' : 'opacity-100 w-auto',
              ]"
              style="overflow: hidden;"
            >
              <template v-if="isExpanded || isHovered || isMobileOpen">
                {{ menuGroup.title }}
              </template>
              <HorizontalDots v-else />
            </h2>
            <ul class="flex flex-col gap-4">
              <li v-for="(item, index) in menuGroup.items" :key="item.name">
                <button
                  v-if="item.subItems && canAccessAnySubItem(item.subItems)"
                  @click="toggleSubmenuLocal(groupIndex, index)"
                  :class="[
                    'menu-item group w-full transition-all duration-300 ease-in-out flex items-center',
                    !isExpanded && !isHovered ? 'justify-center' : 'justify-start',
                  ]"
                >
                  <span
                    :class="[
                      'transition-colors duration-300 ease-in-out flex items-center justify-center',
                      !isExpanded && !isHovered ? 'mx-auto' : '',
                    ]"
                  >
                    <component :is="item.icon" class="text-2xl" />
                  </span>
                  <span
                    v-if="isExpanded || isHovered || isMobileOpen"
                    class="menu-item-text transition-all duration-500 ml-1"
                    :style="{ opacity: isExpanded || isHovered || isMobileOpen ? 1 : 0, width: isExpanded || isHovered || isMobileOpen ? 'auto' : '0', overflow: 'hidden', transition: 'opacity 0.5s, width 0.5s' }"
                  >{{ item.name }}</span>
                  <ChevronDownIcon
                    v-if="isExpanded || isHovered || isMobileOpen"
                    :class="[
                      'ml-auto w-5 h-5 transition-transform duration-300 ease-in-out',
                      isSubmenuOpen(groupIndex, index)
                        ? 'rotate-180 text-brand-700'
                        : ''
                    ]"
                  />
                </button>
                <span
                  v-else-if="item.subItems && !canAccessAnySubItem(item.subItems)"
                  :class="[
                    'menu-item group w-full transition-all duration-300 ease-in-out flex items-center cursor-not-allowed opacity-50',
                    !isExpanded && !isHovered ? 'justify-center' : 'justify-start',
                  ]"
                  :title="`No tienes permisos para acceder a ${item.name}`"
                >
                  <span
                    :class="[
                      'transition-colors duration-300 ease-in-out flex items-center justify-center',
                      !isExpanded && !isHovered ? 'mx-auto' : '',
                    ]"
                  >
                    <component :is="item.icon" class="text-2xl" />
                  </span>
                  <span
                    v-if="isExpanded || isHovered || isMobileOpen"
                    class="menu-item-text transition-all duration-500 ml-1"
                    :style="{ opacity: isExpanded || isHovered || isMobileOpen ? 1 : 0, width: isExpanded || isHovered || isMobileOpen ? 'auto' : '0', overflow: 'hidden', transition: 'opacity 0.5s, width 0.5s' }"
                  >{{ item.name }}</span>
                  <ChevronDownIcon
                    v-if="isExpanded || isHovered || isMobileOpen"
                    :class="[
                      'ml-auto w-5 h-5 transition-transform duration-300 ease-in-out',
                      isSubmenuOpen(groupIndex, index)
                        ? 'rotate-180 text-brand-700'
                        : ''
                    ]"
                  />
                </span>
                <router-link
                  v-else-if="item.path && canAccessRoute(item.path)"
                  :to="item.path"
                  exact-active-class="router-link-active"
                  active-class=""
                  :class="[
                    'menu-item group transition-all duration-300 ease-in-out flex items-center',
                    !isExpanded && !isHovered ? 'justify-center' : 'justify-start',
                  ]"
                >
                  <span
                    :class="[
                      'transition-colors duration-300 ease-in-out flex items-center justify-center',
                      !isExpanded && !isHovered ? 'mx-auto' : '',
                    ]"
                  >
                    <component :is="item.icon" class="text-2xl" />
                  </span>
                  <span
                    v-if="isExpanded || isHovered || isMobileOpen"
                    class="menu-item-text transition-all duration-500 ml-3"
                    :style="{ opacity: isExpanded || isHovered || isMobileOpen ? 1 : 0, width: isExpanded || isHovered || isMobileOpen ? 'auto' : '0', overflow: 'hidden', transition: 'opacity 0.5s, width 0.5s' }"
                  >{{ item.name }}</span>
                </router-link>
                <span
                  v-else-if="item.path && !canAccessRoute(item.path)"
                  :class="[
                    'menu-item group transition-all duration-300 ease-in-out flex items-center cursor-not-allowed opacity-50',
                    !isExpanded && !isHovered ? 'justify-center' : 'justify-start',
                  ]"
                  :title="`No tienes permisos para acceder a ${item.name}`"
                >
                  <span
                    :class="[
                      'transition-colors duration-300 ease-in-out flex items-center justify-center',
                      !isExpanded && !isHovered ? 'mx-auto' : '',
                    ]"
                  >
                    <component :is="item.icon" class="text-2xl" />
                  </span>
                  <span
                    v-if="isExpanded || isHovered || isMobileOpen"
                    class="menu-item-text transition-all duration-500 ml-3"
                    :style="{ opacity: isExpanded || isHovered || isMobileOpen ? 1 : 0, width: isExpanded || isHovered || isMobileOpen ? 'auto' : '0', overflow: 'hidden', transition: 'opacity 0.5s, width 0.5s' }"
                  >{{ item.name }}</span>
                </span>
                <div
                  v-show="
                    isSubmenuOpen(groupIndex, index) &&
                    (isExpanded || isHovered || isMobileOpen)
                  "
                >
                  <ul class="mt-2 space-y-1 ml-5">
                    <li v-for="subItem in item.subItems" :key="subItem.name">
                      <router-link
                        v-if="canAccessRoute(subItem.path)"
                        :to="subItem.path"
                        exact-active-class="router-link-active"
                        active-class=""
                        class="menu-dropdown-item transition-all duration-300 ease-in-out flex items-center"
                      >
                        <span
                          class="transition-all duration-500 ml-3"
                          :style="{ opacity: isExpanded || isHovered || isMobileOpen ? 1 : 0, width: isExpanded || isHovered || isMobileOpen ? 'auto' : '0', overflow: 'hidden', transition: 'opacity 0.5s, width 0.5s' }"
                        >{{ subItem.name }}</span>
                        <span class="flex items-center gap-1 ml-auto">
                          <span
                            v-if="subItem.new"
                            :class="[
                              'menu-dropdown-badge transition-colors duration-300 ease-in-out',
                              isActive(subItem.path)
                                ? 'menu-dropdown-badge-active'
                                : 'menu-dropdown-badge-inactive'
                            ]"
                          >
                            new
                          </span>
                          <span
                            v-if="subItem.pro"
                            :class="[
                              'menu-dropdown-badge transition-colors duration-300 ease-in-out',
                              isActive(subItem.path)
                                ? 'menu-dropdown-badge-active'
                                : 'menu-dropdown-badge-inactive'
                            ]"
                          >
                            pro
                          </span>
                        </span>
                      </router-link>
                      <span
                        v-else
                        class="menu-dropdown-item transition-all duration-300 ease-in-out flex items-center cursor-not-allowed opacity-50"
                        :title="`No tienes permisos para acceder a ${subItem.name}`"
                      >
                        <span
                          class="transition-all duration-500 ml-3"
                          :style="{ opacity: isExpanded || isHovered || isMobileOpen ? 1 : 0, width: isExpanded || isHovered || isMobileOpen ? 'auto' : '0', overflow: 'hidden', transition: 'opacity 0.5s, width 0.5s' }"
                        >{{ subItem.name }}</span>
                      </span>
                    </li>
                  </ul>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, type Component } from "vue";
import { useRoute } from "vue-router";
import { usePermissions } from "@/shared/composables/usePermissions";
import { useAuthStore } from "@/stores/auth.store";

import {
  GridIcon,
  PieChartIcon,
  ChevronDownIcon,
  HorizontalDots,
  PageIcon,
  TableIcon,
  ListIcon,
  PlugInIcon,
  UserCircleIcon,
} from "@/shared/icons";
import { useSidebar } from "@/shared/composables/SidebarControl";
import logoExpanded from '@/assets/images/Logos/Logo-LIME-NoFondo.png'
import logoCollapsed from '@/assets/images/Logos/LOGO-LIME-Inicial.png'

const route = useRoute();
const { isAdmin, isPatologo, isAuxiliar, isResidente } = usePermissions();

const { isExpanded, isMobileOpen, isHovered, openSubmenu, setIsHovered, toggleSubmenu } = useSidebar();



// Función para verificar si el usuario puede acceder a una ruta (solo control visual)
const canAccessRoute = (path: string): boolean => {
  // Administradores pueden acceder a todo
  if (isAdmin.value) return true;
  
  // Patólogos: solo dashboard, listado de casos, resultados y mi perfil
  if (isPatologo.value) {
    // Bloquear submenús específicos
    if (path.includes('/users')) return false; // Gestión de usuarios
    if (path.includes('/cases/new') || path.includes('/cases/edit')) return false; // Nuevo/Editar caso
    if (path.startsWith('/statistics/')) return false; // Todos los submenús de estadísticas
    
    // Permitir solo ciertas rutas
    const result = path.startsWith('/dashboard') || 
                   path.startsWith('/cases/current') || 
                   path.startsWith('/cases/previous') || 
                   path.startsWith('/results/sign') || 
                   path === '/profile';
    return result;
  }
  
  // Auxiliares: todo clickeable excepto firmar resultados y gestión de usuarios
  if (isAuxiliar.value) {
    // Bloquear submenús específicos
    if (path.includes('/users')) return false; // Gestión de usuarios
    if (path.startsWith('/results/sign')) return false; // Firmar resultados
    
    // Permitir todo lo demás
    return true;
  }
  
  // Residentes: igual que patólogos pero pueden realizar resultados (no firmar)
  if (isResidente.value) {
    // Bloquear submenús específicos
    if (path.includes('/users')) return false; // Gestión de usuarios
    if (path.includes('/cases/new') || path.includes('/cases/edit')) return false; // Nuevo/Editar caso
    if (path.startsWith('/statistics/')) return false; // Todos los submenús de estadísticas
    if (path.startsWith('/results/sign')) return false; // Firmar resultados
    
    // Permitir solo ciertas rutas
    const result = path.startsWith('/dashboard') || 
                   path.startsWith('/cases/current') || 
                   path.startsWith('/cases/previous') || 
                   path.startsWith('/results/perform') || 
                   path === '/profile';
    return result;
  }
  
  // Por defecto, permitir acceso
  return true;
};

// Función para verificar si el usuario puede acceder a al menos un subitem
const canAccessAnySubItem = (subItems: SubMenuItem[]): boolean => {
  // Para patólogos, auxiliares y residentes, siempre permitir que los menús principales sean clickeables
  // Los submenús individuales se controlan con canAccessRoute
  if (isPatologo.value || isAuxiliar.value || isResidente.value) return true;
  
  // Para otros roles, verificar si pueden acceder a al menos un subitem
  return subItems.some(subItem => canAccessRoute(subItem.path));
};

interface SubMenuItem {
  name: string;
  path: string;
  pro: boolean;
  new?: boolean;
  alwaysVisible?: boolean;
}

interface MenuItem {
  icon: Component;
  name: string;
  path?: string;
  pro?: boolean;
  subItems?: SubMenuItem[];
  alwaysVisible?: boolean;
}

interface MenuGroup {
  title: string;
  items: MenuItem[];
}

// Computed para filtrar elementos del menú según el rol del usuario
const filteredMenuItems = computed(() => {
  const baseItems = [
    {
      icon: GridIcon,
      name: "Panel principal",
      path: "/dashboard",
      pro: false,
      alwaysVisible: true
    },
    {
      name: "Casos",
      icon: ListIcon,
      subItems: [
        { name: "Nuevo Caso", path: "/cases/new", pro: false, alwaysVisible: true },
        { name: "Editar Caso", path: "/cases/edit", pro: false, alwaysVisible: true },
      ],
      alwaysVisible: true
    },
    {
      name: "Listado de casos",
      icon: TableIcon,
      subItems: [
        { name: "Casos actuales", path: "/cases/current", pro: false, alwaysVisible: true },
      ],
      alwaysVisible: true
    },
    {
      name: "Resultados",
      icon: PageIcon,
      subItems: [
        { name: "Transcribir resultados", path: "/results/perform", pro: false, alwaysVisible: true },
        { name: "Firmar resultados", path: "/results/sign", pro: false, alwaysVisible: true },
      ],
      alwaysVisible: true
    },
    // Estadísticas - SIEMPRE VISIBLE pero no clickeable para patólogos
    {
      icon: PieChartIcon,
      name: "Estadísticas",
      subItems: [
        { name: "Reportes de Oportunidad", path: "/statistics/opportunity", pro: false, alwaysVisible: true },
        { name: "Reportes de Patólogos", path: "/statistics/pathologists", pro: false, alwaysVisible: true },
        { name: "Reportes de Entidades", path: "/statistics/entities", pro: false, alwaysVisible: true },
        { name: "Reportes de Pruebas", path: "/statistics/tests", pro: false, alwaysVisible: true },
      ],
      alwaysVisible: true
    },
    {
      name: "Perfiles",
      icon: UserCircleIcon,
      subItems: [
        { name: "Mi Perfil", path: "/profile", pro: false, alwaysVisible: true },
        { name: "Gestión de Usuarios", path: "/profile/users", pro: false, alwaysVisible: true }
      ],
      alwaysVisible: true
    }
  ];

  return baseItems;
});

const menuGroups = computed<MenuGroup[]>(() => [
  {
    title: "Menú",
    items: filteredMenuItems.value,
  },
]);

const isActive = (path: string): boolean => {
  const normalize = (p: string) => p.replace(/\/+$/,'')
  return normalize(route.path) === normalize(path)
}

const toggleSubmenuLocal = (groupIndex: number, itemIndex: number): void => {
  const key = `${groupIndex}-${itemIndex}`
  const item = menuGroups.value[groupIndex]?.items[itemIndex]
  // Si el item tiene subItems y alguno está activo, no colapsar al hacer click en el propio título
  const hasActiveSub = item?.subItems?.some((sub) => isActive(sub.path))
  if (hasActiveSub) return
  toggleSubmenu(key)
}

const isAnySubmenuRouteActive = computed(() => {
  return menuGroups.value.some((group) =>
    group.items.some(
      (item) =>
        item.subItems && item.subItems.some((subItem) => isActive(subItem.path))
    )
  );
});

const isSubmenuOpen = (groupIndex: number, itemIndex: number): boolean => {
  const key = `${groupIndex}-${itemIndex}`;
  const item = menuGroups.value[groupIndex]?.items[itemIndex];
  return (
    openSubmenu.value === key ||
    (isAnySubmenuRouteActive.value && (item?.subItems?.some((subItem) => isActive(subItem.path)) ?? false))
  );
};
</script>

<style scoped>
/* Sidebar transitions */
.sidebar-transition {
  transition: width 0.3s ease-in-out;
}

.sidebar-expanded {
  transition: width 0.5s, padding 0.5s;
}
.sidebar-collapsed {
  transition: width 0.5s, padding 0.5s;
}
.menu-item-text {
  transition: opacity 0.5s, width 0.5s;
  white-space: nowrap;
}

/* Menu item styles */
.menu-item {
  position: relative;
  display: flex;
  align-items: center;
  padding: 0.75rem;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.5rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: #6B7280;
}

.menu-item:hover {
  background-color: #f3f4f6;
  transform: translateX(4px);
}

.menu-item.router-link-active {
  background-color: #E6FAEC;
  color: #2E7D32;
}

.menu-item:not(.router-link-active) {
  color: #6B7280;
}

/* Submenu styles */
.submenu-enter-active,
.submenu-leave-active {
  transition: all 0.3s ease;
}

.submenu-enter-from,
.submenu-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Animación de deslizamiento y desvanecimiento para submenús */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

/* Mejora del scroll */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Estilos de transición para elementos del menú */
.menu-dropdown-item {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 0.5rem;
  border-radius: 0.375rem;
}

.menu-dropdown-item:hover {
  background-color: #E6FAEC;
  transform: translateX(4px);
}

/* Estilos para items activos e inactivos */
.menu-dropdown-item.router-link-active {
  background-color: #E6FAEC;
  color: #2E7D32;
}

.menu-dropdown-item:not(.router-link-active) {
  color: #6B7280;
}

/* Estilos para elementos no clickeables */
.cursor-not-allowed {
  cursor: not-allowed;
}

.opacity-50 {
  opacity: 0.5;
}

/* Hover para elementos no clickeables */
.cursor-not-allowed:hover {
  background-color: #f3f4f6;
  transform: none;
}

/* Transiciones para íconos y badges */
.menu-item-icon-active,
.menu-item-icon-inactive,
.menu-dropdown-badge {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>