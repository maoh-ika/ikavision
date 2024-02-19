export class ApiError {
    readonly msg: string
    readonly code: number

    constructor(apiError: any) {
        this.msg = apiError.msg
        this.code = apiError.code
    }
}