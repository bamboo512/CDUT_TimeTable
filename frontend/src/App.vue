<template>
  <keep-alive>
    <router-view :key="$route.fullPath" />
  </keep-alive>
  <a href="https://beian.miit.gov.cn" class="fixed bottom-2 hover:underline underline-offset-4">
    蜀 ICP 备 2022026512 号 - 1
  </a>
</template>

<style lang="scss">
@font-face {
  font-family: 'Inter';
  src: url(./assets/fonts/Inter.ttf), local("Inter");
  font-weight: 100 900;
}

html,
body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  background-color: white;
  display: flex;

  justify-content: center;
  align-items: center;

}

#app {
  font-family: "Inter", "Google Sans Text", ui-sans-serif, -apple-system,
    "苹方-简", "MiSans", "MiSans VF", "Segoe UI Variable Display",
    "思源黑体", "思源黑体 VF", sans-serif;
  // -webkit-font-smoothing: antialiased;
  // -moz-osx-font-smoothing: grayscale;

  color: #2c3e50;
  height: 100%;
  width: 100%;
  // background-color: #4b74da;
  background-image: linear-gradient(120deg, #4b74da50, #da554b50);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.text-gradient-blue-red {
  background: linear-gradient(60deg, #da554b, #4b74dacc);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.bg-gradient-blue-red {
  background: linear-gradient(120deg, #4b74dacc, #4b74daa0, #da554b50);

}

/* dark themes go here */
@media (prefers-color-scheme: dark) {
  body {
    background-color: #2c3e50;
  }

  #app {
    background-image: linear-gradient(120deg, #4b74da50, #da554b50);
    color: white;
  }

  .text-gradient-blue-red {
    background: linear-gradient(150deg, #da554b, #4b74da);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }
}
</style>

<script>
export default {
  name: "App",
  data() {
    return {
      loggedInOrNot: false,
    };
  },
  methods: {

  },
}

</script>
