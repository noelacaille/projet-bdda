<template>
	<div class="profile">
		<h1>My profile</h1>

		<section class="profile-info black-box">
			<h2>Profile</h2>
			<div class="info">
				<p><strong>Username:</strong> {{ user.username }}</p>
				<p><strong>Register date:</strong> {{ formattedJoinDate }}</p>
			</div>
		</section>

		<section class="reset-scores black-box">
			<h2>Reset attempts and scores</h2>
			<button @click="confirmResetScores" class="reset-btn">Reset my scores</button>
		</section>

		<div v-if="showResetConfirmation" class="modal">
			<div class="modal-content">
				<h3>Are you sure you want to reset your attempts and scores?</h3>
				<p>This action cannot be undone.</p>
				<div class="modal-actions">
					<button @click="resetScores" class="confirm-btn">Yes, reset</button>
					<button @click="cancelResetScores" class="cancel-btn">Cancel</button>
				</div>
			</div>
		</div>

		<section class="username-change black-box">
			<h2>Change username</h2>
			<form @submit.prevent="updateUsername">
				<div class="username-group">
					<label for="new-username">New username</label>
					<div class="username-wrapper">
						<input id="new-username" v-model="usernameForm.newUsername" :class="usernameClass" required />
					</div>
					<p :class="usernameClass">{{ usernameMessage }}</p>
				</div>
				<p :class="usernameClass">{{ usernameMessage }}</p>
				<div class="password-group">
					<label for="password-confirmation">Confirm password</label>
					<div class="password-wrapper">
						<input :id="'password-confirmation'" :type="showPasswordConfirmation ? 'text' : 'password'"
							v-model="usernameForm.passwordConfirmation" required />
						<span @click="togglePasswordConfirmationVisibility" class="toggle-password">
							<img :src="showPasswordConfirmation ? eyeShowIcon : eyeHideIcon" />
						</span>
					</div>
				</div>
				<p v-if="usernameForm.errorMessage" class="error-message">{{ usernameForm.errorMessage }}</p>
				<p v-if="usernameForm.successMessage" class="success-message">{{ usernameForm.successMessage }}</p>
				<button type="submit">Update</button>
			</form>
		</section>

		<section class="password-change black-box">
			<h2>Change password</h2>
			<form @submit.prevent="updatePassword">
				<div class="password-group">
					<label for="current-password">Current password</label>
					<div class="password-wrapper">
						<input :id="'current-password'" :type="showCurrentPassword ? 'text' : 'password'"
							v-model="passwordForm.currentPassword" required />
						<span @click="toggleCurrentPasswordVisibility" class="toggle-password">
							<img :src="showCurrentPassword ? eyeShowIcon : eyeHideIcon" />
						</span>
					</div>
				</div>

				<div class="password-group">
					<label for="new-password">New password</label>
					<div class="password-wrapper">
						<input :id="'new-password'" :type="showNewPassword ? 'text' : 'password'"
							v-model="passwordForm.newPassword" required />
						<span @click="toggleNewPasswordVisibility" class="toggle-password">
							<img :src="showNewPassword ? eyeShowIcon : eyeHideIcon" />
						</span>
					</div>
				</div>

				<password-checker :password="passwordForm.newPassword"
					:confirm-password="passwordForm.confirmPassword" />

				<div class="password-group">
					<label for="confirm-password">Confirm password</label>
					<div class="password-wrapper">
						<input :id="'confirm-password'" :type="showNewPassword ? 'text' : 'password'"
							v-model="passwordForm.confirmPassword" required />
						<span @click="toggleNewPasswordVisibility" class="toggle-password">
							<img :src="showNewPassword ? eyeShowIcon : eyeHideIcon" />
						</span>
					</div>
					<p :class="confirmPasswordClass">{{ confirmPasswordText }}</p>
				</div>

				<button type="submit" :disabled="!isPasswordFormValid">Update</button>
			</form>
		</section>

		<section class="danger-zone black-box">
			<h2>Danger zone</h2>
			<div class="delete-account">
				<p>Deleting your account is an irreversible action. All your data will be permanently erased.</p>
				<button @click="confirmDeleteAccount" class="delete-btn">Delete my account</button>
			</div>
		</section>

		<div v-if="showDeleteConfirmation" class="modal">
			<div class="modal-content">
				<h3>Are you sure you want to delete your account?</h3>
				<p>This action is irreversible and will result in the permanent loss of all your data.</p>
				<div class="modal-actions">
					<button @click="deleteAccount" class="confirm-btn">Yes, delete</button>
					<button @click="cancelDeleteAccount" class="cancel-btn">Cancel</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import eyeShowIcon from '../assets/icons/eye_show.svg';
import eyeHideIcon from '../assets/icons/eye_hide.svg';
import authService from '@/services/authService';
import PasswordChecker from '../components/PasswordChecker.vue';

export default {
	name: "ProfileView",
	components: {
		PasswordChecker
	},
	data() {
		return {
			user: {
				username: "Username#0000",
				joinDate: "0000-00-00",
			},
			usernameForm: {
				newUsername: "",
				passwordConfirmation: "",
				usernameAvailable: null,
				errorMessage: "",
				successMessage: ""
			},
			passwordForm: {
				currentPassword: "",
				newPassword: "",
				confirmPassword: "",
			},
			showCurrentPassword: false,
			showNewPassword: false,
			showPasswordConfirmation: false,
			eyeShowIcon,
			eyeHideIcon,
			showDeleteConfirmation: false,
			showResetConfirmation: false
		};
	},
	async created() {
		try {
			const user = await authService.fetchUserDetails();
			this.user.username = user.username;
			this.user.joinDate = user.createdAt;
		} catch (error) {
			console.error('Failed to fetch user details:', error);
		}
	},
	computed: {
		formattedJoinDate() {
			return new Date(this.user.joinDate).toLocaleDateString("fr-FR", {
				year: "numeric",
				month: "long",
				day: "numeric",
			});
		},
		isPasswordFormValid() {
			const passwordStrongEnough =
				this.passwordForm.newPassword.length >= 8 &&
				/[A-Z]/.test(this.passwordForm.newPassword) &&
				/\d/.test(this.passwordForm.newPassword) &&
				/[!@#$%^&*(),.?":{}|<>]/.test(this.passwordForm.newPassword);

			return (
				passwordStrongEnough &&
				this.passwordForm.newPassword === this.passwordForm.confirmPassword
			);
		},
		confirmPasswordClass() {
			return this.passwordForm.newPassword === this.passwordForm.confirmPassword ? 'match-success' : 'match-error';
		},
		confirmPasswordText() {
			if (!this.passwordForm.confirmPassword) return '';
			return this.passwordForm.newPassword === this.passwordForm.confirmPassword ? 'Passwords match' : 'Passwords do not match';
		},
		usernameClass() {
			if (this.usernameForm.usernameAvailable === null) return ''; // Inconnu
			return this.usernameForm.usernameAvailable ? 'username-available' : 'username-taken';
		},
		usernameMessage() {
			if (this.usernameForm.usernameAvailable === null) return '';
			return this.usernameForm.usernameAvailable ? 'Username is available' : 'Username is already taken';
		}
	},
	methods: {
		async updateUsername() {
			if (!this.usernameForm.newUsername.trim()) {
				this.usernameForm.errorMessage = "The new username is required.";
				return;
			}
			if (!this.usernameForm.passwordConfirmation.trim()) {
				this.usernameForm.errorMessage = "Please confirm your password.";
				return;
			}

			try {
				await authService.updateUsername(
					this.usernameForm.newUsername.trim(),
					this.usernameForm.passwordConfirmation
				);
				this.usernameForm.successMessage = "Username updated!";
				this.usernameForm.errorMessage = "";
				window.location.reload();
			} catch (error) {
				this.usernameForm.successMessage = "";
				this.usernameForm.errorMessage = error.response?.data.message || "An error occurred while updating your username.";
			} finally {
				this.usernameForm.newUsername = "";
				this.usernameForm.passwordConfirmation = "";
			}
		},
		async updatePassword() {
			if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
				alert("The new passwords do not match.");
				return;
			}
			try {
				await authService.updatePassword(this.passwordForm.currentPassword, this.passwordForm.newPassword);
				alert("Password updated!");
			} catch (error) {
				console.error('Failed to update password:', error);
				alert("An error occurred while updating your password.");
			} finally {
				this.passwordForm.currentPassword = "";
				this.passwordForm.newPassword = "";
				this.passwordForm.confirmPassword = "";
			}
		},
		toggleCurrentPasswordVisibility() {
			this.showCurrentPassword = !this.showCurrentPassword;
		},
		toggleNewPasswordVisibility() {
			this.showNewPassword = !this.showNewPassword;
		},
		togglePasswordConfirmationVisibility() {
			this.showPasswordConfirmation = !this.showPasswordConfirmation;
		},
		confirmDeleteAccount() {
			this.showDeleteConfirmation = true;
		},
		cancelDeleteAccount() {
			this.showDeleteConfirmation = false;
		},
		async deleteAccount() {
			try {
				await authService.deleteAccount();
				this.showDeleteConfirmation = false;
				alert("Your account has been deleted.");
				localStorage.removeItem('token');
				this.$router.push('/login');
			} catch (error) {
				console.error('Failed to delete account:', error);
				alert("An error occurred while deleting your account.");
			}
		},
		confirmResetScores() {
			this.showResetConfirmation = true;
		},
		cancelResetScores() {
			this.showResetConfirmation = false;
		},
		async resetScores() {
			try {
				await authService.resetAttemptsAndScores();
				alert("Your attempts and scores have been reset.");
			} catch (error) {
				console.error('Failed to reset scores:', error);
				alert("An error occurred while resetting your scores.");
			} finally {
				this.showResetConfirmation = false;
			}
		}
	},
	watch: {
		"usernameForm.newUsername"(newUsername) {
			if (!newUsername.trim()) {
				this.usernameForm.usernameAvailable = null;
				this.usernameForm.errorMessage = "";
				return;
			}
			axios
				.get('http://localhost:3000/check-username', {
					params: { username: newUsername.trim() },
				})
				.then((response) => {
					this.usernameForm.usernameAvailable = !response.data.isTaken;
					this.usernameForm.errorMessage = "";
				})
				.catch(() => {
					this.usernameForm.usernameAvailable = null;
					this.usernameForm.errorMessage = "Error checking username availability.";
				});
		},
	}
};
</script>

<style scoped>
.profile {
	max-width: 600px;
	margin: 0 auto;
	padding: 20px;
	margin-bottom: 30px;
	margin-top: 30px;
	background-color: var(--cinequizz-white);
	color: var(--cinequizz-black);
	border: 1px solid var(--cinequizz-black);
	border-radius: 10px;
	margin: 30px auto;
}

h1,
h2 {
	color: var(--cinequizz-red);
}

.black-box {
	margin-bottom: 30px;
	padding: 15px;
	border: 2px solid var(--cinequizz-black);
	border-radius: 8px;
	background: var(--cinequizz-white);
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

label {
	display: block;
	margin-bottom: 5px;
	font-weight: bold;
	color: var(--cinequizz-black);
}

input,
select,
button {
	width: 100%;
	margin-bottom: 15px;
	padding: 10px;
	border: 1px solid var(--cinequizz-black);
	border-radius: 5px;
	font-size: 14px;
}

input:focus,
button:focus {
	outline: none;
	border-color: var(--cinequizz-red);
	box-shadow: 0 0 5px var(--cinequizz-red);
}

button {
	background: var(--cinequizz-red);
	color: var(--cinequizz-white);
	border: none;
	cursor: pointer;
	transition: background-color 0.3s ease, transform 0.2s ease;
}

button:hover {
	background: var(--cinequizz-black);
	color: var(--cinequizz-white);
	transform: translateY(-2px);
}

button:active {
	transform: translateY(0);
}

button:disabled,
.auth-button:disabled {
	background-color: #777;
	cursor: not-allowed;
}

.match-success {
	color: #4caf50;
}

.match-error {
	color: #ff4d4d;
}

.info p {
	margin: 5px 0;
	color: var(--cinequizz-black);
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

.danger-zone {
	margin-top: 30px;
	padding: 15px;
	background-color: #ffe6e6;
	border: 2px solid #ff4d4d;
	border-radius: 8px;
}

.delete-account {
	text-align: center;
}

.delete-btn {
	background-color: #ff4d4d;
	color: white;
	padding: 10px;
	border: none;
	border-radius: 5px;
	cursor: pointer;
}

.delete-btn:hover {
	background-color: #cc0000;
}

.modal {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0, 0, 0, 0.5);
	display: flex;
	justify-content: center;
	align-items: center;
	z-index: 100;
}

.modal-content {
	background-color: white;
	padding: 20px;
	border-radius: 8px;
	text-align: center;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.modal-actions button {
	margin: 10px;
	padding: 10px;
	border: none;
	border-radius: 5px;
	cursor: pointer;
}

.confirm-btn {
	background-color: #ff4d4d;
	color: white;
}

.confirm-btn:hover {
	background-color: #cc0000;
}

.cancel-btn {
	background-color: #cccccc;
	color: black;
}

.cancel-btn:hover {
	background-color: #999999;
}

.username-change {
	margin-bottom: 30px;
	padding: 15px;
	border: 2px solid var(--cinequizz-black);
	border-radius: 8px;
	background: var(--cinequizz-white);
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.password-status {
	margin-top: -10px;
	margin-bottom: 15px;
	font-size: 14px;
	font-weight: bold;
	color: #666666;
}

.password-status:empty {
	display: none;
}

.password-status:after {
	content: attr(data-message);
}

.password-status:matches(:text("Password match")) {
	color: green;
}

.password-status:matches(:text("Password do not match")) {
	color: red;
}

.username-available {
	color: green;
}

.username-taken {
	color: red;
}

.error-message {
	color: red;
	font-size: 14px;
	margin-top: -10px;
}

.success-message {
	color: green;
	font-size: 14px;
	margin-top: -10px;
}
</style>
