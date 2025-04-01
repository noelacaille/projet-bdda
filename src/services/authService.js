import axios from 'axios';

const API_BASE_URL = 'http://localhost:3000';

const authService = {
	async fetchUserDetails() {
		try {
			const token = localStorage.getItem('token');
			if (token) {
				const response = await axios.get(`${API_BASE_URL}/user`, {
					headers: {
						Authorization: `Bearer ${token}`,
					},
				});
				return {
					username: response.data.username,
					createdAt: response.data.created_at,
					isAdmin: response.data.isAdmin,
				};
			}
			throw new Error('No token found');
		} catch (error) {
			console.error('Error fetching user details', error);
			throw error;
		}
	},

	async resetAttemptsAndScores() {
		const token = localStorage.getItem('token');
		if (!token) throw new Error('No token found');
		try {
			const response = await axios.delete(`${API_BASE_URL}/attempts/reset`, {
				headers: {
					Authorization: `Bearer ${token}`,
				},
			});
			return response.data;
		} catch (error) {
			console.error('Error resetting attempts and scores', error);
			throw error;
		}
	},

	async updateUsername(newUsername, passwordConfirmation) {
		const token = localStorage.getItem('token');
		if (!token) throw new Error('No token found');
		try {
			const response = await axios.put(
				`${API_BASE_URL}/user/username`,
				{ newUsername, passwordConfirmation },
				{
					headers: {
						Authorization: `Bearer ${token}`,
					},
				}
			);
			return response.data;
		} catch (error) {
			console.error('Error updating username', error);
			throw error;
		}
	},

	async updatePassword(currentPassword, newPassword) {
		const token = localStorage.getItem('token');
		if (!token) throw new Error('No token found');
		try {
			const response = await axios.put(
				`${API_BASE_URL}/user/password`,
				{ currentPassword, newPassword },
				{
					headers: {
						Authorization: `Bearer ${token}`,
					},
				}
			);
			return response.data;
		} catch (error) {
			console.error('Error updating password', error);
			throw error;
		}
	},

	async deleteAccount() {
		const token = localStorage.getItem('token');
		if (!token) throw new Error('No token found');
		try {
			const response = await axios.delete(`${API_BASE_URL}/user`, {
				headers: {
					Authorization: `Bearer ${token}`,
				},
			});
			return response.data;
		} catch (error) {
			console.error('Error deleting account', error);
			throw error;
		}
	},
};

export default authService;
