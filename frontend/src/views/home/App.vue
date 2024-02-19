<template>
  <q-layout>
    <q-page-container>
      <AppHeader/>
      <RouterView :key="environment"/>
    </q-page-container>
    <q-footer>
      <q-toolbar>
        <div>© 2024 maoh_ika</div>
        <q-space />
        <div>{{ $t('home.nonOfficial') }}</div>
      </q-toolbar>
    </q-footer>
  </q-layout>
</template>

<script lang="ts">
import AppHeader from '@/views/home/AppHeader.vue'
import { defineComponent, computed } from 'vue'
import { useStore } from 'vuex'
export default defineComponent({
  name: 'App',
  components: { AppHeader },
  setup() {
    const store = useStore()

    const environment = computed(() => {
      const matchType = store.getters['battleEnvironment/getEnvironmentMatchType']
      const matchRate = store.getters['battleEnvironment/getEnvironmentXMatchRate']
      return `${matchType}_${matchRate}`
    })

    return { environment }
  }
})
</script>

<style scoped>
.socialLink:visited, .socialLink:hover {
  color: white;
}
</style>
