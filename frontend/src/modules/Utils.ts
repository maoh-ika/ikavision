import { sha256 } from 'js-sha256'

export const chunkArray = <T>(array: T[], chunkSize: number): T[][] => {
    const result: T[][] = [];
    const length = array.length;
    let index = 0;

    while (index < length) {
        result.push(array.slice(index, index + chunkSize));
        index += chunkSize;
    }

    return result;
}

export const remToPt = (rem: number): number => {
    return rem * parseFloat(getComputedStyle(document.documentElement).fontSize)
}

export const toMMSS = (valueInSecond: number, minUnit: string=':', secUnit: string=''): string => {
    const minutes = Math.floor(valueInSecond / 60);
    const seconds = Math.floor(valueInSecond % 60);
    return `${minutes.toString().padStart(2, '0')}${minUnit}${seconds.toString().padStart(2, '0')}${secUnit}`;
}

export const toMMDD = (timestamp: number): string => {
    const date = new Date(timestamp)
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    return `${month}/${day}`
}

export const toYYYYMMDD = (timestamp: number, delim: string='/'): string => {
    const date = new Date(timestamp)
    const year = date.getFullYear().toString().padStart(4, '0')
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    return [year.toString(), month.toString(), day.toString()].join(delim)
}

export const toMMDDHHmm = (timestamp: number): string => {
    const date = new Date(timestamp)
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    return `${month}/${day} ${hours}:${minutes}`
}

export const toYYYYMMDDHHmmss = (timestamp: number): string => {
    const date = new Date(timestamp)
    const year = date.getFullYear().toString().padStart(4, '0')
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    const seconds = date.getSeconds().toString().padStart(2, '0')
    return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`
}

export const toZeroHour = (timestamp: number): number => {
    const date = new Date(timestamp)
    date.setHours(0, 0, 0, 0)
    return date.getTime()
}

export const toDateString = (timestamp: number): string => {
    const date = new Date(timestamp * 1000);
    const options = { year: 'numeric', month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', timeZoneName: undefined };
    return date.toLocaleString('ja-JP', options as any);
}

export const getLaunchDate = (splaVersion: number): Date => {
    switch (splaVersion) {
        case 3: return new Date(2022, 8, 9)
        default: return new Date()
    }
}

export const round10 = (n: number): number => {
    return round(n, 10)
}

export const round = (n: number, ditit: number): number => {
    return Math.round(n * ditit) / ditit
}

export const toSeconds = (ms: number): number => {
    return Math.round(ms / 1000)
}

export const stringToDecimalHash = (str: string): number => {
    const encoder = new TextEncoder()
    const data = encoder.encode(str)
    const decimalHash = data.reduce((acc, byte) => acc + byte, 0)
    return decimalHash
}

export const getColorByString = (str: string): string => {
    const colors = ['black', 'red', 'maroon', 'green', 'lime', 'olive', 'blue', 'navy', 'yellow', 'purple', 'fuchsia', 'aqua', 'teal', 'gray', 'orange', 'pink', 'brown']
    return colors[stringToDecimalHash(str) % colors.length]
}

export const toHash = (params: any): string => {
    const strParams = JSON.stringify(params)
    return sha256(strParams)
}

export const isSmallDevice = (): boolean => {
    return window.innerWidth <= 768
}