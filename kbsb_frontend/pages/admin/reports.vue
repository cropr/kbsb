<template>
  <v-container>
    <h1>{{ $t('Reports') }}</h1>
    <v-data-table
      :headers="headers"
      :items="filteredfiles"
      :footer-props="footerProps"
      class="elevation-1"
      sort-by="topicdate"
      :sort-desc="true"
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
          text: 'Report', value: 'topic'
        },
        {
          text: 'Date', value: 'topicdate'
        },
        {
          text: 'File', value: 'path'
        }
      ],
      files: [],
      footerProps: {
        itemsPerPageOptions: [20, 50, -1],
        itemsPerPage: 20
      }
    }
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
    filteredfiles () {
      const self = this; const fa = []
      if (!this.filter.board && !this.filter.ga) { return this.files }
      this.files.forEach((f) => {
        if (f.topic === 'Report Board Meeting' && self.filter.board) {
          fa.push(f)
          return
        }
        if (f.topic === 'Report General Assembly' && self.filter.ga) {
          fa.push(f)
        }
      })
      return fa
    }
  },

  mounted () {
    this.getReports()
  },

  methods: {

    async getReports () {
      try {
        const resp = await this.$api.file.anon_get_files({ reports: 1 })
        this.files = resp.data.files
      } catch (error) {
        console.error('getting getFiles', error)
        this.$root.$emit('snackbar', { text: 'Getting files failed', reason: error })
      }
    },

    urlfile (url) {
      return '/api/v1/filecontent/' + url
    }

  }

}
</script>
