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
-- Table structure for table `theaterfeatures`
--

DROP TABLE IF EXISTS `theaterfeatures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `theaterfeatures` (
  `Theater_ID` int NOT NULL,
  `Wheel_Chair_Accessibility` tinyint(1) NOT NULL DEFAULT '0',
  `Assistive_Listening` tinyint(1) NOT NULL DEFAULT '0',
  `Caption_Device` tinyint(1) NOT NULL DEFAULT '0',
  `Audio_Description` tinyint(1) NOT NULL DEFAULT '0',
  `Info_Source` varchar(255) NOT NULL,
  `Data_Confidence` varchar(10) NOT NULL,
  PRIMARY KEY (`Theater_ID`),
  CONSTRAINT `fk_theater_features` FOREIGN KEY (`Theater_ID`) REFERENCES `theater` (`Theater_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_assi_lis` CHECK ((`Assistive_Listening` in (0,1))),
  CONSTRAINT `chk_audio` CHECK ((`Audio_Description` in (0,1))),
  CONSTRAINT `chk_bool_wheel` CHECK ((`Wheel_Chair_Accessibility` in (0,1))),
  CONSTRAINT `chk_caption` CHECK ((`Caption_Device` in (0,1)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `theaterfeatures`
--

LOCK TABLES `theaterfeatures` WRITE;
/*!40000 ALTER TABLE `theaterfeatures` DISABLE KEYS */;
INSERT INTO `theaterfeatures` VALUES (1,1,1,1,1,'Official Website, Google','High'),(2,1,1,1,1,'Official Website','High'),(3,1,1,1,1,'Official Website','High'),(5,1,1,1,1,'Official Website','High'),(6,1,1,1,1,'Official Website','High'),(7,1,1,1,1,'Official Website','High'),(8,1,1,1,0,'Official Website','Medium'),(9,1,1,1,1,'Official Website','High'),(10,1,1,1,0,'Official Website','Medium'),(11,1,1,1,1,'Official Website','High'),(12,1,1,1,1,'Official Website','High'),(13,1,1,1,1,'Official Website','Medium'),(14,1,1,1,0,'Official Website','Medium'),(15,1,1,1,1,'Official Website','High'),(16,1,1,1,1,'Official Website','High'),(17,1,1,1,1,'Official Website','High'),(18,1,1,1,1,'Official Website','High'),(19,1,1,1,1,'Official Website ','High'),(20,1,1,1,1,'Official Website','High'),(21,1,1,1,1,'Official Website ','High'),(22,1,1,1,0,'Official Website','Medium'),(23,1,1,1,1,'Official Website ','High'),(27,1,1,1,0,'Official Website ','Medium'),(28,1,1,1,0,'Official Website','Medium'),(29,1,1,1,1,'Official Website','High');
/*!40000 ALTER TABLE `theaterfeatures` ENABLE KEYS */;
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
