-- Mô hình dữ liệu chuẩn hóa
CREATE TABLE core.GENERATION (
	generation_id INT PRIMARY KEY,
	name TEXT NOT NULL,
	region TEXT
);

CREATE TABLE core.POKEMON_SPECIES (
	species_id INT PRIMARY KEY,
	name TEXT NOT NULL,
	generation_id INT NOT NULL,
	is_legendary BOOLEAN NOT NULL DEFAULT FALSE,
	is_mythical BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE core.POKEMON (
	pokemon_id INT PRIMARY KEY,
	species_id INT NOT NULL,
	name TEXT NOT NULL,
	height_m NUMERIC(5, 2) CHECK(height_m > 0),
	weight_kg NUMERIC(7, 2) CHECK(weight_kg > 0),
	base_experience INT,
	is_default BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE core.TYPE (
	type_id INT PRIMARY KEY,
	name TEXT NOT NULL UNIQUE
);

CREATE TABLE core.POKEMON_TYPE (
	pokemon_id INT NOT NULL,
	type_id INT NOT NULL,
	slot INT NOT NULL,
	PRIMARY KEY(pokemon_id, slot)
);

CREATE TABLE core.ABILITY (
	ability_id INT PRIMARY KEY,
	name TEXT NOT NULL UNIQUE
);

CREATE TABLE core.POKEMON_ABILITY (
	pokemon_id INT NOT NULL,
	ability_id INT NOT NULL,
	slot INT NOT NULL,
	is_hidden BOOLEAN NOT NULL,
	PRIMARY KEY(pokemon_id, slot)
);

CREATE TABLE core.POKEMON_STAT (
	pokemon_id INT NOT NULL,
	stat_name TEXT NOT NULL,
	base_stat INT NOT NULL CHECK (base_stat BETWEEN 1 AND 255),
	PRIMARY KEY (pokemon_id, stat_name)
);

ALTER TABLE core.POKEMON_SPECIES
	ADD CONSTRAINT FK_PS_G FOREIGN KEY (generation_id) REFERENCES core.GENERATION (generation_id);

ALTER TABLE core.POKEMON
	ADD CONSTRAINT FK_P_PS FOREIGN KEY (species_id) REFERENCES core.POKEMON_SPECIES (species_id);

ALTER TABLE core.POKEMON_TYPE
	ADD CONSTRAINT FK_PT_T FOREIGN KEY (type_id) REFERENCES core.TYPE (type_id),
	ADD CONSTRAINT FK_PT_P FOREIGN KEY (pokemon_id) REFERENCES core.POKEMON (pokemon_id);

ALTER TABLE core.POKEMON_ABILITY
	ADD CONSTRAINT FK_PA_A FOREIGN KEY (ability_id) REFERENCES core.ABILITY (ability_id),
	ADD CONSTRAINT FK_PA_P FOREIGN KEY (pokemon_id) REFERENCES core.POKEMON (pokemon_id);

ALTER TABLE core.POKEMON_STAT
	ADD CONSTRAINT FK_PSA_PK FOREIGN KEY (pokemon_id) REFERENCES core.POKEMON (pokemon_id);