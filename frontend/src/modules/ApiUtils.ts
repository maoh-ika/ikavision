import store from '@/store'
import type { AnalysisJob } from '@/modules/AnalysisJobApi'
import { analysisResultSammaryRequestProcessor } from '@/modules/AnalysisResultRequestProcessor'

export const requestCompletedAnalysisSammaries = async (userId: string): Promise<void> => {
    const jobs = await store.dispatch('analysisJob/fetchJobs', {userId: userId, state: 'completed'}) as AnalysisJob[]
    jobs.sort((a, b) => a.createdAt - b.createdAt)
    const completedIds = jobs.map(job => job.jobId)
    analysisResultSammaryRequestProcessor.add({
        userId: userId,
        jobIds: completedIds
    })
}