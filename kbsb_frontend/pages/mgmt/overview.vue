<template>
  <v-container>
    <h1>Overview Management FRBE KBSB KSB</h1>
    <p>Here you can add, modify or delete the content of pages and news articles</p>
    <p>
      For the upload of reports of meetings and other files, we still use the old
      interface at
      <a href="/mgmt/filelist">Files (Reports)</a>
    </p>
    <P>Modifying the website is done in 3 steps:</P>
    <ul>
      <li>Make a copy of the operational website</li>
      <li>Modify the copy</li>
      <li>Publish the modifications to the operational site</li>
    </ul>
    <h3 class="mt-3">
      Step 1: Make a copy of the operational site
    </h3>
    <v-btn class="my-2" @click="checkin">
      Make copy
    </v-btn>
    <p v-if="checkinlaunched">
      Copy is being made
    </p>
    <p v-if="checkinsuccess">
      Copy ready.
    </p>
    <h3 class="mt-3">
      Step 2: Make your modifications
    </h3>
    <p>Open the collections (pages, articles) in a separate tab.</p>
    <v-btn class="my-2" @click="openCollections">
      Open collections
    </v-btn>
    <h3 class="mt-3">
      Step 3: Publish of the operational site
    </h3>
    <v-btn class="my-2" @click="checkout">
      Publish
    </v-btn>
    <p v-if="checkoutlaunched">
      The request for publication has been launched
    </p>
    <p v-if="checkoutsuccess">
      The request was successful.   The new version of the operational site will be live in about 10 min.
    </p>
  </v-container>
</template>

<script>
export default {
  layout: 'mgmt',

  data () {
    return {
      checkinlaunched: false,
      checkinsuccess: false,
      checkoutlaunched: false,
      checkoutsuccess: false
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
    person () {
      return this.$store.state.person
    }
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

    openCollections () {
      const stUrl = this.$config.statamic_url
      window.open(`${stUrl}/cp/collections`, '_statamic')
    },

    async checkin () {
      this.checkinlaunched = true
      const data = {
        user: this.person.user,
        email: this.person.email
      }
      const reply = await fetch(this.$config.statamic_url + '/python/checkin', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
          'Content-Type': 'application/json'
        }
      })
      console.log('reply', reply)
      this.checkinlaunched = false
      this.checkinsuccess = true
    },

    async checkout () {
      this.checkoutlaunched = true
      const data = {
        user: this.person.user,
        email: this.person.email
      }
      const reply = await fetch(this.$config.statamic_url + '/python/checkout', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
          'Content-Type': 'application/json'
        }
      })
      console.log('reply', reply)
      this.checkoutlaunched = false
      this.checkoutsuccess = true
    }

  }
}
</script>
