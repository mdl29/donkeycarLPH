<template>
  <router-view/>
</template>

<style>
/* @import url('https://fonts.googleapis.com/icon?family=Material+Icons'); No needed now */


/* fallback */
@font-face {
  font-family: 'Material Icons';
  font-style: normal;
  font-weight: 400;
  src: url('fonts/material.woff2') format('woff2');
}

.material-icons {
  font-family: 'Material Icons';
  font-weight: normal;
  font-style: normal;
  font-size: 24px;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -moz-font-feature-settings: 'liga';
  -moz-osx-font-smoothing: grayscale;
}

/* @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:ital,wght@0,400;1,700&display=swap'); */

/* source-sans-pro-regular - latin-ext_latin */
@font-face {
  font-display: swap; /* Check https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display for other options. */
  font-family: 'Source Sans Pro';
  font-style: normal;
  font-weight: 400;
  src: url('fonts/source-sans-pro-v21-latin-ext_latin/source-sans-pro-v21-latin-ext_latin-regular.eot'); /* IE9 Compat Modes */
  src: url('fonts/source-sans-pro-v21-latin-ext_latin/source-sans-pro-v21-latin-ext_latin-regular.eot?#iefix') format('embedded-opentype'), /* IE6-IE8 */
       url('fonts/source-sans-pro-v21-latin-ext_latin/source-sans-pro-v21-latin-ext_latin-regular.woff2') format('woff2'), /* Super Modern Browsers */
       url('fonts/source-sans-pro-v21-latin-ext_latin/source-sans-pro-v21-latin-ext_latin-regular.woff') format('woff'), /* Modern Browsers */
       url('fonts/source-sans-pro-v21-latin-ext_latin/source-sans-pro-v21-latin-ext_latin-regular.ttf') format('truetype'), /* Safari, Android, iOS */
       url('fonts/source-sans-pro-v21-latin-ext_latin/source-sans-pro-v21-latin-ext_latin-regular.svg#SourceSansPro') format('svg'); /* Legacy iOS */
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}
</style>
