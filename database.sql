CREATE DATABASE IF NOT EXISTS security_quiz
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE security_quiz;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    option_a VARCHAR(255) NOT NULL,
    option_b VARCHAR(255) NOT NULL,
    option_c VARCHAR(255) NOT NULL,
    option_d VARCHAR(255) NOT NULL,
    correct_answer CHAR(1) NOT NULL
);

CREATE TABLE IF NOT EXISTS results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    score INT NOT NULL,
    total_questions INT NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_results_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

INSERT INTO questions (question, option_a, option_b, option_c, option_d, correct_answer)
SELECT * FROM (
    SELECT 'What should you do if you receive an unexpected email asking you to reset your password?' AS question,
           'Click the link immediately' AS option_a, 'Verify the request through the official website' AS option_b,
           'Reply with your current password' AS option_c, 'Forward it to all coworkers' AS option_d, 'B' AS correct_answer
    UNION ALL SELECT 'Which password is strongest?', 'password123', 'Summer2026', 'R7!mQ2#vL9@p', 'yourname', 'C'
    UNION ALL SELECT 'What does multi-factor authentication add?', 'A second verification step', 'A shorter password', 'A public profile', 'Automatic Wi-Fi', 'A'
    UNION ALL SELECT 'You find an unknown USB drive in the parking lot. What is the safest action?', 'Plug it in to identify the owner', 'Give it to IT/security staff without using it', 'Take it home', 'Copy files from it', 'B'
    UNION ALL SELECT 'What does the padlock icon in a browser address bar generally indicate?', 'The website is guaranteed honest', 'The connection is encrypted', 'The website has no malware', 'The page is government-owned', 'B'
    UNION ALL SELECT 'A caller claiming to be IT requests your one-time login code. What should you do?', 'Share it if they know your name', 'Ask them to wait while you read it', 'Do not share it and contact IT through a known channel', 'Send it by email instead', 'C'
    UNION ALL SELECT 'What is a good response to a ransomware warning on a work computer?', 'Pay immediately', 'Disconnect it from the network and notify IT/security', 'Restart it several times', 'Download a cleanup tool from an advert', 'B'
    UNION ALL SELECT 'Why should you install security updates?', 'They can fix known security weaknesses', 'They make passwords unnecessary', 'They stop all phishing', 'They remove the need for backups', 'A'
    UNION ALL SELECT 'Which action is safest when using public Wi-Fi?', 'Use it for banking without checking the network', 'Avoid sensitive activity unless using a trusted secure connection', 'Turn off your device password', 'Share files with everyone nearby', 'B'
    UNION ALL SELECT 'What is the purpose of a backup?', 'To keep a recoverable copy of important data', 'To publish files online', 'To speed up phishing emails', 'To replace all software updates', 'A'
) AS starter_questions
WHERE NOT EXISTS (SELECT 1 FROM questions LIMIT 1);