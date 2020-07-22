CREATE DATABASE `model_catalog` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `model_catalog`.`deployments`;
DROP TABLE IF EXISTS `model_catalog`.`artifacts`;
DROP TABLE IF EXISTS `model_catalog`.`models`;
DROP TABLE IF EXISTS `model_catalog`.`namespaces`;


CREATE TABLE `model_catalog`.`namespaces` (
    id SMALLINT AUTO_INCREMENT,
    name VARCHAR(120) NOT NULL,
    owner VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,

    PRIMARY KEY (id)
);


CREATE TABLE `model_catalog`.`models` (
    id INT AUTO_INCREMENT,
    namespace_id SMALLINT,
    name VARCHAR(120) NOT NULL,
    owner VARCHAR(50) NOT NULL,
    language VARCHAR(20) NOT NULL,
    flavor VARCHAR(50),
    region VARCHAR(50),
    repository VARCHAR(250),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,

    PRIMARY KEY (id),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(id)
);


CREATE TABLE `model_catalog`.`artifacts` (
    id BIGINT AUTO_INCREMENT,
    model_id INT,
    version VARCHAR(20) NOT NULL,
    type VARCHAR(25) NOT NULL,
    path VARCHAR(250) NOT NULL,
    storage VARCHAR(25) NOT NULL,
    platform VARCHAR(25) NOT NULL,
    input_schema JSON,
    output_schema JSON,
    is_compliant BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    FOREIGN KEY (model_id) REFERENCES models(id)
);


CREATE TABLE `model_catalog`.`deployments` (
    id BIGINT AUTO_INCREMENT,
    artifact_id BIGINT,
    job_id VARCHAR(80) NOT NULL,
    job_type VARCHAR(25) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    FOREIGN KEY (artifact_id) REFERENCES artifacts(id)
);

INSERT INTO `model_catalog`.`namespaces` (name, owner) VALUES ('Microsoft', 'omldev@microsoft.com');

CREATE USER 'oml_users'@'%';
GRANT ALL PRIVILEGES ON model_catalog.* TO 'oml_users'@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
