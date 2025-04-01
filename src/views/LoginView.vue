<template>
	<div class="auth-container">
		<div class="auth-content">
			<a>
				<!-- Logo dans public -->
				<img src="../assets/img/logo-no-bg.png" alt="Logo" class="app-logo" style="width: 300px;"/>
			</a>

			<h1 class="auth-title">{{ isLoginMode ? 'Welcome back !' : 'Join us !' }}</h1>

			<form @submit.prevent="submitForm" class="auth-form">
				<div class="input-group">
					<label for="username">Username</label>
					<input type="text" id="username" placeholder="Enter your username" v-model="username"
						:class="usernameClass" required />
					<p :class="usernameClass">{{ usernameMessage }}</p>
				</div>
				<div class="input-group password-group">
					<label for="password">Password</label>
					<div class="password-wrapper">
						<input :type="showPassword ? 'text' : 'password'" id="password"
							placeholder="Enter your password" v-model="password" required />
						<span @click="togglePasswordVisibility" class="toggle-password">
							<img :src="showPassword ? eyeShowIcon : eyeHideIcon" />
						</span>
					</div>
				</div>

				<div v-if="!isLoginMode">
					<password-checker :password="password" :confirm-password="confirmPassword"
						@update-strength="updateStrength" />
					<div class="input-group password-group">
						<label for="confirmPassword">Confirm Password</label>
						<div class="password-wrapper">
							<input :type="showPassword ? 'text' : 'password'" id="confirmPassword"
								placeholder="Confirm your password" v-model="confirmPassword" required />
							<span @click="togglePasswordVisibility" class="toggle-password">
								<img :src="showPassword ? eyeShowIcon : eyeHideIcon" />
							</span>
						</div>
						<p :class="confirmPasswordClass">{{ confirmPasswordText }}</p>
					</div>
				</div>

				<button type="submit" class="auth-button" :disabled="!isFormValid">
					{{ isLoginMode ? 'Login' : 'Register' }}
				</button>

				<p class="error-message" v-if="errorMessage">{{ errorMessage }}</p>

				<p class="toggle-mode">
					{{ isLoginMode ? "Don't have an account ?" : "Already have an account ?" }}
					<a href="#" @click.prevent="toggleMode">
						{{ isLoginMode ? 'Sign up' : 'Login' }}
					</a>
				</p>
			</form>
		</div>
	</div>
</template>

<script>
import axios from 'axios';
import PasswordChecker from '../components/PasswordChecker.vue';
import eyeShowIcon from '../assets/icons/eye_show.svg';
import eyeHideIcon from '../assets/icons/eye_hide.svg';

export default {
	components: {
		PasswordChecker,
	},
	data() {
		return {
			username: '',
			password: '',
			confirmPassword: '',
			isLoginMode: true,
			showPassword: false,
			errorMessage: '',
			eyeShowIcon,
			eyeHideIcon,
			usernameAvailable: null
		};
	},
	watch: {
		username(newUsername) {
			if (!newUsername || this.isLoginMode) {
				this.usernameAvailable = null;
				return;
			}
			axios
				.get('http://localhost:3000/check-username', {
					params: { username: newUsername },
				})
				.then((response) => {
					this.usernameAvailable = !response.data.isTaken;
				})
				.catch(() => {
					this.usernameAvailable = null;
				});
		},
	},
	computed: {
		confirmPasswordClass() {
			return this.password === this.confirmPassword ? 'match-success' : 'match-error';
		},
		confirmPasswordText() {
			if (!this.confirmPassword) return '';
			return this.password === this.confirmPassword ? 'Passwords match' : 'Passwords do not match';
		},
		isFormValid() {
			if (this.isLoginMode) {
				return this.username && this.password;
			} else {
				const passwordStrongEnough = this.password.length >= 8 &&
					/[A-Z]/.test(this.password) &&
					/\d/.test(this.password) &&
					/[!@#$%^&*(),.?":{}|<>]/.test(this.password);

				return this.username && passwordStrongEnough && this.password === this.confirmPassword;
			}
		},
		usernameClass() {
			if (this.usernameAvailable === null) return '';
			return this.usernameAvailable ? 'username-available' : 'username-taken';
		},
		usernameMessage() {
			if (this.usernameAvailable === null) return '';
			return this.usernameAvailable ? 'Username is available' : 'Username is already taken';
		}
	},
	methods: {
		resetFormState() {
			this.username = '';
			this.password = '';
			this.confirmPassword = '';
			this.usernameAvailable = null;
			this.errorMessage = '';
		},
		toggleMode() {
			this.isLoginMode = !this.isLoginMode;
			this.resetFormState();
		},
		togglePasswordVisibility() {
			this.showPassword = !this.showPassword;
		},
		async submitForm() {
			if (this.isLoginMode) {
				await this.login();
			} else {
				await this.register();
			}
		},
		async login() {
			try {
				const response = await axios.post('http://localhost:3000/login', {
					username: this.username,
					password: this.password,
				});
				localStorage.setItem('token', response.data.token);
				this.$router.push('/home');
			} catch (error) {
				this.errorMessage = error.response?.data.message || 'Login failed';
			}
		},
		async register() {
			if (this.usernameAvailable === false) {
				this.errorMessage = 'Username is already taken';
				return;
			}
			try {
				await axios.post('http://localhost:3000/register', {
					username: this.username,
					password: this.password,
				});
				alert('Registration successful! You can now log in.');
				this.isLoginMode = true;
				this.resetFormState();
			} catch (error) {
				this.errorMessage = error.response?.data.message || 'Registration failed';
			}
		}
	}
};
</script>

<style scoped>
.app-title {
	font-size: 2.5rem;
	color: var(--pnt-button);
}

.auth-container {
	position: relative;
	display: flex;
	align-items: center;
	justify-content: center;
	min-height: 100vh;
	background: url('@/assets/img/background.jpg') no-repeat center center/cover;
}

.auth-container::before {
	content: '';
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background: rgba(0, 0, 0, 0.8);
	z-index: 1;
}

.auth-content {
	position: relative;
	z-index: 2;
	background: rgb(253, 241, 240);
	padding: 40px;
	border-radius: 10px;
	width: 100%;
	max-width: 400px;
	text-align: center;
}

.auth-title {
	font-size: 24px;
	margin-bottom: 20px;
	color: black;
}

.auth-form {
	display: flex;
	flex-direction: column;
	color: black;
}

.input-group {
	margin-bottom: 15px;
}

.input-group label {
	display: block;
	margin: 10px 0;
	font-weight: bold;
}

.input-group input {
	width: 100%;
	padding: 10px;
	border: none;
	border-radius: 5px;
	font-size: 16px;
	margin-bottom: 10px;
}

.auth-button {
	margin: 10px 0;
	background-color: var(--pnt-button);
	color: white;
	border: none;
	padding: 10px;
	border-radius: 5px;
	font-size: 16px;
	cursor: pointer;
	transition: background-color 0.3s ease;
}

.auth-button:disabled {
	background-color: #777;
	cursor: not-allowed;
}

.auth-button:hover:not(:disabled) {
	background-color: var(--pnt-button-hover);
}

.error-message {
	color: var(--pnt-button);
	margin-top: 10px;
}

.toggle-mode {
	margin-top: 15px;
}

.toggle-mode a {
	color: var(--pnt-button);
	text-decoration: underline;
	cursor: pointer;
}

.password-group {
	position: relative;
}

.password-wrapper {
	position: relative;
	display: flex;
	align-items: center;
}

.password-wrapper input {
	width: 100%;
	padding-right: 40px;
}

.toggle-password {
	position: absolute;
	right: 10px;
	top: 50%;
	transform: translateY(-50%);
	cursor: pointer;
}

.toggle-password img {
	width: 25px;
	height: 25px;
}

.match-success {
	color: #4caf50;
}

.match-error {
	color: #ff4d4d;
}

.username-available {
	color: #4caf50;
}

.username-taken {
	color: #ff4d4d;
}
</style>
