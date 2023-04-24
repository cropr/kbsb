<template>
  <div>
    <v-container>
      <v-row>
        <v-col cols="4" md="2">
          <v-img contain src="/img/logo.svg" />
        </v-col>
        <v-col cols="8" sm="7">
          <h1>{{ pagetitle }}</h1>
          <div class="nuxt-content" v-html="pagecontent" />
        </v-col>
        <v-col cols="12" sm="3">
          <v-card>
            <v-card-title class="green darken-1 white--text pa-3">
              <h4>{{ $t('Tools') }}</h4>
            </v-card-title>
            <v-card-text>
              <div class="pa-2">
                <a
                  class="green--text"
                  :href="phpbaseurl + 'sites/manager/GestionFICHES/FRBE_Fiche.php'"
                >
                  Elo
                </a>
              </div>
              <div class="pa-2">
                <b>NEW</b> <a class="green--text" href="/tools/club">
                  Club manager
                </a>
              </div>
              <div class="pa-2">
                <a class="green--text" href="/tools/interclub">
                  Interclub manager
                </a>
              </div>
              <div class="pa-2">
                <a
                  class="green--text"
                  :href="phpbaseurl + 'sites/manager/GestionCOMMON/GestionLogin.php'"
                >
                  Player manager
                </a>
              </div>
              <div class="pa-2">
                <a
                  class="green--text"
                  :href="phpbaseurl + 'sites/manager/GestionSWAR/SwarResults.php'"
                >
                  {{ $t('Results SWAR') }}
                </a>
              </div>
              <div class="pa-2">
                <a class="green--text" @click="ratingtrn">
                  {{ $t('ELO tournaments') }}
                </a>
              </div>
            </v-card-text>
          </v-card>
          <v-card class="mt-2">
            <v-card-title class="green darken-1 white--text pa-3 hyphen">
              {{ $t('Calendar') }}
            </v-card-title>
            <v-card-text class="mt-2">
              <ul>
                <li v-for="c, ix in future_4ci" :key="ix">
                  {{ calenderItem(c) }}
                </li>
              </ul>
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn to="/info/calendar">
                {{ $t('More') }} ...
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
      <v-row class="mt-2">
        <v-col v-for="a in articles3" :key="a.id" cols="12" sm="6" md="4">
          <v-card>
            <v-card-title class="green lighten-1 black--text pa-3 hyphen">
              {{ a.title }}
            </v-card-title>
            <v-card-text class="mt-2" v-html="a.intro" />
            <v-card-actions>
              <v-spacer />
              <v-btn @click="gotoArticle(a)">
                {{ $t('read more') }}
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    <v-parallax v-if="$vuetify.breakpoint.mdAndUp" src="/img/chesscrowd_big.jpg" height="400" />
    <v-parallax v-if="$vuetify.breakpoint.sm" src="/img/chesscrowd_medium.jpg" height="300" />
    <v-parallax v-if="$vuetify.breakpoint.xs" src="/img/chesscrowd_small.jpg" height="200" />
    <v-container>
      <v-row class="mt-2">
        <v-col v-for="a in articlesRest" :key="a.id" cols="12" sm="6" md="4">
          <v-card>
            <v-card-title class="green lighten-1 black--text pa-3 hyphen">
              {{ a.title }}
            </v-card-title>
            <v-card-text class="mt-2" v-html="a.intro" />
            <v-card-actions>
              <v-spacer />
              <v-btn @click="gotoArticle(a)">
                {{ $t('read more') }}
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>

import showdown from 'showdown'
import { phpbaseurl } from '@/util/cms'

function compareDates (a, b) {
  return a.date - b.date
}

export default {
  layout: 'landing',

  data () {
    return {
      articles3: [],
      articlesRest: [],
      calitems: [],
      page: {},
      parsed: {},
      micromark: null,
      phpbaseurl
    }
  },

  async fetch () {
    this.page = await this.$content('pages', 'home').fetch()
    const articles = await this.$content('articles').fetch()
    const calenderItems = await this.$content('calendar').fetch()
    this.readArticles(articles)
    this.parseCalendarItems(calenderItems)
    this.calitems.sort(compareDates)
  },

  computed: {

    future_4ci () {
      const yesterday = new Date() - 86400000
      return this.calitems.filter(ci => ci.date > yesterday).slice(0, 4)
    },

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

  },

  methods: {

    calenderItem (c) {
      const output = []
      output.push(c.date.toLocaleDateString(this.$i18n.locale, { dateStyle: 'medium' }) + ':')
      output.push(c.title)
      if (c.round) {
        output.push(this.$t('Round'))
        output.push(c.round)
      }
      return output.join(' ')
    },

    gotoArticle (a) {
      window.location.href = '/article?slug=' + a.slug
    },

    parseCalendarItems (listci) {
      listci.forEach((ci) => {
        if (ci.multiple) {
          this.parseCalendarItems(ci.multiple)
        }
        if (ci.date) {
          const item = { ...ci, date: new Date(ci.date) }
          this.calitems.push(item)
          return
        }
        if (ci.rounds) {
          Object.entries(ci.rounds).forEach(([rnr, date]) => {
            const { rounds, ...item } = { ...ci, date: new Date(date), round: rnr }
            this.calitems.push(item)
          })
        }
      })
    },

    ratingtrn () {
      if (this.$i18n.locale === 'nl') {
        window.location.href = '/tools/ratingnl'
      } else {
        window.location.href = '/tools/ratingfr'
      }
    },

    readArticles (articles) {
      const now = new Date()
      const activearticles = []
      const locale = this.$i18n.locale
      this.articles3 = []
      this.articleRest = []
      articles.forEach((a, index) => {
        const activedate = new Date(a.active_since)
        const expirydate = new Date(activedate)
        expirydate.setDate(expirydate.getDate() + Number(a.active_days))
        if (activedate < now && expirydate > now) {
          const titlei18n = a[`title_${locale}`]
          const introi18n = a[`intro_${locale}`]
          activearticles.push({
            activedate,
            expirydate,
            title: titlei18n && titlei18n.length ? titlei18n : a.title,
            intro: introi18n && introi18n.length ? introi18n : a.intro,
            text: a[`text_${locale}`],
            slug: a.slug
          })
        }
      })
      activearticles.sort((a, b) => b.activedate - a.activedate)
      activearticles.forEach((a, ix) => {
        if (ix < 3) {
          this.articles3.push(a)
        } else {
          this.articlesRest.push(a)
        }
      })
    }

  }

}
</script>

<style>
h1:after {
  content: ' ';
  display: block;
  border: 1px solid #aaa;
  margin-bottom: 1em;
}

.nuxt-content td,
.nuxt-content th {
  padding: 8px;
  border: 1px solid #ddd;
}

.nuxt-content table {
  border-collapse: collapse;
}

.nuxt-content ul,
.nuxt-content ol,
.nuxt-content h2,
.nuxt-content h3 {
  margin-bottom: 0.5em;
}
</style>
