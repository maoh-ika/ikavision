export const hover = {
  id: 'hover',
  afterEvent: (chart: any, event: any, options: any) => {
    const xValue = event.event.x
    const yValue = event.event.y
    const yAxis = chart.scales.y
    const xAxis = chart.scales.x
    if (options.onHover) {
        options.onHover(xValue, yValue, xAxis, yAxis)
    }
  }
}

export const isContained = (
    area: {top: number, bottom: number, left: number, right: number},
    x: number,
    y: number
    ): boolean => {
       return area.left <= x &&
        x <= area.right &&
        area.top <= y &&
        y <= area.bottom
}

export const toTime = (x: number, xAxis: any): number => {
   return (xAxis.end - xAxis.start) * (x - xAxis.left) / (xAxis.right - xAxis.left)
}

export const chartInitialized = {
    id: 'updated',
    afterLayout: (chart: any, b: any, options: any) => {
        if (options.onUpdate) {
            options.onUpdate(chart)
        }
    }
}

export const drawVertLine = (
    canvas: HTMLCanvasElement,
    color: string,
    x: number,
    top: number,
    bottom: number) => {
    const ctx = canvas.getContext('2d')
    if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        ctx.beginPath()
        ctx.moveTo(x, top)
        ctx.lineTo(x, bottom)
        ctx.strokeStyle = color
        ctx.stroke()
    }
}

export const drawHorzLine = (
    canvas: HTMLCanvasElement,
    color: string,
    y: number,
    left: number,
    right: number,
    lineWidth: number=1) => {
    const ctx = canvas.getContext('2d')
    if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        ctx.beginPath()
        ctx.moveTo(left, y)
        ctx.lineTo(right, y)
        ctx.strokeStyle = color
        ctx.lineWidth = lineWidth
        ctx.stroke()
    }
}

export const drawRect = (
    canvas: HTMLCanvasElement,
    x: number,
    y: number,
    w: number,
    h: number,
    color: string) => {
    const ctx = canvas.getContext('2d')
    if (ctx) {
        ctx.fillStyle = color
        ctx.fillRect(x, y, w, h)
    }
}

export const clearCanvas = (canvas: HTMLCanvasElement) => {
    const ctx = canvas.getContext('2d')
    if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
    }
}