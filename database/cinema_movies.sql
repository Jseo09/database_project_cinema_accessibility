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
-- Table structure for table `movies`
--

DROP TABLE IF EXISTS `movies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movies` (
  `Show_ID` int NOT NULL AUTO_INCREMENT,
  `Movie_Title` varchar(255) NOT NULL,
  PRIMARY KEY (`Show_ID`),
  UNIQUE KEY `Movie_Title_UNIQUE` (`Movie_Title`),
  UNIQUE KEY `Show_ID_UNIQUE` (`Show_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movies`
--

LOCK TABLES `movies` WRITE;
/*!40000 ALTER TABLE `movies` DISABLE KEYS */;
INSERT INTO `movies` VALUES (7,'After the Hunt'),(39,'Alamo: The Price Of Freedom'),(30,'Anniversary'),(20,'Back To The Future: 40th Anniversary'),(42,'Blue Moon'),(22,'Bugonia'),(13,'Chainsaw man - The Movie: Reze Arc'),(40,'Corpse Bride'),(23,'Demon Slayer: Kimetsu no Yaiba Infinity Castle-Dub'),(37,'Eli Roth Presents: Dream Eater'),(36,'Frankenstein'),(12,'Gabby\'s DollHouse: The Movie'),(29,'Good Boy'),(5,'Good Fortune'),(32,'Grow'),(18,'Karen Kingsbury\'s The Christmas Ring'),(21,'Kpop Demon Hunters A Sing-Along Event'),(28,'Last Days'),(33,'One Battle After Another'),(31,'ParaNorman(Remastered)'),(16,'Pets On a Train'),(26,'Predator: Badlands'),(1,'Queens of the Dead '),(2,'Regretting You '),(8,'Roofman'),(38,'Screams: Dracula'),(10,'Shelby Oaks'),(6,'Soul On Fire '),(3,'SpringSteen: Deliver Me From Nowhere'),(25,'Stitch Head'),(35,'The Bad Guys 2'),(4,'The Black Phone 2'),(15,'The Conjuring: Last Rite '),(14,'The Long Walk'),(17,'The Nightmare Before Christmas '),(41,'The Rocky Horror Picture Show'),(34,'The Smashing Machine'),(11,'The Strangers: Chapter 2'),(9,'Tron: Ares'),(27,'Truth & Treason'),(24,'Weapons'),(19,'Wicked: For Good');
/*!40000 ALTER TABLE `movies` ENABLE KEYS */;
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
