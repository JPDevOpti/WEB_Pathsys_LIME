declare module 'axios' {
  export type AxiosInstance = any
  export type AxiosRequestConfig = any
  export type AxiosResponse<T = any> = { data: T } & any

  const axios: any
  export default axios
}

