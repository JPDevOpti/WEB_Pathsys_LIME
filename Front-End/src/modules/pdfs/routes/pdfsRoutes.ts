import { RouteRecordRaw } from 'vue-router'

export const pdfsRoutes: RouteRecordRaw[] = [
  {
    path: '/pdfs/preview/:caseCode?',
    name: 'pdfs-preview',
    component: () => import('../views/PdfPreviewView.vue'),
    meta: { title: 'Previsualizador de PDFs' }
  }
]
