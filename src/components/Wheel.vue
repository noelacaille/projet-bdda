<template>
	<div v-if="isVisible" class="popup-overlay" @click.self="closePopup">
		<div class="popup">
			<div class="popup-header">
				<button class="close-button" @click="closePopup">✖</button>
			</div>
			<h1>Random Quiz Wheel</h1>
			<div id="spin_the_wheel">
				<div id="indicator"></div>
				<canvas id="wheel" width="800" height="800"></canvas>
				<div id="spin">SPIN</div>
			</div>
			<div id="start_the_quiz">
				<div v-if="!spinStarted && !spinInProgress && selectedQuiz">
					<h3>Selected Quiz : {{ selectedQuiz.title }}</h3>
					<button class="start-button" @click="startQuiz">Start the Quiz</button>
				</div>
				<div v-else-if="spinStarted && spinInProgress">The wheel is spinning...</div>
				<div v-else>Spin the wheel to randomly choose a quiz.</div>
			</div>
		</div>
	</div>
</template>

<script>
import JSConfetti from 'js-confetti'

const jsConfetti = new JSConfetti()

export default {
	name: "Wheel",
	props: {
		isVisible: {
			type: Boolean,
			required: true,
		},
		quizzes: {
			type: Array,
			required: true,
		},
	},
	data() {
		return {
			spinStarted: false,
			spinInProgress: false,
			selectedQuiz: null,
		};
	},
	mounted() {
		this.initializeWheel();
	},
	methods: {
		closePopup() {
			this.$emit("close");
		},
		initializeWheel() {
			const sectors = this.filteredQuizzes().map((quiz) => ({
				color: quiz.color || this.getRandomColor(),
				text: "#333333",
				label: quiz.title,
				id: quiz.id,
			}));

			const rand = (m, M) => Math.random() * (M - m) + m;
			const tot = sectors.length;
			const spinEl = document.querySelector("#spin");
			const ctx = document.querySelector("#wheel").getContext("2d");
			const dia = ctx.canvas.width;
			const rad = dia / 2;
			const PI = Math.PI;
			const TAU = 2 * PI;
			const arc = TAU / sectors.length;
			const friction = 0.991;
			let angVel = 0;
			let ang = 0;

			const getIndex = () => Math.floor(tot - (ang / TAU) * tot) % tot;

			function drawSector(sector, i) {
				const ang = arc * i;
				ctx.save();
				ctx.beginPath();
				ctx.fillStyle = sector.color;
				ctx.moveTo(rad, rad);
				ctx.arc(rad, rad, rad, ang, ang + arc);
				ctx.lineTo(rad, rad);
				ctx.fill();

				ctx.translate(rad, rad);
				ctx.rotate(ang + arc / 2);
				ctx.textAlign = "right";
				ctx.fillStyle = sector.text;
				ctx.font = "bold 25px sans-serif";
				ctx.fillText(sector.label, rad - 30, 10);
				ctx.restore();
			}

			function rotate() {
				ctx.canvas.style.transform = `rotate(${ang - PI / 2}rad)`;
			}

			const frame = () => {
				if (!angVel && this.spinStarted) {
					const finalSector = sectors[getIndex()];
					this.selectedQuiz = { title: finalSector.label, id: finalSector.id };
					this.spinStarted = false;
					this.spinInProgress = false;
					jsConfetti.addConfetti();
					return;
				}
				angVel *= friction;
				if (angVel < 0.002) angVel = 0;
				ang += angVel;
				ang %= TAU;
				rotate();
			};

			const engine = () => {
				frame();
				requestAnimationFrame(engine);
			};

			sectors.forEach(drawSector);
			rotate();
			engine();

			spinEl.addEventListener("click", () => {
				if (!angVel) {
					this.spinStarted = true;
					this.spinInProgress = true;
					angVel = rand(0.25, 0.45);
				}
			});
		},
		getRandomColor() {
			const letters = "0123456789ABCDEF";
			let color = "#";
			for (let i = 0; i < 6; i++) {
				color += letters[Math.floor(Math.random() * 16)];
			}
			return color;
		},
		startQuiz() {
			if (this.selectedQuiz && this.selectedQuiz.id) {
				const quiz = this.quizzes.find(q => q.id === this.selectedQuiz.id);
				if (quiz) {
					const url = `/quiz?name=${quiz.id}&title=${encodeURIComponent(quiz.title)}&model=${quiz.model}&scale=${quiz.scale}&height=${quiz.height}&bg=${quiz.background}`;
					this.$router.push(url);
				} else {
					console.error("Quiz data not found for selected quiz");
				}
			} else {
				console.error("No quiz selected or quiz ID is undefined");
			}
		},
		filteredQuizzes() {
			return this.quizzes.filter(
				quiz => !['superquiz', 'streakquiz', 'flashquiz'].includes(quiz.id)
			);
		},
	},
};
</script>

<style scoped>
.popup-overlay {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background: rgba(0, 0, 0, 0.8);
	display: flex;
	justify-content: center;
	align-items: center;
	z-index: 1000;
	user-select: none;
}

.popup {
	background: #fff;
	border-radius: 8px;
	padding: 20px;
	position: relative;
	box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
	width: auto;
	height: 80vh;
	max-height: 80vh;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: space-between;
}

.popup-header {
	display: flex;
	justify-content: flex-end;
	position: absolute;
	top: 10px;
	right: 10px;
	width: calc(100% - 20px);
}

.close-button {
	background: none;
	border: none;
	font-size: 1.5rem;
	cursor: pointer;
	color: #333;
}

.close-button:hover {
	color: #666;
}

#spin_the_wheel {
	display: flex;
	justify-content: center;
	align-items: center;
	flex: 9;
	overflow: hidden;
	width: 90%;
	height: auto;
	margin: 0 auto;
}

#start_the_quiz {
	display: flex;
	justify-content: center;
	align-items: center;
	flex: 2;
	width: 90%;
	height: auto;
	flex-direction: column;
	text-align: center;
}

#wheel {
	width: auto;
	height: 100%;
}

#spin {
	font: bold 1.2em sans-serif;
	cursor: pointer;
	padding: 10px 20px;
	background-color: #ffffff;
	border-radius: 50%;
	border: 2px solid #333333;
	transition: all 0.3s ease;
	position: absolute;
	z-index: 11;
}

#spin:hover {
	background-color: #f0f0f0;
}

.start-button {
	background-color: green;
	color: white;
	font-size: 1.2rem;
	padding: 10px 20px;
	border: none;
	border-radius: 5px;
	cursor: pointer;
	margin-top: 10px;
}

.start-button:hover {
	background-color: darkgreen;
}

h1 {
	color: var(--cinequizz-red);
	font-style: bold;
}

#indicator {
	position: absolute;
	top: 95px;
	left: 50%;
	transform: translateX(-50%);
	width: 4px;
	height: calc(0.5 * 80 / 100 * (80vh - 40px));
	border-radius: 2px;
	box-shadow: 0 0 10px rgba(0, 0, 0, 0.9);
	z-index: 10;
}
</style>
