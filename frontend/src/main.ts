import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import App from '@/views/home/App.vue'
import router from './router'
import store from './store'
import i18nConfig from './i18n'
import { Quasar, Loading, Dialog } from 'quasar'
import '@quasar/extras/material-icons/material-icons.css'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  TimeScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'
import 'chartjs-adapter-moment'
import { hover, chartInitialized  } from '@/modules/Chart'
import 'vue3-draggable-resizable/dist/Vue3DraggableResizable.css'
 
import './assets/main.css'
import 'video.js/dist/video-js.css'

ChartJS.register(
  CategoryScale,
  LinearScale,
  TimeScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  hover,
  chartInitialized
)

const i18n = createI18n(i18nConfig)
const app = createApp(App)
.use(i18n)
.use(router)
.use(store)
.use(Quasar, {
  plugins: {
    Loading,
    Dialog
  },
  config: {
    loading: {},
    brand: {
      primary: '#121258',
      secondary: '#FFC039',
      accent: '#ff6000',

      dark: '#1d1d1d',
      'dark-page': '#121212',

      positive: '#21BA45',
      negative: '#C10015',
      info: '#31CCEC',
      warning: '#F2C037'
    }
  }
} as any)

app.mount('#app')
