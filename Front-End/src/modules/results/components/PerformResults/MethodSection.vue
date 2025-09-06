<template>
  <div class="h-full flex flex-col">
    <div class="p-3 bg-gray-50 rounded-lg border border-gray-200 flex-1 min-h-0">
      <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
        <TaskIcon class="w-4 h-4 mr-2 text-gray-500" />
        Métodos
      </h3>

      <!-- Selector dinámico de métodos -->
      <div class="flex flex-col h-full min-h-0">
        <div class="flex items-center justify-between mb-3">
          <label class="block text-sm font-medium text-gray-700">Métodos Utilizados</label>
          <AddButton text="Agregar" size="sm" @click="addMethod" />
        </div>
        
        <div class="flex-1 min-h-0 overflow-y-auto">
          <div class="space-y-2">
            <div v-for="(method, index) in methods" :key="index" class="flex items-center gap-3 bg-white border border-gray-200 rounded-lg p-2">
              <div class="flex-1 min-w-0">
                <MethodSelector 
                  v-model="method.code" 
                  :label="`Método ${index + 1}`" 
                  placeholder="Seleccionar método..." 
                  @method-selected="(m) => handleMethodSelected(index, m)" 
                />
              </div>
              <div class="flex items-center justify-center w-8 mt-6">
                <RemoveButton v-if="methods.length > 1" size="sm" @click="removeMethod(index)" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { AddButton, RemoveButton } from '@/shared/components/buttons'
import { MethodSelector } from '@/shared/components/List'
import { TaskIcon } from '@/assets/icons'

// Props
interface Props {
  modelValue?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: ''
})

// Emits
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

// Estado local
interface MethodItem { 
  code: string
  name: string
}

const methods = ref<MethodItem[]>([{ code: '', name: '' }])
const methodsError = ref('')

// Computed para generar el texto del método
const generatedMethodText = computed(() => {
  const validMethods = methods.value.filter(method => method.code.trim() !== '')
  
  if (validMethods.length === 0) return ''
  
  const methodTexts = validMethods.map(method => method.name || method.code)
  
  if (methodTexts.length === 1) {
    return `Método utilizado: ${methodTexts[0]}.`
  } else {
    return `Métodos utilizados: ${methodTexts.join(', ')}.`
  }
})

// Manipulación de métodos
const addMethod = () => {
  methods.value.push({ code: '', name: '' })
}

const removeMethod = (index: number) => {
  if (methods.value.length > 1) {
    methods.value.splice(index, 1)
    updateModelValue()
  }
}

const handleMethodSelected = (index: number, method: any) => {
  if (!method) return
  const item = methods.value[index]
  if (item) {
    item.code = method.value || ''
    item.name = method.label || ''
    updateModelValue()
  }
}

// Actualizar el model value
const updateModelValue = () => {
  emit('update:modelValue', generatedMethodText.value)
}

// Watch para cambios en methods
watch(methods, () => {
  updateModelValue()
}, { deep: true })
</script>
