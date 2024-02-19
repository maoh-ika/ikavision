import store from '@/store'

export class BattleMonitor {
  imageSrc?: HTMLVideoElement

  constructor() {
  }

  async start(imageSrc: HTMLVideoElement): Promise<boolean> {
    if (!await store.dispatch('ikalamp/start')) {
      throw new Error('IkalampStore start failed')
    }
    if (!await store.dispatch('ikaPlayer/start')) {
      throw new Error('IkaPlayerStore start failed')
    }
    this.imageSrc = imageSrc
    //this._updateIkalamps()
    this._updateIkaPlayers()
    return true
  }

  stop() {
    this.imageSrc = undefined
  }

  private _updateIkalamps() {
    if (this.imageSrc === undefined) {
      return
    }
    createImageBitmap(this.imageSrc)
      .then(b => {
        store.dispatch('ikalamp/updateIkalamps', b)
          .catch(err => {
            //console.log(err)
          })
          .finally(() => this._setTimeout(this._updateIkalamps.bind(this), 200))
      })
      .catch(err => {
        //console.log(err)
        this._setTimeout(this._updateIkalamps.bind(this), 200)
      })
  }

  private _updateIkaPlayers() {
    if (this.imageSrc === undefined) {
      return
    }
    createImageBitmap(this.imageSrc)
      .then(b => {
        store.dispatch('ikaPlayer/updatePlayers', b)
          .catch(err => {
            //console.log(err)
          })
          .finally(() => {
            this._setTimeout(this._updateIkaPlayers.bind(this), 200)
          })
      })
      .catch(err => {
        //console.log(err)
        this._setTimeout(this._updateIkaPlayers.bind(this), 200)
      })
  }

  private _setTimeout(func: any, interval: number=0) {
    if (interval === 0) {
      requestAnimationFrame(func)
    } else {
      setTimeout(func, interval)
    }
  }
}