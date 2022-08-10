<template>
  <div>
    <h1>A cool title</h1>
    <br />
    <div class="input-box">
      <button @click="addEntry">Submit</button><br />
      <h3>{{ boy }}</h3>
      <input type="text" v-model="query" @keypress:enter="addEntry" />
    </div>

    <div class="data">
      <div class="title" v-for="(people, index) in quote" :key="index">
        <h1>{{ people.name }} first</h1>
        <MDBAccordion v-model="activeItem">
          <MDBAccordionItem
            headerTitle="Accordion Item #1"
            collapseId="collapseOne"
          >
            <ul v-for="(tag, index) in people.tags" :key="index">
              <li>
                <strong>
                  {{ tag.name }}
                </strong>
                <p>-</p>
                <p>
                  {{ tag.value }}
                </p>
              </li>
            </ul>
            <strong>This is the first item's accordion body.</strong> It is
            shown by default, until the collapse plugin adds the appropriate
            classes that we use to style each element. These classes control the
            overall appearance, as well as the showing and hiding via CSS
            transitions. You can modify any of this with custom CSS or
            overriding our default variables. It's also worth noting that just
            about any HTML can go within the MDBAccordionItem, though the
            transition does limit overflow.
          </MDBAccordionItem>
        </MDBAccordion>
        <!-- <h3>{{people.tags}}</h3> -->
      </div>
    </div>
    <!-- <MDBAccordion v-model="activeItem">
    <MDBAccordionItem
      headerTitle="Accordion Item #1"
      collapseId="collapseOne"
    >
      <strong>This is the first item's accordion body.</strong> It is
      shown by default, until the collapse plugin adds the appropriate
      classes that we use to style each element. These classes control
      the overall appearance, as well as the showing and hiding via
      CSS transitions. You can modify any of this with custom CSS or
      overriding our default variables. It's also worth noting that
      just about any HTML can go within the
      MDBAccordionItem, though the transition does limit
      overflow.
    </MDBAccordionItem>
    <MDBAccordionItem
      headerTitle="Accordion Item #2"
      collapseId="collapseTwo"
    >
      <strong>This is the second item's accordion body.</strong>
      It is hidden by default, until the collapse plugin adds the
      appropriate classes that we use to style each element. These
      classes control the overall appearance, as well as the showing
      and hiding via CSS transitions. You can modify any of this with
      custom CSS or overriding our default variables. It's also worth
      noting that just about any HTML can go within the
      MDBAccordionItem, though the transition does limit
      overflow.
    </MDBAccordionItem>
    <MDBAccordionItem
      headerTitle="Accordion Item #3"
      collapseId="collapseThree"
    >
      <strong>This is the third item's accordion body.</strong> It is
      hidden by default, until the collapse plugin adds the
      appropriate classes that we use to style each element. These
      classes control the overall appearance, as well as the showing
      and hiding via CSS transitions. You can modify any of this with
      custom CSS or overriding our default variables. It's also worth
      noting that just about any HTML can go within the
      MDBAccordionItem, though the transition does limit
      overflow.
    </MDBAccordionItem>
  </MDBAccordion> -->
  </div>
</template>

<script>
import axios from "axios";
import { ref } from "vue";
import { MDBAccordion, MDBAccordionItem } from "mdb-vue-ui-kit";

let banana = 0;
export default {
  name: "app",
  components: {
    MDBAccordion,
    MDBAccordionItem,
  },
  data() {
    return {
      dbData: [],
      api_root: process.env.VUE_APP_API_ROOT,
      responseData: "",
      query: "",
    };
  },
  methods: {
    addBoy() {
      const boy = ref("");
      axios
        .post(`http://${this.api_root}/entries/`, {
          name: "batman",
          tags: [{ name: "love-interest", value: "alfred" }],
        })
        .then((response) => {
          boy.value = response;
        });
      return {
        boy,
      };
    },
    addEntry() {},
    // fetchy (){
    //   console.log('Hello there')
    //   fetch(`http://${this.api_root}/entries/`)
    //   .then((response) => {
    //     // console.log(response)
    //     return response.json()
    //   })
    //   .then(this.setResults)
    // },
    // setResults(results) {
    //   this.responseData = results;
    // }
  },
  created: function () {
    // this.fetchy()
  },
  setup() {
    const activeItem = ref("collapseOne");
    const quote = ref("");
    axios.get("http://localhost:8000/entries/").then((response) => {
      quote.value = response["data"];
    });
    return {
      quote,
      activeItem,
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
