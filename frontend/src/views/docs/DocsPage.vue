<template>
<q-layout view="hhh lpr fff">
  <q-drawer
      v-model="open"
      show-if-above
      :width="200"
      :breakpoint="500"
      bordered
    >
      <q-scroll-area class="fit q-pt-lg">
        <q-list class="topicList">
          <q-item
            v-for="topic, key in topics"
            :key="topic.title"
            class="topicLink"
            :active="curTopicPath === topic.path"
            active-class="bg-teal-1 text-grey-8"
            dense :to="{ name: 'docs', params: { topic: topic.path} }"
            @click="() => curTopicPath = topic.path"
          >
            <q-item-section>{{ topic.title }}</q-item-section>
          </q-item>
        </q-list>

        <q-expansion-item
          v-for="category in categories"
          :key="category.name"
          :label="category.name"
          :default-opened="true"
          expand-separator
          dense
        >
          <q-list class="q-ml-md topicList">
            <q-item
              v-for="topic, key in category.topics"
              :key="topic.title"
              class="topicLink"
              :active="curTopicPath === topic.path"
              active-class="bg-teal-1 text-grey-8"
              dense :to="{ name: 'docs', params: { topic: topic.path} }"
              @click="() => curTopicPath = topic.path"
            >
              <q-item-section>{{ topic.title }}</q-item-section>
            </q-item>
          </q-list>
        </q-expansion-item>
      </q-scroll-area>
  </q-drawer>
  <q-page-container>
    <q-page class="q-pa-md column items-center">
      <WhatIsIkaVision v-if="curTopicPath === 'what-is-ikavision'"/>
      <SearchConditions v-if="curTopicPath === 'search-conditions'"/>
    </q-page>
  </q-page-container>
</q-layout>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import WhatIsIkaVision from './overview/WhatIsIkaVision.vue'
import SearchConditions from './search/SearchConditions.vue'

interface Topic {
  title: string
  path: string
}

interface Category {
  name: string
  topics: Topic[]
}

export default defineComponent({
  name: 'DocsPage',
  components: {
    WhatIsIkaVision,
    SearchConditions
  },
  props: {
    initCategory: {
      type: String,
      default: 'Overview'
    },
    initTopic: {
      type: String,
      required: false
    },
  },
  setup(props) {
    const router = useRoute()
    const $t = useI18n()
    const open = ref(true)
    const curPath = props.initTopic || router.path.substring(router.path.lastIndexOf('/') + 1)
    const curTopicPath = ref(curPath)

    const topics = [
      { title: $t.t('docs.about'), path: 'what-is-ikavision' },
    ]

    const categories: Category[] = [
      {
        name: $t.t('docs.search.title'),
        topics: [
          { title: $t.t('docs.search.conditions'), path: 'search-conditions' },
        ]
      },
    ]

    return {
      open,
      curTopicPath,
      topics,
      categories
    }
  }
})
</script>

<style scoped>
.topicList {
  border-left: 1px solid rgba(0,0,0,.12);
}
.topicLink {
  font-weight: normal;
}
</style>