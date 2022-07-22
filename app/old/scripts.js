const app = new Vue({
  el: '#app',
  data: {
    entries: [],

    new_entry: '',
    new_tags: [],
    tag_name: '',
    tag_value: '',
  },
  methods: {
    query: function() {
      axios({
        url: 'http://localhost:8000/entries/',
        method: 'get',
      }).then((response) => {
        console.log('burrs');
        this.entries = response.data;
      });
    },
    addEntry: function() {
      axios({
        url: 'http://localhost:8000/entries/',
        method: 'post',
        data: {'name': this.new_entry, 'tags': [{'name': this.tag_name, 'value': this.tag_value}]},
      });
    },
  },
  created: function() {
    alert('I love tacos');
    this.query();
  },
});
