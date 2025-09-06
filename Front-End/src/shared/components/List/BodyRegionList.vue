<template>
  <div class="body-region-combobox">
    <!-- Label -->
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>

    <!-- Combobox Container -->
    <div class="relative">
      <!-- Input field -->
      <div class="relative">
<input
          ref="inputRef"
          :value="displayText"
          type="text"
          :placeholder="placeholder"
          :disabled="disabled"
          :class="[
            'w-full px-3 py-2 pr-10 border rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors',
            errorString ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300',
            disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : 'bg-white text-gray-900'
          ]"
          @focus="handleFocus"
          @blur="handleBlur"
          @keydown="handleKeyDown"
          @input="(e:any) => { searchQuery = e?.target?.value || '' }"
          autocomplete="off"
        />
        
        <div class="absolute inset-y-0 right-0 pr-3 flex items-center">
          <svg 
            class="h-4 w-4 text-gray-400 cursor-pointer transition-transform"
            :class="{ 'transform rotate-180': isOpen }"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
            @click="toggleDropdown"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      <!-- Dropdown options -->
      <div
        v-if="isOpen && !disabled"
        class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto"
      >
        <!-- No results -->
        <div v-if="filteredOptions.length === 0" class="px-3 py-2 text-sm text-gray-500 text-center">
          {{ searchQuery.trim() ? 'No se encontraron regiones' : 'No hay regiones disponibles' }}
        </div>
        
        <!-- Options -->
        <div
          v-for="(option, index) in filteredOptions"
          :key="option.value"
          :class="[
            'px-3 py-2 text-sm cursor-pointer transition-colors',
            index === highlightedIndex ? 'bg-blue-50 text-blue-900' : 'text-gray-900 hover:bg-gray-50',
            selectedRegion === option.label ? 'bg-blue-100 text-blue-900 font-medium' : ''
          ]"
          @click="selectOption(option)"
          @mouseenter="highlightedIndex = index"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-gray-400 text-xs">{{ option.category }}</span>
              <span class="font-medium">{{ option.label }}</span>
            </div>
            <svg 
              v-if="selectedRegion === option.label"
              class="h-4 w-4 text-blue-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Help text -->
    <p v-if="helpText" class="mt-1 text-xs text-gray-500">
      {{ helpText }}
    </p>

    <!-- Error message -->
    <p v-if="errorString" class="mt-1 text-sm text-red-600">
      {{ errorString }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick, onMounted } from 'vue'
// import { useBodyRegionsAPI } from '@/modules/cases/composables/useBodyRegionsAPI'

// Props
interface Props {
  modelValue?: string
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  helpText?: string
  errors?: string[]
  autoLoad?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  label: '',
  placeholder: 'Buscar región del cuerpo...',
  required: false,
  disabled: false,
  helpText: '',
  errors: () => [],
  autoLoad: true
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string]
  'region-selected': [region: BodyRegion | null]
}>()

// Tipos
interface BodyRegion {
  value: string
  label: string
  category: string
}

// Lista exhaustiva de regiones del cuerpo para laboratorio de patología
const bodyRegions: BodyRegion[] = [
  // Sistema Nervioso Central
  { value: 'cerebro', label: 'Cerebro', category: 'Sistema Nervioso Central' },
  { value: 'corteza_cerebral', label: 'Corteza Cerebral', category: 'Sistema Nervioso Central' },
  { value: 'lobulo_frontal', label: 'Lóbulo Frontal', category: 'Sistema Nervioso Central' },
  { value: 'lobulo_parietal', label: 'Lóbulo Parietal', category: 'Sistema Nervioso Central' },
  { value: 'lobulo_temporal', label: 'Lóbulo Temporal', category: 'Sistema Nervioso Central' },
  { value: 'lobulo_occipital', label: 'Lóbulo Occipital', category: 'Sistema Nervioso Central' },
  { value: 'cerebelo', label: 'Cerebelo', category: 'Sistema Nervioso Central' },
  { value: 'tronco_encefalico', label: 'Tronco Encefálico', category: 'Sistema Nervioso Central' },
  { value: 'mesencefalo', label: 'Mesencéfalo', category: 'Sistema Nervioso Central' },
  { value: 'protuberancia', label: 'Protuberancia', category: 'Sistema Nervioso Central' },
  { value: 'bulbo_raquideo', label: 'Bulbo Raquídeo', category: 'Sistema Nervioso Central' },
  { value: 'medula_espinal', label: 'Médula Espinal', category: 'Sistema Nervioso Central' },
  { value: 'medula_cervical', label: 'Médula Espinal Cervical', category: 'Sistema Nervioso Central' },
  { value: 'medula_toracica', label: 'Médula Espinal Torácica', category: 'Sistema Nervioso Central' },
  { value: 'medula_lumbar', label: 'Médula Espinal Lumbar', category: 'Sistema Nervioso Central' },
  { value: 'medula_sacra', label: 'Médula Espinal Sacra', category: 'Sistema Nervioso Central' },
  { value: 'meninges', label: 'Meninges', category: 'Sistema Nervioso Central' },
  { value: 'duramadre', label: 'Duramadre', category: 'Sistema Nervioso Central' },
  { value: 'aracnoides', label: 'Aracnoides', category: 'Sistema Nervioso Central' },
  { value: 'piamadre', label: 'Piamadre', category: 'Sistema Nervioso Central' },
  
  // Sistema Nervioso Periférico
  { value: 'nervio_optico', label: 'Nervio Óptico', category: 'Sistema Nervioso Periférico' },
  { value: 'nervio_facial', label: 'Nervio Facial', category: 'Sistema Nervioso Periférico' },
  { value: 'nervio_trigemino', label: 'Nervio Trigémino', category: 'Sistema Nervioso Periférico' },
  { value: 'nervio_vago', label: 'Nervio Vago', category: 'Sistema Nervioso Periférico' },
  { value: 'nervio_ciatico', label: 'Nervio Ciático', category: 'Sistema Nervioso Periférico' },
  { value: 'nervio_mediano', label: 'Nervio Mediano', category: 'Sistema Nervioso Periférico' },
  { value: 'nervio_cubital', label: 'Nervio Cubital', category: 'Sistema Nervioso Periférico' },
  { value: 'nervio_radial', label: 'Nervio Radial', category: 'Sistema Nervioso Periférico' },
  { value: 'plexo_braquial', label: 'Plexo Braquial', category: 'Sistema Nervioso Periférico' },
  { value: 'plexo_lumbosacro', label: 'Plexo Lumbosacro', category: 'Sistema Nervioso Periférico' },
  
  // Cabeza y Cuello
  { value: 'cuero_cabelludo', label: 'Cuero Cabelludo', category: 'Cabeza y Cuello' },
  { value: 'frente', label: 'Frente', category: 'Cabeza y Cuello' },
  { value: 'mejilla', label: 'Mejilla', category: 'Cabeza y Cuello' },
  { value: 'menton', label: 'Mentón', category: 'Cabeza y Cuello' },
  { value: 'mandibula', label: 'Mandíbula', category: 'Cabeza y Cuello' },
  { value: 'maxilar', label: 'Maxilar', category: 'Cabeza y Cuello' },
  { value: 'parpado_superior', label: 'Párpado Superior', category: 'Cabeza y Cuello' },
  { value: 'parpado_inferior', label: 'Párpado Inferior', category: 'Cabeza y Cuello' },
  { value: 'conjuntiva', label: 'Conjuntiva', category: 'Cabeza y Cuello' },
  { value: 'cornea', label: 'Córnea', category: 'Cabeza y Cuello' },
  { value: 'iris', label: 'Iris', category: 'Cabeza y Cuello' },
  { value: 'retina', label: 'Retina', category: 'Cabeza y Cuello' },
  { value: 'oido_externo', label: 'Oído Externo', category: 'Cabeza y Cuello' },
  { value: 'oido_medio', label: 'Oído Medio', category: 'Cabeza y Cuello' },
  { value: 'oido_interno', label: 'Oído Interno', category: 'Cabeza y Cuello' },
  { value: 'trompa_eustaquio', label: 'Trompa de Eustaquio', category: 'Cabeza y Cuello' },
  { value: 'fosas_nasales', label: 'Fosas Nasales', category: 'Cabeza y Cuello' },
  { value: 'senos_paranasales', label: 'Senos Paranasales', category: 'Cabeza y Cuello' },
  { value: 'seno_frontal', label: 'Seno Frontal', category: 'Cabeza y Cuello' },
  { value: 'seno_maxilar', label: 'Seno Maxilar', category: 'Cabeza y Cuello' },
  { value: 'seno_etmoidal', label: 'Seno Etmoidal', category: 'Cabeza y Cuello' },
  { value: 'seno_esfenoidal', label: 'Seno Esfenoidal', category: 'Cabeza y Cuello' },
  { value: 'cavidad_oral', label: 'Cavidad Oral', category: 'Cabeza y Cuello' },
  { value: 'lengua', label: 'Lengua', category: 'Cabeza y Cuello' },
  { value: 'piso_boca', label: 'Piso de la Boca', category: 'Cabeza y Cuello' },
  { value: 'paladar_duro', label: 'Paladar Duro', category: 'Cabeza y Cuello' },
  { value: 'paladar_blando', label: 'Paladar Blando', category: 'Cabeza y Cuello' },
  { value: 'uvula', label: 'Úvula', category: 'Cabeza y Cuello' },
  { value: 'encias', label: 'Encías', category: 'Cabeza y Cuello' },
  { value: 'labio_superior', label: 'Labio Superior', category: 'Cabeza y Cuello' },
  { value: 'labio_inferior', label: 'Labio Inferior', category: 'Cabeza y Cuello' },
  { value: 'glandula_parotida', label: 'Glándula Parótida', category: 'Cabeza y Cuello' },
  { value: 'glandula_submandibular', label: 'Glándula Submandibular', category: 'Cabeza y Cuello' },
  { value: 'glandula_sublingual', label: 'Glándula Sublingual', category: 'Cabeza y Cuello' },
  { value: 'faringe', label: 'Faringe', category: 'Cabeza y Cuello' },
  { value: 'nasofaringe', label: 'Nasofaringe', category: 'Cabeza y Cuello' },
  { value: 'orofaringe', label: 'Orofaringe', category: 'Cabeza y Cuello' },
  { value: 'hipofaringe', label: 'Hipofaringe', category: 'Cabeza y Cuello' },
  { value: 'laringe', label: 'Laringe', category: 'Cabeza y Cuello' },
  { value: 'cuerdas_vocales', label: 'Cuerdas Vocales', category: 'Cabeza y Cuello' },
  { value: 'epiglotis', label: 'Epiglotis', category: 'Cabeza y Cuello' },
  { value: 'amigdalas', label: 'Amígdalas', category: 'Cabeza y Cuello' },
  { value: 'adenoides', label: 'Adenoides', category: 'Cabeza y Cuello' },
  { value: 'tiroides', label: 'Tiroides', category: 'Cabeza y Cuello' },
  { value: 'paratiroides', label: 'Paratiroides', category: 'Cabeza y Cuello' },
  { value: 'cuello_anterior', label: 'Cuello Anterior', category: 'Cabeza y Cuello' },
  { value: 'cuello_posterior', label: 'Cuello Posterior', category: 'Cabeza y Cuello' },
  { value: 'cuello_lateral', label: 'Cuello Lateral', category: 'Cabeza y Cuello' },
  
  // Sistema Respiratorio
  { value: 'tráquea', label: 'Tráquea', category: 'Sistema Respiratorio' },
  { value: 'bronquio_principal_derecho', label: 'Bronquio Principal Derecho', category: 'Sistema Respiratorio' },
  { value: 'bronquio_principal_izquierdo', label: 'Bronquio Principal Izquierdo', category: 'Sistema Respiratorio' },
  { value: 'bronquio_lobar', label: 'Bronquio Lobar', category: 'Sistema Respiratorio' },
  { value: 'bronquio_segmentario', label: 'Bronquio Segmentario', category: 'Sistema Respiratorio' },
  { value: 'bronquiolo', label: 'Bronquiolo', category: 'Sistema Respiratorio' },
  { value: 'pulmon_derecho', label: 'Pulmón Derecho', category: 'Sistema Respiratorio' },
  { value: 'pulmon_izquierdo', label: 'Pulmón Izquierdo', category: 'Sistema Respiratorio' },
  { value: 'lobulo_superior_derecho', label: 'Lóbulo Superior Derecho', category: 'Sistema Respiratorio' },
  { value: 'lobulo_medio_derecho', label: 'Lóbulo Medio Derecho', category: 'Sistema Respiratorio' },
  { value: 'lobulo_inferior_derecho', label: 'Lóbulo Inferior Derecho', category: 'Sistema Respiratorio' },
  { value: 'lobulo_superior_izquierdo', label: 'Lóbulo Superior Izquierdo', category: 'Sistema Respiratorio' },
  { value: 'lobulo_inferior_izquierdo', label: 'Lóbulo Inferior Izquierdo', category: 'Sistema Respiratorio' },
  { value: 'pleura_parietal', label: 'Pleura Parietal', category: 'Sistema Respiratorio' },
  { value: 'pleura_visceral', label: 'Pleura Visceral', category: 'Sistema Respiratorio' },
  { value: 'espacio_pleural', label: 'Espacio Pleural', category: 'Sistema Respiratorio' },
  { value: 'diafragma', label: 'Diafragma', category: 'Sistema Respiratorio' },
  
  // Sistema Cardiovascular
  { value: 'corazon', label: 'Corazón', category: 'Sistema Cardiovascular' },
  { value: 'pericardio', label: 'Pericardio', category: 'Sistema Cardiovascular' },
  { value: 'auricula_derecha', label: 'Aurícula Derecha', category: 'Sistema Cardiovascular' },
  { value: 'auricula_izquierda', label: 'Aurícula Izquierda', category: 'Sistema Cardiovascular' },
  { value: 'ventriculo_derecho', label: 'Ventrículo Derecho', category: 'Sistema Cardiovascular' },
  { value: 'ventriculo_izquierdo', label: 'Ventrículo Izquierdo', category: 'Sistema Cardiovascular' },
  { value: 'valvula_tricuspide', label: 'Válvula Tricúspide', category: 'Sistema Cardiovascular' },
  { value: 'valvula_mitral', label: 'Válvula Mitral', category: 'Sistema Cardiovascular' },
  { value: 'valvula_aortica', label: 'Válvula Aórtica', category: 'Sistema Cardiovascular' },
  { value: 'valvula_pulmonar', label: 'Válvula Pulmonar', category: 'Sistema Cardiovascular' },
  { value: 'aorta_ascendente', label: 'Aorta Ascendente', category: 'Sistema Cardiovascular' },
  { value: 'aorta_toracica', label: 'Aorta Torácica', category: 'Sistema Cardiovascular' },
  { value: 'aorta_abdominal', label: 'Aorta Abdominal', category: 'Sistema Cardiovascular' },
  { value: 'arteria_coronaria_izquierda', label: 'Arteria Coronaria Izquierda', category: 'Sistema Cardiovascular' },
  { value: 'arteria_coronaria_derecha', label: 'Arteria Coronaria Derecha', category: 'Sistema Cardiovascular' },
  { value: 'vena_cava_superior', label: 'Vena Cava Superior', category: 'Sistema Cardiovascular' },
  { value: 'vena_cava_inferior', label: 'Vena Cava Inferior', category: 'Sistema Cardiovascular' },
  { value: 'arteria_pulmonar', label: 'Arteria Pulmonar', category: 'Sistema Cardiovascular' },
  { value: 'venas_pulmonares', label: 'Venas Pulmonares', category: 'Sistema Cardiovascular' },
  { value: 'arteria_carotida', label: 'Arteria Carótida', category: 'Sistema Cardiovascular' },
  { value: 'arteria_subclavia', label: 'Arteria Subclavia', category: 'Sistema Cardiovascular' },
  { value: 'arteria_braquial', label: 'Arteria Braquial', category: 'Sistema Cardiovascular' },
  { value: 'arteria_radial', label: 'Arteria Radial', category: 'Sistema Cardiovascular' },
  { value: 'arteria_cubital', label: 'Arteria Cubital', category: 'Sistema Cardiovascular' },
  { value: 'arteria_femoral', label: 'Arteria Femoral', category: 'Sistema Cardiovascular' },
  { value: 'arteria_poplitea', label: 'Arteria Poplítea', category: 'Sistema Cardiovascular' },
  { value: 'arteria_tibial', label: 'Arteria Tibial', category: 'Sistema Cardiovascular' },
  { value: 'mediastino', label: 'Mediastino', category: 'Sistema Cardiovascular' },
  
  // Sistema Digestivo
  { value: 'esofago', label: 'Esófago', category: 'Sistema Digestivo' },
  { value: 'esofago_cervical', label: 'Esófago Cervical', category: 'Sistema Digestivo' },
  { value: 'esofago_toracico', label: 'Esófago Torácico', category: 'Sistema Digestivo' },
  { value: 'esofago_abdominal', label: 'Esófago Abdominal', category: 'Sistema Digestivo' },
  { value: 'estomago', label: 'Estómago', category: 'Sistema Digestivo' },
  { value: 'cardias', label: 'Cardias', category: 'Sistema Digestivo' },
  { value: 'fundus_gastrico', label: 'Fundus Gástrico', category: 'Sistema Digestivo' },
  { value: 'cuerpo_gastrico', label: 'Cuerpo Gástrico', category: 'Sistema Digestivo' },
  { value: 'antro_gastrico', label: 'Antro Gástrico', category: 'Sistema Digestivo' },
  { value: 'piloro', label: 'Píloro', category: 'Sistema Digestivo' },
  { value: 'duodeno', label: 'Duodeno', category: 'Sistema Digestivo' },
  { value: 'yeyuno', label: 'Yeyuno', category: 'Sistema Digestivo' },
  { value: 'ileon', label: 'Íleon', category: 'Sistema Digestivo' },
  { value: 'valvula_ileocecal', label: 'Válvula Ileocecal', category: 'Sistema Digestivo' },
  { value: 'ciego', label: 'Ciego', category: 'Sistema Digestivo' },
  { value: 'apendice', label: 'Apéndice', category: 'Sistema Digestivo' },
  { value: 'colon_ascendente', label: 'Colon Ascendente', category: 'Sistema Digestivo' },
  { value: 'colon_transverso', label: 'Colon Transverso', category: 'Sistema Digestivo' },
  { value: 'colon_descendente', label: 'Colon Descendente', category: 'Sistema Digestivo' },
  { value: 'colon_sigmoide', label: 'Colon Sigmoide', category: 'Sistema Digestivo' },
  { value: 'recto', label: 'Recto', category: 'Sistema Digestivo' },
  { value: 'canal_anal', label: 'Canal Anal', category: 'Sistema Digestivo' },
  { value: 'ano', label: 'Ano', category: 'Sistema Digestivo' },
  { value: 'higado', label: 'Hígado', category: 'Sistema Digestivo' },
  { value: 'lobulo_hepatico_derecho', label: 'Lóbulo Hepático Derecho', category: 'Sistema Digestivo' },
  { value: 'lobulo_hepatico_izquierdo', label: 'Lóbulo Hepático Izquierdo', category: 'Sistema Digestivo' },
  { value: 'lobulo_caudado', label: 'Lóbulo Caudado', category: 'Sistema Digestivo' },
  { value: 'lobulo_cuadrado', label: 'Lóbulo Cuadrado', category: 'Sistema Digestivo' },
  { value: 'vesicula_biliar', label: 'Vesícula Biliar', category: 'Sistema Digestivo' },
  { value: 'via_biliar', label: 'Vía Biliar', category: 'Sistema Digestivo' },
  { value: 'conducto_cistico', label: 'Conducto Cístico', category: 'Sistema Digestivo' },
  { value: 'conducto_hepatico', label: 'Conducto Hepático', category: 'Sistema Digestivo' },
  { value: 'conducto_coledoco', label: 'Conducto Colédoco', category: 'Sistema Digestivo' },
  { value: 'pancreas', label: 'Páncreas', category: 'Sistema Digestivo' },
  { value: 'cabeza_pancreas', label: 'Cabeza del Páncreas', category: 'Sistema Digestivo' },
  { value: 'cuerpo_pancreas', label: 'Cuerpo del Páncreas', category: 'Sistema Digestivo' },
  { value: 'cola_pancreas', label: 'Cola del Páncreas', category: 'Sistema Digestivo' },
  { value: 'conducto_pancreatico', label: 'Conducto Pancreático', category: 'Sistema Digestivo' },
  { value: 'ampolla_vater', label: 'Ampolla de Vater', category: 'Sistema Digestivo' },
  
  // Sistema Genitourinario
  { value: 'rinon_derecho', label: 'Riñón Derecho', category: 'Sistema Genitourinario' },
  { value: 'rinon_izquierdo', label: 'Riñón Izquierdo', category: 'Sistema Genitourinario' },
  { value: 'corteza_renal', label: 'Corteza Renal', category: 'Sistema Genitourinario' },
  { value: 'medula_renal', label: 'Médula Renal', category: 'Sistema Genitourinario' },
  { value: 'pelvis_renal', label: 'Pelvis Renal', category: 'Sistema Genitourinario' },
  { value: 'calices_renales', label: 'Cálices Renales', category: 'Sistema Genitourinario' },
  { value: 'ureter_derecho', label: 'Uréter Derecho', category: 'Sistema Genitourinario' },
  { value: 'ureter_izquierdo', label: 'Uréter Izquierdo', category: 'Sistema Genitourinario' },
  { value: 'vejiga', label: 'Vejiga', category: 'Sistema Genitourinario' },
  { value: 'cupula_vesical', label: 'Cúpula Vesical', category: 'Sistema Genitourinario' },
  { value: 'cuello_vesical', label: 'Cuello Vesical', category: 'Sistema Genitourinario' },
  { value: 'trigono_vesical', label: 'Trígono Vesical', category: 'Sistema Genitourinario' },
  { value: 'uretra', label: 'Uretra', category: 'Sistema Genitourinario' },
  { value: 'uretra_masculina', label: 'Uretra Masculina', category: 'Sistema Genitourinario' },
  { value: 'uretra_femenina', label: 'Uretra Femenina', category: 'Sistema Genitourinario' },
  { value: 'glandula_suprarrenal_derecha', label: 'Glándula Suprarrenal Derecha', category: 'Sistema Genitourinario' },
  { value: 'glandula_suprarrenal_izquierda', label: 'Glándula Suprarrenal Izquierda', category: 'Sistema Genitourinario' },
  
  // Sistema Reproductivo Masculino
  { value: 'testiculo_derecho', label: 'Testículo Derecho', category: 'Sistema Reproductivo Masculino' },
  { value: 'testiculo_izquierdo', label: 'Testículo Izquierdo', category: 'Sistema Reproductivo Masculino' },
  { value: 'epididimo_derecho', label: 'Epidídimo Derecho', category: 'Sistema Reproductivo Masculino' },
  { value: 'epididimo_izquierdo', label: 'Epidídimo Izquierdo', category: 'Sistema Reproductivo Masculino' },
  { value: 'cordon_espermatico', label: 'Cordón Espermático', category: 'Sistema Reproductivo Masculino' },
  { value: 'conducto_deferente', label: 'Conducto Deferente', category: 'Sistema Reproductivo Masculino' },
  { value: 'vesicula_seminal', label: 'Vesícula Seminal', category: 'Sistema Reproductivo Masculino' },
  { value: 'prostata', label: 'Próstata', category: 'Sistema Reproductivo Masculino' },
  { value: 'glandula_bulbouretral', label: 'Glándula Bulbouretral', category: 'Sistema Reproductivo Masculino' },
  { value: 'pene', label: 'Pene', category: 'Sistema Reproductivo Masculino' },
  { value: 'glande', label: 'Glande', category: 'Sistema Reproductivo Masculino' },
  { value: 'prepucio', label: 'Prepucio', category: 'Sistema Reproductivo Masculino' },
  { value: 'escroto', label: 'Escroto', category: 'Sistema Reproductivo Masculino' },
  
  // Sistema Reproductivo Femenino
  { value: 'ovario_derecho', label: 'Ovario Derecho', category: 'Sistema Reproductivo Femenino' },
  { value: 'ovario_izquierdo', label: 'Ovario Izquierdo', category: 'Sistema Reproductivo Femenino' },
  { value: 'trompa_falopio_derecha', label: 'Trompa de Falopio Derecha', category: 'Sistema Reproductivo Femenino' },
  { value: 'trompa_falopio_izquierda', label: 'Trompa de Falopio Izquierda', category: 'Sistema Reproductivo Femenino' },
  { value: 'utero', label: 'Útero', category: 'Sistema Reproductivo Femenino' },
  { value: 'fondo_uterino', label: 'Fondo Uterino', category: 'Sistema Reproductivo Femenino' },
  { value: 'cuerpo_uterino', label: 'Cuerpo Uterino', category: 'Sistema Reproductivo Femenino' },
  { value: 'cuello_uterino', label: 'Cuello Uterino', category: 'Sistema Reproductivo Femenino' },
  { value: 'endometrio', label: 'Endometrio', category: 'Sistema Reproductivo Femenino' },
  { value: 'miometrio', label: 'Miometrio', category: 'Sistema Reproductivo Femenino' },
  { value: 'perimetrio', label: 'Perimetrio', category: 'Sistema Reproductivo Femenino' },
  { value: 'cervix', label: 'Cérvix', category: 'Sistema Reproductivo Femenino' },
  { value: 'vagina', label: 'Vagina', category: 'Sistema Reproductivo Femenino' },
  { value: 'fornix_vaginal', label: 'Fórnix Vaginal', category: 'Sistema Reproductivo Femenino' },
  { value: 'vulva', label: 'Vulva', category: 'Sistema Reproductivo Femenino' },
  { value: 'labios_mayores', label: 'Labios Mayores', category: 'Sistema Reproductivo Femenino' },
  { value: 'labios_menores', label: 'Labios Menores', category: 'Sistema Reproductivo Femenino' },
  { value: 'clitoris', label: 'Clítoris', category: 'Sistema Reproductivo Femenino' },
  { value: 'vestibulo_vaginal', label: 'Vestíbulo Vaginal', category: 'Sistema Reproductivo Femenino' },
  { value: 'glandula_bartolino', label: 'Glándula de Bartolino', category: 'Sistema Reproductivo Femenino' },
  { value: 'himen', label: 'Himen', category: 'Sistema Reproductivo Femenino' },
  
  // Glándulas Mamarias
  { value: 'mama_derecha', label: 'Mama Derecha', category: 'Glándulas Mamarias' },
  { value: 'mama_izquierda', label: 'Mama Izquierda', category: 'Glándulas Mamarias' },
  { value: 'cuadrante_superior_externo', label: 'Cuadrante Superior Externo', category: 'Glándulas Mamarias' },
  { value: 'cuadrante_superior_interno', label: 'Cuadrante Superior Interno', category: 'Glándulas Mamarias' },
  { value: 'cuadrante_inferior_externo', label: 'Cuadrante Inferior Externo', category: 'Glándulas Mamarias' },
  { value: 'cuadrante_inferior_interno', label: 'Cuadrante Inferior Interno', category: 'Glándulas Mamarias' },
  { value: 'areola', label: 'Areola', category: 'Glándulas Mamarias' },
  { value: 'pezon', label: 'Pezón', category: 'Glándulas Mamarias' },
  { value: 'tejido_mamario_central', label: 'Tejido Mamario Central', category: 'Glándulas Mamarias' },
  { value: 'cola_spencer', label: 'Cola de Spencer', category: 'Glándulas Mamarias' },
  
  // Sistema Endocrino
  { value: 'hipofisis', label: 'Hipófisis', category: 'Sistema Endocrino' },
  { value: 'adenohipofisis', label: 'Adenohipófisis', category: 'Sistema Endocrino' },
  { value: 'neurohipofisis', label: 'Neurohipófisis', category: 'Sistema Endocrino' },
  { value: 'glandula_pineal', label: 'Glándula Pineal', category: 'Sistema Endocrino' },
  { value: 'timo', label: 'Timo', category: 'Sistema Endocrino' },
  { value: 'islotes_langerhans', label: 'Islotes de Langerhans', category: 'Sistema Endocrino' },
  
  // Sistema Hematolinfático
  { value: 'bazo', label: 'Bazo', category: 'Sistema Hematolinfático' },
  { value: 'pulpa_roja_esplenica', label: 'Pulpa Roja Esplénica', category: 'Sistema Hematolinfático' },
  { value: 'pulpa_blanca_esplenica', label: 'Pulpa Blanca Esplénica', category: 'Sistema Hematolinfático' },
  { value: 'medula_osea', label: 'Médula Ósea', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_cervical', label: 'Ganglio Linfático Cervical', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_axilar', label: 'Ganglio Linfático Axilar', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_inguinal', label: 'Ganglio Linfático Inguinal', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_mediastinico', label: 'Ganglio Linfático Mediastínico', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_abdominal', label: 'Ganglio Linfático Abdominal', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_mesenterico', label: 'Ganglio Linfático Mesentérico', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_iliaco', label: 'Ganglio Linfático Ilíaco', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_obturador', label: 'Ganglio Linfático Obturador', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_supraclavicular', label: 'Ganglio Linfático Supraclavicular', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_infraclavicular', label: 'Ganglio Linfático Infraclavicular', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_intercostal', label: 'Ganglio Linfático Intercostal', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_mamario_interno', label: 'Ganglio Linfático Mamario Interno', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_paraesofagico', label: 'Ganglio Linfático Paraesofágico', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_periaortico', label: 'Ganglio Linfático Periaórtico', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_paracaval', label: 'Ganglio Linfático Paracaval', category: 'Sistema Hematolinfático' },
  { value: 'ganglio_retroperitoneal', label: 'Ganglio Linfático Retroperitoneal', category: 'Sistema Hematolinfático' },
  { value: 'tejido_linfoide', label: 'Tejido Linfoide', category: 'Sistema Hematolinfático' },
  
  // Sistema Musculoesquelético - Huesos
  { value: 'craneo', label: 'Cráneo', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'frontal', label: 'Frontal', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'parietal', label: 'Parietal', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'temporal', label: 'Temporal', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'occipital', label: 'Occipital', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'etmoides', label: 'Etmoides', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'esfenoides', label: 'Esfenoides', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'vertebras_cervicales', label: 'Vértebras Cervicales', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'vertebras_toracicas', label: 'Vértebras Torácicas', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'vertebras_lumbares', label: 'Vértebras Lumbares', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'sacro', label: 'Sacro', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'coccix', label: 'Cóccix', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'costillas', label: 'Costillas', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'esternon', label: 'Esternón', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'clavicula', label: 'Clavícula', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'escapula', label: 'Escápula', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'humero', label: 'Húmero', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'radio', label: 'Radio', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'cubito', label: 'Cúbito', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'huesos_carpo', label: 'Huesos del Carpo', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'metacarpianos', label: 'Metacarpianos', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'falanges_mano', label: 'Falanges de la Mano', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'pelvis', label: 'Pelvis', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'ilion', label: 'Ilion', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'isquion', label: 'Isquion', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'pubis', label: 'Pubis', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'femur', label: 'Fémur', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'tibia', label: 'Tibia', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'perone', label: 'Peroné', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'rotula', label: 'Rótula', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'huesos_tarso', label: 'Huesos del Tarso', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'metatarsianos', label: 'Metatarsianos', category: 'Sistema Musculoesquelético - Huesos' },
  { value: 'falanges_pie', label: 'Falanges del Pie', category: 'Sistema Musculoesquelético - Huesos' },
  
  // Extremidades Superiores
  { value: 'hombro_derecho', label: 'Hombro Derecho', category: 'Extremidades Superiores' },
  { value: 'hombro_izquierdo', label: 'Hombro Izquierdo', category: 'Extremidades Superiores' },
  { value: 'axila_derecha', label: 'Axila Derecha', category: 'Extremidades Superiores' },
  { value: 'axila_izquierda', label: 'Axila Izquierda', category: 'Extremidades Superiores' },
  { value: 'brazo_derecho', label: 'Brazo Derecho', category: 'Extremidades Superiores' },
  { value: 'brazo_izquierdo', label: 'Brazo Izquierdo', category: 'Extremidades Superiores' },
  { value: 'codo_derecho', label: 'Codo Derecho', category: 'Extremidades Superiores' },
  { value: 'codo_izquierdo', label: 'Codo Izquierdo', category: 'Extremidades Superiores' },
  { value: 'antebrazo_derecho', label: 'Antebrazo Derecho', category: 'Extremidades Superiores' },
  { value: 'antebrazo_izquierdo', label: 'Antebrazo Izquierdo', category: 'Extremidades Superiores' },
  { value: 'muneca_derecha', label: 'Muñeca Derecha', category: 'Extremidades Superiores' },
  { value: 'muneca_izquierda', label: 'Muñeca Izquierda', category: 'Extremidades Superiores' },
  { value: 'mano_derecha', label: 'Mano Derecha', category: 'Extremidades Superiores' },
  { value: 'mano_izquierda', label: 'Mano Izquierda', category: 'Extremidades Superiores' },
  { value: 'pulgar_derecho', label: 'Pulgar Derecho', category: 'Extremidades Superiores' },
  { value: 'pulgar_izquierdo', label: 'Pulgar Izquierdo', category: 'Extremidades Superiores' },
  { value: 'indice_derecho', label: 'Índice Derecho', category: 'Extremidades Superiores' },
  { value: 'indice_izquierdo', label: 'Índice Izquierdo', category: 'Extremidades Superiores' },
  { value: 'medio_derecho', label: 'Dedo Medio Derecho', category: 'Extremidades Superiores' },
  { value: 'medio_izquierdo', label: 'Dedo Medio Izquierdo', category: 'Extremidades Superiores' },
  { value: 'anular_derecho', label: 'Anular Derecho', category: 'Extremidades Superiores' },
  { value: 'anular_izquierdo', label: 'Anular Izquierdo', category: 'Extremidades Superiores' },
  { value: 'menique_derecho', label: 'Meñique Derecho', category: 'Extremidades Superiores' },
  { value: 'menique_izquierdo', label: 'Meñique Izquierdo', category: 'Extremidades Superiores' },
  
  // Extremidades Inferiores
  { value: 'cadera_derecha', label: 'Cadera Derecha', category: 'Extremidades Inferiores' },
  { value: 'cadera_izquierda', label: 'Cadera Izquierda', category: 'Extremidades Inferiores' },
  { value: 'ingle_derecha', label: 'Ingle Derecha', category: 'Extremidades Inferiores' },
  { value: 'ingle_izquierda', label: 'Ingle Izquierda', category: 'Extremidades Inferiores' },
  { value: 'muslo_derecho', label: 'Muslo Derecho', category: 'Extremidades Inferiores' },
  { value: 'muslo_izquierdo', label: 'Muslo Izquierdo', category: 'Extremidades Inferiores' },
  { value: 'rodilla_derecha', label: 'Rodilla Derecha', category: 'Extremidades Inferiores' },
  { value: 'rodilla_izquierda', label: 'Rodilla Izquierda', category: 'Extremidades Inferiores' },
  { value: 'pierna_derecha', label: 'Pierna Derecha', category: 'Extremidades Inferiores' },
  { value: 'pierna_izquierda', label: 'Pierna Izquierda', category: 'Extremidades Inferiores' },
  { value: 'pantorrilla_derecha', label: 'Pantorrilla Derecha', category: 'Extremidades Inferiores' },
  { value: 'pantorrilla_izquierda', label: 'Pantorrilla Izquierda', category: 'Extremidades Inferiores' },
  { value: 'tobillo_derecho', label: 'Tobillo Derecho', category: 'Extremidades Inferiores' },
  { value: 'tobillo_izquierdo', label: 'Tobillo Izquierdo', category: 'Extremidades Inferiores' },
  { value: 'pie_derecho', label: 'Pie Derecho', category: 'Extremidades Inferiores' },
  { value: 'pie_izquierdo', label: 'Pie Izquierdo', category: 'Extremidades Inferiores' },
  { value: 'talon_derecho', label: 'Talón Derecho', category: 'Extremidades Inferiores' },
  { value: 'talon_izquierdo', label: 'Talón Izquierdo', category: 'Extremidades Inferiores' },
  { value: 'planta_pie_derecha', label: 'Planta del Pie Derecha', category: 'Extremidades Inferiores' },
  { value: 'planta_pie_izquierda', label: 'Planta del Pie Izquierda', category: 'Extremidades Inferiores' },
  { value: 'dedo_gordo_derecho', label: 'Dedo Gordo Derecho', category: 'Extremidades Inferiores' },
  { value: 'dedo_gordo_izquierdo', label: 'Dedo Gordo Izquierdo', category: 'Extremidades Inferiores' },
  
  // Piel y Tejidos Blandos
  { value: 'piel_cabeza_cuello', label: 'Piel de Cabeza y Cuello', category: 'Piel y Tejidos Blandos' },
  { value: 'piel_torax', label: 'Piel del Tórax', category: 'Piel y Tejidos Blandos' },
  { value: 'piel_abdomen', label: 'Piel del Abdomen', category: 'Piel y Tejidos Blandos' },
  { value: 'piel_espalda', label: 'Piel de la Espalda', category: 'Piel y Tejidos Blandos' },
  { value: 'piel_miembro_superior', label: 'Piel del Miembro Superior', category: 'Piel y Tejidos Blandos' },
  { value: 'piel_miembro_inferior', label: 'Piel del Miembro Inferior', category: 'Piel y Tejidos Blandos' },
  { value: 'piel_genital', label: 'Piel Genital', category: 'Piel y Tejidos Blandos' },
  { value: 'piel_perianal', label: 'Piel Perianal', category: 'Piel y Tejidos Blandos' },
  { value: 'epidermis', label: 'Epidermis', category: 'Piel y Tejidos Blandos' },
  { value: 'dermis', label: 'Dermis', category: 'Piel y Tejidos Blandos' },
  { value: 'hipodermis', label: 'Hipodermis', category: 'Piel y Tejidos Blandos' },
  { value: 'foliculo_piloso', label: 'Folículo Piloso', category: 'Piel y Tejidos Blandos' },
  { value: 'glandula_sebacea', label: 'Glándula Sebácea', category: 'Piel y Tejidos Blandos' },
  { value: 'glandula_sudoripara', label: 'Glándula Sudorípara', category: 'Piel y Tejidos Blandos' },
  { value: 'una', label: 'Uña', category: 'Piel y Tejidos Blandos' },
  { value: 'tejido_adiposo', label: 'Tejido Adiposo', category: 'Piel y Tejidos Blandos' },
  { value: 'tejido_conectivo', label: 'Tejido Conectivo', category: 'Piel y Tejidos Blandos' },
  
  // Músculos y Tejidos Blandos
  { value: 'musculo_esqueletico', label: 'Músculo Esquelético', category: 'Músculos y Tejidos Blandos' },
  { value: 'musculo_liso', label: 'Músculo Liso', category: 'Músculos y Tejidos Blandos' },
  { value: 'musculo_cardiaco', label: 'Músculo Cardíaco', category: 'Músculos y Tejidos Blandos' },
  { value: 'tendones', label: 'Tendones', category: 'Músculos y Tejidos Blandos' },
  { value: 'ligamentos', label: 'Ligamentos', category: 'Músculos y Tejidos Blandos' },
  { value: 'fascias', label: 'Fascias', category: 'Músculos y Tejidos Blandos' },
  { value: 'cartilago', label: 'Cartílago', category: 'Músculos y Tejidos Blandos' },
  { value: 'menisco', label: 'Menisco', category: 'Músculos y Tejidos Blandos' },
  { value: 'sinovial', label: 'Membrana Sinovial', category: 'Músculos y Tejidos Blandos' },
  
  // Articulaciones
  { value: 'articulacion_temporomandibular', label: 'Articulación Temporomandibular', category: 'Articulaciones' },
  { value: 'articulacion_hombro', label: 'Articulación del Hombro', category: 'Articulaciones' },
  { value: 'articulacion_codo', label: 'Articulación del Codo', category: 'Articulaciones' },
  { value: 'articulacion_muneca', label: 'Articulación de la Muñeca', category: 'Articulaciones' },
  { value: 'articulacion_cadera', label: 'Articulación de la Cadera', category: 'Articulaciones' },
  { value: 'articulacion_rodilla', label: 'Articulación de la Rodilla', category: 'Articulaciones' },
  { value: 'articulacion_tobillo', label: 'Articulación del Tobillo', category: 'Articulaciones' },
  { value: 'articulaciones_intervertebrales', label: 'Articulaciones Intervertebrales', category: 'Articulaciones' },
  { value: 'articulaciones_costovertebrales', label: 'Articulaciones Costovertebrales', category: 'Articulaciones' },
  
  // Áreas Especiales para Patología
  { value: 'region_supraclavicular', label: 'Región Supraclavicular', category: 'Áreas Especiales' },
  { value: 'region_infraclavicular', label: 'Región Infraclavicular', category: 'Áreas Especiales' },
  { value: 'region_retroauricular', label: 'Región Retroauricular', category: 'Áreas Especiales' },
  { value: 'region_preauricular', label: 'Región Preauricular', category: 'Áreas Especiales' },
  { value: 'region_submandibular', label: 'Región Submandibular', category: 'Áreas Especiales' },
  { value: 'region_submental', label: 'Región Submental', category: 'Áreas Especiales' },
  { value: 'region_parotidea', label: 'Región Parotídea', category: 'Áreas Especiales' },
  { value: 'region_epitroclear', label: 'Región Epitroclear', category: 'Áreas Especiales' },
  { value: 'region_poplitea', label: 'Región Poplítea', category: 'Áreas Especiales' },
  { value: 'region_retroperitoneal', label: 'Región Retroperitoneal', category: 'Áreas Especiales' },
  { value: 'espacio_pleural_especial', label: 'Espacio Pleural', category: 'Áreas Especiales' },
  { value: 'espacio_pericardico', label: 'Espacio Pericárdico', category: 'Áreas Especiales' },
  { value: 'espacio_peritoneal', label: 'Espacio Peritoneal', category: 'Áreas Especiales' },
  { value: 'ligamento_ancho', label: 'Ligamento Ancho', category: 'Áreas Especiales' },
  { value: 'parametrio', label: 'Parametrio', category: 'Áreas Especiales' },
  { value: 'paracolpos', label: 'Paracolpos', category: 'Áreas Especiales' },
  { value: 'fondo_saco_douglas', label: 'Fondo de Saco de Douglas', category: 'Áreas Especiales' },
  
  // Regiones Anatómicas Complejas
  { value: 'triangulo_anterior_cuello', label: 'Triángulo Anterior del Cuello', category: 'Regiones Anatómicas Complejas' },
  { value: 'triangulo_posterior_cuello', label: 'Triángulo Posterior del Cuello', category: 'Regiones Anatómicas Complejas' },
  { value: 'fosa_infratemporal', label: 'Fosa Infratemporal', category: 'Regiones Anatómicas Complejas' },
  { value: 'fosa_pterigopalatina', label: 'Fosa Pterigopalatina', category: 'Regiones Anatómicas Complejas' },
  { value: 'seno_cavernoso', label: 'Seno Cavernoso', category: 'Regiones Anatómicas Complejas' },
  { value: 'angulo_pontocerebeloso', label: 'Ángulo Pontocerebeloso', category: 'Regiones Anatómicas Complejas' },
  { value: 'silla_turca', label: 'Silla Turca', category: 'Regiones Anatómicas Complejas' },
  { value: 'canal_vertebral', label: 'Canal Vertebral', category: 'Regiones Anatómicas Complejas' },
  { value: 'foramen_magno', label: 'Foramen Magno', category: 'Regiones Anatómicas Complejas' },
  
  // Misceláneos
  { value: 'multiple', label: 'Múltiples Regiones', category: 'Misceláneos' },
  { value: 'sistémico', label: 'Sistémico', category: 'Misceláneos' },
  { value: 'bilateral', label: 'Bilateral', category: 'Misceláneos' },
  { value: 'otro', label: 'Otro (Especificar)', category: 'Misceláneos' },
  { value: 'no_especificado', label: 'No Especificado', category: 'Misceláneos' },
  { value: 'no_aplica', label: 'No Aplica', category: 'Misceláneos' }
]

// Refs
const inputRef = ref<HTMLInputElement>()
const searchQuery = ref('')
const isOpen = ref(false)
const highlightedIndex = ref(-1)
const isFocused = ref(false)

// Estado interno del componente seleccionado
const selectedRegion = ref(props.modelValue)

// API disponible para futuro uso si es necesario
// const { regions, loadRegions } = useBodyRegionsAPI()

// Opciones disponibles (usar lista local expandida, API como respaldo futuro)
const availableOptions = computed<BodyRegion[]>(() => {
  // Priorizar la lista local expandida para laboratorio de patología
  return bodyRegions
})

// Computed
const errorString = computed(() => {
  return Array.isArray(props.errors) ? props.errors.join(', ') : ''
})

// Filtrar opciones basado en la búsqueda
const filteredOptions = computed((): BodyRegion[] => {
  if (!searchQuery.value.trim()) {
    return availableOptions.value
  }
  
  const query = searchQuery.value.toLowerCase().trim()
  return availableOptions.value.filter(option => {
    const label = option.label.toLowerCase()
    const category = option.category.toLowerCase()
    const value = option.value.toLowerCase()
    
    return (
      label.includes(query) ||
      category.includes(query) ||
      value.includes(query)
    )
  })
})

// Obtener la región seleccionada actual
const currentSelectedRegion = computed((): BodyRegion | null => {
  if (!selectedRegion.value) return null
  
  const option = availableOptions.value.find(opt => opt.label === selectedRegion.value)
  return option || null
})

// Texto que se muestra en el input
const displayText = computed(() => {
  if (isFocused.value) {
    return searchQuery.value
  }
  
  if (selectedRegion.value && currentSelectedRegion.value) {
    return currentSelectedRegion.value.label
  }
  
  return searchQuery.value
})

// Funciones del combobox
const handleFocus = () => {
  isFocused.value = true
  searchQuery.value = ''
  isOpen.value = true
  highlightedIndex.value = -1
}

const handleBlur = () => {
  // Delay para permitir click en opciones
  setTimeout(() => {
    isFocused.value = false
    isOpen.value = false
    
    // Restaurar texto si no hay selección válida
    if (!selectedRegion.value) {
      searchQuery.value = ''
    }
    // Asegurar que el input muestre siempre el label de la selección
    if (selectedRegion.value) {
      nextTick(() => {
        searchQuery.value = displayText.value
      })
    }
  }, 150)
}

const toggleDropdown = () => {
  if (props.disabled) return
  
  if (isOpen.value) {
    inputRef.value?.blur()
  } else {
    inputRef.value?.focus()
  }
}

const selectOption = (option: BodyRegion) => {
  selectedRegion.value = option.label
  searchQuery.value = ''
  isOpen.value = false
  highlightedIndex.value = -1
  
  // Emit events
  emit('update:modelValue', option.label)
  emit('region-selected', option)
  
  // Quitar focus del input
  inputRef.value?.blur()
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (props.disabled) return
  
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      if (!isOpen.value) {
        isOpen.value = true
      }
      highlightedIndex.value = Math.min(highlightedIndex.value + 1, filteredOptions.value.length - 1)
      break
      
    case 'ArrowUp':
      event.preventDefault()
      if (isOpen.value) {
        highlightedIndex.value = Math.max(highlightedIndex.value - 1, -1)
      }
      break
      
    case 'Enter':
      event.preventDefault()
      if (isOpen.value && highlightedIndex.value >= 0 && filteredOptions.value[highlightedIndex.value]) {
        selectOption(filteredOptions.value[highlightedIndex.value])
      }
      break
      
    case 'Escape':
      event.preventDefault()
      isOpen.value = false
      highlightedIndex.value = -1
      inputRef.value?.blur()
      break
      
    case 'Tab':
      isOpen.value = false
      break
  }
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  if (!newValue) {
    selectedRegion.value = ''
    return
  }
  
  // Buscar si el valor es un label (nombre legible)
  const optionByLabel = bodyRegions.find(opt => opt.label === newValue)
  if (optionByLabel) {
    selectedRegion.value = newValue
    return
  }
  
  // Si no es un label, buscar por value (valor simplificado) y convertir a label
  const optionByValue = bodyRegions.find(opt => opt.value === newValue)
  if (optionByValue) {
    selectedRegion.value = optionByValue.label
  } else {
    selectedRegion.value = newValue
  }
}, { immediate: true })

watch(selectedRegion, (newValue) => {
  if (newValue !== props.modelValue) {
    emit('update:modelValue', newValue)
  }
})

// Watcher para la búsqueda - esto permite la búsqueda automática
watch(searchQuery, () => {
  if (isFocused.value && searchQuery.value.trim()) {
    isOpen.value = true
    highlightedIndex.value = -1
  }
})

// Sync display text
watch([displayText, isFocused], () => {
  if (!isFocused.value) {
    nextTick(() => {
      searchQuery.value = displayText.value
    })
  }
})

// Asegurar que el texto se refleje al montar y cuando cambie el modelo desde el padre
onMounted(() => {
  nextTick(() => {
    searchQuery.value = displayText.value
  })
  // API carga comentada - usando lista local expandida
  // if (props.autoLoad && regions.value.length === 0) {
  //   loadRegions()
  // }
})

watch(() => selectedRegion.value, () => {
  if (!isFocused.value) {
    nextTick(() => {
      searchQuery.value = displayText.value
    })
  }
}, { immediate: false })
</script>

<style scoped>
.body-region-combobox {
  position: relative;
}
</style> 