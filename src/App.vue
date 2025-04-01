<template>
	<div id="app">
		<div v-if="isLoginPage">
			<RouterView />
		</div>
		<div v-else>
			<NavBar />
			<main>
				<RouterView />
			</main>
			<FooterView />
		</div>
	</div>
</template>

<script setup>
import { RouterView, useRoute } from 'vue-router';
import NavBar from './components/NavBar.vue';
import FooterView from './components/FooterView.vue';
import { computed } from 'vue';

const route = useRoute();
const isLoginPage = computed(() => route.path === '/login');
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Balsamiq+Sans:ital,wght@0,400;0,700;1,400;1,700&display=swap');

:root {
	--cinequizz-red: #bb0d16;
	--cinequizz-black: rgb(30, 30, 30);
	--cinequizz-white: rgb(254, 255, 246);
	--navbar-height: 80px;
}

* {
	box-sizing: border-box;
}

#app {
	color: var(--cinequizz-black);
	background-color: var(--cinequizz-white);
	min-height: 100vh;
}

body {
	font-family: "Balsamiq Sans", sans-serif !important;
	margin: 0;
}

img, button{
	user-select: none;
}

</style>
