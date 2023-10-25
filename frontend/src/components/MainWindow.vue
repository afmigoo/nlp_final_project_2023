<template>
  <v-container fluid class="justify-center alighn-center fill-height">
    <v-row>
      <v-col cols="12" class="justify-center align-center">
        <v-form class="mt-4" @submit.prevent="findGrams" id="search-form">
          <v-row class="justify-center align-center">
            <v-col cols="8">
              <v-text-field v-model="request" prepend-icon="mdi-help" variant="filled" clear-icon="mdi-close-circle"
                clearable label="Введите запрос" type="text" @click:prepend="overlay = !overlay" :rules="rules"
                class="mt-4"></v-text-field>
            </v-col>
            <v-col cols="2">
              <v-btn variant="tonal" class="ma-auto" size="large" form="search-form" type="submit"
                :disabled="!request">Искать</v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-col>
    </v-row>
    <v-overlay :model-value="overlay" class="align-center justify-center">
      <v-card max-width="1000" class="pl-8">
        <v-card-item>
          <v-card-actions class="d-flex justify-end">
            <v-btn size="x-small" icon="mdi-close" variant="plain" @click="overlay=!overlay"></v-btn>
          </v-card-actions>
          <v-card-text class="pt-0">
            <div class="text-body-1">
              Поиск принимает от 1- до триграмм, в которых токены записаны через запятую без знаков препинания <br />
              Токены могут иметь следующий вид:
              <ul class="ml-8">
                <li>
                  слово без кавычек -> поиск по лемме данного слова. <a class="font-weight-light">поиск, поиска</a>
                </li>
                <li>
                  слово в кавычках -> поиск по словоформе. <a class="font-weight-light">"поиск", 'поиска'</a>
                </li>
                <li>
                  POS-тег (формат <a href="https://universaldependencies.org/u/pos/index.html">CoNLL-U upos</a>) -> ищутся
                  все токены такой части речи. <a class="font-weight-light">NOUN, VERB</a>
                </li>
                <li>
                  слово с кавчками/без кавычек+POS-тег -> поиск по сочетанию словоформы/леммы с POS-тегом соответственно.
                  <a class="font-weight-light">поиск+NOUN, 'поиск'+NOUN</a>
                </li>
              </ul>
            </div>
          </v-card-text>
        </v-card-item>
      </v-card>
    </v-overlay>
  </v-container>
</template>

<script>

export default {
  data: () => ({
    overlay: false,
    form: false,
    request: null,
    rules: [
      value => {
        if (value) return true

        return 'Запрос не может быть пустым'
      },
    ],
  }),
  methods: {
    async findGrams() {
      if (!this.request) return
      this.$router.push({
        path: 'result',
        query: { request: this.request }
      })
    }
  }
}
</script>
