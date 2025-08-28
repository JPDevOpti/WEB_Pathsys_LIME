import { apiClient } from "@/core/config/axios.config";

export async function testBackendConnection() {
  try {
    await Promise.allSettled([
      apiClient.get("/health"),
      apiClient.get("/casos/estadisticas"),
      apiClient.get("/pacientes/estadisticas"),
      apiClient.get("/casos/", { params: { limite: 5 } }),
    ]);
  } catch (error) {
    throw error;
  }
}
