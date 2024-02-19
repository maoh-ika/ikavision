<template>
  <div class="items-center column full-width">
    <SectionTitle id="environment-usage-rule" :title="$t('environment.bukiUsage.descRuleBased')" :info="$t('environment.bukiUsage.infoRuleBased')" />
    <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
    <BukiUsageRuleTable class="usageTable" />
    <SectionTitle id="environment-usage-stage" class="q-mt-xl" :title="$t('environment.bukiUsage.descStageBased')" :info="$t('environment.bukiUsage.infoStageBased')" />
    <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
    <BukiUsageStageTable class="usageTable" />
    <SectionTitle class="q-mt-xl" :title="$t('environment.bukiUsage.descRuleStageBased')" :info="$t('environment.bukiUsage.infoRuleStageBased')" />
    <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
    <q-btn-dropdown color="primary" auto-close :label="$t(`buki.main.${selectedBuki}`)">
      <q-list>
        <q-item v-for="buki in bukiList" :key="buki.id" dense clickable @click="() => selectBuki(buki.id)">
          <q-item-section>
            <q-item-label>{{ buki.name }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-btn-dropdown>
    <BukiUsageRuleStageTable class="usageTable" :buki="selectedBuki" />
    <q-page-scroller position="bottom-right" :scroll-offset="150" :offset="[18, 64]">
      <q-btn fab icon="keyboard_arrow_up" color="primary" />
    </q-page-scroller>
  </div>
</template>

<script lang="ts">
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { defineComponent, ref, computed, onMounted } from 'vue'
import SectionTitle from '@/components/SectionTitle.vue'
import BukiUsageRuleTable from '@/components/BukiUsageRuleTable.vue'
import BukiUsageStageTable from '@/components/BukiUsageStageTable.vue'
import BukiUsageRuleStageTable from '@/components/BukiUsageRuleStageTable.vue'
import type { MainWeapon } from '@/models/Buki'

export default defineComponent({
  name: 'BattleEnvironment',
  components: {
    SectionTitle,
    BukiUsageRuleTable,
    BukiUsageStageTable,
    BukiUsageRuleStageTable
  },
  setup(props) {
    const store = useStore()
    const t = useI18n()
    const route = useRoute()
    const selectedBuki = ref('wakaba_shooter')

    onMounted(() => {
      if (route.query.section === 'rule') {
        document.getElementById('environment-usage-rule')?.scrollIntoView({ behavior: 'smooth' })
      } else if (route.query.section === 'stage') {
        document.getElementById('environment-usage-stage')?.scrollIntoView({ behavior: 'smooth' })
      }
    })

    const bukiList = computed(() => {
      const bukis = store.getters['battleEnvironment/getAllBukis']() as MainWeapon[]
      bukis.sort((a, b) => t.t(`buki.main.${a}`) < t.t(`buki.main.${b}`) ? -1 : 1)
      return bukis.map(buki => {
        return { id: buki, name: t.t(`buki.main.${buki}`) }
      })
    })

    const selectBuki = (buki: MainWeapon) => {
      selectedBuki.value = buki
    }
    
    return {
      bukiList,
      selectedBuki,
      selectBuki
    }
  }
})
</script>

<style scoped>
.usageTable {
  width: 80%;
  max-height: 600px;
}
</style>