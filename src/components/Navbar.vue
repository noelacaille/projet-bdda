<template>
	<div class="navbar">
		<div class="navLink">
			<router-link to="/home">Home</router-link>
		</div>
		<div class="navLink">
			<router-link to="/leaderboard">Leaderboard</router-link>
		</div>

		<!-- Profil à droite -->
		<div class="profile" @click="toggleProfileMenu">
			<svg class="profile-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
				<path fill="white" d="M224 256A128 128 0 1 0 224 0a128 128 0 1 0 0 256zm-45.7 48C79.8 304 0 383.8 0 482.3C0 498.7 13.3 512 29.7 512l388.6 0c16.4 0 29.7-13.3 29.7-29.7C448 383.8 368.2 304 269.7 304l-91.4 0z" />
			</svg>
			<span class="username">{{ username || "Guest" }}</span>

			<!-- Menu déroulant -->
			<div v-if="showProfileMenu" class="profile-menu" ref="profileMenu">
				<ul>
					<li v-if="isAdmin" @click="adminPanel">ADMIN PANEL</li>
					<li @click="editProfile">Settings</li>
					<li @click="logout">Logout</li>
				</ul>
			</div>
		</div>
	</div>
</template>


<script>
import authService from '@/services/authService';

export default {
	name: 'NavBar',
	data() {
		return {
			showProfileMenu: false,
			username: '',
			isAdmin: false,
		};
	},
	async created() {
		try {
			const user = await authService.fetchUserDetails();
			this.username = user.username;
			this.isAdmin = user.isAdmin;
		} catch (error) {
			console.error('Failed to fetch user details:', error);
		}
	},
	mounted() {
		document.addEventListener('click', this.handleOutsideClick);
	},
	beforeDestroy() {
		document.removeEventListener('click', this.handleOutsideClick);
	},
	methods: {
		toggleProfileMenu(event) {
			this.showProfileMenu = !this.showProfileMenu;
			event.stopPropagation();
		},
		editProfile() {
			this.$router.push('/profile');
		},
		logout() {
			localStorage.removeItem('token');
			this.$router.push('/login');
		},
		adminPanel() {
			this.$router.push('/admin');
		},
		handleOutsideClick(event) {
			if (this.showProfileMenu && this.$refs.profileMenu && !this.$refs.profileMenu.contains(event.target)) {
				this.showProfileMenu = false;
			}
		},
	},
};
</script>


<style scoped>
.navbar {
	width: 100%;
	height: var(--navbar-height);
	background-color: var(--cinequizz-black);
	display: flex;
	flex-direction: row;
	padding: 8px;
	color: var(--cinequizz-white);
	position: sticky;
	top: 0;
	z-index: 100;
	user-select: none;
}

.navbar ul {
	list-style-type: none;
	padding: 0;
}

.navLink {
	margin: 20px;
}

.navbar a {
	color: var(--cinequizz-white);
	text-decoration: none;
	font-size: 18px;
}

.navbar a:hover {
	color: var(--cinequizz-red);
}

.profile {
	display: flex;
	align-items: center;
	cursor: pointer;
	position: relative;
	margin-left: auto;
	margin-right: 20px;
}

.profile-icon {
	font-size: 24px;
	color: var(--cinequizz-white);
	margin-right: 8px;
}

.username {
	font-size: 18px;
	color: var(--cinequizz-white);
}

.profile-menu {
	position: absolute;
	top: 40px;
	right: -10px;
	background-color: var(--cinequizz-black);
	padding: 10px;
	border-radius: 8px;
	box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
	z-index: 200;
	width: 150px;	
}

.profile-menu ul {
	padding: 0;
	margin: 0;
}

.profile-menu li {
	color: var(--cinequizz-white);
	padding: 8px;
	cursor: pointer;
}

.profile-menu li:hover {
	background-color: var(--cinequizz-red);
}

.profile-icon {
	height: 25px;
	margin: 10px;
}
</style>
