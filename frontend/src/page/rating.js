import Vue from 'vue'
import vuetify from '@/plugins/vuetify';
import { i18n } from '@/util/lang'
import Rating from '@/page/Rating.vue'
import {router} from '@/page/router_page'
import store from '@/page/store_page'

Vue.config.productionTip = false

window.vm = new Vue({
  vuetify,
  router,
  store,
  i18n,
  render: h => h(Rating)
}).$mount('#app')

