<template>
	<div class="home">
		<div class="hero">
			<h1>Welcome to <span class="app-title">CineQuizz</span></h1>
			<p>Test your knowledge about your favorite movies!</p>
		</div>
	</div>
	
</template>

<script>
import axios from 'axios';
import quizzes from '@/assets/data/quizzes.json';
import Wheel from "@/components/Wheel.vue";

export default {
	name: 'HomeView',
	data() {
		return {
			quizzes: quizzes,
			favoriteQuizzes: [],
			loadingFavorites: true,
			wheelVisible: false
		};
	},
	mounted() {
		const newQuizzes = [
			{ id: 'superquiz', title: 'Super Quiz', description: 'Test your knowledge with super quiz!', image: '/images/superquiz.png', bestScore: 'Never attempted' },
			{ id: 'streakquiz', title: 'Streak Quiz', description: 'See how long you can keep your streak!', image: '/images/streakquiz.png', bestScore: 'Never attempted' },
			{ id: 'flashquiz', title: 'Flash Quiz', description: 'Answer as fast as you can!', image: '/images/flashquiz.png', bestScore: 'Never attempted' }
		];
		newQuizzes.forEach((quiz) => {
			if (!this.quizzes.some(existingQuiz => existingQuiz.id === quiz.id)) {
				this.quizzes.push(quiz);
			}
		});
		this.fetchFavoritesAndScores();
	},
	components: {
		Wheel,
	},
	methods: {
		async fetchFavorites() {
			try {
				const token = localStorage.getItem('token');
				const response = await axios.get('http://localhost:3000/favorites', {
					headers: { Authorization: `Bearer ${token}` },
				});
				this.favoriteQuizzes = this.quizzes.filter((quiz) =>
					response.data.includes(quiz.id)
				);
			} catch (error) {
				console.log('Error fetching favorite quizzes:', error);
			}
		},
		isFavorite(quizId) {
			return this.favoriteQuizzes.some((quiz) => quiz.id === quizId);
		},
		async toggleFavorite(quiz) {
			try {
				const token = localStorage.getItem('token');
				const isCurrentlyFavorite = this.isFavorite(quiz.id);

				await axios.post(
					`http://localhost:3000/favorites`,
					{ quizId: quiz.id, favorite: !isCurrentlyFavorite },
					{ headers: { Authorization: `Bearer ${token}` } }
				);

				if (isCurrentlyFavorite) {
					this.favoriteQuizzes = this.favoriteQuizzes.filter(
						(fav) => fav.id !== quiz.id
					);
				} else {
					this.favoriteQuizzes.push(quiz);
				}
			} catch (error) {
				console.log('Error updating favorite status:', error);
			}
		},
		async fetchBestScores() {
			const token = localStorage.getItem('token');
			const bestScores = {};

			for (const quiz of this.quizzes) {
				try {
					const response = await axios.get(`http://localhost:3000/attempts/best/${quiz.id}`, {
						headers: { Authorization: `Bearer ${token}` },
					});
					bestScores[quiz.id] = response.data.bestScore !== undefined ? response.data.bestScore : "Never attempted";
				} catch (error) {
					console.error(`Error fetching best score for quiz ${quiz.id}:`, error);
					bestScores[quiz.id] = "Never attempted";
				}
			}

			this.quizzes.forEach((quiz) => {
				quiz.bestScore = bestScores[quiz.id];
			});
		},
		async fetchFavoritesAndScores() {
			await this.fetchFavorites();
			await this.fetchBestScores();
			['superquiz', 'streakquiz', 'flashquiz'].forEach(async (quizName) => {
				try {
					const token = localStorage.getItem('token');
					const response = await axios.get(`http://localhost:3000/attempts/best/${quizName}`, {
						headers: { Authorization: `Bearer ${token}` },
					});
					const bestScore = response.data.bestScore || 'Never attempted';
					const quiz = this.quizzes.find(q => q.id === quizName);
					if (!quiz) {
						console.error(`Quiz with id "${quizName}" not found in quizzes.`);
						return;
					}
					quiz.bestScore = bestScore;

				} catch (error) {
					console.error(`Error fetching best score for ${quizName}:`, error);
				}
			});
		},
		openWheelPopup() {
			this.wheelVisible = true;
		},
		closeWheelPopup() {
			this.wheelVisible = false;
		},
		superQuiz() {
			this.$router.push({
				path: '/quiz',
				query: {
					name: 'superquiz',
					title: 'Super Quiz',
					bg: '/background/superquiz.jpg',
					bestScore: 'Never attempted'
				}
			});
		},
		streakQuiz() {
			this.$router.push({
				path: '/quiz',
				query: {
					name: 'streakquiz',
					title: 'Streak Quiz',
					bg: '/background/streakquiz.jpg',
					bestScore: 'Never attempted'
				}
			});
		},
		flashQuiz() {
			this.$router.push({
				path: '/quiz',
				query: {
					name: 'flashquiz',
					title: 'Flash Quiz',
					bg: '/background/flashquiz.jpg',
					bestScore: 'Never attempted'
				}
			});
		},
		formatBestScore(bestScore, quizType) {
			if (bestScore === "Never attempted") {
				return "Never attempted";
			}
			var maxScore = 10;
			if (quizType === "superquiz") maxScore = 80;
			if (quizType === "streakquiz") maxScore = 80;
			if (quizType === "flashquiz") maxScore = 20;
			return `Best score: ${bestScore} / ${maxScore}`;
		}
	},
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
