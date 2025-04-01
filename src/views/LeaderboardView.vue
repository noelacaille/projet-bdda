<template>
	<div class="leaderboard">
		<h1>Leaderboard</h1>
		<div class="section">
			<h2>Overall leaderboard</h2>
			<table class="overall-leaderboard">
				<thead>
					<tr>
						<th>Rank</th>
						<th>User</th>
						<th>Total score</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="(user, index) in overallLeaderboards" :key="user.user_id">
						<td>{{ index + 1 }}</td>
						<td :class="{ 'highlight-username': user.username === loggedInUsername }">
							{{ user.username }} <span v-if="getMedal(index)">{{ getMedal(index) }}</span>
						</td>
						<td>{{ user.total_score }}</td>
					</tr>
				</tbody>
			</table>
		</div>
		<div class="section">
			<h2>Best scores per quiz</h2>
			<table class="quiz-leaderboard">
				<thead>
					<tr>
						<th>Quiz name</th>
						<th>Best score</th>
						<th>User</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="quiz in quizLeaderboards" :key="quiz.quiz_id">
						<td>{{ quiz.quiz_id }}</td>
						<td>{{ quiz.best_score }}</td>
						<td :class="{ 'highlight-username': quiz.username === loggedInUsername }">
							{{ quiz.username }}
						</td>
					</tr>
				</tbody>
			</table>
		</div>
	</div>
</template>
<script>
import axios from "axios";
export default {
	data() {
		return {
			quizLeaderboards: [],
			overallLeaderboards: [],
			loggedInUsername: ""
		};
	},
	methods: {
		async fetchLeaderboards() {
			try {
				const { data: quizData } = await axios.get("http://localhost:3000/leaderboard/quiz");
				const { data: overallData } = await axios.get("http://localhost:3000/leaderboard/overall");
				this.quizLeaderboards = quizData;
				this.overallLeaderboards = overallData;
			} catch (error) {
				console.error("Error fetching leaderboards:", error);
			}
		},
		getMedal(index) {
			switch (index) {
				case 0:
					return "🥇";
				case 1:
					return "🥈";
				case 2:
					return "🥉";
				default:
					return "";
			}
		},
		async fetchLoggedInUser() {
			try {
				const { data } = await axios.get("http://localhost:3000/user", {
					headers: {
						Authorization: `Bearer ${localStorage.getItem("token")}`,
					},
				});
				this.loggedInUsername = data.username;
			} catch (error) {
				console.error("Failed to fetch logged-in user:", error);
			}
		}
	},
	mounted() {
		this.fetchLeaderboards();
		this.fetchLoggedInUser();
	},
};
</script>

<style>
.leaderboard {
	padding: 20px;
	margin: 0 15vw;
}

.section {
	margin-bottom: 40px;
}

table {
	width: 100%;
	border-collapse: collapse;
	margin-top: 20px;
}

thead {
	background-color: #f4f4f4;
}

th,
td {
	padding: 10px;
	text-align: left;
	border: 1px solid #ddd;
}

tr:nth-child(even) {
	background-color: #f9f9f9;
}

.highlight-username {
	background-color: #fff9c4;
	font-weight: bold;
}

table td span {
	margin-left: 5px;
}
</style>
