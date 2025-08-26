import { ref, onMounted, onUnmounted } from "vue";

export function useProfileAccessibility() {
  const isReducedMotion = ref(false);
  const isHighContrast = ref(false);
  const screenSize = ref<"mobile" | "tablet" | "desktop">("desktop");

  // Check for user preferences
  const checkAccessibilityPreferences = () => {
    // Check for reduced motion preference
    const reducedMotionQuery = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    );
    isReducedMotion.value = reducedMotionQuery.matches;

    // Check for high contrast preference
    const highContrastQuery = window.matchMedia("(prefers-contrast: high)");
    isHighContrast.value = highContrastQuery.matches;

    // Check screen size
    updateScreenSize();
  };

  const updateScreenSize = () => {
    const width = window.innerWidth;
    if (width < 641) {
      screenSize.value = "mobile";
    } else if (width < 1025) {
      screenSize.value = "tablet";
    } else {
      screenSize.value = "desktop";
    }
  };

  // Keyboard navigation helpers
  const trapFocus = (element: HTMLElement) => {
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ) as NodeListOf<HTMLElement>;

    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== "Tab") return;

      if (e.shiftKey) {
        if (document.activeElement === firstFocusable) {
          lastFocusable.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastFocusable) {
          firstFocusable.focus();
          e.preventDefault();
        }
      }
    };

    element.addEventListener("keydown", handleTabKey);
    firstFocusable?.focus();

    return () => {
      element.removeEventListener("keydown", handleTabKey);
    };
  };

  // Announce changes to screen readers
  const announceToScreenReader = (
    message: string,
    priority: "polite" | "assertive" = "polite"
  ) => {
    const announcement = document.createElement("div");
    announcement.setAttribute("aria-live", priority);
    announcement.setAttribute("aria-atomic", "true");
    announcement.className = "sr-only";
    announcement.textContent = message;

    document.body.appendChild(announcement);

    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  };

  // Get appropriate grid classes based on screen size
  const getGridClasses = () => {
    switch (screenSize.value) {
      case "mobile":
        return "profile-grid-mobile grid-cols-1";
      case "tablet":
        return "profile-grid-tablet grid-cols-2";
      default:
        return "profile-grid-desktop grid-cols-3";
    }
  };

  // Get transition classes based on motion preference
  const getTransitionClasses = () => {
    return isReducedMotion.value
      ? ""
      : "profile-transition transition-all duration-200";
  };

  // Event listeners
  let resizeListener: (() => void) | null = null;
  let motionListener: ((e: MediaQueryListEvent) => void) | null = null;
  let contrastListener: ((e: MediaQueryListEvent) => void) | null = null;

  onMounted(() => {
    checkAccessibilityPreferences();

    // Set up resize listener
    resizeListener = () => updateScreenSize();
    window.addEventListener("resize", resizeListener);

    // Set up media query listeners
    const reducedMotionQuery = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    );
    motionListener = (e) => {
      isReducedMotion.value = e.matches;
    };
    reducedMotionQuery.addEventListener("change", motionListener);

    const highContrastQuery = window.matchMedia("(prefers-contrast: high)");
    contrastListener = (e) => {
      isHighContrast.value = e.matches;
    };
    highContrastQuery.addEventListener("change", contrastListener);
  });

  onUnmounted(() => {
    if (resizeListener) {
      window.removeEventListener("resize", resizeListener);
    }
    if (motionListener) {
      const reducedMotionQuery = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
      );
      reducedMotionQuery.removeEventListener("change", motionListener);
    }
    if (contrastListener) {
      const highContrastQuery = window.matchMedia("(prefers-contrast: high)");
      highContrastQuery.removeEventListener("change", contrastListener);
    }
  });

  return {
    isReducedMotion,
    isHighContrast,
    screenSize,
    trapFocus,
    announceToScreenReader,
    getGridClasses,
    getTransitionClasses,
  };
}
