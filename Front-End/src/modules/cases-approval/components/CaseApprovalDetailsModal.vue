<template>
	<transition enter-active-class="transition ease-out duration-300" enter-from-class="opacity-0 transform scale-95" enter-to-class="opacity-100 transform scale-100" leave-active-class="transition ease-in duration-200" leave-from-class="opacity-100 transform scale-100" leave-to-class="opacity-0 transform scale-95">
		<div
			v-if="caseItem"
			:class="[
				'fixed right-0 bottom-0 z-[9999] flex items-end sm:items-center justify-center p-2 sm:p-4 bg-black/40',
				'top-16',
				overlayLeftClass
			]"
			@click.self="$emit('close')"
		>
			<div class="relative bg-white w-full max-w-5xl rounded-t-2xl sm:rounded-2xl shadow-2xl h-[90vh] sm:h-auto sm:max-h-[92vh] overflow-y-auto overflow-x-hidden">
				<!-- Header -->
				<div class="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-4 rounded-t-2xl flex items-center justify-between">
					<div class="flex flex-col">
						<h3 class="text-xl font-semibold text-gray-900">Revisión de Solicitud de Aprobación</h3>
						<p class="text-xs text-gray-500" v-if="caseItem.approval_code">Código: {{ caseItem.approval_code }}</p>
					</div>
					<button @click="$emit('close')" class="text-gray-400 hover:text-gray-600" aria-label="Cerrar">✕</button>
				</div>

				<div class="p-6 space-y-6">
					<!-- Información de la solicitud -->
					<section class="grid grid-cols-2 lg:grid-cols-4 gap-4 bg-gray-50 rounded-xl p-4">
						<div>
							<p class="text-xs text-gray-500">Código de Solicitud</p>
							<p class="text-sm font-medium text-gray-900">{{ caseItem.approval_code || 'N/A' }}</p>
						</div>
						<div>
							<p class="text-xs text-gray-500">Caso Original</p>
							<p class="text-sm font-medium text-gray-900">{{ caseItem.original_case_code || 'N/A' }}</p>
						</div>
						<div>
							<p class="text-xs text-gray-500">Estado</p>
							<p class="text-sm font-medium text-gray-900">{{ getStatusText(caseItem.approval_state) }}</p>
						</div>
						<div>
							<p class="text-xs text-gray-500">Fecha de Solicitud</p>
							<p class="text-sm font-medium text-gray-900">{{ formatDate(caseItem.created_at) }}</p>
						</div>
					</section>

					<!-- Información adicional -->
					<section class="grid grid-cols-2 lg:grid-cols-3 gap-4 bg-gray-50 rounded-xl p-4">
						<div>
							<p class="text-xs text-gray-500">Fecha de Creación</p>
							<p class="text-sm font-medium text-gray-900">{{ formatDate(caseItem.created_at) }}</p>
						</div>
						<div>
							<p class="text-xs text-gray-500">Última Actualización</p>
							<p class="text-sm font-medium text-gray-900">{{ formatDate(caseItem.updated_at) }}</p>
						</div>
						<div>
							<p class="text-xs text-gray-500">Patólogo Asignado</p>
							<p class="text-sm font-medium text-gray-900">{{ getPathologistName() }}</p>
						</div>
					</section>

					<!-- Motivo de la solicitud -->
					<section v-if="getReason()" class="bg-gray-50 rounded-xl p-4 space-y-2">
						<h5 class="text-xs font-medium text-gray-600">Motivo de la Solicitud</h5>
						<p class="text-sm text-gray-800 whitespace-pre-line">{{ getReason() }}</p>
					</section>

					<!-- Editor de Pruebas Complementarias -->
					<section class="bg-gray-50 rounded-xl p-4 space-y-3">
						<div class="flex items-center justify-between">
							<h5 class="text-xs font-medium text-gray-600">Pruebas Complementarias Solicitadas</h5>
							<BaseButton
								v-if="!isEditingTests"
								variant="outline"
								size="xs"
								text="Editar"
								custom-class="bg-white border-blue-600 text-blue-600 hover:bg-blue-50"
								@click="startEditingTests"
							/>
						</div>
            
						<div v-if="!isEditingTests">
							<div v-if="getComplementaryTests()?.length" class="border border-gray-200 rounded-lg p-3 bg-white">
								<div class="flex flex-wrap gap-2">
									<span
										v-for="(test, idx) in getComplementaryTests()"
										:key="idx"
										class="relative inline-flex items-center justify-center bg-blue-100 text-blue-700 font-mono text-[11px] pl-2 pr-6 py-0.5 rounded border text-nowrap"
										:title="test.name"
									>
										{{ test.code }} - {{ test.name }}
										<span
											v-if="test.quantity > 1"
											class="absolute -top-1 -right-1 inline-flex items-center justify-center w-4 h-4 rounded-full bg-blue-600 text-white text-[10px] font-bold"
										>
											{{ test.quantity }}
										</span>
									</span>
								</div>
							</div>
							<div v-else class="text-xs text-gray-500">Sin pruebas complementarias</div>
						</div>

						<div v-else class="space-y-3">
							<div v-if="editableTests.length === 0" class="text-center py-4">
								<p class="text-sm text-gray-500">No hay pruebas complementarias configuradas</p>
								<p class="text-xs text-gray-400 mt-1">Las pruebas se configuran al crear la solicitud</p>
							</div>
              
							<div v-else class="space-y-2">
								<div
									v-for="(test, index) in editableTests"
									:key="index"
									class="flex items-center gap-2 p-3 bg-white border border-gray-200 rounded-lg"
								>
									<div class="flex-1">
										<p class="text-sm font-medium text-gray-900">{{ test.code }} - {{ test.name }}</p>
									</div>
									<div class="flex items-center gap-2">
										<label class="text-xs text-gray-500">Cantidad:</label>
										<input
											v-model.number="test.quantity"
											type="number"
											min="1"
											max="20"
											class="w-16 px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
										/>
										<button
											@click="removeTest(index)"
											class="p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
											title="Eliminar prueba"
										>
											<svg class="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
												<path fill-rule="evenodd" d="M10 8.586l4.95-4.95 1.414 1.414L11.414 10l4.95 4.95-1.414 1.414L10 11.414l-4.95 4.95-1.414-1.414L8.586 10l-4.95-4.95L5.05 3.636 10 8.586z" clip-rule="evenodd" />
											</svg>
										</button>
									</div>
								</div>
							</div>
              
							<div class="flex gap-2 pt-2">
								<BaseButton
									variant="outline"
									size="sm"
									text="Guardar Cambios"
									loading-text="Guardando..."
									custom-class="bg-white border-green-600 text-green-600 hover:bg-green-50"
									:loading="savingTests"
									:disabled="editableTests.length === 0"
									@click="saveTests"
								/>
								<BaseButton
									variant="outline"
									size="sm"
									text="Cancelar"
									custom-class="bg-white border-gray-600 text-gray-600 hover:bg-gray-50"
									:disabled="savingTests"
									@click="cancelEditingTests"
								/>
							</div>
						</div>
					</section>

				</div>

				<!-- Footer -->
				<div class="sticky bottom-0 bg-white border-t border-gray-200 px-4 sm:px-6 py-3 sm:py-4 rounded-b-2xl">
					<div class="flex justify-end">
						<BaseButton
							variant="outline"
							size="sm"
							text="Cerrar"
							custom-class="bg-white border-gray-600 text-gray-600 hover:bg-gray-50"
							@click="$emit('close')"
						/>
					</div>
				</div>
			</div>
		</div>
	</transition>
	<!-- Dialogo de confirmación eliminación prueba nueva (fuera del <transition> para evitar múltiples hijos) -->
	<ConfirmDialog
		v-model="showConfirm"
		title="Eliminar prueba"
		:subtitle="pendingRemoval ? pendingRemoval.test?.name || pendingRemoval.test?.id : ''"
		message="Esta acción eliminará la prueba asignada. ¿Desea continuar?"
		confirm-text="Eliminar"
		cancel-text="Cancelar"
		@confirm="confirmRemoval"
		@cancel="cancelRemoval"
	/>
</template>

<script setup lang="ts">
import { BaseButton } from '@/shared/components'
import { ConfirmDialog } from '@/shared/components/ui/feedback'
import { computed, ref } from 'vue'
import { useSidebar } from '@/shared/composables/SidebarControl'
import type { ApprovalRequestResponse } from '@/shared/services/approval.service'

interface Props {
	caseItem: ApprovalRequestResponse | null
}

const props = withDefaults(defineProps<Props>(), {
})

const emit = defineEmits<{
	(e: 'close'): void
	(e: 'testsUpdated', tests: any[]): void
}>()

function formatDate(dateString?: string) {
	if (!dateString) return 'N/A'
	const d = new Date(dateString)
	return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const { isExpanded, isMobileOpen, isHovered } = useSidebar()
const overlayLeftClass = computed(() => {
	const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
	return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})

const showConfirm = ref(false)
const pendingRemoval = ref<{ index: number; test: any } | null>(null)
const isEditingTests = ref(false)
const editableTests = ref<any[]>([])
const savingTests = ref(false)


function confirmRemoval() {
	if (pendingRemoval.value !== null) {
		// Eliminar solo la prueba seleccionada del array editable
		editableTests.value.splice(pendingRemoval.value.index, 1)
	}
	showConfirm.value = false
	pendingRemoval.value = null
}

function cancelRemoval() {
	showConfirm.value = false
	pendingRemoval.value = null
}

const getStatusText = (status?: string): string => {
	if (!status) return 'N/A'
	const statusMap: Record<string, string> = {
		'request_made': 'Solicitud Hecha',
		'pending_approval': 'Pendiente de Aprobación',
		'approved': 'Aprobado',
		'rejected': 'Rechazado'
	}
	return statusMap[status] || status
}

const getPathologistName = (): string => {
	if (!props.caseItem?.approval_info?.assigned_pathologist) {
		return 'Sin asignar'
	}
	return props.caseItem.approval_info.assigned_pathologist.name || 'Sin asignar'
}

const getReason = (): string | null => {
	return props.caseItem?.approval_info?.reason || null
}

const getComplementaryTests = () => {
	return props.caseItem?.complementary_tests || []
}

const startEditingTests = () => {
	editableTests.value = [...(getComplementaryTests() || [])]
	isEditingTests.value = true
}

const cancelEditingTests = () => {
	isEditingTests.value = false
	editableTests.value = []
}

const removeTest = (index: number) => {
	const test = editableTests.value[index]
	if (!test) return
  
	pendingRemoval.value = { index, test }
	showConfirm.value = true
}

const saveTests = async () => {
	if (!props.caseItem) return
  
	savingTests.value = true
	try {
		emit('testsUpdated', editableTests.value)
		isEditingTests.value = false
		editableTests.value = []
	} catch (error) {
		console.error('Error al guardar pruebas:', error)
	} finally {
		savingTests.value = false
	}
}
</script>

