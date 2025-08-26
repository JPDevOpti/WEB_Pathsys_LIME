declare module 'jszip' {
  interface JSZipFileOptions {
    binary?: boolean
    date?: Date
    comment?: string
    unixPermissions?: number
    dosPermissions?: number
    createFolders?: boolean
  }

  interface JSZipObject {
    name: string
    dir: boolean
    date: Date
    comment: string
    unixPermissions: number
    dosPermissions: number
    options: JSZipFileOptions
    async(type: string): Promise<any>
    nodeStream(type?: string): any
  }

  interface JSZipFolder {
    file(name: string, data: any, options?: JSZipFileOptions): JSZip
    folder(name: string): JSZipFolder
  }

  interface JSZip {
    file(name: string, data: any, options?: JSZipFileOptions): JSZip
    folder(name: string): JSZipFolder
    remove(name: string): JSZip
    generateAsync(options?: { type: string; compression?: string; compressionOptions?: any }): Promise<Blob>
  }

  class JSZip {
    constructor()
    static loadAsync(data: any): Promise<JSZip>
  }

  export default JSZip
}
