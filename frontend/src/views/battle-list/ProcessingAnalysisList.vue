<template>
  <q-table
    flat
    align="left"
    :rows="processingJobs"
    :columns="columns"
    :pagination="{rowsPerPage: 10}"
    :rows-per-page-label="$t('general.rowsPerPageLabel')"
    :rows-per-page-options="[5, 10, 20, 50]"
    :no-data-label="$t('jobList.processing.noData')"
    row-key="name"
  >
    <template v-slot:body="props">
      <q-tr :props="props">
        <q-td key="jobName" :props="props">
          {{ props.row.jobName }}
        </q-td>
        <q-td key="state" :props="props">
          {{ $t(`jobState.${props.row.state}`) }}
        </q-td>
        <q-td key="createdAt" :props="props">
          {{ toDateString(props.row.createdAt) }}
        </q-td>
      </q-tr>
    </template>
  </q-table>
</template>
  
<script lang="ts">
import { defineComponent, computed } from 'vue'
import type { QTableColumn } from 'quasar'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import type { AnalysisJob } from '@/modules/AnalysisJobApi'
import { toDateString } from '@/modules/Utils'

export default defineComponent({
  name: 'ProcessingAnalysisList',
  components: { },
  props: {
    userId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const t = useI18n()
    const store = useStore()
    
    const processingJobs = computed(() => {
      return store.getters['analysisJob/getProcessingJobs'](props.userId) as AnalysisJob[]
    })

    const columns: QTableColumn[] = [
      { name: 'jobName', label: t.t('jobList.processing.jobName'), field: 'jobName', align: 'left', sortable: true },
      { name: 'state', label: t.t('jobList.processing.state'), field: 'state', align: 'left', sortable: true },
      { name: 'createdAt', label: t.t('jobList.processing.createdAt'), field: 'createdAt', align: 'left', sortable: true },
    ]
    
    return {
      columns,
      processingJobs,
      toDateString
    }
  }
})
</script>

<style scoped>
</style>