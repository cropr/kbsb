<template>
  <v-container>
    <h1>Clubs</h1>
    <v-data-table
      :headers="headers"
      :items="filtered"
      :footer-props="footerProps"
      class="elevation-1"
      sort-by="idclub"
    >
      <template #top>
        <v-toolbar flat color="white">
          <v-toolbar-title> {{ $t('Reports') }}</v-toolbar-title>
          <v-spacer />
          <v-row>
            <v-col cols="6">
              <v-checkbox v-model="filter.board" :label="$t('Report Board Meeting')" />
            </v-col>
            <v-col cols="6">
              <v-checkbox v-model="filter.ga" :label="$t('Report General Assembly')" />
            </v-col>
          </v-row>
        </v-toolbar>
      </template>
      <template #item.topic="{ item }">
        {{ $t(item.topic) }}
      </template>
      <template #item.path="{ item }">
        URL: <a :href="urlfile(item.url)">{{ item.name }}</a>
      </template>
      <template #no-data>
        No reports yet.
      </template>
    </v-data-table>
  </v-container>
</template>

<script>
export default {
  layout: 'default',
  data () {
    return {
      filter: {},
      headers: [
        {
          text: 'N.', value: 'idclub'
        },
        {
          text: this.$t('Long name'), value: 'name_long'
        },
        {
          text: this.$t('Short name'), value: 'name_short'
        },
        {
          text: 'Actions', value: 'action', sortable: false
        }

      ],
      clubs: [],
      footerProps: {
        itemsPerPageOptions: [20, 50, -1],
        itemsPerPage: 20
      }
    }
  },

  head: {
    title: 'Clubs',
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

  methods: {
    urlfile (url) {
      return '/api/v1/filecontent/' + url
    }
  }

}
</script>
