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
-- Table structure for table `transitstops`
--

DROP TABLE IF EXISTS `transitstops`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transitstops` (
  `Stop_ID` int NOT NULL AUTO_INCREMENT,
  `Stop_Name` varchar(255) NOT NULL,
  `Accessibility` tinyint(1) NOT NULL,
  `Latitude` decimal(9,6) NOT NULL DEFAULT '0.000000',
  `Longitude` decimal(9,6) NOT NULL DEFAULT '0.000000',
  PRIMARY KEY (`Stop_ID`),
  CONSTRAINT `chk_accessible` CHECK ((`Accessibility` in (0,1)))
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transitstops`
--

LOCK TABLES `transitstops` WRITE;
/*!40000 ALTER TABLE `transitstops` DISABLE KEYS */;
INSERT INTO `transitstops` VALUES (1,'SE Military Dr & City Base Landing',1,29.351807,-98.434952),(2,'Stone Oak Park & Ride',1,29.647623,-98.452497),(3,'Perrin Beitel & Loop 410 East',1,29.515924,-98.411139),(4,'City Base Landing & Sidney Brooks',1,29.349011,-98.434909),(5,'SE Military DR & Goliad',1,29.351928,-98.431110),(6,'Henderson Pass & Cedar Ridge',1,29.595583,-98.453888),(7,'Henderson Pass & Shadow Oak Dr',1,0.000000,0.000000),(8,'Thousand Oaks & Jones Maltsberger',1,29.578188,-98.441536),(9,'Northwoods Shopping Center',1,29.605103,-98.464233),(10,'NW Loop 410 W Access Rd & Palatine Dr',1,29.488014,-98.585564),(11,'Glen Ridge & Knights Bridge',1,29.489168,-98.591174),(12,'Evers Opposite Glen Ridge',1,29.704404,-98.486988),(13,'NW Loop 410 W Access Rd & Palatine',1,29.390281,-98.642379),(14,'La Cantera & Vance Jackson',1,29.535477,-98.554342),(15,'La Cantera & Loop 1604 Access Rd',1,29.592912,-98.620040),(16,'La Cantera Pkwy & La Cantera Terrace',1,29.424120,-98.493630),(17,'Utsa Loop 1604 Campus',1,29.586417,-98.618564),(18,'SW Loop 410 S Access Rd & Waters Edge Rd',1,29.419000,-98.620900),(19,'Cable Ranch Rd & Waters Edge Dr',1,29.456000,-98.579000),(20,'I-H Loop 410 S Access Rd & Waters Edge Dr',1,29.486000,-98.610000),(21,'Potranco Rd & Cable Ranch Rd',1,29.437600,-98.681200),(22,'Market / Front Of Convention Center',1,29.425300,-98.488500),(23,'Chestnut & E. Houston',1,29.423600,-98.488000),(24,'Navarro & Commerce',1,29.427400,-98.489700),(25,'Jones-Maltsberger & Alamo Quarry',1,29.454000,-98.486000),(26,'Basse Opposite Whole Foods',1,29.502300,-98.488100),(27,'Jones-Maltsberger & E Basse Rd',1,29.454800,-98.485200),(28,'Quarry Market (North Entrance)',1,29.491990,-98.481730),(29,'Basse Rd & Jones-Maltsberger Rd (West Side)',1,29.502400,-98.485500),(30,'SW Military Dr & Nock Ave',1,29.523200,-98.555900),(31,'Commercial Opposite Sharmain St',1,29.492000,-98.532000),(32,'SW Military Dr & Commercial Ave',1,29.472000,-98.518000),(33,'SW Military Dr & Pleasanton Rd',1,29.391600,-98.527900),(34,'Commercial Ave & Harlan Ave',1,29.497500,-98.531000),(35,'NW Loop 410 N Access Rd & Ent to SW Research',1,29.521000,-98.476000),(36,'San Pedro Ave & Isom Rd',1,29.506100,-98.498600),(37,'San Pedro Ave & Ramsey Rd',1,29.504000,-98.490000),(38,'McCullough Ave & Rector Dr',1,29.432600,-98.486100),(39,'Isom Rd & Rector Dr',1,29.505000,-98.495000),(40,'Huebner & Huebner Oaks',1,29.528000,-98.548000),(41,'Huebner & Expo',1,29.529000,-98.552000),(42,'Fredericksburg Rd. Opposite Prue',1,29.493000,-98.535000),(43,'9700 Menchaca/Slaughter',1,30.175500,-97.822700),(44,'Slaughter/Menchaca',1,30.172000,-97.820000),(45,'1312 Slaughter/Bilbrook',1,30.172000,-97.815000),(46,'9000 S 1st/Slaughter',1,30.160000,-97.820000),(47,'906 Lamar/Treadwell',1,30.250000,-97.750000),(48,'Lamar Square Station',1,30.260000,-97.750000),(49,'Barton Springs Station',1,30.266000,-97.762000),(50,'Barton Creek Mall',1,30.274000,-97.824000),(51,'Walsh Tarlton / Tamarron',1,30.261600,-97.809900),(52,'Highland Station',1,30.309000,-97.708000),(53,'Airport Highland Mall Station',1,0.000000,0.000000),(54,'Middle Fiskville Highland Mall',1,30.323000,-97.715000),(55,'2nd & Congress St',1,30.264200,-97.744800),(56,'Lavaca St & 4th St',1,30.279600,-97.740800),(57,'Guadalupe St & 2nd St',1,30.265200,-97.745400),(58,'Esperanza Crossing / Domain',1,30.403700,-97.725500),(59,'Braker',1,30.386800,-97.717900),(60,'Burnet Stadium Rapid NW Corner',1,30.338500,-97.735500),(61,'Stonelake & Capital of Texas Hwy',1,30.389400,-97.747500),(62,'Westgate Transit Center',1,30.219200,-97.799500),(63,'I-H-35 S Service Rd',1,30.187500,-97.776500),(64,'S I-H-35 Service Rd SB',1,30.183900,-97.778800),(65,'S I-H-35 Service Rd SB & Billye Hill Ln',1,30.174600,-97.779300),(66,'Testing',0,123.000000,13.000000);
/*!40000 ALTER TABLE `transitstops` ENABLE KEYS */;
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
