<template>
<div>
<h1> HEY THERE GUY </h1><br>
  <h2> HOWDY FRIEND </h2><br>
  <button @click="addEntry">Submit</button><br>
  <h3>{{ boy }}</h3>
  <input type="text" v-model="query" @keypress="addEntry">
  <h1>
    {{ quote }}
    </h1>
</div>
  
</template>

<script>
import axios from 'axios';
import {ref} from 'vue';
let banana = 0;
export default {
  name: 'app',
  data (){
    return {
      responseData: '',
      query: '',
    }
  },
  methods: {
    addBoy() {
      const boy = ref('');
      axios.post('http://localhost:8000/entries/', {
        name: 'batman',
        tags: [{name: 'love-interest', value: 'alfred'}],
      })
          .then((response) => {
            boy.value = response;
          });
      return {
        boy,
      };
    },
    addEntry(){
      console.log(this.query)
      
    },
    fetchy (){
      console.log('Hello there')
      fetch('http://localhost:8000/entries/')
      .then((response) => {
        console.log(response)
        return response.json()
      })
      .then(this.setResults)
    },
    setResults(results) {
      this.responseData = results;
    }
  },
  created: function(){
    this.fetchy()
  },
  setup() {
    console.log('hi there')
    const quote = ref('');
    axios.get('http://localhost:8000/entries/')
        .then((response) => {
          quote.value = response;
          console.log(quote.value)
        });
    return {
      quote,
    };
  },
};
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
