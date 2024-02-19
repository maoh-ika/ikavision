import store from '@/store'
import { QueuedRequestProcessor } from './QueuedRequestProcessor'
import type { JobRequestParams } from '@/store/AnalysisJobStore'

export class AnalysisJobRequestProcessor extends QueuedRequestProcessor<JobRequestParams> {
  override async _request(params: JobRequestParams): Promise<any> {
    return await store.dispatch('analysisJob/fetchJob', params)
  }
}

export const analysisJobRequestProcessor = new AnalysisJobRequestProcessor(200)
analysisJobRequestProcessor.start()