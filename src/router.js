import { createRouter, createWebHistory } from 'vue-router'
import authService from '@/services/authService';

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: '/',
			redirect: '/login'
		},
		{
			path: '/:pathMatch(.*)*',
			redirect: '/'
		},
		{
			path: '/login',
			name: 'LoginView',
			component: () => import('./views/LoginView.vue')
		},
		{
			path: '/home',
			name: 'HomeView',
			component: () => import('./views/HomeView.vue'),
			meta: { requiresAuth: true }
		},
		{
			path: '/profile',
			name: 'ProfileView',
			component: () => import('./views/ProfileView.vue'),
			meta: { requiresAuth: true }
		},
		{
			path: '/quiz',
			name: 'QuizView',
			component: () => import('./views/QuizView.vue'),
			meta: { requiresAuth: true }
		},
		{
			path: '/about',
			name: 'AboutView',
			component: () => import('./views/AboutView.vue')
		},
		{
			path: '/admin',
			name: 'AdminView',
			component: () => import('./views/AdminView.vue'),
			meta: { requiresAuth: true, isAdmin: true }
		}
	]
});

router.beforeEach(async (to, from, next) => {
	const isAuthenticated = localStorage.getItem('token');

	if (to.meta.requiresAuth && !isAuthenticated) {
		return next('/login');
	}

	if (to.meta.isAdmin) {
		const userDetails = await authService.fetchUserDetails();
		if (!userDetails.isAdmin) {
			return next('/');
		}
	}

	next();
});

export default router;
