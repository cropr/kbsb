<template>
  <v-container>
    <h1>{{ pagetitle }}</h1>
    <div class="mt-1" v-html="pagecontent" />
  </v-container>
</template>

<script>

import showdown from 'showdown'

export default {
  layout: 'default',

  data () {
    return {
      page: {}
    }
  },

  async fetch () {
    this.page = await this.$content('pages', 'partners').fetch()
  },

  head: {
    title: 'Partners',
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
    pagecontent () {
      const pcontent = this.page[`content_${this.$i18n.locale}`]
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
