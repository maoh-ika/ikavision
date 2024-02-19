<template>
  <div class="fit">
    <p>
      {{ $t('upload.successDesc1') }}
      <RouterLink :to="{ name: 'battleList', query: { tab: 'processing' } }">{{ $t('drawer.battleList') }}</RouterLink>
      {{ $t('upload.successDesc2') }}
    </p>
    <div class="q-mt-lg text-center">
      <q-btn @click="() => closed()" outline :label="$t('general.close')"/>
    </div>
  </div>
</template>
  
<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'RequestSuccess',
  components: {},
  props: {
    closed: {
      type: Function,
      default: () => {}
    }
  },
  setup(props) {
  }
})
</script>

<style scoped>

</style>