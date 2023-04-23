<template>
  <v-container>
    <p>Overview Management FRBE KBSB KSB</p>
    <p>Here you can add, modify or deleet the content of pages and news articles</p>
    <p>
      For the upload offiels and reports, we still use the old interface at
      <a href="/mgmt/filelist">Files (Reports)</a>
    </p>
    <P>Modifying the website is done in 3 steps:</P>
    <ul>
      <li>Make a copy of the operational website</li>
      <li>Modify the copy</li>
      <li>Publish the modifications on the operational site</li>
    </ul>
    <h3 class="mt-3">
      Step 1: Make a copy of the operational site
    </h3>
    <v-btn class="my-2" @click="setupwork">
      Make copy
    </v-btn>
    <p v-if="setupworklaunched">
      Copy is being made
    </p>
    <p v-if="setupworksuccess">
      Copy ready.
    </p>
    <h3 class="mt-3">
      Step 2: Make your modifications
    </h3>
    <h3 class="mt-3">
      Step 3: Publish of the operational site
    </h3>
  </v-container>
</template>

<script>

export default {
  layout: 'mgmt',

  data () {
    return {
      setupworklaunched: false,
      setupworksuccess: false,
      productionlaunched: false,
      productionsuccess: false
    }
  },

  head: {
    title: 'Management Overview',
    // we need google script to load because we might redirect internally
    // to index in case we fail the authentication
    script: [
      {
        src: 'https://accounts.google.com/gsi/client',
        async: true,
        defer: true
      }
    ]
  },

  computed: {
    person () { return this.$store.state.person }
  },

  mounted () {
    this.checkAuth()
  },

  methods: {

    checkAuth () {
      console.log('checking if auth is already set')
      if (this.person.token.length === 0) {
        this.$router.push('/mgmt')
      }
      if (!this.person.email.endsWith('@frbe-kbsb-ksb.be')) {
        this.$router.push('/mgmt')
      }
    },

    async setupwork () {
      this.setupworklaunched = true
      const data = {
        user: this.person.user,
        email: this.person.email
      }
      console.log('data', data)
      const reply = await fetch(
        this.$config.statamic_url + '/python/setupwork', {
          method: 'POST',
          body: JSON.stringify(data),
          headers: {
            'Content-Type': 'application/json'
          }
        })
      console.log('reply', reply)
      this.setupworklaunched = false
      this.setupworksuccess = true
    }

  }

}
</script>
