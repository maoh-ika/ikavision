<template>
  <div class="row justify-center tableContainer">
    <q-carousel
      class="full-width carousel"
      v-model="curSlide"
      swipeable
      animated
      transition-prev="slide-right"
      transition-next="slide-left"
      navigation-position="top"
      navigation
      padding
      control-color="accent"
      height="420px"
    >
      <q-carousel-slide
        :name="i"
        class="q-px-none column row fit justify-start items-center carouselSlide"
        v-for="items, i in carouselItems"
        :key="i"
      >
        <div class="q-ma-sm q-my-lg" v-for="item in items" :key="item" height="300px">
          <div class="text-center"> {{ makeItemLabel(item) }}</div>
          <q-table
            flat bordered dense
            class="cst-sticky-header"
            align="left"
            style="max-height: 300px;"
            :rows="makeRanking(item)"
            :columns="columns"
            :hide-pagination="true"
            :pagination="{rowsPerPage: 1000}"
            :no-data-label="$t('statistics.bukiStatistics.noData')"
            row-key="bukiId"
            column-sort-order="ad"
            binary-state-sort
          >
            <template v-slot:body="props">
              <q-tr :props="props">
                <q-td key="number" :props="props">
                  {{ props.rowIndex + 1 }}
                </q-td>
                <q-td key="bukiId" :props="props">
                  <div class="row items-center q-pa-sm">
                    <div>
                      {{ $t(`buki.main.${props.row.bukiId}`) }}
                    </div>
                  </div>
                </q-td>
                <q-td key="value" :props="props">
                  {{ props.row.value + valueUnit }}
                </q-td>
                <!--
                <q-td key="rocIn24h" :props="props" :class="{increase: props.row.rocIn24h > 0, decrease: props.row.rocIn24h < 0}" >
                  {{ `${round(props.row.rocIn24h * 100, 10)}%` }}
                </q-td>
                -->
              </q-tr>
            </template>
          </q-table>
        </div>
      </q-carousel-slide>
    </q-carousel>
  </div>
</template>
  
<script lang="ts">
import { defineComponent, computed, ref, type PropType } from 'vue'
import type { QTableColumn } from 'quasar'
import { useI18n } from 'vue-i18n'
import { round, isSmallDevice } from '@/modules/Utils'

export interface BukiItem {
  bukiId: string
  value: string
  rocIn24h: number
}

export default defineComponent({
  name: 'BukiRankingTable',
  components: {},
  props: {
    rankItems: {
      type: Array as PropType<string[]>,
      required: true 
    },
    makeItemLabel: {
      type: Function,
      required: true 
    },
    makeRanking: {
      type: Function,
      required: true 
    },
    valueColumnName: {
      type: String,
      required: true
    },
    valueUnit: {
      type: String,
      default: ''
    },
    itemsPerSlide: {
      type: Number,
    }
  },
  setup(props) {
    const t = useI18n()
    const curSlide = ref(0)
      
    const columns: QTableColumn[] = [
      { name: 'number', label: 'No.', field: 'number', align: 'left', sortable: false , classes: 'rowItem cst-text-overflow', headerClasses: 'cst-caption'},
      { name: 'bukiId', label: t.t('general.buki'), field: 'bukiId', align: 'left', sortable: false, style: 'max-width: 150px', classes: 'rowItem cst-text-overflow', headerClasses: 'cst-caption' },
      { name: 'value', label: props.valueColumnName, field: 'value', align: 'left', sortable: true, classes: 'cst-text-overflow', headerClasses: 'cst-caption' },
      //{ name: 'rocIn24h', label: t.t('general.rocIn24h'), field: 'rocIn24h', align: 'left', sortable: true, classes: 'cst-text-overflow', headerClasses: 'cst-caption'},
    ]

    const carouselItems = computed(() => {
      const carousels: string[][] = []
      let carousel: string[] = []
      for (let i = props.rankItems.length - 1; i >= 0; --i) {
        carousel.push(props.rankItems[i])
        if (carousel.length === itemsPerSlide.value) {
          carousels.push(carousel)
          carousel = []
        }
      }
      if (carousel.length > 0) {
        carousels.push(carousel)
      }
      return carousels
    })

    const itemsPerSlide = computed(() => {
      return props.itemsPerSlide || (isSmallDevice() ? 1 : 3)
    })
    
    return {
      curSlide,
      columns,
      carouselItems,
      round,
    }
  }
})
</script>

<style scoped>
.rowItem {
  font-size: 1rem;
}
.increase {
  color: red;
}
.decrease {
  color: blue;
}
.tableContainer {
  width: 100%;
}
.carousel {
}
.carouselSlide {
  overflow-x: scroll;
  overflow-y: hidden;

}
</style>