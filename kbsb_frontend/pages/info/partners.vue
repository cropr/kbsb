<template>
  <v-container>
    <h1>{{ page.title }}</h1>
    <nuxt-content :document="page" />
  </v-container>
</template>

<script>
export default {
  layout: 'default',

  data () {
    return {
      page: {}
    }
  },

  async fetch () {
    this.page = await this.$content('pages', 'info', 'partner').fetch()
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
  }
}
</script>
