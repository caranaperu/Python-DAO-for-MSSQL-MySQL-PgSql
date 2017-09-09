CREATE TABLE py_dbtest.`tb_maintable` (
  `id_key` int(11) NOT NULL AUTO_INCREMENT,
  `anytext` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id_key`),
  UNIQUE KEY `id_ukey_UNIQUE` (`id_key`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

CREATE TABLE py_dbtest.`tb_triggertest` (
  `id_key` int(11) NOT NULL AUTO_INCREMENT,
  `anytext` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id_key`),
  UNIQUE KEY `id_ukey_UNIQUE` (`id_key`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

-- No permite mysql insertar a la misma tabla que invoca el trigger.
CREATE TRIGGER py_dbtest.`tr_insertTest` AFTER INSERT ON `tb_maintable`
FOR EACH ROW
BEGIN
		IF new.anytext <> 'DUMMY' THEN
			INSERT INTO tb_triggertest SET anytext= 'DUMMY';
		END IF;
END;

DROP procedure IF EXISTS py_dbtest.`directspInsertTest`;
DELIMITER $$
CREATE PROCEDURE py_dbtest.`directspInsertTest`(IN p_anytext varchar(10))
BEGIN
	insert into tb_maintable(anytext) values (p_anytext);
	-- Si se enciende este insert este sera el id recogido.
    -- last_insert_id() retorna el ultimo de cualquier tabla agregada.
    --INSERT INTO tb_triggertest SET anytext= 'DUMMY??';
	select * from tb_maintable;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE `withSelectspInsertTest`(IN p_anytext varchar(10))
BEGIN
	DECLARE v_id INT;
	insert into tb_maintable(anytext)values (p_anytext);
	select last_insert_id() into v_id;
	-- Ejecutar cualquier operacion aqui es indiferente
    -- sentence; sentence; etc.

    -- Al final retornar el id
	select v_id;
END$$


DELIMITER $$

CREATE DEFINER=`root`@`localhost` FUNCTION `withReturnspInsertTest`(p_anytext varchar(10)) RETURNS int(11)
BEGIN
	DECLARE newid INT;
	insert into tb_maintable(anytext) values (p_anytext);
	set newId = (select last_insert_id());
    select * from tb_maintable;
	return newId;
END

DELIMITER $$

CREATE DEFINER=`root`@`localhost` PROCEDURE `withOutParamInsertTest`(IN p_anytext VARCHAR(10), OUT p_id INT)
BEGIN
	insert into tb_maintable(anytext) values (p_anytext);
	select last_insert_id() into p_id;
	insert into tb_triggertest(anytext) values(p_anytext);
	select * from tb_maintable;
END
