<template>
  <v-container>
    <v-card>
      <v-card-title color="grey lighten-4">
        <h2>Edit File: {{ name }}</h2>
        <v-spacer />
        <v-tooltip bottom>
          <template #activator="{ on }">
            <v-btn
              slot="activator"
              outlined
              fab
              color="deep-purple"
              v-on="on"
              @click="back()"
            >
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
          </template>
          <span>Go Back</span>
        </v-tooltip>
        <v-tooltip bottom>
          <template #activator="{ on }">
            <v-btn
              slot="activator"
              outlined
              fab
              color="deep-purple"
              v-on="on"
              @click="save()"
            >
              <v-icon>mdi-content-save</v-icon>
            </v-btn>
          </template>
          <span>Save file</span>
        </v-tooltip>
        <v-tooltip bottom>
          <template #activator="{ on }">
            <v-btn
              slot="activator"
              outlined
              fab
              color="deep-purple"
              v-on="on"
              @click="remove()"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
          <span>Delete file</span>
        </v-tooltip>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field v-model="f.name" label="Name" />
              <v-text-field v-model="f.created_by" label="Owner" />
              <v-select v-model="f.topic" label="Topic" :items="topictypes" />
            </v-col>
            <v-col cols="12" sm="6">
              <p>
                URL: <a :href="urlfile(f.url)">/api/v1/filecontent/{{ f.url }}</a>
              </p>
              <v-menu
                v-model="menu_topicdate"
                :close-on-content-click="false"
                :nudge-right="40"
                transition="scale-transition"
                offset-y
                min-width="290px"
              >
                <template #activator="{ on }">
                  <v-text-field
                    v-model="f.topicdate"
                    label="Topic date"
                    prepend-icon="mdi-calendar-range"
                    readonly
                    v-on="on"
                  />
                </template>
                <v-date-picker
                  v-model="f.topicdate"
                  color="deep-purple"
                  @input="menu_topicdate = false"
                />
              </v-menu>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import { topictypes } from '@/util/cms'

export default {

  name: 'Fileedit',

  layout: 'mgmt',

  data () {
    return {
      f: {},
      menu_topicdate: false,
      name: '',
      photosrc: null,
      savefile: false,
      topictypes,
      yesno: [
        { value: true, text: 'Yes' },
        { value: false, text: 'No' }
      ]
    }
  },

  computed: {
    token () { return this.$store.state.newlogin.value }
  },

  mounted () {
    this.getFile()
  },

  methods: {

    back () {
      this.$router.push('/mgmt/filelist')
    },

    async getFile () {
      try {
        const resp = await this.$api.file.get_file({
          id: this.$route.query.id,
          token: this.token
        })
        this.readFile(resp.data)
      } catch (error) {
        const resp = error.response
        console.error('getting getFiles', resp)
        if (resp.status === 401) {
          this.$router.push('/mgmt/login')
        } else {
          this.$root.$emit('snackbar', { text: 'Getting file failed', reason: resp.data.detail })
        }
      }
    },

    readFile (file) {
      this.f = file
      this.name = this.f.name + ''
    },

    async remove () {
      if (window.confirm('Are you sure to delete file "' + this.name + '"?')) {
        try {
          await this.$api.file.delete_file({
            id: this.$route.query.id,
            token: this.token
          })
          this.$root.$emit('snackbar', { text: 'File deleted' })
          this.$router.push('/mgmt/filelist')
        } catch (error) {
          const resp = error.response
          console.error('delete_file', resp)
          if (resp.status === 401) {
            this.$router.push('/mgmt/login')
          } else {
            this.$root.$emit('snackbar', { text: 'Deleting file failed', reason: resp.data.detail })
          }
        }
      }
    },

    async save () {
      try {
        await this.$api.file.update_file({
          ...this.f,
          token: this.token
        })
        console.log('save successful')
        this.$root.$emit('snackbar', { text: 'File saved' })
      } catch (error) {
        const resp = error.response
        console.error('getting getFiles', resp)
        if (resp.status === 401) {
          this.$router.push('/mgmt/login')
        } else {
          this.$root.$emit('snackbar', { text: 'Saving file failed', reason: resp.data.detail })
        }
      }
    },

    urlfile (url) {
      return '/api/v1/filecontent/' + url
    }

  }

}
</script>

<style scoped>
.bordermd {
  border: 1px solid grey;
}
</style>
