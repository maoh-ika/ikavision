export interface ContractAddresses {
  exeTokenAddress: string
  tokenCategoryStoreAddress: string
  snippetJsAddress: string
  payoutHandlerAddress: string
  jsdocParserAddress: string
}

export const addressesLocalhost: ContractAddresses = {
  exeTokenAddress: '0xa82fF9aFd8f496c3d6ac40E2a0F282E47488CFc9',
  tokenCategoryStoreAddress: '0x67d269191c92Caf3cD7723F116c85e6E9bf55933',
  snippetJsAddress: '0x322813Fd9A801c5507c9de605d63CEA4f2CE6c44',
  payoutHandlerAddress: '0xc3e53F4d16Ae77Db1c982e75a937B9f60FE63690',
  jsdocParserAddress: '0xf5059a5D33d5853360D16C683c16e67980206f36'
}

export const addressesGoerli: ContractAddresses = {
  exeTokenAddress: '0x18934649EAe953bEe53d85Bb9d650072b6FB47C4',
  tokenCategoryStoreAddress: '0x38e7E0b8Efd0c3c642f54DaB71A6754f85Ef96d1',
  snippetJsAddress: '0xeb4F5152cE54a9cb0A271DC537Bc7954e4d0dd4b',
  payoutHandlerAddress: '0x7C61fd26eB1E379A0c3E62d44101B6Ca589B36c7',
  jsdocParserAddress: '0xcba40Dc6249D3b5E59c33a94f09a2880d6EBfdfC'
}
