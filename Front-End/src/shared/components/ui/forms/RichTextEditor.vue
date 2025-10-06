<template>
  <div class="rich-text-editor border border-gray-300 rounded-lg overflow-hidden">
    <!-- Barra de herramientas compacta y responsive -->
    <div class="toolbar bg-gray-50 border-b border-gray-300 px-2 py-1.5 flex flex-wrap gap-1 items-center">
      <!-- Deshacer/Rehacer -->
      <div class="toolbar-group">
        <button @click="execCommand('undo')" type="button" class="toolbar-btn-compact" title="Deshacer">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"/>
          </svg>
        </button>
        <button @click="execCommand('redo')" type="button" class="toolbar-btn-compact" title="Rehacer">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 10H11a8 8 0 00-8 8v2m18-10l-6 6m6-6l-6-6"/>
          </svg>
        </button>
      </div>

      <div class="toolbar-separator-compact"></div>

      <!-- Tipo de letra -->
      <select @change="(e) => handleSelectChange(e, 'fontName')" class="toolbar-select-compact">
        <option value="Arial">Sans Serif</option>
        <option value="Arial">Arial</option>
        <option value="Helvetica">Helvetica</option>
        <option value="Times New Roman">Times</option>
        <option value="Georgia">Georgia</option>
        <option value="Courier New">Courier</option>
        <option value="Verdana">Verdana</option>
      </select>

      <div class="toolbar-separator-compact"></div>

      <!-- Tamaño de letra -->
      <select @change="(e) => handleSelectChange(e, 'fontSize')" class="toolbar-select-compact">
        <option value="1">1</option>
        <option value="2">2</option>
        <option value="3" selected>3</option>
        <option value="4">4</option>
        <option value="5">5</option>
        <option value="6">6</option>
        <option value="7">7</option>
      </select>

      <div class="toolbar-separator-compact"></div>

      <!-- Formato de texto -->
      <div class="toolbar-group">
        <button @click="execCommand('bold')" type="button" class="toolbar-btn-compact font-bold" :class="{ 'bg-blue-100': isActive('bold') }" title="Negrita">
          <span class="text-xs">B</span>
        </button>
        <button @click="execCommand('italic')" type="button" class="toolbar-btn-compact italic" :class="{ 'bg-blue-100': isActive('italic') }" title="Cursiva">
          <span class="text-xs">I</span>
        </button>
        <button @click="execCommand('underline')" type="button" class="toolbar-btn-compact underline" :class="{ 'bg-blue-100': isActive('underline') }" title="Subrayado">
          <span class="text-xs">U</span>
        </button>
        <button @click="execCommand('strikeThrough')" type="button" class="toolbar-btn-compact line-through" :class="{ 'bg-blue-100': isActive('strikeThrough') }" title="Tachado">
          <span class="text-xs">S</span>
        </button>
      </div>

      <div class="toolbar-separator-compact"></div>

      <!-- Alineación -->
      <div class="toolbar-group">
        <button @click="execCommand('justifyLeft')" type="button" class="toolbar-btn-compact" :class="{ 'bg-blue-100': isActive('justifyLeft') }" title="Alinear izquierda">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h10M4 18h16"/>
          </svg>
        </button>
        <button @click="execCommand('justifyCenter')" type="button" class="toolbar-btn-compact" :class="{ 'bg-blue-100': isActive('justifyCenter') }" title="Centrar">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M7 12h10M4 18h16"/>
          </svg>
        </button>
        <button @click="execCommand('justifyRight')" type="button" class="toolbar-btn-compact" :class="{ 'bg-blue-100': isActive('justifyRight') }" title="Alinear derecha">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M10 12h10M4 18h16"/>
          </svg>
        </button>
        <button @click="execCommand('justifyFull')" type="button" class="toolbar-btn-compact" :class="{ 'bg-blue-100': isActive('justifyFull') }" title="Justificar">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
      </div>

      <div class="toolbar-separator-compact"></div>

      <!-- Listas -->
      <div class="toolbar-group">
        <button @click="execCommand('insertUnorderedList')" type="button" class="toolbar-btn-compact" :class="{ 'bg-blue-100': isActive('insertUnorderedList') }" title="Lista sin orden">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
        <button @click="execCommand('insertOrderedList')" type="button" class="toolbar-btn-compact" :class="{ 'bg-blue-100': isActive('insertOrderedList') }" title="Lista ordenada">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
        <button @click="execCommand('indent')" type="button" class="toolbar-btn-compact" title="Aumentar sangría">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
          </svg>
        </button>
        <button @click="execCommand('outdent')" type="button" class="toolbar-btn-compact" title="Disminuir sangría">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
        </button>
      </div>

      <div class="toolbar-separator-compact"></div>

      <!-- Color de texto -->
      <div class="toolbar-group">
        <div class="relative">
          <input 
            type="color" 
            @input="(e) => handleColorChange(e, 'foreColor')" 
            class="toolbar-color-input-compact"
            title="Color de texto"
          />
        </div>
        <div class="relative">
          <input 
            type="color" 
            @input="(e) => handleColorChange(e, 'hiliteColor')" 
            class="toolbar-color-input-compact"
            title="Color de fondo"
          />
        </div>
      </div>

      <div class="toolbar-separator-compact"></div>

      <!-- Limpiar formato -->
      <button @click="execCommand('removeFormat')" type="button" class="toolbar-btn-compact" title="Limpiar formato">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <!-- Área de edición con altura configurable -->
    <div 
      ref="editorRef"
      class="editor-content p-4 overflow-y-auto focus:outline-none"
      :style="{ minHeight: computedMinHeight, maxHeight: computedMaxHeight }"
      contenteditable="true"
      @input="handleInput"
      @blur="handleBlur"
      :placeholder="placeholder"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'

const props = defineProps<{
  modelValue: string
  placeholder?: string
  minHeight?: number
  maxHeight?: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const editorRef = ref<HTMLDivElement>()

// Alturas por defecto ligeramente más bajas que antes (era 400/600)
const defaultMin = 360
const defaultMax = 560

const computedMinHeight = computed(() => `${props.minHeight ?? defaultMin}px`)
const computedMaxHeight = computed(() => `${props.maxHeight ?? defaultMax}px`)

// Ejecutar comando de formato
const execCommand = (command: string, value: string | undefined = undefined) => {
  document.execCommand(command, false, value)
  editorRef.value?.focus()
}

// Verificar si un comando está activo
const isActive = (command: string): boolean => {
  return document.queryCommandState(command)
}

// Manejar cambios en el select
const handleSelectChange = (event: Event, command: string) => {
  const target = event.target as HTMLSelectElement
  if (target) {
    execCommand(command, target.value)
  }
}

// Manejar cambios en color
const handleColorChange = (event: Event, command: string) => {
  const target = event.target as HTMLInputElement
  if (target) {
    execCommand(command, target.value)
  }
}

// Manejar cambios en el contenido
const handleInput = () => {
  if (editorRef.value) {
    emit('update:modelValue', editorRef.value.innerHTML)
  }
}

// Manejar pérdida de foco
const handleBlur = () => {
  if (editorRef.value) {
    emit('update:modelValue', editorRef.value.innerHTML)
  }
}

// Sincronizar contenido cuando cambia el modelValue desde fuera
watch(() => props.modelValue, (newValue) => {
  if (editorRef.value && editorRef.value.innerHTML !== newValue) {
    editorRef.value.innerHTML = newValue || ''
  }
}, { immediate: true })

// Inicializar contenido al montar
onMounted(() => {
  if (editorRef.value && props.modelValue) {
    editorRef.value.innerHTML = props.modelValue
  }
})
</script>

<style scoped>
.toolbar-btn-compact {
  @apply px-1.5 py-0.5 rounded hover:bg-gray-200 transition-colors flex items-center justify-center min-w-[24px] h-6 text-xs;
}

.toolbar-btn-compact:active {
  @apply bg-gray-300;
}

.toolbar-select-compact {
  @apply px-1 py-0.5 text-xs border border-gray-300 rounded bg-white hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-blue-500 min-w-[60px];
}

.toolbar-separator-compact {
  @apply w-px h-4 bg-gray-300 mx-0.5;
}

.toolbar-group {
  @apply flex gap-0.5 items-center;
}

.toolbar-color-input-compact {
  @apply w-6 h-6 cursor-pointer border border-gray-300 rounded;
}

.editor-content:empty:before {
  content: attr(placeholder);
  @apply text-gray-400 pointer-events-none;
}

.editor-content:focus {
  @apply ring-2 ring-blue-500 ring-inset;
}

/* Estilos para el contenido del editor */
.editor-content :deep(p) {
  @apply mb-2;
}

.editor-content :deep(ul),
.editor-content :deep(ol) {
  @apply ml-6 mb-2;
}

.editor-content :deep(ul) {
  @apply list-disc;
}

.editor-content :deep(ol) {
  @apply list-decimal;
}

.editor-content :deep(li) {
  @apply mb-1;
}

.editor-content :deep(strong) {
  @apply font-bold;
}

.editor-content :deep(em) {
  @apply italic;
}

.editor-content :deep(u) {
  @apply underline;
}
</style>
