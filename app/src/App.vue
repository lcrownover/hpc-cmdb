<template>
  <h1> HEY THERE GUY </h1><br>
  <h2> HOWDY FRIEND </h2><br>
  <button @click="addBoy">Submit</button><br>
  <h3>{{ boy }}</h3>
  <input type="text" v-model="name">
  {{ quote }}
</template>

<script>
import axios from 'axios'
import { ref } from 'vue'
export default {
  methods: {
    addBoy() {
      const boy = ref('')
      axios.post('http://localhost:8000/entries/', {
        name: "batman",
        tags: [{ name: "love-interest", value: "alfred" }]
      })
        .then(response => {
          boy.value = response
        })
      return {
        boy
      }
    }
  },
  setup() {
    const quote = ref('')
    axios.get('http://localhost:8000/entries/')
      .then(response => {
        quote.value = response
      })
    return {
      quote
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
