import type { Commit } from 'vuex'
import type { AnalysisJob, AnalysisJobState } from '@/modules/AnalysisJobApi'
import { queryAnalysisJobs, getAnaysisJob } from '@/modules/AnalysisJobApi'

export interface JobRequestParams {
  userId: string
  jobId: string
}

interface State {
  jobs: {[key:string]:AnalysisJob} // jobId to job
  loaded: {[key:string]:boolean} // userId to bool
  processingJobs: {[key:string]:AnalysisJob} // jobId to job
  processingJobLoaded: {[key:string]:boolean} // userId to bool
}

const initialState: State = {
  jobs: {},
  loaded: {},
  processingJobs: {},
  processingJobLoaded: {}
}

export default {
  namespaced: true,
  state: initialState,
  getters: {
    getJobs: (state: State) => (userId: string): AnalysisJob[] => {
      return Object.values(state.jobs).filter(job => job.userId === userId)
    },
    getProcessingJobs: (state: State) => (userId: string): AnalysisJob[] => {
      return Object.values(state.processingJobs).filter(job => job.userId === userId)
    },
    getJob: (state: State) => (jobId: string): AnalysisJob | undefined => {
      return state.jobs[jobId]
    }
  },
  mutations: {
    setJobs(state: State, payload: { userId: string, jobs: AnalysisJob[] }): void {
      payload.jobs.forEach(job => state.jobs[job.jobId] = job)
      state.loaded[payload.userId] = true
    },
    setProcessingJobs(state: State, payload: { userId: string, jobs: AnalysisJob[] }): void {
      payload.jobs.forEach(job => state.processingJobs[job.jobId] = job)
      state.processingJobLoaded[payload.userId] = true
    },
    addJob(state: State, job: AnalysisJob): void {
      state.jobs[job.jobId] = job
    }
  },
  actions: {
    async fetchJobs(context: { state: State, commit: Commit, getters: any }, payload: {userId: string, state?: AnalysisJobState}): Promise<AnalysisJob[]> {
      let isLoaded = context.state.loaded[payload.userId]
      if (isLoaded) {
        return context.getters['getJobs'](payload.userId)
      }

      const jobs = await queryAnalysisJobs(payload.userId, payload.state)
      context.commit('setJobs', { userId: payload.userId, jobs: jobs })
      return jobs
    },
    async fetchProcessingJobs(context: { state: State, commit: Commit, getters: any }, payload: {userId: string}): Promise<AnalysisJob[]> {
      let isLoaded = context.state.processingJobLoaded[payload.userId]
      if (isLoaded) {
        return context.getters['getProcessingJobs'](payload.userId)
      }

      const jobs = await queryAnalysisJobs(payload.userId, 'processing')
      context.commit('setProcessingJobs', { userId: payload.userId, jobs: jobs })
      return jobs
    },
    async fetchJob(context: { state: State, commit: Commit, getters: any }, payload: JobRequestParams): Promise<AnalysisJob> {
      let job = context.getters['getJob'](payload.jobId)
      if (job !== undefined) {
        return job
      }

      job = await getAnaysisJob(payload.userId, payload.jobId)
      context.commit('addJob', job)
      return job
    }
  }
}
