<template>
    <div>
      <q-btn
        :color="color"
        :text-color="textColor"
        :rounded="rounded"
        :glossy="glossy"
        :no-caps="noCaps"
        @click="login"
        :label="label || $t('general.login')"
      />
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref } from 'vue'
  import { useStore } from 'vuex'
  import { useI18n } from 'vue-i18n'
  import { useQuasar } from 'quasar'
  import { config } from '@/modules/Config'
  
  export default defineComponent({
    name: 'LoginButton',
    components: { },
    props: {
      noCaps: {
        type: Boolean,
        default: false
      },
      label: {
        type: String
      },
      rounded: {
        type: Boolean,
        default: false
      },
      glossy: {
        type: Boolean,
        default: false
      },
      color: {
        type: String,
        default: 'white'
      },
      textColor: {
        type: String,
        default: 'black'
      },
      connected: {
        type: Function,
        default: () => {}
      }
    },
    setup(props) {
      const store = useStore()
      const { t } = useI18n()
      const $q = useQuasar()
      const showTermsOfUse = ref(false)
  
      const login = async () => {
        location.assign(config.aws.loginUrl)
      }
  
      return {
        showTermsOfUse,
        login
      }
    }
  })
  </script>
  
  <style scoped>
  </style>