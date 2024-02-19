import store from '@/store'
import { QueuedRequestProcessor } from './QueuedRequestProcessor'
import type { SammaryRequestParams } from '@/store/AnalysisResultStore'
import { chunkArray } from '@/modules/Utils'

export class AnalysisResultSammaryRequestProcessor extends QueuedRequestProcessor<SammaryRequestParams> {
  override add(request: SammaryRequestParams, success?: Function, error?: Function): void {
    chunkArray(request.jobIds, 5).forEach(jobIds => super.add({
      userId: request.userId,
      jobIds: jobIds
    }))
  }
  
  override async _request(params: SammaryRequestParams): Promise<any> {
    return await store.dispatch('analysisResult/fetchSammaries', params)
  }
}

export const analysisResultSammaryRequestProcessor = new AnalysisResultSammaryRequestProcessor(200)
analysisResultSammaryRequestProcessor.start()