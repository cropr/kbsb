<template>
  <v-container>
    <h1>{{ page.title }}</h1>
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
          <div class="mt-1" v-html="pagecontent_nl" />
        </v-tab-item>
        <v-tab-item>
          <div class="mt-1" v-html="pagecontent_fr" />
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
      tab: 0,
      page: {}
    }
  },

  async fetch () {
    this.page__nl = await this.$content('pages', 'admin', 'internalrules_nl').fetch()
    this.page__fr = await this.$content('pages', 'admin', 'internalrules_fr').fetch()
    this.page__de = await this.$content('pages', 'admin', 'internalrules_de').fetch()
    this.page__en = await this.$content('pages', 'admin', 'internalrules_en').fetch()
  },

  head: {
    title: 'Intern reglement KBSB - Règlement interne FRBE',
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
