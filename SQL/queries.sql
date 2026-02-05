CREATE TABLE vacantes (
	id SERIAL PRIMARY KEY,
	titulo VARCHAR (255),
	EMPRESA varchar (255),
	descripcion TEXT, 
	url_vacante TEXT,
	fecha_extracción DATE DEFAULT CURRENT_DATE
);