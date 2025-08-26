// Necessary Vue imports for reactive state management, lifecycle, and dependency injection system
import { ref, computed, onMounted, onUnmounted, provide, inject } from 'vue'
import type { Ref } from 'vue'

// Interface that defines the sidebar context structure
interface SidebarContextType {
  isExpanded: Ref<boolean>                      // Controls if the sidebar is expanded
  isMobileOpen: Ref<boolean>                    // Controls if the sidebar is open in mobile view
  isHovered: Ref<boolean>                       // Controls if the mouse is over the sidebar
  activeItem: Ref<string | null>                // Stores the current active item
  openSubmenu: Ref<string | null>               // Stores the current open submenu
  sidebarOpen: Ref<boolean>                     // Combined sidebar state for compatibility
  toggleSidebar: () => void                     // Function to toggle sidebar state
  toggleMobileSidebar: () => void               // Function to toggle mobile state
  setIsHovered: (isHovered: boolean) => void    // Function to set hover state
  setActiveItem: (item: string | null) => void  // Function to set active item
  toggleSubmenu: (item: string) => void         // Function to toggle submenus
}

// Unique symbol for dependency injection
const SidebarSymbol = Symbol()

// Main function that provides the sidebar context
export function useSidebarProvider() {
  // Reactive sidebar states
  const isExpanded = ref(true)                    // Sidebar expanded by default
  const isMobileOpen = ref(false)                 // Mobile sidebar closed by default
  const isMobile = ref(false)                     // Mobile detection state
  const isHovered = ref(false)                    // Hover state
  const activeItem = ref<string | null>(null)     // Active item
  const openSubmenu = ref<string | null>(null)    // Open submenu

  // Function to handle window resize changes
  const handleResize = () => {
    const mobile = window.innerWidth < 768    // Detects if it's mobile view (< 768px)
    isMobile.value = mobile
    if (!mobile) {
      isMobileOpen.value = false              // Closes mobile sidebar on desktop
    }
  }

  // Event setup when mounting the component
  onMounted(() => {
    handleResize()                                  // Checks initial size
    window.addEventListener('resize', handleResize) // Listens for size changes
  })

  // Event cleanup when unmounting
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })

  // Function to toggle sidebar state
  const toggleSidebar = () => {
    if (isMobile.value) {
      isMobileOpen.value = !isMobileOpen.value    // Toggle on mobile
    } else {
      isExpanded.value = !isExpanded.value        // Toggle on desktop
    }
  }

  // Specific function to toggle sidebar on mobile
  const toggleMobileSidebar = () => {
    isMobileOpen.value = !isMobileOpen.value
  }

  // Function to set hover state
  const setIsHovered = (value: boolean) => {
    isHovered.value = value
  }

  // Function to set active item
  const setActiveItem = (item: string | null) => {
    activeItem.value = item
  }

  // Function to toggle submenus
  const toggleSubmenu = (item: string) => {
    openSubmenu.value = openSubmenu.value === item ? null : item
  }

  // Context creation with all states and functions
  const context: SidebarContextType = {
    isExpanded: computed(() => (isMobile.value ? false : isExpanded.value)), // Computed to handle mobile expansion
    isMobileOpen,
    isHovered,
    activeItem,
    openSubmenu,
    sidebarOpen: computed(() => isMobile.value ? isMobileOpen.value : isExpanded.value), // Combined state
    toggleSidebar,
    toggleMobileSidebar,
    setIsHovered,
    setActiveItem,
    toggleSubmenu,
  }

  // Provides context for child components
  provide(SidebarSymbol, context)

  return context
}

// Function to consume sidebar context in child components
export function useSidebar(): SidebarContextType {
  const context = inject<SidebarContextType>(SidebarSymbol)
  if (!context) {
    throw new Error(
      'useSidebar must be used within a component that has SidebarProvider as an ancestor',
    )
  }
  return context
}