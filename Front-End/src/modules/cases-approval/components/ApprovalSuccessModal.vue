<template>
  <teleport to="body">
    <CaseSuccessCard
      v-if="visible && !!caseData"
      :visible="visible"
      :case-data="caseData"
      :close-on-esc="closeOnEsc"
      :mode="mode"
      @close="$emit('close')"
    />
  </teleport>
</template>

<script setup lang="ts">
import CaseSuccessCard from '@/shared/components/ui/feedback/CaseSuccessCard.vue'

interface Props {
  visible: boolean
  caseData: any
  closeOnEsc?: boolean
  mode?: 'created' | 'updated'
}

withDefaults(defineProps<Props>(), {
  closeOnEsc: true,
  mode: 'created'
})

defineEmits<{ (e: 'close'): void }>()
</script>
