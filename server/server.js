import express from 'express';
import mysql from 'mysql2';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import cors from 'cors';
import dotenv from 'dotenv';
import helmet from 'helmet';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config();

const app = express();
app.use(express.json());
app.use(helmet());

app.use((req, res, next) => {
	console.log(`${req.method} ${req.url}`);
	next();
});


app.use(cors({
	origin: 'http://localhost:5173',
	methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
	allowedHeaders: ['Content-Type', 'Authorization'],
	credentials: true,
}));

app.use((req, res, next) => {
	if (req.method === 'OPTIONS') {
		res.header('Access-Control-Allow-Origin', 'http://localhost:5173');
		res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
		res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
		res.status(200).end();
	} else {
		next();
	}
});

app.options('*', cors());

const db = mysql.createConnection({
	host: '127.0.0.1',
	user: 'root',
	password: '',
	database: 'cinequiz',
	port: 3306,
	ssl: {
		rejectUnauthorized: false
	}
});

db.on('error', (err) => {
	console.error('Database error:', err);
	if (err.code === 'PROTOCOL_CONNECTION_LOST') {
		console.log('Reconnecting to the database...');
		db.connect();
	}
});

db.connect((err) => {
	if (err) {
		console.error('Error connecting to the database:', err);
		return;
	}
	console.log('Connected to the database');
});

db.query(`
  CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	isAdmin INT DEFAULT 0
  )
  `, (err) => {
	if (err) {
		console.error('Error creating "users" table:', err);
	} else {
		console.log('"users" table initialized');
	}
});

db.query(`
	CREATE TABLE IF NOT EXISTS favorites (
		id INT AUTO_INCREMENT PRIMARY KEY,
		user_id INT NOT NULL,
		quiz_id VARCHAR(255) NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (user_id) REFERENCES users(id)
	)
  `, (err) => {
	if (err) {
		console.error('Error creating "favorites" table:', err);
	} else {
		console.log('"favorites" table initialized');
	}
});

const authenticateToken = (req, res, next) => {
	const token = req.headers['authorization'];
	if (!token) {
		return res.status(401).json({ message: 'Unauthorized: No token provided' });
	}

	jwt.verify(token.split(' ')[1], process.env.JWT_SECRET, (err, decoded) => {
		if (err) {
			return res.status(401).json({ message: 'Unauthorized: Invalid token' });
		}
		req.userId = decoded.id;
		next();
	});
};

app.use('/assets', express.static(path.join(__dirname, 'server', 'assets')));

app.post('/login', (req, res) => {
	const { username, password } = req.body;

	db.query('SELECT * FROM users WHERE username = ?', [username], (err, result) => {
		if (err) {
			return res.status(500).json({ message: 'Server error' });
		}

		if (result.length === 0) {
			return res.status(400).json({ message: 'User not found' });
		}

		const user = result[0];

		bcrypt.compare(password, user.password, (err, isMatch) => {
			if (err || !isMatch) {
				return res.status(400).json({ message: 'Invalid credentials' });
			}

			const token = jwt.sign({ id: user.id }, process.env.JWT_SECRET, { expiresIn: '1h' });
			res.json({ token });
		});
	});
});

app.post('/register', (req, res) => {
	const { username, password } = req.body;

	const hashedPassword = bcrypt.hashSync(password, 10);

	db.query('INSERT INTO users (username, password) VALUES (?, ?)', [username, hashedPassword], (err) => {
		if (err) {
			return res.status(500).json({ message: 'Server error' });
		}

		res.json({ message: 'User registered successfully' });
	});
});

app.get('/status', authenticateToken, (req, res) => {
	res.json({ message: 'Authenticated', userId: req.userId });
});

app.get('/user', authenticateToken, (req, res) => {
	console.log('User ID from token:', req.userId);
	db.query('SELECT username, created_at, isAdmin FROM users WHERE id = ?', [req.userId], (err, result) => {
		if (err) {
			console.error('Database error:', err);
			return res.status(500).json({ message: 'Server error' });
		}
		if (result.length === 0) {
			console.log('No user found for ID:', req.userId);
			return res.status(404).json({ message: 'User not found' });
		}
		res.json({
			username: result[0].username,
			created_at: result[0].created_at,
			isAdmin: result[0].isAdmin
		});
	});
});

app.get('/quiz', (req, res) => {
	const { name } = req.query;

	if (!name) {
		return res.status(400).json({ message: 'File name is required' });
	}

	if (['superquiz', 'streakquiz', 'flashquiz'].includes(name)) {
		const directoryPath = path.join(__dirname, './assets/quiz/');

		fs.readdir(directoryPath, (err, files) => {
			if (err) {
				console.error('Error reading quiz directory:', err);
				return res.status(500).json({ message: 'Error reading quiz directory' });
			}

			const jsonFiles = files.filter(file => file.endsWith('.json'));
			let allQuestions = [];
			let hasError = false;

			jsonFiles.forEach((file, index) => {
				const filePath = path.join(directoryPath, file);
				try {
					const data = fs.readFileSync(filePath, 'utf8');
					const quizData = JSON.parse(data);
					allQuestions = allQuestions.concat(quizData.questions);
				} catch (err) {
					console.error(`Error processing file (${file}):`, err);
					hasError = true;
				}

				if (index === jsonFiles.length - 1) {
					if (hasError) {
						console.warn('Some files were skipped due to errors.');
					}

					allQuestions = shuffleArray(allQuestions);

					if (name === 'flashquiz') {
						allQuestions = allQuestions.slice(0, 20);
					}

					res.json({ questions: allQuestions });
				}
			});
		});
	} else {
		const fileName = `./assets/quiz/${name}.json`;
		const filePath = path.join(__dirname, fileName);

		fs.readFile(filePath, 'utf8', (err, data) => {
			if (err) {
				console.error('Error reading JSON file:', err);
				return res.status(500).json({ message: 'Error reading file' });
			}

			try {
				const jsonData = JSON.parse(data);
				res.json(jsonData);
			} catch (parseError) {
				console.error('Error parsing JSON file:', parseError);
				res.status(500).json({ message: 'Invalid JSON format' });
			}
		});
	}
});

function shuffleArray(array) {
	return array
		.map(item => ({ item, sort: Math.random() }))
		.sort((a, b) => a.sort - b.sort)
		.map(({ item }) => item);
}

const verifyAdmin = (req, res, next) => {
	const token = req.headers['authorization'];
	if (!token) return res.status(401).json({ message: 'Unauthorized: No token provided' });

	jwt.verify(token.split(' ')[1], process.env.JWT_SECRET, (err, decoded) => {
		if (err) return res.status(401).json({ message: 'Unauthorized: Invalid token' });

		db.query('SELECT isAdmin FROM users WHERE id = ?', [decoded.id], (err, result) => {
			if (err || result.length === 0 || result[0].isAdmin !== 1) {
				return res.status(403).json({ message: 'Forbidden: Admins only' });
			}
			next();
		});
	});
};

app.get('/admin/users', authenticateToken, verifyAdmin, (req, res) => {
	db.query('SELECT id, username, created_at, isAdmin FROM users', (err, results) => {
		if (err) return res.status(500).json({ message: 'Server error' });

		const users = results.map(user => ({
			...user,
			isAdmin: parseInt(user.isAdmin, 10),
		}));

		res.json({ users });
	});
});

app.put('/admin/users/:id', authenticateToken, verifyAdmin, (req, res) => {
	const { id } = req.params;
	const { username, isAdmin } = req.body;

	const isAdminValue = isAdmin === true || isAdmin === 1 ? 1 : 0;

	db.query(
		'UPDATE users SET username = ?, isAdmin = ? WHERE id = ?',
		[username, isAdminValue, id],
		(err) => {
			if (err) return res.status(500).json({ message: 'Server error' });
			res.json({ message: 'User updated successfully' });
		}
	);
});

app.delete('/admin/users/:id', authenticateToken, verifyAdmin, (req, res) => {
	const { id } = req.params;

	db.query('DELETE FROM users WHERE id = ?', [id], (err) => {
		if (err) return res.status(500).json({ message: 'Server error' });
		res.json({ message: 'User deleted successfully' });
	});
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
	console.log(`Server is running on port ${PORT}`);
});

app.get('/favorites', authenticateToken, (req, res) => {
	const userId = req.userId;

	db.query('SELECT quiz_id FROM favorites WHERE user_id = ?', [userId], (err, results) => {
		if (err) {
			console.error('Database error:', err);
			return res.status(500).json({ message: 'Server error' });
		}

		const favoriteQuizIds = results.map(row => row.quiz_id);
		res.json(favoriteQuizIds);
	});
});

app.post('/favorites', authenticateToken, (req, res) => {
	const userId = req.userId;
	const { quizId, favorite } = req.body;

	if (favorite) {
		db.query(
			'INSERT INTO favorites (user_id, quiz_id) VALUES (?, ?) ON DUPLICATE KEY UPDATE created_at = CURRENT_TIMESTAMP',
			[userId, quizId],
			(err) => {
				if (err) {
					console.error('Database error:', err);
					return res.status(500).json({ message: 'Server error' });
				}
				res.json({ message: 'Quiz added to favorites' });
			}
		);
	} else {
		db.query('DELETE FROM favorites WHERE user_id = ? AND quiz_id = ?', [userId, quizId], (err) => {
			if (err) {
				console.error('Database error:', err);
				return res.status(500).json({ message: 'Server error' });
			}
			res.json({ message: 'Quiz removed from favorites' });
		});
	}
});

db.query(`
    CREATE TABLE IF NOT EXISTS attempts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        quiz_id VARCHAR(255) NOT NULL,
        score INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
`, (err) => {
	if (err) {
		console.error('Error creating "attempts" table:', err);
	} else {
		console.log('"attempts" table initialized');
	}
});

app.get('/attempts/best/:quizId', authenticateToken, (req, res) => {
	const { quizId } = req.params;
	const userId = req.userId;

	db.query(
		'SELECT MAX(score) AS best_score FROM attempts WHERE user_id = ? AND quiz_id = ?',
		[userId, quizId],
		(err, results) => {
			if (err) {
				console.error('Database error:', err);
				return res.status(500).json({ message: 'Server error' });
			}

			const bestScore = results[0]?.best_score;
			if (bestScore === null || bestScore === undefined) {
				return res.json({ bestScore: "Never attempted" });
			}

			return res.json({ bestScore });
		}
	);
});

app.post('/attempts', authenticateToken, (req, res) => {
	const { quizId, score } = req.body;
	const userId = req.userId;

	db.query(
		'INSERT INTO attempts (user_id, quiz_id, score) VALUES (?, ?, ?)',
		[userId, quizId, score],
		(err) => {
			if (err) {
				console.error('Error inserting attempt:', err);
				return res.status(500).json({ message: 'Failed to record attempt' });
			}
			res.json({ message: 'Attempt recorded successfully' });
		}
	);
});

app.delete('/attempts/reset', authenticateToken, (req, res) => {
	const userId = req.userId;
	db.query('DELETE FROM attempts WHERE user_id = ?', [userId], (err) => {
		if (err) {
			console.error('Database error:', err);
			return res.status(500).json({ message: 'Server error' });
		}
		res.json({ message: 'Attempts and scores reset successfully' });
	});
});

app.get('/attempts/best/:quizId', authenticateToken, (req, res) => {
	const { quizId } = req.params;
	const userId = req.userId;

	db.query(
		'SELECT MAX(score) AS best_score FROM attempts WHERE user_id = ? AND quiz_id = ?',
		[userId, quizId],
		(err, results) => {
			if (err) {
				console.error('Database error:', err);
				return res.status(500).json({ message: 'Server error' });
			}
			res.json({ bestScore: results[0]?.best_score || 'Never attempted' });
		}
	);
});

app.put('/user/password', authenticateToken, (req, res) => {
	const userId = req.userId;
	const { currentPassword, newPassword } = req.body;

	db.query('SELECT password FROM users WHERE id = ?', [userId], (err, result) => {
		if (err || result.length === 0) {
			return res.status(500).json({ message: 'Server error' });
		}

		const hashedPassword = result[0].password;
		bcrypt.compare(currentPassword, hashedPassword, (err, isMatch) => {
			if (err || !isMatch) {
				return res.status(400).json({ message: 'Current password is incorrect' });
			}

			const newHashedPassword = bcrypt.hashSync(newPassword, 10);
			db.query('UPDATE users SET password = ? WHERE id = ?', [newHashedPassword, userId], (err) => {
				if (err) {
					return res.status(500).json({ message: 'Server error' });
				}
				res.json({ message: 'Password updated successfully' });
			});
		});
	});
});

app.put('/user/username', authenticateToken, (req, res) => {
	const userId = req.userId;
	const { newUsername, passwordConfirmation } = req.body;

	if (!newUsername || !passwordConfirmation) {
		return res.status(400).json({ message: 'New username and password are required.' });
	}

	db.query('SELECT id FROM users WHERE username = ?', [newUsername], (err, results) => {
		if (err) {
			console.error('Error checking username availability:', err);
			return res.status(500).json({ message: 'Server error. Please try again later.' });
		}

		if (results.length > 0) {
			return res.status(400).json({ message: 'This username is already taken.' });
		}

		db.query('SELECT password FROM users WHERE id = ?', [userId], (err, result) => {
			if (err || result.length === 0) {
				console.error('Error retrieving user password:', err);
				return res.status(500).json({ message: 'Server error. Please try again later.' });
			}

			const hashedPassword = result[0].password;

			bcrypt.compare(passwordConfirmation, hashedPassword, (err, isMatch) => {
				if (err || !isMatch) {
					console.error('Password mismatch:', err);
					return res.status(400).json({ message: 'The password you provided is incorrect.' });
				}

				db.query('UPDATE users SET username = ? WHERE id = ?', [newUsername, userId], (err) => {
					if (err) {
						console.error('Error updating username:', err);
						return res.status(500).json({ message: 'Unable to update your username. Please try again.' });
					}

					res.json({ message: 'Your username has been updated successfully!' });
				});
			});
		});
	});
});

app.delete('/user', authenticateToken, (req, res) => {
	const userId = req.userId;

	db.query('DELETE FROM favorites WHERE user_id = ?', [userId], (err) => {
		if (err) {
			console.error('Error deleting favorites:', err);
			return res.status(500).json({ message: 'Server error' });
		}

		db.query('DELETE FROM attempts WHERE user_id = ?', [userId], (err) => {
			if (err) {
				console.error('Error deleting attempts:', err);
				return res.status(500).json({ message: 'Server error' });
			}

			db.query('DELETE FROM users WHERE id = ?', [userId], (err) => {
				if (err) {
					console.error('Error deleting user:', err);
					return res.status(500).json({ message: 'Server error' });
				}
				res.json({ message: 'Account deleted successfully' });
			});
		});
	});
});

app.get('/check-username', (req, res) => {
	const { username } = req.query;

	if (!username) {
		return res.status(400).json({ message: 'Username is required' });
	}

	db.query('SELECT COUNT(*) AS count FROM users WHERE username = ?', [username], (err, results) => {
		if (err) {
			return res.status(500).json({ message: 'Server error' });
		}

		const isTaken = results[0].count > 0;
		res.json({ isTaken });
	});
});

app.get('/admin/attempts', authenticateToken, verifyAdmin, (req, res) => {
	const query = `
        SELECT 
            attempts.id, 
            attempts.user_id, 
            users.username, 
            attempts.quiz_id, 
            attempts.score, 
            DATE_FORMAT(attempts.created_at, '%Y-%m-%d %H:%i:%s') AS attempt_time
        FROM 
            attempts
        JOIN 
            users ON attempts.user_id = users.id
        ORDER BY 
            attempts.created_at DESC;
    `;

	db.query(query, (err, results) => {
		if (err) {
			console.error('Error fetching attempts:', err);
			return res.status(500).json({ message: 'Server error' });
		}
		res.json({ attempts: results });
	});
});

app.get('/leaderboard/quiz', (req, res) => {
	const query = `
        SELECT 
            attempts.quiz_id,
            MAX(attempts.score) AS best_score,
            (SELECT users.username 
             FROM attempts a
             JOIN users ON users.id = a.user_id
             WHERE a.quiz_id = attempts.quiz_id
             ORDER BY a.score DESC, users.username ASC
             LIMIT 1) AS username
        FROM 
            attempts
        GROUP BY 
            attempts.quiz_id
        ORDER BY 
            attempts.quiz_id;
    `;
	db.query(query, (err, results) => {
		if (err) {
			console.error('Error in leaderboard/quiz query:', err);
			return res.status(500).json({ message: 'Database query failed', error: err.message });
		}
		res.json(results);
	});
});

app.get('/leaderboard/overall', (req, res) => {
	const query = `
        SELECT 
            attempts.user_id, 
            SUM(attempts.score) AS total_score, 
            users.username
        FROM 
            attempts
        JOIN 
            users ON users.id = attempts.user_id
        GROUP BY 
            attempts.user_id, users.username
        ORDER BY 
            total_score DESC;
    `;
	db.query(query, (err, results) => {
		if (err) {
			console.error('Error in leaderboard/overall query:', err);
			return res.status(500).json({ message: 'Database query failed', error: err.message });
		}
		res.json(results);
	});
});
