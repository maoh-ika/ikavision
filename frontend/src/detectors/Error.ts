export enum DetectorErrorCode {
  unknown,
  initFailed,
  notReady,
  busy,
  processingFailed,
  lowAccuracy,
  invalidCommand
}

export class DetectorError extends Error {
  code: DetectorErrorCode

  constructor(code: DetectorErrorCode, msg: string) {
    super(msg)
    this.code = code
  }
}

export const makeError = (err: MessageEvent | ErrorEvent | DetectorErrorCode): DetectorError => {
  if (err instanceof MessageEvent) {
    return new DetectorError(err.data.code, err.data.code)
  } else if (err instanceof ErrorEvent) {
    return new DetectorError(DetectorErrorCode.unknown, err.message)
  } else  {
    return new DetectorError(err, '')
  }
}