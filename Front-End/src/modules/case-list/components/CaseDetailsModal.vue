<template>
  <transition name="fade-scale">
    <div 
      v-if="isOpen" 
      :class="['fixed right-0 bottom-0 z-[10000] flex items-center justify-center p-4 bg-black/40 top-16', overlayLeftClass]"
      @click.self="$emit('close')"
    >
      <div class="relative w-full max-w-3xl bg-white rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        <!-- Header fijo -->
        <div class="flex-shrink-0 px-6 py-5 border-b border-gray-200 bg-white rounded-t-2xl">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center">
                  <CaseIcon class="w-5 h-5 text-blue-600" />
                </div>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900">Detalles del Caso</h3>
                <p class="text-gray-600 text-xs mt-1">Información completa del caso</p>
              </div>
            </div>
            
            <!-- Close button -->
            <button
              @click="$emit('close')"
              class="flex-shrink-0 p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-all duration-200 text-gray-600 hover:text-gray-800"
              title="Cerrar"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Contenido scrolleable -->
        <div class="flex-1 overflow-y-auto p-6 space-y-6">
      <!-- Encabezado con icono, código, paciente y badges -->
      <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
        <div class="px-6 py-5 border-b border-gray-200">
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center">
                <CaseIcon class="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
                <div class="min-w-0">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">Detalles del Caso</h3>
                  <div class="flex items-center flex-wrap gap-2">
                    <div class="flex items-center gap-1.5">
                      <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Código</span>
                      <span class="text-lg font-bold text-gray-900 font-mono">{{ caseCode || 'Sin código' }}</span>
                    </div>
                    <div v-if="patientName" class="flex items-center gap-1.5">
                      <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Paciente</span>
                      <span class="text-lg font-semibold text-gray-900">{{ patientName }}</span>
                    </div>
                  </div>
                </div>
                <div class="flex flex-wrap gap-2">
                  <span v-if="caseState" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold"
                        :class="getCaseStatusClass(caseState)">
                    {{ caseState }}
                  </span>
                  <span v-if="casePriority" :class="['inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border', priorityBadgeClasses]">
                    {{ casePriority }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tarjetas de información del paciente -->
        <div class="p-6">
          <div class="grid grid-cols-2 gap-3">
            <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-center space-x-2">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                    <ProfileIcon class="w-4 h-4 text-gray-700" />
                  </div>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Documento</p>
                  <p class="text-sm font-bold text-gray-900 font-mono">{{ patientDocument || '—' }}</p>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-center space-x-2">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                    <CalendarIcon class="w-4 h-4 text-gray-700" />
                  </div>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Edad</p>
                  <p class="text-sm font-bold text-gray-900">{{ patientAge ? `${patientAge} años` : '—' }}</p>
                </div>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3 mt-3">
            <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-center space-x-2">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                    <GerdenIcon class="w-4 h-4 text-gray-700" />
                  </div>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Género</p>
                  <p class="text-sm font-bold text-gray-900 capitalize">{{ patientGender || '—' }}</p>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-center space-x-2">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                    <AtentionTypeIcon class="w-4 h-4 text-gray-700" />
                  </div>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Tipo de atención</p>
                  <p class="text-sm font-bold text-gray-900 capitalize">{{ patientCareType || '—' }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Entidad y Patólogo -->
        <div class="px-6 pb-6 grid grid-cols-1 lg:grid-cols-2 gap-3">
          <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                  <EntityIcon class="w-5 h-5 text-gray-700" />
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">Entidad</p>
                <p class="text-sm font-semibold text-gray-900 break-words">{{ entityName || 'No especificada' }}</p>
                <p v-if="entityCode" class="text-xs text-gray-600 font-mono mt-1 break-all">Código: {{ entityCode }}</p>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                  <DoctorIcon class="w-5 h-5 text-gray-700" />
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">Patólogo Asignado</p>
                <p class="text-sm font-semibold text-gray-900 break-words">{{ caseItem?.pathologist || 'Sin asignar' }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Fechas -->
      <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
        <div class="px-6 py-4 border-b border-gray-200">
          <h4 class="text-lg font-semibold text-gray-900">Información Temporal</h4>
        </div>
        <div class="p-6 grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
            <div class="flex items-center space-x-2">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                  <CalendarIcon class="w-4 h-4 text-gray-700" />
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Fecha de creación</p>
                <p class="text-sm font-bold text-gray-900">{{ caseItem?.receivedAt ? formatDate(caseItem.receivedAt) : 'N/A' }}</p>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
            <div class="flex items-center space-x-2">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                  <CalendarIcon class="w-4 h-4 text-gray-700" />
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Fecha de firma</p>
                <p class="text-sm font-bold text-gray-900">{{ (caseItem?.signedAt || caseItem?.deliveredAt) ? formatDate((caseItem?.signedAt || caseItem?.deliveredAt) as string) : 'Pendiente' }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Submuestras y pruebas -->
      <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center gap-3">
          <div class="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center">
            <SampleIcon class="w-4 h-4 text-blue-600" />
          </div>
          <h4 class="text-lg font-semibold text-gray-900">Muestras y Pruebas</h4>
          <span v-if="caseItem?.subsamples?.length" class="ml-auto inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700">
            {{ caseItem?.subsamples?.length }} submuestra{{ caseItem?.subsamples?.length !== 1 ? 's' : '' }}
          </span>
        </div>
        <div class="p-6">
          <div v-if="caseItem?.subsamples && caseItem.subsamples.length" class="space-y-4">
            <div v-for="(muestra, mIdx) in caseItem.subsamples" :key="mIdx" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 bg-white rounded-md flex items-center justify-center border border-gray-200">
                    <span class="text-xs font-bold text-gray-600">{{ mIdx + 1 }}</span>
                  </div>
                  <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Región del cuerpo</span>
                </div>
                <span class="text-sm font-semibold text-gray-900">{{ muestra.bodyRegion || 'No especificada' }}</span>
              </div>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="(prueba, pIdx) in muestra.tests"
                  :key="pIdx"
                  class="relative inline-flex items-center justify-center bg-white text-gray-700 font-mono text-xs px-3 py-2 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
                  :title="prueba.name && prueba.name !== prueba.id ? prueba.name : ''"
                >
                  {{ prueba.id }} - {{ prueba.name || prueba.id }}
                  <span
                    v-if="prueba.quantity > 1"
                    class="absolute -top-1 -right-1 inline-flex items-center justify-center w-5 h-5 rounded-full bg-blue-100 text-blue-600 text-[10px] font-bold border border-white"
                  >
                    {{ prueba.quantity }}
                  </span>
                </span>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8">
            <div class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <SampleIcon class="w-6 h-6 text-gray-400" />
            </div>
            <p class="text-sm text-gray-500">Sin muestras registradas</p>
          </div>
        </div>
      </div>

      <!-- Resultado del informe -->
      <div v-if="caseItem?.result && caseItem?.status !== 'En proceso'" class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center gap-3">
          <div class="w-8 h-8 bg-green-50 rounded-lg flex items-center justify-center">
            <DocsIcon class="w-4 h-4 text-green-600" />
          </div>
          <h5 class="text-lg font-semibold text-gray-900">Resultado del Informe</h5>
        </div>
        <div class="p-6 space-y-4">
          <div v-if="caseItem.result.method && caseItem.result.method.length > 0" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <div class="flex items-center gap-2 mb-3">
              <div class="w-6 h-6 bg-white rounded-md flex items-center justify-center border border-gray-200">
                <span class="text-xs font-bold text-blue-600">M</span>
              </div>
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Método</span>
            </div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(metodo, index) in caseItem.result.method"
                :key="index"
                class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold bg-blue-50 text-blue-800 border border-blue-100"
              >
                {{ metodo }}
              </span>
            </div>
          </div>

          <div v-if="caseItem.result.macro_result" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <div class="flex items-center gap-2 mb-3">
              <div class="w-6 h-6 bg-white rounded-md flex items-center justify-center border border-gray-200">
                <span class="text-xs font-bold text-purple-600">MA</span>
              </div>
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Resultado Macroscópico</span>
            </div>
            <div class="text-sm text-gray-800 break-words leading-relaxed" v-html="safeMacro"></div>
          </div>

          <div v-if="caseItem.result.micro_result" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <div class="flex items-center gap-2 mb-3">
              <div class="w-6 h-6 bg-white rounded-md flex items-center justify-center border border-gray-200">
                <span class="text-xs font-bold text-indigo-600">MI</span>
              </div>
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Resultado Microscópico</span>
            </div>
            <div class="text-sm text-gray-800 break-words leading-relaxed" v-html="safeMicro"></div>
          </div>

          <div v-if="caseItem.result.diagnosis" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <div class="flex items-center gap-2 mb-3">
              <div class="w-6 h-6 bg-white rounded-md flex items-center justify-center border border-gray-200">
                <span class="text-xs font-bold text-red-600">D</span>
              </div>
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Diagnóstico</span>
            </div>
            <div class="text-sm text-gray-800 break-words leading-relaxed font-medium" v-html="safeDiagnosis"></div>
          </div>

          <div v-if="caseItem.result.observations" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <div class="flex items-center gap-2 mb-3">
              <div class="w-6 h-6 bg-white rounded-md flex items-center justify-center border border-gray-200">
                <span class="text-xs font-bold text-orange-600">O</span>
              </div>
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Observaciones</span>
            </div>
            <div class="text-sm text-gray-800 break-words leading-relaxed" v-html="safeObservations"></div>
          </div>
        </div>
      </div>

      <!-- Diagnósticos clasificados -->
      <div v-if="caseItem?.result && caseItem?.status !== 'En proceso' && (caseItem.result.cie10_diagnosis || caseItem.result.cieo_diagnosis)" class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center gap-3">
          <div class="w-8 h-8 bg-purple-50 rounded-lg flex items-center justify-center">
            <DocsIcon class="w-4 h-4 text-purple-600" />
          </div>
          <h5 class="text-lg font-semibold text-gray-900">Diagnósticos Clasificados</h5>
        </div>
        <div class="p-6 space-y-4">
          <div v-if="caseItem.result.cie10_diagnosis" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-3">
                <div class="w-6 h-6 bg-white rounded-md flex items-center justify-center border border-gray-200">
                  <span class="text-xs font-bold text-blue-600">C10</span>
                </div>
                <span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold bg-blue-50 text-blue-800 border border-blue-100">CIE-10</span>
              </div>
              <span class="text-sm font-bold text-gray-800 bg-white px-3 py-1 rounded-lg border border-gray-200 font-mono">{{ caseItem.result.cie10_diagnosis.code }}</span>
            </div>
            <p class="text-sm text-gray-800 leading-relaxed font-medium">{{ caseItem.result.cie10_diagnosis.name }}</p>
          </div>

          <div v-if="caseItem.result.cieo_diagnosis" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-3">
                <div class="w-6 h-6 bg-white rounded-md flex items-center justify-center border border-gray-200">
                  <span class="text-xs font-bold text-green-600">CO</span>
                </div>
                <span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold bg-green-50 text-green-800 border border-green-100">CIE-O</span>
              </div>
              <span class="text-sm font-bold text-gray-800 bg-white px-3 py-1 rounded-lg border border-gray-200 font-mono">{{ caseItem.result.cieo_diagnosis.code }}</span>
            </div>
            <p class="text-sm text-gray-800 leading-relaxed font-medium">{{ caseItem.result.cieo_diagnosis.name }}</p>
          </div>
        </div>
      </div>

      <!-- Pruebas complementarias -->
      <div v-if="caseItem?.complementary_tests && caseItem.complementary_tests.length > 0" class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center gap-3">
          <div class="w-8 h-8 bg-orange-50 rounded-lg flex items-center justify-center">
            <DocsIcon class="w-4 h-4 text-orange-600" />
          </div>
          <h5 class="text-lg font-semibold text-gray-900">Pruebas Complementarias</h5>
        </div>
        <div class="p-6 space-y-4">
          <div v-for="(test, index) in caseItem.complementary_tests" :key="index">
            <div v-if="test.code && test.name && test.quantity" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-3">
                  <div class="w-6 h-6 bg-white rounded-md flex items-center justify-center border border-gray-200">
                    <span class="text-xs font-bold text-orange-600">{{ index + 1 }}</span>
                  </div>
                  <span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold bg-orange-50 text-orange-800 border border-orange-100">{{ test.code }}</span>
                </div>
                <div v-if="test.quantity > 1" class="flex items-center gap-2">
                  <span class="text-xs text-gray-500 font-medium">Cantidad:</span>
                  <span class="text-xs font-bold text-gray-800 bg-white px-2 py-1 rounded-md border border-gray-200">{{ test.quantity }}</span>
                </div>
              </div>
              <p class="text-sm text-gray-800 leading-relaxed font-medium">{{ test.name }}</p>
            </div>
            <div v-else-if="test.reason" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <div class="flex items-center gap-2 mb-3">
                <div class="w-6 h-6 bg-white rounded-md flex items-center justify-center border border-gray-200">
                  <span class="text-xs font-bold text-orange-600">R</span>
                </div>
                <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Motivo de la solicitud</span>
              </div>
              <p class="text-sm text-gray-800 break-words leading-relaxed">{{ test.reason }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Notas adicionales -->
      <div v-if="props.caseItem?.status === 'Completado' && props.caseItem?.additional_notes && props.caseItem.additional_notes.length > 0" class="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-200 flex items-center gap-2">
          <DocsIcon class="w-4 h-4 text-gray-600" />
          <h5 class="text-sm font-semibold text-gray-800">Notas Adicionales</h5>
          <span v-if="props.caseItem?.additional_notes && props.caseItem.additional_notes.length > 0" class="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {{ props.caseItem.additional_notes.length }} {{ props.caseItem.additional_notes.length === 1 ? 'nota' : 'notas' }}
          </span>
        </div>
        <div class="p-5">
          <div v-if="props.caseItem?.additional_notes && props.caseItem.additional_notes.length > 0" class="space-y-3">
            <div v-for="(nota, index) in props.caseItem.additional_notes" :key="index" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="text-xs text-gray-600 font-medium">{{ formatDate(nota.date, true) }}</span>
                </div>
                <span class="text-xs text-gray-400">#{{ index + 1 }}</span>
              </div>
              <p class="text-sm text-gray-800 break-words leading-relaxed">{{ nota.note }}</p>
            </div>
          </div>
          <div v-else class="text-center py-4">
            <DocsIcon class="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p class="text-sm text-gray-500">No hay notas adicionales para este caso</p>
            <p class="text-xs text-gray-400 mt-1">Puedes agregar notas usando el botón "Notas adicionales"</p>
          </div>
        </div>
        </div>
        </div>

        <!-- Footer fijo -->
        <div class="flex-shrink-0 flex items-center justify-between pt-3 border-t border-gray-200 px-4 pb-4 bg-white rounded-b-2xl">
          <div class="flex items-center space-x-4">
            <PrintPdfButton
              text="Imprimir PDF"
              :caseCode="props.caseItem?.caseCode || props.caseItem?.id"
              :caseData="props.caseItem"
              @pdf-generated="handlePdfGenerated"
              @error="handlePdfError"
              class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-offset-2"
            />
            <button
              v-if="String(props.caseItem?.status) === 'Por entregar' || String(props.caseItem?.status) === 'Completado'"
              @click="showNotesDialog = true"
              class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold border border-orange-500 text-orange-500 bg-white hover:bg-orange-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
            >
              <DocsIcon class="w-3 h-3 mr-1.5" />
              Notas
            </button>
          </div>
          <button
            @click="$emit('close')"
            class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold border border-blue-500 text-blue-500 bg-white hover:bg-blue-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  </transition>

  <NotesDialog
    v-model="showNotesDialog"
    title="Notas adicionales"
    subtitle="Agregar información complementaria al caso"
    textarea-label="Nueva nota"
    textarea-placeholder="Escriba aquí la nueva nota adicional para este caso..."
    help-text="Esta información será agregada al caso como nota adicional con fecha y hora actual"
    confirm-text="Agregar nota"
    cancel-text="Cancelar"
    @confirm="handleNotesConfirm"
    @cancel="handleNotesCancel"
  />
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { sanitizeHtml } from '../../../utils/sanitizeHtml'
import type { Case } from '../types/case.types'
import { DocsIcon } from '@/assets/icons'
import { NotesDialog } from '@/shared/components/ui/feedback'
import { PrintPdfButton } from '@/shared/components/ui/buttons'
import { casesApiService } from '@/modules/cases/services/casesApi.service'
import { useNotifications } from '@/modules/cases/composables/useNotifications'
import { useSidebar } from '@/shared/composables/SidebarControl'
import CaseIcon from '@/assets/icons/CaseIcon.vue'
import EntityIcon from '@/assets/icons/EntityIcon.vue'
import SampleIcon from '@/assets/icons/SampleIcon.vue'
import CalendarIcon from '@/assets/icons/CalendarIcon.vue'
import ProfileIcon from '@/assets/icons/ProfileIcon.vue'
import GerdenIcon from '@/assets/icons/GerdenIcon.vue'
import AtentionTypeIcon from '@/assets/icons/AtentionTypeIcon.vue'
import DoctorIcon from '@/assets/icons/DoctorIcon.vue'

const props = defineProps<{ caseItem: Case | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'edit', c: Case): void; (e: 'preview', c: Case): void; (e: 'notes', c: Case): void }>()

const showNotesDialog = ref(false)
const isOpen = computed(() => !!props.caseItem)
const { showSuccess, showError } = useNotifications()
const { isExpanded, isMobileOpen, isHovered } = useSidebar()

// Computed class for overlay positioning based on sidebar state
const overlayLeftClass = computed(() => {
  const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})

// Normalizadores para mostrar datos con estilo similar a la notificación de caso creado
const activePatient = computed<any>(() => (props.caseItem as any)?.patient || (props.caseItem as any)?.patient_info || {})
const caseCode = computed(() => props.caseItem?.caseCode || (props.caseItem as any)?.case_code || props.caseItem?.id || '')
const caseState = computed(() => props.caseItem?.status || '')
const casePriority = computed(() => translateCasePriority((props.caseItem as any)?.priority))

const patientName = computed(() => activePatient.value.fullName || activePatient.value.name || 'No registrado')
const patientDocument = computed(() => activePatient.value.id || activePatient.value.patient_code || '')
const patientAge = computed(() => activePatient.value.age || '')
const patientGender = computed(() => normalizeGender(activePatient.value.sex || activePatient.value.gender))
const patientCareType = computed(() => normalizeCareType(activePatient.value.attentionType || activePatient.value.care_type))

const entityName = computed(() => activePatient.value.entity || (props.caseItem as any)?.entity || '')
const entityCode = computed(() => activePatient.value.entityCode || activePatient.value.entity_code || '')

// Contenido HTML seguro para mostrar formato en resultados
const safeMacro = computed(() => sanitizeHtml(props.caseItem?.result?.macro_result || ''))
const safeMicro = computed(() => sanitizeHtml(props.caseItem?.result?.micro_result || ''))
const safeDiagnosis = computed(() => sanitizeHtml(props.caseItem?.result?.diagnosis || ''))
const safeObservations = computed(() => sanitizeHtml(props.caseItem?.result?.observations || ''))

const priorityBadgeClasses = computed(() => {
  const base = 'border-1'
  const key = (casePriority.value || '').toString().trim().toLowerCase()
  if (key === 'normal') return `${base} bg-green-50 text-green-700 border-green-100`
  if (['prioritario','priority','urgente','urgent'].includes(key)) return `${base} bg-red-50 text-red-700 border-red-100`
  return `${base} bg-gray-50 text-gray-700 border-gray-200`
})

const formatDate = (dateString: string, includeTime: boolean = false) => {
  if (!dateString) return 'N/A'
  const d = new Date(dateString)
  
  if (includeTime) {
    return d.toLocaleString('es-ES', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function normalizeGender(value?: string | null) {
  if (!value) return ''
  const text = value.toString().trim().toLowerCase()
  if (text.startsWith('masc') || text === 'm') return 'masculino'
  if (text.startsWith('fem') || text === 'f') return 'femenino'
  return value
}

function normalizeCareType(value?: string | null) {
  if (!value) return ''
  const text = value.toString().trim().toLowerCase()
  if (text.startsWith('ambu')) return 'ambulatorio'
  if (text.startsWith('hosp')) return 'hospitalizado'
  return value
}

function translateCasePriority(value?: string | null) {
  if (!value) return ''
  const map: Record<string, string> = { normal: 'Normal', priority: 'Prioritario', prioritario: 'Prioritario', urgente: 'Urgente' }
  const key = value.toString().trim().toLowerCase()
  return map[key] || value
}

const handleNotesConfirm = async (notes: string) => {
  try {
    const caseCode = props.caseItem?.caseCode || (props.caseItem as any)?.caso_code
    if (!caseCode) {
      showError('Error', 'No se pudo identificar el caso')
      return
    }

    const nuevaNota = {
      date: new Date().toISOString(),
      note: notes
    }
    
    const todasLasNotas = [
      ...(props.caseItem?.additional_notes || []),
      nuevaNota
    ]

    const updateData = {
      additional_notes: todasLasNotas
    }
    
    await casesApiService.updateCase(caseCode, updateData)
    showSuccess('Nota agregada', 'La nota adicional se ha guardado exitosamente')
    showNotesDialog.value = false
    
    const casoActualizado = {
      ...props.caseItem,
      additional_notes: todasLasNotas
    }
    
    emit('notes', casoActualizado as any)
  } catch (error: any) {
    showError('Error', error.message || 'No se pudo guardar la nota adicional')
  }
}

const handleNotesCancel = () => {
  showNotesDialog.value = false
}

const handlePdfGenerated = (pdfBlob: Blob) => {
  console.log('PDF generado exitosamente:', pdfBlob.size, 'bytes')
}

const handlePdfError = (error: string) => {
  console.error('Error al generar PDF:', error)
}

const getCaseStatusClass = (status: string) => {
  const statusClasses = {
    // Database states (Spanish with spaces)
    'En proceso': 'bg-blue-100 text-blue-800',
    'Pendiente': 'bg-yellow-100 text-yellow-800',
    'Completado': 'bg-green-100 text-green-800',
    'Entregado': 'bg-gray-100 text-gray-800',
    'Cancelado': 'bg-red-100 text-red-800',
    // Legacy states (for backward compatibility)
    'pendiente': 'bg-yellow-100 text-yellow-800',
    'en_proceso': 'bg-blue-100 text-blue-800',
    'completado': 'bg-green-100 text-green-800',
    'entregado': 'bg-gray-100 text-gray-800',
    'cancelado': 'bg-red-100 text-red-800'
  }
  return statusClasses[status as keyof typeof statusClasses] || 'bg-gray-100 text-gray-800'
}

</script>