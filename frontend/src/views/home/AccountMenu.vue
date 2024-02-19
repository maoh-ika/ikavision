<template>
<q-btn-dropdown id="accountMenuButton" class="q-px-xs q-py-xs" flat no-caps color="white" :label="address">
  <q-list>  
    <q-item dense clickable @click="goProfile">
      <q-item-section>
        <q-item-label>{{ $t('header.profileLink') }}</q-item-label>
      </q-item-section>
    </q-item>
    <q-item dense clickable @click="goCreate">
      <q-item-section>
        <q-item-label>Create</q-item-label>
      </q-item-section>
    </q-item>
    <q-separator />
    <q-item dense clickable @click="logout">
      <q-item-section>
        <q-item-label class="text-negative">Logout</q-item-label>
      </q-item-section>
    </q-item>
  </q-list>
</q-btn-dropdown>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
export default defineComponent({
  name: 'AccountMenu',
  setup() {
    const store = useStore()
    const router = useRouter()

    const address = computed((): string => {
      return store.getters['ethereum/getAccount']
    })

    const goProfile = () => {
      router.push({ name: 'profile', params: { account: address.value }})
    }
    
    const goCreate = () => {
      router.push({ name: 'create', params: { account: address.value }})
    }

    const logout = () => {
      store.commit('ethereum/setAccount', null)
      router.push({ name: 'home' })
    }

    return {
      address,
      goProfile,
      goCreate,
      logout
    }
  }
})
</script>

<style scoped>
button#accountMenuButton :deep(span > span.block) {
  text-overflow: ellipsis !important;
  overflow: hidden !important;
  white-space: nowrap !important;
}
</style>