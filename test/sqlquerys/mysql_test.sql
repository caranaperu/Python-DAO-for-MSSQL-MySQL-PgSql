CREATE DATABASE  IF NOT EXISTS 'py_dbtest' /*!40100 DEFAULT CHARACTER SET latin1 */;
USE 'py_dbtest';
-- MySQL dump 10.13  Distrib 5.5.57, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: py_dbtest
-- ------------------------------------------------------
-- Server version	5.5.57-0ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table 'tb_maintable'
--

DROP TABLE IF EXISTS 'tb_maintable';
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE 'tb_maintable' (
  'id_key' int(11) NOT NULL AUTO_INCREMENT,
  'anytext' varchar(10) DEFAULT NULL,
  PRIMARY KEY ('id_key'),
  UNIQUE KEY 'id_ukey_UNIQUE' ('id_key')
) ENGINE=InnoDB AUTO_INCREMENT=74 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER='root'@'localhost'*/ /*!50003 TRIGGER py_dbtest.'tr_insertTest' AFTER INSERT ON 'tb_maintable'
FOR EACH ROW
BEGIN
		IF new.anytext <> 'DUMMY' THEN
			INSERT INTO tb_triggertest SET anytext= 'DUMMY';
		END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table 'tb_maintable_ckeys'
--

DROP TABLE IF EXISTS 'tb_maintable_ckeys';
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE 'tb_maintable_ckeys' (
  'main_code' varchar(5) NOT NULL,
  'main_number' int(11) NOT NULL,
  'anytext' varchar(10) NOT NULL,
  UNIQUE KEY 'index1' ('main_code','main_number')
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table 'tb_maintable_fk'
--

DROP TABLE IF EXISTS 'tb_maintable_fk';
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE 'tb_maintable_fk' (
  'pk_id' int(11) NOT NULL AUTO_INCREMENT,
  'anytext' varchar(10) NOT NULL,
  'fktest' int(11) NOT NULL,
  'nondup' varchar(100) DEFAULT NULL,
  PRIMARY KEY ('pk_id'),
  UNIQUE KEY 'pk_id_UNIQUE' ('pk_id'),
  UNIQUE KEY 'nondup_UNIQUE' ('nondup'),
  KEY 'fk_tb_maintable_fk_1_idx' ('fktest'),
  CONSTRAINT 'fk_tb_maintable_fk_1' FOREIGN KEY ('fktest') REFERENCES 'tb_testfk' ('fk_test') ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table 'tb_testfk'
--

DROP TABLE IF EXISTS 'tb_testfk';
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE 'tb_testfk' (
  'fk_test' int(11) NOT NULL,
  PRIMARY KEY ('fk_test')
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table 'tb_triggertest'
--

DROP TABLE IF EXISTS 'tb_triggertest';
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE 'tb_triggertest' (
  'id_key' int(11) NOT NULL AUTO_INCREMENT,
  'anytext' varchar(10) DEFAULT NULL,
  PRIMARY KEY ('id_key'),
  UNIQUE KEY 'id_ukey_UNIQUE' ('id_key')
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'py_dbtest'
--
/*!50003 DROP FUNCTION IF EXISTS 'withReturnspInsertTest' */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER='root'@'localhost' FUNCTION 'withReturnspInsertTest'(p_anytext varchar(10)) RETURNS int(11)
BEGIN
	DECLARE newid INT;
	insert into tb_maintable(anytext) values (p_anytext);
	set newId = (select last_insert_id());
	return newId;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS 'directspInsertTest' */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER='root'@'localhost' PROCEDURE 'directspInsertTest'(IN p_anytext varchar(10))
BEGIN
	insert into tb_maintable(anytext) values (p_anytext);
	-- Si se enciende este inser este sera el id recogido.
	-- INSERT INTO tb_triggertest SET anytext= 'DUMMY??';
	select * from tb_maintable;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS 'withOutParamInsertTest' */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER='root'@'localhost' PROCEDURE 'withOutParamInsertTest'(IN p_anytext VARCHAR(10), OUT p_id INT)
BEGIN
	insert into tb_maintable(anytext) values (p_anytext);
	select last_insert_id() into p_id;
	insert into tb_triggertest(anytext) values(p_anytext);
	select * from tb_maintable;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS 'withSelectspInsertTest' */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER='root'@'localhost' PROCEDURE 'withSelectspInsertTest'(IN p_anytext varchar(10))
BEGIN
	DECLARE v_id INT;
	insert into tb_maintable(anytext)values (p_anytext);
	select last_insert_id() into v_id;
	select v_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-09-27  0:07:55
