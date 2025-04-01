import axios from 'axios';

const API_BASE_URL = 'http://localhost:3000';

const adminService = {
    async getUsers() {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`${API_BASE_URL}/admin/users`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            return response.data.users;
        } catch (error) {
            console.error('Failed to fetch users:', error);
            throw error;
        }
    },

    async updateUser(user) {
        try {
            const token = localStorage.getItem('token');
            await axios.put(`${API_BASE_URL}/admin/users/${user.id}`, {
                username: user.username,
                isAdmin: user.isAdmin,
            }, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
        } catch (error) {
            console.error('Failed to update user:', error);
            throw error;
        }
    },


    async deleteUser(userId) {
        try {
            const token = localStorage.getItem('token');
            await axios.delete(`${API_BASE_URL}/admin/users/${userId}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
        } catch (error) {
            console.error('Failed to delete user:', error);
            throw error;
        }
    },

    async getAttempts() {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`${API_BASE_URL}/admin/attempts`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            return response.data.attempts;
        } catch (error) {
            console.error('Failed to fetch attempts:', error);
            throw error;
        }
    },

    async updateAttempt(attemptId, status) {
        try {
            const token = localStorage.getItem('token');
            await axios.put(`${API_BASE_URL}/admin/attempts/${attemptId}`, {
                status: status,
            }, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
        } catch (error) {
            console.error('Failed to update attempt:', error);
            throw error;
        }
    }

};

export default adminService;
