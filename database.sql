-- --------------------------------------------------------
-- Hôte:                         127.0.0.1
-- Version du serveur:           8.0.30 - MySQL Community Server - GPL
-- SE du serveur:                Win64
-- HeidiSQL Version:             12.1.0.6537
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Listage de la structure de la base pour cinequiz
DROP DATABASE IF EXISTS `cinequiz`;
CREATE DATABASE IF NOT EXISTS `cinequiz` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `cinequiz`;

-- Listage de la structure de table cinequiz. attempts
DROP TABLE IF EXISTS `attempts`;
CREATE TABLE IF NOT EXISTS `attempts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `quiz_id` varchar(255) NOT NULL,
  `score` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `attempts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=358 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Listage des données de la table cinequiz.attempts : ~20 rows (environ)
INSERT INTO `attempts` (`id`, `user_id`, `quiz_id`, `score`, `created_at`) VALUES
	(309, 11, 'FLASHQUIZ', 6, '2024-12-07 09:33:06'),
	(310, 11, 'FLASHQUIZ', 6, '2024-12-07 09:33:10'),
	(311, 11, 'FLASHQUIZ', 6, '2024-12-07 09:33:14'),
	(312, 11, 'GHIBLI', 2, '2024-12-07 09:36:35'),
	(313, 11, 'FLASHQUIZ', 3, '2024-12-07 14:00:51'),
	(314, 11, 'FLASHQUIZ', 3, '2024-12-07 14:00:55'),
	(315, 11, 'FLASHQUIZ', 3, '2024-12-07 14:00:59'),
	(316, 11, 'FLASHQUIZ', 3, '2024-12-07 14:01:03'),
	(317, 11, 'FLASHQUIZ', 3, '2024-12-07 14:01:07'),
	(318, 11, 'FLASHQUIZ', 3, '2024-12-07 14:01:11'),
	(319, 11, 'FLASHQUIZ', 3, '2024-12-07 14:01:15'),
	(320, 11, 'HARRYPOTTER', 4, '2024-12-07 14:04:35'),
	(321, 11, 'GHIBLI', 3, '2024-12-07 15:24:55'),
	(351, 12, 'STREAKQUIZ', 0, '2024-12-07 17:10:36'),
	(352, 12, 'STREAKQUIZ', 0, '2024-12-07 17:12:10'),
	(353, 13, 'FLASHQUIZ', 5, '2024-12-08 00:28:10'),
	(354, 13, 'STREAKQUIZ', 0, '2024-12-08 00:28:20'),
	(355, 13, 'STREAKQUIZ', 3, '2024-12-08 00:28:36'),
	(356, 11, 'GHIBLI', 3, '2024-12-08 01:00:48'),
	(357, 11, 'FLASHQUIZ', 0, '2024-12-08 01:06:28');

-- Listage de la structure de table cinequiz. favorites
DROP TABLE IF EXISTS `favorites`;
CREATE TABLE IF NOT EXISTS `favorites` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `quiz_id` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=72 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Listage des données de la table cinequiz.favorites : ~7 rows (environ)
INSERT INTO `favorites` (`id`, `user_id`, `quiz_id`, `created_at`) VALUES
	(58, 6, 'ghibli', '2024-12-06 19:01:20'),
	(59, 6, 'jurassicpark', '2024-12-06 19:01:23'),
	(60, 11, 'ghibli', '2024-12-06 19:50:47'),
	(62, 11, 'jurassicpark', '2024-12-07 05:25:13'),
	(68, 12, 'marvel', '2024-12-07 16:34:51'),
	(69, 12, 'pirates', '2024-12-07 16:34:53'),
	(71, 13, 'jurassicpark', '2024-12-08 00:26:05');

-- Listage de la structure de table cinequiz. users
DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `isAdmin` int DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Listage des données de la table cinequiz.users : ~5 rows (environ)
INSERT INTO `users` (`id`, `username`, `password`, `created_at`, `isAdmin`) VALUES
	(6, 'noe', '$2a$10$thjKpntfdUOY/Br27o3JpufNHOji4cAuPrjMfCvTIgohcYgHmbrk2', '2024-12-06 19:01:05', 0),
	(9, 'clemo', '$2a$10$C0c./FpKJu8ywdUJg7fAVeEi3UNPLP.ed8ABsF5ftaeCNfuL6ZJIm', '2024-12-06 19:46:12', 0),
	(11, 'admin', '$2a$10$VANJmrPchqu50ElbZGaO7uXWoC/lfenYPTcWbFQnLyw89Ft5BFK.S', '2024-12-06 19:49:26', 1),
	(12, 'bily', '$2a$10$NrP0uUMUmJPy/Si5ke7BfeVxJCUQOis3XE.423snDLZHXaGPEyaK6', '2024-12-07 14:31:19', 1),
	(13, 'goldor', '$2a$10$gMlAUYOWc1jWC4lBpW2aVuClZs35CvZSIkwAy6ObVTITTR9WYdRmu', '2024-12-08 00:25:43', 1);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
