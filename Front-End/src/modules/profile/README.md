# Profile Module

Este módulo contiene la funcionalidad mejorada de "Mi Perfil" para el sistema LIS PathSys.

## Características

- ✅ Vista de perfil rica con información organizada en tarjetas
- ✅ Modal de edición con validación en tiempo real
- ✅ Soporte para diferentes roles de usuario
- ✅ Diseño responsive y accesible
- ✅ Datos mock para desarrollo y testing
- ✅ Componentes reutilizables y modulares

## Estructura

```
profile/
├── components/           # Componentes Vue
│   ├── ProfileHeader.vue
│   ├── ProfileInfoCards.vue
│   ├── ProfileActions.vue
│   ├── ProfileEditModal.vue
│   ├── ProfileEditForm.vue
│   ├── InfoCard.vue
│   ├── ActionButton.vue
│   └── index.ts
├── composables/          # Composables de Vue
│   └── useProfileAccessibility.ts
├── services/             # Servicios y API
│   └── mockProfileService.ts
├── types/                # Definiciones TypeScript
│   └── userProfile.types.ts
├── views/                # Vistas principales
│   └── MyProfileView.vue
├── styles/               # Estilos CSS
│   └── profile.css
└── routes/               # Configuración de rutas
    └── profileRoutes.ts
```

## Componentes

### ProfileHeader
Muestra la información principal del usuario con avatar, nombre, rol y estado.

**Props:**
- `user: UserProfile` - Datos del usuario
- `isEditable?: boolean` - Si se puede editar (default: true)

**Events:**
- `edit` - Se emite cuando se hace clic en editar

### ProfileInfoCards
Muestra la información del usuario en tarjetas organizadas con iconos.

**Props:**
- `user: UserProfile` - Datos del usuario

### ProfileActions
Botones de acciones rápidas para el perfil.

**Props:**
- `availableActions?: string[]` - Acciones disponibles

**Events:**
- `editProfile` - Editar perfil
- `changePassword` - Cambiar contraseña
- `configureNotifications` - Configurar notificaciones
- `downloadInfo` - Descargar información

### ProfileEditModal
Modal para editar la información del perfil.

**Props:**
- `isOpen: boolean` - Si el modal está abierto
- `user: UserProfile` - Datos del usuario
- `isLoading?: boolean` - Estado de carga
- `errors?: ValidationError[]` - Errores de validación

**Events:**
- `close` - Cerrar modal
- `submit` - Enviar formulario
- `change` - Cambios en el formulario

## Tipos de Usuario

El sistema soporta los siguientes roles:

- **admin** - Administrador del sistema
- **patologo** - Patólogo con especialidad y licencia
- **residente** - Residente con año y supervisor
- **recepcion** - Personal de recepción
- **auxiliar** - Personal auxiliar

## Uso

```vue
<template>
  <MyProfileView />
</template>

<script setup>
import { MyProfileView } from '@/modules/profile/views'
</script>
```

## Datos Mock

Para desarrollo y testing, el módulo incluye `MockProfileService` que proporciona:

- Datos de ejemplo para todos los roles
- Simulación de delays de API
- Validación de formularios
- Manejo de errores simulados

### Cambiar usuario de prueba

```typescript
import { MockProfileService } from '@/modules/profile/services'

// Cambiar a patólogo
MockProfileService.setCurrentUser('patologo')

// Cambiar a residente
MockProfileService.setCurrentUser('residente')
```

## Accesibilidad

El módulo incluye soporte completo para accesibilidad:

- Navegación por teclado
- Soporte para lectores de pantalla
- Respeto por preferencias de movimiento reducido
- Soporte para alto contraste
- Etiquetas ARIA apropiadas

## Responsive Design

- **Mobile** (< 641px): Layout de una columna
- **Tablet** (641px - 1024px): Layout de dos columnas
- **Desktop** (> 1024px): Layout de tres columnas

## Próximas Mejoras

- [ ] Integración con API real
- [ ] Carga de imágenes de perfil
- [ ] Historial de cambios
- [ ] Configuración de notificaciones
- [ ] Exportación de datos
- [ ] Cambio de contraseña
- [ ] Autenticación de dos factores