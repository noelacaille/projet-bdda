<template>
    <div class="quiz-container" :class="{ centered: isCenteredQuiz }">
        <div v-if="!isCenteredQuiz" id="threedimension-container"></div>
        <img v-if="background" :src="background" class="quiz-background" />

        <div class="quiz-view">
            <div class="title-div">
                <h1>{{ title }}</h1>
            </div>

            <div v-if="loading" class="loading">Loading...</div>
            <div v-else-if="error" class="error">{{ error }}</div>
            <div v-else>
                <div v-if="currentQuestionIndex < questions.length" class="question-card" :class="{ shake: isShaking }">
                    <h2>Question {{ currentQuestionIndex + 1 }} / {{ questions.length }}</h2>
                    <div v-if="quizType === 'flashquiz'" class="countdown" :style="{ color: 'red' }">
                        {{ formatTimeInSeconds(timeRemaining) }} seconds remaining
                    </div>
                    <div v-if="currentQuestion.picture" class="image-container">
                        <img :src="`${currentQuestion.picture}`" />
                    </div>
                    <p class="question">{{ currentQuestion.question }}</p>

                    <div class="answers">
                        <button v-for="(answer, i) in currentQuestion.answers" :key="i" :class="{
                            'correct': answered && i === currentQuestion.good_answer,
                            'incorrect': answered && i !== currentQuestion.good_answer && i === selectedAnswer,
                        }" @click="selectAnswer(i)" class="answer-btn" :disabled="answered">
                            {{ answer }}
                        </button>
                    </div>

                    <button v-if="answered && quizType !== 'flashquiz'" class="next-btn" @click="nextQuestion">
                        Next Question
                    </button>
                </div>
                <div v-else-if="quizFinished || currentQuestionIndex >= questions.length" class="score-card">
                    <h2>Quiz Completed</h2>
                    <p v-if="endMessage">{{ endMessage }}</p>
                    <p>Your Score: {{ correctAnswers }} / {{ questions.length }}</p>
                    <button @click="goHome" class="return-btn">Back to quizzes</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import axios from "axios";
import JSConfetti from 'js-confetti';
import positiveSound from '../assets/audio/correct.mp3';
import negativeSound from '../assets/audio/wrong.mp3';
import fanfareSound from '../assets/audio/fanfare.mp3';

export default {
    name: "QuizView",
    data() {
        return {
            quizID: "",
            title: "",
            questions: [],
            loading: true,
            error: null,
            model: null,
            currentQuestionIndex: 0,
            selectedAnswer: null,
            answered: false,
            correctAnswers: 0,
            background: null,
            isShaking: false,
            audioPositive: positiveSound,
            audioNegative: negativeSound,
            audioFanfare: fanfareSound,
            fanfarePlaying: false,
            isPlaying: false,
            currentTime: 0,
            audioDuration: 0,
            timer: null,
            timeSpent: [],
            quizType: "",
            endMessage: "",
            timeRemaining: null,
            bestScore: "Never attempted",
            quizFinished: false
        };
    },
    computed: {
        currentQuestion() {
            return this.questions[this.currentQuestionIndex] || {};
        },
        isCenteredQuiz() {
            return ['superquiz', 'streakquiz', 'flashquiz'].includes(this.$route.query.name);
        },
        currentQuestion() {
            return this.questions[this.currentQuestionIndex] || {};
        }
    },
    methods: {
        fetchQuizData(name) {
            this.loading = true;
            this.error = null;
            axios
                .get(`http://localhost:3000/quiz?name=${name}`)
                .then((response) => {
                    this.questions = response.data.questions.map(question => {
                        const shuffledAnswers = this.shuffleArray(question.answers);
                        return {
                            ...question,
                            answers: shuffledAnswers,
                            good_answer: shuffledAnswers.indexOf(question.answers[question.good_answer])
                        };
                    });
                    this.questions = this.shuffleArray(this.questions);
                    this.quizID = name.replace(/-/g, " ").toUpperCase();
                    this.loading = false;
                })
                .catch((error) => {
                    console.error("Error fetching quiz data:", error);
                    this.error = "Failed to load the quiz. Please try again later.";
                    this.loading = false;
                });

            this.bestScore = this.$route.query.bestScore || 'Never attempted';
        },
        shuffleArray(array) {
            return array
                .map((item) => ({ item, sort: Math.random() }))
                .sort((a, b) => a.sort - b.sort)
                .map(({ item }) => item);
        },
        selectAnswer(selectedIndex) {
            this.selectedAnswer = selectedIndex;
            this.answered = true;

            if (selectedIndex === this.currentQuestion.good_answer) {
                this.correctAnswers++;
                this.triggerConfetti();
                this.playPositiveSound();
            } else {
                this.shakeScreen();
                this.playNegativeSound();
                if (this.quizType === "streakquiz") {
                    this.endMessage = "Game Over! You lost your streak!";
                    this.shakeScreen();
                    this.currentQuestionIndex = this.questions.length;
                    this.saveAttempt();
                }
            }
            if (this.quizType === "flashquiz") {
                clearTimeout(this.timer);
                const elapsedTime = 3000 - (this.timeRemaining || 0);
                this.timeSpent.push(elapsedTime);
                setTimeout(() => this.nextQuestion(), 1000);
            }
        },
        nextQuestion() {
            if (this.currentQuestionIndex >= this.questions.length - 1) {
                clearInterval(this.timer);
                this.quizFinished = true;
                this.currentQuestionIndex = this.questions.length;

                if (this.quizType === "flashquiz") {
                    const averageTime =
                        this.timeSpent.reduce((a, b) => a + b, 0) / this.timeSpent.length;
                    this.endMessage = `Quiz completed! Average time per question: ${this.formatTimeInSeconds(averageTime)}`;
                }

                if (this.quizType === "streakquiz" && !this.endMessage) {
                    this.endMessage = "Congratulations! You completed the streak!";
                }

                this.playFanfareSound();
                this.saveAttempt();
                return;
            }

            this.currentQuestionIndex++;
            this.selectedAnswer = null;
            this.answered = false;
            this.isShaking = false;
            if (this.quizType === "flashquiz") this.startTimer();
        },
        playPositiveSound() {
            const audio = new Audio(this.audioPositive);
            audio.play().catch(error => {
                console.error('Error playing "Positive" sound:', error);
            });
        },
        playNegativeSound() {
            const audio = new Audio(this.audioNegative);
            audio.play().catch(error => {
                console.error('Error playing "Negative" sound:', error);
            });
        },
        playFanfareSound() {
            if (this.fanfarePlaying) return;
            this.fanfarePlaying = true;
            const audio = new Audio(this.audioFanfare);
            audio.play().then(() => {
                audio.addEventListener('ended', () => {
                    this.fanfarePlaying = false;
                });
            }).catch(error => {
                console.error('Error playing "Fanfare" sound:', error);
                this.fanfarePlaying = false;
            });
        },
        stopAllTimers() {
            clearInterval(this.timer);
        },
        shakeScreen() {
            this.isShaking = true;
            const questionCard = document.querySelector('.question-card');
            questionCard.style.backgroundColor = 'rgba(255, 0, 0, 0.4)';
            setTimeout(() => {
                questionCard.style.backgroundColor = '';
                this.isShaking = false;
            }, 500);
        },
        init3D(model, scale = 0.2, height = -0.5) {
            const container = document.getElementById('threedimension-container');
            const width = container.clientWidth;
            const heightViewport = container.clientHeight;

            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, width / heightViewport, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({ alpha: true });
            renderer.setSize(width, heightViewport);
            container.appendChild(renderer.domElement);

            const ambientLight = new THREE.AmbientLight(0xffffff, 2);
            scene.add(ambientLight);
            const directionalLight = new THREE.DirectionalLight(0xffffff, 2.5);
            directionalLight.position.set(5, 10, 7.5);
            scene.add(directionalLight);

            const loader = new GLTFLoader();
            loader.load(model, (gltf) => {
                const gltfModel = gltf.scene;
                gltfModel.scale.set(scale, scale, scale);
                gltfModel.position.set(0, height, 0);
                scene.add(gltfModel);

                const rotateModel = () => {
                    if (gltfModel) {
                        gltfModel.rotation.y += 0.01;
                    }
                    requestAnimationFrame(rotateModel);
                };
                rotateModel();
            });

            camera.position.set(0, 1, 5);

            const controls = new OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;

            controls.minPolarAngle = Math.PI / 4;
            controls.maxPolarAngle = Math.PI / 2;

            controls.enableZoom = false;
            controls.enablePan = false;

            const animate = () => {
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            };
            animate();

            window.addEventListener('resize', () => {
                const width = container.clientWidth;
                const heightViewport = container.clientHeight;
                camera.aspect = width / heightViewport;
                camera.updateProjectionMatrix();
                renderer.setSize(width, heightViewport);
            });
        },
        triggerConfetti() {
            const jsConfetti = new JSConfetti();
            jsConfetti.addConfetti({
                emojis: ['🎉', '✨'],
                emojiSize: 50,
                confettiNumber: 100,
            });
        },
        togglePlayPause() {
            const audio = this.$refs.audioPlayer;
            if (audio.paused) {
                audio.play();
                this.isPlaying = true;
            } else {
                audio.pause();
                this.isPlaying = false;
            }
        },
        seekAudio(event) {
            const audio = this.$refs.audioPlayer;
            audio.currentTime = event.target.value;
        },
        updateAudioTime() {
            const audio = this.$refs.audioPlayer;
            this.currentTime = audio.currentTime;
        },
        formatTime(seconds) {
            const minutes = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60).toString().padStart(2, '0');
            return `${minutes}:${secs}`;
        },
        formatTimeInSeconds(milliseconds) {
            return `${(milliseconds / 1000).toFixed(1)}s`;
        },
        goHome() {
            this.$router.push('/home');
        },
        async saveAttempt() {
            const token = localStorage.getItem('token');
            try {
                const response = await axios.post(
                    'http://localhost:3000/attempts',
                    { quizId: this.quizID, score: this.correctAnswers },
                    { headers: { Authorization: `Bearer ${token}` } }
                );

                const serverBestScore = response.data.bestScore;
                if (serverBestScore !== undefined && serverBestScore !== null) {
                    this.bestScore = Math.max(
                        parseInt(this.bestScore) || 0,
                        parseInt(serverBestScore)
                    );
                } else {
                    this.bestScore = this.correctAnswers;
                }
            } catch (error) {
                console.error('Error saving attempt:', error);
            }
        },
        startTimer() {
            if (this.quizType !== "flashquiz") return;
            clearInterval(this.timer);
            this.timeRemaining = 3000;
            this.timer = setInterval(() => {
                if (this.timeRemaining <= 0) {
                    clearInterval(this.timer);
                    this.timeSpent.push(3000);
                    this.nextQuestion();
                } else {
                    this.timeRemaining -= 100;
                }
            }, 100);
        },
    },
    mounted() {
        const name = this.$route.query.name;
        const model = this.$route.query.model;
        const scale = parseFloat(this.$route.query.scale) || 0.2;
        const height = parseFloat(this.$route.query.height) || -0.5;
        const bg = this.$route.query.bg;

        this.quizType = name;
        this.title = this.$route.query.title.toUpperCase();

        if (name) {
            this.fetchQuizData(name);
        } else {
            this.error = "No quiz name specified.";
            this.loading = false;
        }

        if (model) {
            this.model = model;
            this.init3D(model, scale, height);
        }

        if (bg) {
            this.background = bg;
        }

        if (this.quizType === "flashquiz") {
            this.startTimer();
        }
    },
    beforeDestroy() {
        this.stopAllTimers();
        const audio = this.$refs.audioPlayer;

        if (audio) {
            audio.removeEventListener('timeupdate', this.updateAudioTime);
            audio.removeEventListener('loadedmetadata', () => {
                this.audioDuration = audio.duration;
            });
        }

        if (this.timer) {
            clearInterval(this.timer);
        }
    }
};

</script>

<style scoped>
.quiz-container {
    position: relative;
    display: flex;
    overflow: hidden;
}

.quiz-container.centered {
    justify-content: center;
    align-items: center;
    height: calc(100vh - var(--navbar-height));
}

.quiz-background {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 1;
    filter: blur(5px);
    outline: 10px solid black;
}

.quiz-view {
    position: relative;
    z-index: 1;
    width: 67vw;
    height: calc(100vh - var(--navbar-height));
    padding: 0 30px;
}

.quiz-container.centered .quiz-view {
    width: 100%;
    max-width: 800px;
    height: auto;
    padding: 20px;
}

#threedimension-container {
    width: 33vw;
    height: calc(100vh - var(--navbar-height));
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 2;
}

.question-card.shake {
    animation: shake 0.5s;
}

@keyframes shake {

    0%,
    100% {
        transform: translateX(0);
    }

    25% {
        transform: translateX(-10px);
    }

    50% {
        transform: translateX(10px);
    }

    75% {
        transform: translateX(-10px);
    }
}

.title-div {
    height: calc(10 / 100 * (100vh - var(--navbar-height)));
}

h1 {
    text-align: center;
    color: var(--cinequizz-red);
}

.loading,
.error {
    text-align: center;
    font-size: 1.2rem;
    margin-top: 20px;
}

.question-card,
.score-card {
    margin-bottom: 30px;
    padding: 20px;
    border-radius: 8px;
    background: #fff;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    text-align: center;
    background-color: rgba(255, 255, 255, 0.4);
    width: 100%;
    max-height: calc(85 / 100 * (100vh - var(--navbar-height)));
    overflow-y: auto;
    overflow-x: hidden;
}

.question-card::-webkit-scrollbar {
    width: 8px;
}

.question-card::-webkit-scrollbar-thumb {
    background: rgba(128, 128, 128, 0.5);
    border-radius: 4px;
}

.question-card::-webkit-scrollbar-thumb:hover {
    background: rgba(128, 128, 128, 0.7);
}

.question {
    font-size: xx-large;
    font-weight: bold;
}

.answers {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-top: 15px;
    justify-content: center;
}

.answer-btn {
    padding: 15px 25px;
    background-color: var(--cinequizz-red);
    color: #fff;
    border: none;
    border-radius: 5px;
    font-size: large;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.2s ease;
}

.answer-btn.correct {
    background-color: green;
}

.answer-btn.incorrect {
    background-color: red;
}

.answer-btn.correct:hover {
    background-color: #1e5811;
    transform: translateY(-2px);
}

.answer-btn:hover {
    background-color: #560707;
    transform: translateY(-2px);
}

.answer-btn:active {
    transform: translateY(0);
}

.image-container {
    margin-top: 20px;
    text-align: center;
}

.image-container img {
    max-height: calc(35 / 100 * (100vh - var(--navbar-height)));
    width: auto;
    max-width: 80%;
    border-radius: 8px;
}

.audio-container {
    margin-top: 20px;
    text-align: center;
}

.next-btn {
    margin-top: 20px;
    padding: 15px 25px;
    background-color: var(--cinequizz-black);
    color: #fff;
    font-size: large;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.2s ease;
}

.next-btn:hover {
    background-color: #494949;
}

.custom-audio-player {
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(45deg, #6a11cb, #2575fc);
    padding: 10px 15px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    color: white;
}

.play-pause-btn {
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    transition: transform 0.2s ease-in-out;
}

.play-pause-btn:hover {
    transform: scale(1.1);
}

.progress-bar-container {
    flex: 1;
    display: flex;
    align-items: center;
}

.progress-bar {
    width: 100%;
    background: #fff;
    appearance: none;
    height: 6px;
    border-radius: 5px;
    outline: none;
}

.progress-bar::-webkit-slider-thumb {
    appearance: none;
    width: 12px;
    height: 12px;
    background: #2575fc;
    border-radius: 50%;
    cursor: pointer;
}

.current-time,
.duration {
    font-size: 0.9rem;
}

.return-btn {
    margin-top: 20px;
    padding: 15px 25px;
    background-color: var(--cinequizz-black);
    color: #fff;
    font-size: large;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.2s ease;
}

.return-btn:hover {
    background-color: #494949;
}

.countdown {
    font-size: 1.5rem;
    font-weight: bold;
    margin: 10px 0;
}

@media screen and (max-width: 768px) {
    #threedimension-container {
        display: none;
    }

    .quiz-view {
        width: 100%;
        height: auto;
        padding: 15px;
    }

    .question {
        font-size: large;
    }

    .answer-btn {
        font-size: medium;
        padding: 10px 15px;
    }

    .custom-audio-player {
        flex-direction: column;
        gap: 5px;
    }

    .play-pause-btn {
        font-size: 1rem;
    }

    .progress-bar {
        height: 4px;
    }
}
</style>
