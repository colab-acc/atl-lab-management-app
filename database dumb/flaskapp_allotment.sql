-- MySQL dump 10.13  Distrib 8.0.27, for Win64 (x86_64)
--
-- Host: localhost    Database: flaskapp
-- ------------------------------------------------------
-- Server version	8.0.27

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `allotment`
--

DROP TABLE IF EXISTS `allotment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `allotment` (
  `item_code` char(5) DEFAULT NULL,
  `issued_to` varchar(50) DEFAULT NULL,
  `issued_by` varchar(20) DEFAULT NULL,
  `date_of_issue` date DEFAULT NULL,
  `status` varchar(10) DEFAULT NULL,
  `renewed_on` date DEFAULT NULL,
  `renewed_by` varchar(20) DEFAULT NULL,
  KEY `item_code` (`item_code`),
  CONSTRAINT `allotment_ibfk_1` FOREIGN KEY (`item_code`) REFERENCES `equipments` (`item_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `allotment`
--

LOCK TABLES `allotment` WRITE;
/*!40000 ALTER TABLE `allotment` DISABLE KEYS */;
INSERT INTO `allotment` VALUES ('102','raianurag552@gmail.com','m/s leelambika','2022-02-14','Consumed','2022-02-25','m/s saroj'),('102','raianurag552@gmail.coms','m/s leelambika','2022-02-14','Active','2022-02-25','m/s saroj'),('102','raianurag552@gmail.coms','m/s leelambika','2022-02-17','Active','2022-02-25','m/s saroj'),('104','raimohan','m/s leelambika','2022-03-13','Active','2022-03-14','m/s saroj'),('104','Raianurag552@gmail.com','sclskcbjslc','2022-02-14','Consumed',NULL,NULL),('103','anuragh@afshebbal.ac.in','anurag','2022-02-14','Consumed',NULL,NULL);
/*!40000 ALTER TABLE `allotment` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-02-17 21:03:13
