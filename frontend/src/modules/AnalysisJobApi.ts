import { invokeApi } from './ApiGateway'
import { ApiError } from './ApiError'

export interface CreateJobRes {
    jobId: string
    userId: string
    jobName: string
    jobState: string
    createdAt: number
    battleDate: number
    uploadUrl: string
    expirationTime: number
    movieSource: MovieSource
    channelId?: string
    videoId?: string
    thumbnailUrl: string
}

export interface DownnloadUrlRes {
    downloadUrl: string
    expirationTime: number
}

export type AnalysisJobState =
    'created' |
    'movieUploaded' |
    'processing' |
    'completed' |
    'failed ' |
    'cancelled' |
    'invalid'

export type MovieSource = 
    'user' |
    'youtube'

export interface AnalysisJob {
    userId: string
    jobId: string
    jobName: string 
    state: AnalysisJobState
    movieSource: MovieSource
    channelId?: string
    videoId?: string
    battleDate: number
    thumbnailUrl: string
    createdAt: number
}

export type ProgressCallback = (prog: number) => void

const toJobState = (state: string): AnalysisJobState => {
    switch (state) {
        case 'movie_uploaded': return 'movieUploaded'
        default: return state as AnalysisJobState
    }
}

const toJob = (res: any): AnalysisJob => {
    return {
        jobId: res.job_id,
        userId: res.user_id,
        jobName: res.job_name,
        state: toJobState(res.job_state),
        battleDate: res.battle_date * 1000,
        createdAt: res.created_at,
        movieSource: res.movie_source,
        channelId: res.channel_id,
        videoId: res.video_id,
        thumbnailUrl: res.thumbnail_url
    }
}

const invokeAnalysisJobApi = async (payload: any): Promise<any> => {
    const res = await invokeApi('/analysis_job', payload)
    if ('error' in res) {
        throw new ApiError(res.error)
    }
    return res
}

const createJobApi = async (userId: string, jobName: string, battleDate: number, format: string): Promise<CreateJobRes> => {
    const payload = {
        method: 'create_job',
        user_id: userId,
        job_name: jobName,
        format: format,
        movie_source: 'user',
        battle_date: Math.round(battleDate / 1000)
    }
    const res = await invokeAnalysisJobApi(payload)
    return {
        uploadUrl: res['upload_url'],
        jobId: res['job_id'],
        userId: res['user_id'],
        jobName: res['job_name'],
        jobState: res['job_state'],
        battleDate: battleDate,
        createdAt: res['created_at'],
        expirationTime: res['expiration_time'],
        movieSource: res['movie_source'],
        channelId: res['channel_id'],
        videoId: res['video_id'],
        thumbnailUrl: res['thumbnail_url']
    }
}

export const generateDownloadUrl = async (userId: string, jobId: string): Promise<DownnloadUrlRes> => {
    const payload = {
        method: 'download_url',
        user_id: userId,
        job_id: jobId
    }
    const res = await invokeAnalysisJobApi(payload)
    return {
        downloadUrl: res['download_url'],
        expirationTime: res['expiration_time']
    }
}

export const createAnalysisJob = async (userId: string, jobName: string, battleDate: number, movFile: File, callback: ProgressCallback=(prog) => {}): Promise<AnalysisJob> => {
    const format = movFile.name.split('.').pop()?.toLowerCase()
    if (format === undefined) {
        throw new ApiError({
            msg: 'invalid format',
            code: 403
        })
    }
    const jobRes = await createJobApi(userId, jobName, battleDate, format)

    await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest()
        xhr.upload.addEventListener('progress', (event) => {
            if (event.lengthComputable) {
                const progress = (event.loaded / event.total) * 100
                callback(progress)
            }
        })

        xhr.onreadystatechange = () => {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    resolve(true)
                } else {
                    reject(new ApiError({
                        msg: 'upload failed',
                        code: xhr.status
                    }))
                }
            }
        }

        xhr.open('PUT', jobRes.uploadUrl, true)
        xhr.setRequestHeader('Content-Type', movFile.type)
        xhr.send(movFile)
    })

    return {
        userId: userId,
        jobId: jobRes.jobId,
        jobName: jobRes.jobName,
        state: toJobState(jobRes.jobState),
        battleDate: battleDate,
        createdAt: jobRes.createdAt,
        movieSource: jobRes.movieSource,
        channelId: jobRes.channelId,
        videoId: jobRes.videoId,
        thumbnailUrl: jobRes.thumbnailUrl
    }
}

export const queryAnalysisJobs = async (userId: string, state?: AnalysisJobState): Promise<AnalysisJob[]> => {
    const payload = {
        method: 'query',
        user_id: userId,
        state: state
    }
    const res = await invokeAnalysisJobApi(payload) as any[]
    return res.map(r => toJob(r))
}

export const queryAnalysisJobIds = async (userId: string, state: AnalysisJobState): Promise<string[]> => {
    const payload = {
        method: 'query_job_ids',
        user_id: userId,
        state: state
    }
    const res = await invokeAnalysisJobApi(payload) as any[]
    return res.map(job => job.job_id)
}

export const getAnaysisJob = async (userId: string, jobId: string): Promise<AnalysisJob> => {
    const payload = {
        method: 'get',
        user_id: userId,
        job_id: jobId
    }
    const res = await invokeAnalysisJobApi(payload) as any[]
    return toJob(res)
}