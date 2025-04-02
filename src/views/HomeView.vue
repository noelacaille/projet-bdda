<script setup>
import TinderBoardgames from './components/TinderView.vue';
</script>

<template>
	<div class="home">
		<div class="hero">
			<h1>Welcome to <span class="app-title">CineQuizz</span></h1>
			<p>Test your knowledge about your favorite movies!</p>
		</div>
	</div>
	<TinderBoardgames />
</template>

<script>
import axios from 'axios';

export default {
	name: 'HomeView',
};
</script>

<style scoped>
.app-title {
	color: var(--pnt-button);
}

.home {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 20px;
}

.hero {
	text-align: center;
	margin-bottom: 40px;
}

.hero h1 {
	font-size: 2.5rem;
	color: #333;
}

.hero p {
	font-size: 1.2rem;
	color: #666;
}

.quiz-list {
	width: 100%;
	max-width: 1200px;
	margin-bottom: 40px;
}

.quiz-list h2 {
	font-size: 1.8rem;
	margin-bottom: 20px;
	color: #333;
	text-align: center;
}

.no-favorites {
	text-align: center;
	font-size: 1.2rem;
	color: #999;
}

.quiz-grid {
	display: grid;
	grid-template-columns: repeat(auto-fit, 300px);
	gap: 20px;
	justify-content: center;
}

.quiz-card {
	width: 300px;
	background: #fff;
	border: 1px solid #ddd;
	border-radius: 8px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	padding: 20px;
	text-align: center;
	transition: transform 0.3s ease, box-shadow 0.3s ease;
	user-select: none;
	position: relative;
}

.quiz-card:hover {
	transform: translateY(-5px);
	box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
}

.favorite-icon {
	position: absolute;
	top: 10px;
	right: 10px;
	width: 24px;
	height: 24px;
	cursor: pointer;
	transition: transform 0.3s ease;
}

.favorite-icon .favorite-star {
	fill: #ddd;
	transition: fill 0.3s ease;
}

.favorite-icon.active .favorite-star {
	fill: #FFD700;
}

.favorite-icon:hover {
	transform: scale(1.2);
}

.quiz-image {
	width: 100%;
	height: 150px;
	overflow: hidden;
	border-radius: 8px;
	margin-bottom: 15px;
}

.quiz-image img {
	width: 100%;
	height: 100%;
	object-fit: contain;
	object-position: center;
}

.quiz-card h3 {
	font-size: 1.3rem;
	margin-bottom: 10px;
	color: #333;
}

.quiz-card p {
	font-size: 1rem;
	color: #666;
	margin-bottom: 15px;
}

.start-button {
	display: inline-block;
	background-color: #e50914;
	color: #fff;
	padding: 10px 20px;
	border-radius: 4px;
	text-decoration: none;
	font-weight: bold;
	transition: background-color 0.3s ease;
}

.start-button:hover {
	background-color: #b50710;
}

.quiz-score {
	font-size: 0.9rem;
	color: gray;
	margin-top: 0.5rem;
	font-weight: bold;
}

.top-buttons {
	display: flex;
	gap: 20px;
	margin-bottom: 40px;
	justify-content: center;
}

.big-button {
	font-size: 1.5rem;
	padding: 15px 25px;
	border-radius: 8px;
	background-color: #e50914;
	color: white;
	font-weight: bold;
	cursor: pointer;
	border: none;
	transition: transform 0.3s ease, background-color 0.3s ease;
}

.big-button:hover {
	background-color: #b50710;
	transform: scale(1.05);
}

.big-button:active {
	transform: scale(0.95);
}

.button-card img {
	width: 200px;
	height: 200px;
	object-fit: cover;
	transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.button-card img:hover {
	transform: scale(1.05);
}

.button-card p {
	font-size: 1.2rem;
	font-weight: bold;
	color: #333;
	margin: 20px 0 10px 0;
}

.top-buttons {
	display: flex;
	flex-wrap: wrap;
	gap: 20px;
	margin-bottom: 40px;
	justify-content: center;
	align-items: center;
}

.button-card {
	display: flex;
	flex-direction: column;
	align-items: center;
	cursor: pointer;
	text-align: center;
	transition: transform 0.3s ease, box-shadow 0.3s ease;
	width: 200px;
}

@media (max-width: 768px) {
	.button-card img {
		width: 150px;
		height: 150px;
	}

	.top-buttons {
		gap: 40px;
		justify-content: center;
	}

	.button-card {
		width: 150px;
	}
}

@media (max-width: 480px) {

	.button-card img {
		width: 120px;
		height: 120px;
	}

	.button-card p {
		font-size: 1rem;
	}
}

.quiz-score-small {
	font-size: 0.75rem !important;
	color: gray !important;
	margin-top: 0 !important;
}
</style>
