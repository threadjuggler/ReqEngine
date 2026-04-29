CREATE TABLE IF NOT EXISTS users (
    id            INT           NOT NULL UNIQUE AUTO_INCREMENT,
    name          VARCHAR(80)   NOT NULL,
    role          VARCHAR(20)   NOT NULL,
    hashed_password VARCHAR(200) NOT NULL,
    log_in_active INT           NOT NULL DEFAULT 0 CHECK (log_in_active IN (0, 1)),
    last_log_in   DATE
);

ALTER TABLE users AUTO_INCREMENT = 10000;
