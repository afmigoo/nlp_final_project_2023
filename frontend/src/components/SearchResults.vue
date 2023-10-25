<template>
    <v-container fluid class="pa-0 cont d-flex align-center justify-center">
        <v-progress-linear class="align-self-start" v-if="!error && !responce_length" indeterminate rounded
            height="3"></v-progress-linear>
        <v-col cols="11" class="px-16 align-self-start" v-if="!!responce_length">
            <v-row class="mt-8 ml-12">
                <v-col cols="1">
                    <v-btn icon @click="toSearch">
                        <v-icon>
                            mdi-arrow-left
                        </v-icon>
                        <v-tooltip activator="parent" location="start">Вернуться к поиску</v-tooltip>
                    </v-btn>
                </v-col>
                <v-col cols="8">
                    <h1>
                        Результаты поиска по запросу <a class="n-gram">{{ request }}</a>
                    </h1>
                </v-col>
                <v-col cols="3" class="pr-12">
                    <h6 class="mb-5 text-center">
                        Кол-во результатов выдачи на странице
                    </h6>
                    <v-select v-model="page_size" :items="page_size_variants" density="compact"
                        @update:model-value="initPage"></v-select>
                </v-col>
            </v-row>


            <v-card v-for="item in current_page_responces" v-bind:key="item.context" class="ma-10">
                <v-card-item>
                    <v-card-text>
                        <div>
                            <a v-for="token, index in item.absolute_ngram_indexes" v-bind:key="token[0]">
                                {{ item.context.slice(item.absolute_ngram_indexes[index - 1] ?
                                    item.absolute_ngram_indexes[index
                                    -
                                    1][1] - item.context_start : 0, token[0] - item.context_start) }}
                                <a class="n-gram">{{ item.context.slice(token[0] - item.context_start, token[1] -
                                    item.context_start) }}</a>
                            </a>
                            <a>
                                {{ item.context.slice(item.absolute_ngram_indexes[item.absolute_ngram_indexes.length - 1][1]
                                    -
                                    item.context_start) }}
                            </a>
                            [ <a v-for="link, i in item.href" v-bind:key="link" :href="link"> {{ link }} {{ i <
                                item.href.length - 1 ? ', ' : '' }}</a> ]
                                    <v-btn variant="plain" size="small" @click="widenContext(item)">
                                        &lt;...>
                                        <v-tooltip activator="parent" location="end">Посмотреть расширенный
                                            контекст</v-tooltip>
                                    </v-btn>
                        </div>
                    </v-card-text>
                </v-card-item>

            </v-card>
            <v-pagination class="mb-8" v-model="page" :total-visible="10" :length="pages"
                @update:model-value="updatePage"></v-pagination>

            <v-overlay :model-value="wide_context_overlay"
                @after-leave="curr_item_wide_context = {}; wide_context_overlay = false"
                class="align-center justify-center">
                <v-card max-width="1000" class="pl-8 pb-8">
                    <v-card-item>
                        <v-card-actions class="d-flex justify-end pb-0">
                            <v-btn size="x-small" icon="mdi-close" variant="plain"
                                @click="wide_context_overlay = false"></v-btn>
                        </v-card-actions>
                        <v-card-text class="pt-0">
                            <div class="text-body-1">
                                <a v-for="token, index in curr_item_wide_context.absolute_ngram_indexes"
                                    v-bind:key="token[0]">
                                    {{
                                        curr_item_wide_context.context.slice(curr_item_wide_context.absolute_ngram_indexes[index
                                            - 1] ?
                                            curr_item_wide_context.absolute_ngram_indexes[index
                                            -
                                            1][1] - curr_item_wide_context.context_start : 0, token[0] -
                                        curr_item_wide_context.context_start) }}
                                    <a class="n-gram">{{ curr_item_wide_context.context.slice(token[0] -
                                        curr_item_wide_context.context_start, token[1] -
                                    curr_item_wide_context.context_start) }}</a>
                                </a>
                                <a>
                                    {{
                                        curr_item_wide_context.context.slice(curr_item_wide_context.absolute_ngram_indexes[curr_item_wide_context.absolute_ngram_indexes.length
                                            - 1][1]
                                            -
                                            curr_item_wide_context.context_start) }}
                                </a>
                            </div>
                        </v-card-text>
                    </v-card-item>
                </v-card>
            </v-overlay>
        </v-col>
        <v-col cols="9" v-if="!!error">
            <v-row class="d-flex justify-center">
                <v-col cols="2" class="d-flex justify-end">
                    <v-btn icon @click="toSearch">
                        <v-icon>
                            mdi-arrow-left
                        </v-icon>
                        <v-tooltip activator="parent" location="start">Вернуться к поиску</v-tooltip>
                    </v-btn>
                </v-col>
                <v-col cols="10">
                    <v-alert type="error" :text="error" variant="outlined" max-width="800"></v-alert>
                </v-col>
            </v-row>
        </v-col>
    </v-container>
</template>

<script>

export default {
    data: function () {
        return {
            page_size_variants: [5, 10, 20, 50],
            page: 1,
            page_size: 10,
            request: this.$route.query.request,
            responces: null,
            current_page_responces: null,
            responce_length: 0,
            pages: 0,
            error: null,
            curr_item_wide_context: {},
            wide_context_overlay: false
        }
    },
    methods: {
        initPage() {
            this.page = 1
            if (this.responce_length < this.page_size) {
                this.current_page_responces = this.responces;
            } else {
                this.current_page_responces = this.responces.slice(0, this.page_size);
            }
            this.pages = Math.ceil(this.responce_length / this.page_size)
        },
        async findGrams() {
            try {
                this.responces = (await this.$api.search.findGrams({ n_gram: this.request })).data
                console.log(this.responces)
                this.responce_length = this.responces.length;
                this.initPage()
            }
            catch (err) {
                this.error = err.response.data.detail
            }
        },
        updatePage(page_index) {
            console.log(page_index)
            let _start = (page_index - 1) * this.page_size;
            let _end = page_index * this.page_size;
            this.current_page_responces = this.responces.slice(_start, _end);
            this.page = page_index;
        },
        toSearch() {
            this.$router.push('/')
        },
        async widenContext(item) {
            console.log(item, this.wide_context_overlay, this.curr_item_wide_context)
            const answer = (await this.$api.search.widenContext({
                sentence_id: item.sentence_id, text_id: item.text_id, context_start: item.context_start,
                context_end: item.context_end
            })).data
            Object.assign(this.curr_item_wide_context, item)
            this.curr_item_wide_context.context_start = answer.context_start
            this.curr_item_wide_context.context_end = answer.context_end
            this.curr_item_wide_context.context = answer.context
            this.wide_context_overlay = true
        }
    },
    mounted: async function () {
        await this.findGrams()
    },
}
</script>

<style>
.n-gram {
    color: #FFF59D;
    font-weight: 600;
}

.cont {
    height: 100%;
}</style>