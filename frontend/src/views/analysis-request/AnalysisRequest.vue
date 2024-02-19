<template>
  <q-layout view="hhh lpr fff">
    <div class="q-pa-md q-gutter-sm">
      <q-breadcrumbs>
        <q-breadcrumbs-el icon="home" to="/" />
        <q-breadcrumbs-el :label="$t('drawer.analyze')" icon="add_circle" />
      </q-breadcrumbs>
    </div>
    <q-page class="q-pa-md column items-center root">
      <div class="col-6">
        <div v-if="!openSuccess && !openFail">
          <div>
            <p>{{ $t('upload.desc2') }}</p>
            <p class="cst-caption">{{ $t('upload.cap1') }}<RouterLink to="/examples">{{ $t('upload.movieReqLink') }}</RouterLink></p>

            <q-uploader
              class="full-width q-mt-md"
              style="height: 300px;"
              flat
              bordered
              text-color="accent"
              max-file-size="20000000000"
              accept=".mp4,.mov"
              @added="fileSelected"
              @removed="fileRemoved"
            >
              <template v-slot:header="scope"/>
              <template v-slot:list="scope">
                  <div class="text-center fit column justify-center">
                    <div v-if="scope.canAddFiles">
                      <q-btn
                        :disable="!scope.canAddFiles"
                        type="a"
                        icon="cloud_upload"
                        size="xl"
                        @click="scope.pickFiles"
                        round dense flat>
                        <q-uploader-add-trigger />
                        <q-tooltip>{{ $t('upload.add') }}</q-tooltip>
                      </q-btn>
                      <div class="text-h6">
                        {{ $t('upload.desc1') }}
                      </div>
                    </div>
                    <div v-else-if="scope.files.length > 0">
                      <p class="full-width ellipsis">
                        {{ scope.files[0].name }}
                      </p>
                      <p>
                        {{ scope.files[0].__sizeLabel }}
                      </p>
                      <q-btn
                        class="gt-xs"
                        size="md"
                        flat
                        dense
                        round
                        icon="delete"
                        @click="scope.removeFile(scope.files[0])"
                      >
                        <q-tooltip>{{ $t('upload.delete') }}</q-tooltip>
                      </q-btn>
                    </div>
                  </div>
              </template>
            </q-uploader>
          </div>
          <div class="q-mt-lg text-center">
            <q-btn
              :disable="movieFile === undefined"
              class=""
              color="primary"
              text-color="secondary"
              :label="$t('upload.analyze')"
              no-caps
              @click="requestAnalysis"
            />
          </div>
        </div>
        <div v-if="openSuccess">
          <RequestSuccess :closed="() => openSuccess = false" />
        </div>
      </div>
    </q-page>
  </q-layout>
</template>
  
<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import { useI18n } from 'vue-i18n'
import { createAnalysisJob } from '@/modules/AnalysisJobApi'
import RequestSuccess from './RequestSuccess.vue'

export default defineComponent({
  name: 'AnalysisRequest',
  components: { RequestSuccess },
  setup(props) {
    const $q = useQuasar()
    const $t = useI18n()
    const movieFile = ref()
    const openSuccess = ref(false)
    const openFail = ref(false)

    const fileSelected = async (files: readonly any[]) => {
      movieFile.value = files[0]
    }
    
    const fileRemoved = async () => {
      movieFile.value = undefined
    }

    const getUploadMessage = (prog: number): string => {
      return `${$t.t('upload.requesting')} (${Math.round(prog)}%)`
    }
    
    const requestAnalysis = async () => {
      if (movieFile.value === undefined) {
        return
      }
      try {
        $q.loading.show({ message: getUploadMessage(0) })
        const job = await createAnalysisJob(
          'testuser',
          movieFile.value.name,
          Date.now(),
          movieFile.value,
          (prog) => {
            $q.loading.show({ message: getUploadMessage(prog) })
          }
        )
        openSuccess.value = true
        //console.log(job)
      } catch(err) {
        console.log(err)
        openFail.value = true
      } finally {
        $q.loading.hide()
      }
    }
    
    return {
      movieFile,
      openSuccess,
      openFail,
      fileSelected,
      fileRemoved,
      requestAnalysis
    }
  }
})
</script>

<style scoped>

</style>