<template>
  <v-app-bar v-cloak dark app class="green darken-2" landing="landing" :drawer="drawer" 
        clipped-left>
    <v-app-bar-nav-icon @click.stop="toggleDrawer" />
    <v-toolbar-items>
      <v-btn text large to="/">
        {{ $t("RBCF") }}
      </v-btn>
    </v-toolbar-items>
    <v-spacer />
    <v-toolbar-items class="hidden-sm-and-down">
      <v-btn text large to="/competition/interclubs-2022-23">
        Interclub 22-23
      </v-btn>
      <v-btn text large :href="phpbaseurl + 'sites/manager/GestionFICHES/FRBE_Fiche.php'">
        ELO
      </v-btn>
    </v-toolbar-items>
  </v-app-bar>
</template>

<script>

import { phpbaseurl } from '@/util/cms'

export default {

  props: {
    landing: {
      type: String,
      default: null
    },
    drawer: {
      type: Boolean,
      default: false
    }
  },

  data () {
    return {
      phpbaseurl
    }
  },

  methods: {

    toggleDrawer () {
      this.$emit('updateDrawer', !this.drawer)
    }
  }
}
</script>
