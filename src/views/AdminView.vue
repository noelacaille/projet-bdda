<template>
    <div class="admin">
        <h1>Admin panel</h1>

        <div v-if="loading" class="loading">Loading...</div>
        <div v-else>
            <h2>User list</h2>
            <table class="user-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Created at</th>
                        <th>Is admin</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="user in users" :key="user.id">
                        <td>{{ user.id }}</td>
                        <td>
                            <input v-model="user.username" :disabled="!isEditing(user.id)" placeholder="Username" />
                        </td>
                        <td>
                            <p>{{ formatDate(user.created_at) }}</p>
                        </td>
                        <td>
                            <input type="checkbox" :disabled="!isAdmin || !isEditing(user.id)"
                                @change="toggleAdmin(user)" :checked="user.isAdmin === 1" />
                        </td>
                        <td>
                            <button v-if="!isEditing(user.id)" @click="startEditing(user.id)">Edit</button>
                            <button v-if="isEditing(user.id)" @click="saveUser(user)">Save</button>
                            <button @click="deleteUser(user.id)">Delete</button>
                        </td>
                    </tr>
                </tbody>
            </table>

            <h2>Attempts</h2>
            <table class="attempts-table">
                <thead>
                    <tr>
                        <th>Quiz</th>
                        <th>User</th>
                        <th>Score</th>
                        <th>Attempted at</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="attempt in attempts" :key="attempt.id">
                        <td>{{ attempt.quiz_id }}</td>
                        <td>{{ attempt.username }}</td>
                        <td>{{ attempt.score }}</td>
                        <td>{{ attempt.attempt_time.split(' ')[0] }}</td>
                        <td>{{ attempt.attempt_time.split(' ')[1] }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script>
import adminService from '@/services/adminService';
import authService from '@/services/authService';

export default {
    name: 'Admin',
    data() {
        return {
            users: [],
            attempts: [],
            editingUserId: null,
            editingAttemptId: null,
            loading: true,
            isAdmin: false
        };
    },
    methods: {
        async fetchUsers() {
            try {
                this.loading = true;
                this.users = await adminService.getUsers();
            } catch (error) {
                console.error('Failed to fetch users:', error);
            } finally {
                this.loading = false;
            }
        },
        async fetchAttempts() {
            try {
                const response = await adminService.getAttempts();
                this.attempts = response;
            } catch (error) {
                console.error('Failed to fetch attempts:', error);
            }
        },
        startEditing(userId) {
            this.editingUserId = userId;
        },
        isEditing(userId) {
            return this.editingUserId === userId;
        },
        async saveUser(user) {
            try {
                await adminService.updateUser(user);
                this.editingUserId = null;
                alert('User updated successfully!');
            } catch (error) {
                console.error('Failed to update user:', error);
                alert('Failed to update user.');
            }
        },
        async deleteUser(userId) {
            if (!confirm('Are you sure you want to delete this user?')) return;
            try {
                await adminService.deleteUser(userId);
                this.users = this.users.filter((user) => user.id !== userId);
                alert('User deleted successfully!');
            } catch (error) {
                console.error('Failed to delete user:', error);
                alert('Failed to delete user.');
            }
        },
        startEditingAttempt(attemptId) {
            this.editingAttemptId = attemptId;
        },
        isEditingAttempt(attemptId) {
            return this.editingAttemptId === attemptId;
        },
        async saveAttempt(attempt) {
            try {
                await adminService.updateAttempt(attempt);
                this.editingAttemptId = null;
                alert('Attempt updated successfully!');
            } catch (error) {
                console.error('Failed to update attempt:', error);
                alert('Failed to update attempt.');
            }
        },
        async deleteAttempt(attemptId) {
            if (!confirm('Are you sure you want to delete this attempt?')) return;
            try {
                await adminService.deleteAttempt(attemptId);
                this.attempts = this.attempts.filter((attempt) => attempt.id !== attemptId);
                alert('Attempt deleted successfully!');
            } catch (error) {
                console.error('Failed to delete attempt:', error);
                alert('Failed to delete attempt.');
            }
        },
        formatDate(date) {
            const options = { year: 'numeric', month: 'long', day: 'numeric' };
            const userLocale = navigator.language || 'en-US';
            const newDate = new Date(date);
            return newDate.toLocaleDateString(userLocale, options);
        },
        async toggleAdmin(user) {
            try {
                if (!this.isAdmin) {
                    alert("You don't have permission to change admin status.");
                    return;
                }
                user.isAdmin = user.isAdmin === 1 ? 0 : 1;
                await adminService.updateUser(user);
                alert('Admin status updated successfully!');
            } catch (error) {
                console.error('Failed to update admin status:', error);
                alert('Failed to update admin status.');
            }
        }
    },
    async created() {
        try {
            const userDetails = await authService.fetchUserDetails();
            this.isAdmin = userDetails.isAdmin === 1;
            await this.fetchUsers();
            await this.fetchAttempts();
        } catch (error) {
            console.error('Error fetching user details:', error);
        }
    }
};
</script>

<style scoped>
.admin {
    padding: 20px;
    margin: 0 15vw;
}

.loading {
    text-align: center;
    font-size: 18px;
}

.user-table,
.attempts-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

.user-table th,
.attempts-table th,
.user-table td,
.attempts-table td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: left;
}

.user-table th,
.attempts-table th {
    background-color: #f4f4f4;
}

button {
    margin-right: 5px;
    padding: 5px 10px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background-color: #0056b3;
}

button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}
</style>
