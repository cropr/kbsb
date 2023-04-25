<template>
  <v-container>
    <h1>{{ pagetitle }}</h1>
    <v-container class="mt-1 markedcontent elevation-2">
      <v-tabs v-model="tab" light slider-color="deep-purple">
        <v-tab class="mx-2">
          NL
        </v-tab>
        <v-tab class="mx-2">
          FR
        </v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <div class="mt-2" v-html="pagecontent_nl" />
        </v-tab-item>
        <v-tab-item>
          <div class="mt-2" v-html="pagecontent_fr" />
        </v-tab-item>
      </v-tabs-items>
    </v-container>
  </v-container>
</template>

<script>

import showdown from 'showdown'

export default {

  layout: 'default',

  data () {
    return {
      page: {},
      tab: 0
    }
  },

  async fetch () {
    this.page = await this.$content('pages', 'tournament-rules').fetch()
  },

  head: {
    title: 'Toernooireglement KBSB - Règlement tournois FRBE -Turnierregeln SVDB',
    link: [
      {
        rel: 'stylesheet',
        href:
          'https://fonts.googleapis.com/css?family=Roboto:100,300,400,500,700,900'
      },
      {
        rel: 'stylesheet',
        href: 'https://fonts.googleapis.com/css?family=Material+Icons'
      },
      {
        rel: 'stylesheet',
        href:
          'https://cdn.jsdelivr.net/npm/@mdi/font@latest/css/materialdesignicons.min.css'
      },
      { rel: 'favicon', href: 'favicon.ico' }
    ],
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'home', name: 'description', content: 'Meta description' }
    ],
    script: [
      {
        src: 'https://apis.google.com/js/platform.js',
        async: true,
        defer: true
      }
    ]
  },

  computed: {
    pagecontent_nl () {
      const pcontent = this.page.content_nl
      const converter = new showdown.Converter()
      return converter.makeHtml(pcontent)
    },

    pagecontent_fr () {
      const pcontent = this.page.content_fr
      const converter = new showdown.Converter()
      return converter.makeHtml(pcontent)
    },

    pagetitle () {
      const locale = this.$i18n.locale
      const pti18 = this.page[`title_${locale}`]
      const ptitle = pti18 && pti18.length ? pti18 : this.page.title
      return ptitle
    }
  }
}
</script>
