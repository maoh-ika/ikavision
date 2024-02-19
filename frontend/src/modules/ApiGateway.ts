import { config } from '@/modules/Config'
import { ApiError } from './ApiError'

export const invokeApi = async (path: string, payload: any, method: string='PUT', headers: any={}): Promise<any> => {
    const url = `${config.aws.battleAnalyzerEndpoint}${path}`
    try {
        const response = await fetch(url,  {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                ...headers
            },
            body: JSON.stringify(payload)
        })
        if (!response.ok) {
            throw new ApiError({
                msg: response.statusText,
                code: response.status
            })
        }
        return await response.json()
    } catch (err: any) {
        throw new ApiError({
            msg: 'api error',
            code: 500
        })
    }
}