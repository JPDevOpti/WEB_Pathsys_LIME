<template>
  <div class="h-full flex flex-col">
    <div class="p-3 bg-gray-50 rounded-lg border border-gray-200 flex-1 min-h-0">
      <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
        <TaskIcon class="w-4 h-4 mr-2 text-gray-500" />Métodos
      </h3>
      <div class="flex flex-col h-full min-h-0">
        <div class="flex items-center justify-between mb-3">
          <label class="block text-sm font-medium text-gray-700">Métodos Utilizados</label>
          <AddButton
            text="Agregar"
            size="sm"
            @click="addMethod"
          />
        </div>
        <div class="flex-1 min-h-0 overflow-y-auto">
          <div class="space-y-2">
            <div v-for="(_, i) in methods" :key="i" class="flex items-center gap-3 bg-white border border-gray-200 rounded-lg p-2">
              <div class="flex-1 min-w-0">
                <MethodSelector
                  v-model="methods[i]"
                  :options="availableMethods"
                  :label="`Método ${i+1}`"
                  placeholder="Seleccionar método..."
                  :class="{ 'ring-1 ring-red-300 rounded-md': showValidation && isEmpty(i) }"
                  :aria-invalid="showValidation && isEmpty(i) ? 'true' : 'false'"
                />
              </div>
              <div class="flex items-center justify-center w-8 mt-6">
                <RemoveButton v-if="methods.length > 1" size="sm" @click="removeMethod(i)" />
              </div>
            </div>
          </div>
          <div v-if="showValidation && hasEmpty" class="mt-2 p-2 text-xs rounded border border-red-200 bg-red-50 text-red-700">
            Hay métodos vacíos. Selecciona un método o elimínalo.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
import { AddButton, RemoveButton } from '@/shared/components/ui/buttons'
import { MethodSelector } from '@/shared/components/ui/lists'
import { TaskIcon } from '@/assets/icons'
import { AVAILABLE_METHODS, normalizeMethod } from '@/shared/data/methods'

// Props
const props = withDefaults(defineProps<{ modelValue?: string[]; showValidation?: boolean }>(), { modelValue: () => [], showValidation: false })
const emit = defineEmits< (e: 'update:modelValue', value: string[]) => void >()
const methods = ref<string[]>([''])
const availableMethods = ref(AVAILABLE_METHODS.slice())
let isUpdatingFromProps = ref(false)
const skipEmitOnPush = ref(false)
const addMethod = () => { skipEmitOnPush.value = true; methods.value.push(''); nextTick(() => { skipEmitOnPush.value = false }) }
const removeMethod = (i:number) => { if (methods.value.length>1) { methods.value.splice(i,1); updateModelValue() } }

// Normaliza un valor recibido (puede ser un 'value' ya guardado, o un 'label' antiguo)
const normalizeIncomingMethod = (s:string) => normalizeMethod(s)
// Emitir SIEMPRE el arreglo completo (con placeholders vacíos)
// para evitar que el padre "colapse" la lista y aparente borrar todo.
const updateModelValue = () => {
  if ((isUpdatingFromProps as any).value || skipEmitOnPush.value) return
  emit('update:modelValue', methods.value)
}

// Validación local: marcar vacíos y mostrar mensaje solo cuando showValidation=true
const isEmpty = (i: number) => !methods.value[i] || !methods.value[i].trim()
const hasEmpty = computed(() => methods.value.some(m => !m || !m.trim()))

watch(methods, () => {
  updateModelValue()
}, { deep: true })

// Watch para cambios en modelValue (para cargar datos existentes)
watch(()=>props.modelValue, nv=>{
  (isUpdatingFromProps as any).value = true
  if (nv && Array.isArray(nv) && nv.length>0) methods.value = nv.map((m:string)=>{ const z=normalizeIncomingMethod(m); if(z && !availableMethods.value.find(a=>a.value===z)) availableMethods.value.push({value:z,label:m}); return z })
  else methods.value = ['']
  nextTick(()=> (isUpdatingFromProps as any).value = false)
}, { immediate:true })
</script>
