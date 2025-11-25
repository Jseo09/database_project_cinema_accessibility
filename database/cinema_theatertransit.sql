-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: cinema
-- ------------------------------------------------------
-- Server version	8.0.42

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
-- Table structure for table `theatertransit`
--

DROP TABLE IF EXISTS `theatertransit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `theatertransit` (
  `Theater_ID` int NOT NULL,
  `Stop_ID` int NOT NULL,
  `Walk_Distance_m` int DEFAULT NULL,
  `Walk_Time_min` int DEFAULT NULL,
  PRIMARY KEY (`Theater_ID`,`Stop_ID`),
  KEY `fk_transit_stop` (`Stop_ID`),
  CONSTRAINT `fk_transit_stop` FOREIGN KEY (`Stop_ID`) REFERENCES `transitstops` (`Stop_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_transit_theater` FOREIGN KEY (`Theater_ID`) REFERENCES `theater` (`Theater_ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `theatertransit`
--

LOCK TABLES `theatertransit` WRITE;
/*!40000 ALTER TABLE `theatertransit` DISABLE KEYS */;
INSERT INTO `theatertransit` VALUES (1,1,38,1),(1,4,226,4),(1,5,427,6),(2,2,667,9),(3,3,140,2),(5,10,294,4),(5,11,32,1),(5,12,488,7),(5,13,662,9),(6,14,252,4),(6,15,420,6),(6,16,610,8),(6,17,670,9),(7,18,354,6),(7,19,120,2),(7,20,520,8),(7,21,690,9),(9,22,317,5),(9,23,442,6),(9,24,539,7),(10,25,304,5),(10,26,328,5),(10,27,460,6),(10,28,590,8),(10,29,650,9),(11,30,306,5),(11,31,270,4),(11,32,420,6),(11,33,580,8),(11,34,680,9),(13,35,325,5),(13,36,410,6),(13,37,480,7),(13,38,620,9),(13,39,670,9),(14,40,550,8),(14,41,680,9),(14,42,752,10),(17,43,223,3),(17,44,450,6),(17,45,697,9),(17,46,700,10),(19,47,113,2),(19,48,74,1),(19,49,605,8),(20,50,185,3),(20,51,518,9),(21,52,130,2),(21,53,230,3),(21,54,300,4),(22,55,120,2),(22,56,180,3),(22,57,300,5),(23,58,375,5),(23,59,516,7),(23,60,942,12),(27,61,380,7),(28,62,500,8),(29,63,400,5),(29,64,580,8),(29,65,650,10);
/*!40000 ALTER TABLE `theatertransit` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-13 15:44:44
