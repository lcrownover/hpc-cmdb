<template>
  <div>
    {{ quote }}
  </div>
</template>

<script>
import axios from 'axios'
import { ref } from 'vue'
export default{
  setup(){
    
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
