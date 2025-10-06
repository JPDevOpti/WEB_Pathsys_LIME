<!--
  Componente SearchBar
  Barra de búsqueda en el encabezado.
  Permite buscar casos, pacientes o análisis.
-->
<template>
  <div class="hidden lg:block">
    <form @submit.prevent="handleSearch">
      <div class="relative max-w-[430px]" ref="containerRef">
        <button 
          type="button"
          class="absolute -translate-y-1/2 left-4 top-1/2 hover:text-primary-500 transition-colors duration-200"
        >
          <svg
            class="fill-current"
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M3.04175 9.37363C3.04175 5.87693 5.87711 3.04199 9.37508 3.04199C12.8731 3.04199 15.7084 5.87693 15.7084 9.37363C15.7084 12.8703 12.8731 15.7053 9.37508 15.7053C5.87711 15.7053 3.04175 12.8703 3.04175 9.37363ZM9.37508 1.54199C5.04902 1.54199 1.54175 5.04817 1.54175 9.37363C1.54175 13.6991 5.04902 17.2053 9.37508 17.2053C11.2674 17.2053 13.003 16.5344 14.357 15.4176L17.177 18.238C17.4699 18.5309 17.9448 18.5309 18.2377 18.238C18.5306 17.9451 18.5306 17.4703 18.2377 17.1774L15.418 14.3573C16.5365 13.0033 17.2084 11.2669 17.2084 9.37363C17.2084 5.04817 13.7011 1.54199 9.37508 1.54199Z"
              fill=""
            />
          </svg>
        </button>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar páginas... (Ejemplo: crear caso, firmar resultados)"
          class="h-11 w-full rounded-lg border border-gray-200 bg-white py-2.5 pl-12 pr-3 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 transition-all duration-200"
          @focus="openDropdown()"
          @keydown.down.prevent="moveActive(1)"
          @keydown.up.prevent="moveActive(-1)"
          @keydown.enter.prevent="selectActive()"
          @keydown.esc.prevent="closeDropdown()"
        />

        <!-- Dropdown de sugerencias -->
        <div
          v-if="isOpen && filteredItems.length"
          class="absolute z-[9999] mt-1 w-full rounded-lg border border-gray-200 bg-white shadow-lg overflow-hidden"
          role="listbox"
        >
          <ul class="max-h-72 overflow-auto">
            <li
              v-for="(item, index) in filteredItems"
              :key="item.path"
              :class="[
                'px-3 py-2 text-sm cursor-pointer flex items-center gap-2',
                index === activeIndex ? 'bg-brand-50 text-brand-700' : 'hover:bg-gray-50 text-gray-700'
              ]"
              role="option"
              :aria-selected="index === activeIndex"
              @mousedown.prevent
              @click="navigate(item.path)"
              @mouseenter="activeIndex = index"
            >
              <span class="font-medium">{{ item.title }}</span>
              <span class="ml-auto text-xs text-gray-400">{{ item.path }}</span>
            </li>
          </ul>
        </div>
      </div>
    </form>
  </div>
  
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const searchQuery = ref('')
const router = useRouter()
const isOpen = ref(false)
const activeIndex = ref(0)
const containerRef = ref<HTMLElement | null>(null)

interface QuickNavItem {
  title: string
  path: string
  keywords: string[]
}

// Mapeo de destinos frecuentes (ampliado)
const quickNavItems: QuickNavItem[] = [
  {
    title: 'Nuevo Caso',
    path: '/cases/new',
    keywords: ['nuevo caso', 'crear caso', 'crear', 'nuevo', 'case new', 'crear muestra', 'nueva muestra']
  },
  {
    title: 'Editar Caso',
    path: '/cases/edit',
    keywords: ['editar caso', 'editar', 'modificar caso', 'case edit', 'actualizar caso']
  },
  {
    title: 'Listado de Casos (Actuales)',
    path: '/cases/list',
    keywords: ['listar casos', 'listado de casos', 'casos actuales', 'lista casos', 'current cases', 'bandeja casos']
  },
  {
    title: 'Listado de Casos (Anteriores)',
    path: '/cases/previous',
    keywords: ['casos previos', 'casos anteriores', 'histórico de casos', 'previous cases', 'historial']
  },
  {
    title: 'Dashboard',
    path: '/dashboard',
    keywords: ['dashboard', 'inicio', 'home', 'panel', 'principal']
  },
  {
    title: 'Transcribir Resultados',
    path: '/results/perform',
    keywords: ['resultados', 'transcribir', 'realizar resultados', 'perform results', 'capturar resultados']
  },
  {
    title: 'Firmar Resultados',
    path: '/results/sign',
    keywords: ['firmar', 'firmar resultados', 'sign results', 'firma', 'completar resultados']
  },
  {
    title: 'Mi Perfil',
    path: '/profile/my-profile',
    keywords: ['perfil', 'mi perfil', 'usuario', 'datos usuario']
  },
  {
    title: 'Gestión de Usuarios',
    path: '/profile/users',
    keywords: ['usuarios', 'gestión de usuarios', 'admin usuarios', 'perfiles']
  },
  {
    title: 'Reportes de Oportunidad',
    path: '/statistics/opportunity',
    keywords: ['reportes', 'estadísticas', 'oportunidad', 'kpi', 'tiempos']
  },
  {
    title: 'Reportes de Patólogos',
    path: '/statistics/pathologists',
    keywords: ['reportes', 'estadísticas', 'patólogos', 'producción', 'firma']
  },
  {
    title: 'Reportes de Entidades',
    path: '/statistics/entities',
    keywords: ['reportes', 'estadísticas', 'entidades', 'eps', 'ips']
  },
  {
    title: 'Reportes de Pruebas',
    path: '/statistics/tests',
    keywords: ['reportes', 'estadísticas', 'pruebas', 'exámenes']
  },
  {
    title: 'Iniciar Sesión',
    path: '/login',
    keywords: ['login', 'iniciar sesión', 'autenticación', 'entrar']
  },
]

function normalize(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

const normalizedQuery = computed(() => normalize(searchQuery.value))

function scoreItem(item: QuickNavItem, q: string): number {
  if (!q) return 0
  const haystack = normalize(`${item.title} ${item.keywords.join(' ')} ${item.path}`)
  const tokens = q.split(' ').filter(Boolean)
  let score = 0
  for (const t of tokens) {
    if (haystack.startsWith(t)) score += 5
    if (haystack.includes(` ${t}`)) score += 3
    if (haystack.includes(t)) score += 2
  }
  if (normalize(item.title).includes(q)) score += 3
  return score
}

const filteredItems = computed(() => {
  const q = normalizedQuery.value
  const items = quickNavItems
    .map(it => ({ it, s: scoreItem(it, q) }))
    .filter(x => (q ? x.s > 0 : true))
    .sort((a, b) => b.s - a.s || a.it.title.length - b.it.title.length)
    .slice(0, 8)
    .map(x => x.it)
  return items
})

function openDropdown() {
  isOpen.value = true
  activeIndex.value = 0
}

function closeDropdown() {
  isOpen.value = false
}

function moveActive(delta: number) {
  if (!isOpen.value) openDropdown()
  const total = filteredItems.value.length
  if (!total) return
  activeIndex.value = (activeIndex.value + delta + total) % total
}

function selectActive() {
  if (!filteredItems.value.length) return
  navigate(filteredItems.value[activeIndex.value].path)
}

function navigate(path: string) {
  closeDropdown()
  router.push(path)
}

// Cerrar al hacer click fuera
function onDocumentClick(e: MouseEvent) {
  const el = containerRef.value
  if (!el) return
  if (!el.contains(e.target as Node)) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', onDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', onDocumentClick)
})

const handleSearch = () => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return

  // Coincidencia por palabra clave
  const direct = quickNavItems.find(item =>
    item.keywords.some(k => q.includes(k)) || item.title.toLowerCase().includes(q)
  )

  if (direct) {
    router.push(direct.path)
    return
  }

  // Heurística básica por términos sueltos
  if (q.includes('crear') || q.includes('nuevo')) return router.push('/cases/new')
  if (q.includes('editar')) return router.push('/cases/edit')
  if (q.includes('listar') || q.includes('listado') || q.includes('lista')) return router.push('/cases/list')
  if (q.includes('prev')) return router.push('/cases/previous')
  if (q.includes('dashboard') || q.includes('inicio') || q.includes('home')) return router.push('/dashboard')
  if (q.includes('firmar')) return router.push('/results/sign')
  if (q.includes('result')) return router.push('/results/perform')
  if (q.includes('perfil')) return router.push('/profile')

  // Si no hay match, mantener comportamiento actual
  if (filteredItems.value.length === 0) {
    // showNoResults.value = true // This line was removed from the original file, so it's removed here.
  }
}
</script>