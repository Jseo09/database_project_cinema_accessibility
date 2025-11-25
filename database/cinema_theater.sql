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
-- Table structure for table `theater`
--

DROP TABLE IF EXISTS `theater`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `theater` (
  `Theater_ID` int NOT NULL AUTO_INCREMENT,
  `Theater_Name` varchar(255) NOT NULL,
  `Website` varchar(255) DEFAULT NULL,
  `City` varchar(100) NOT NULL,
  `State` char(2) NOT NULL,
  `Zip` varchar(10) DEFAULT NULL,
  `Address` varchar(255) NOT NULL,
  `Latitude` decimal(9,6) NOT NULL DEFAULT '0.000000',
  `Longitude` decimal(9,6) NOT NULL DEFAULT '0.000000',
  `Status` varchar(20) DEFAULT 'Closed',
  `Phone_Number` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`Theater_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `theater`
--

LOCK TABLES `theater` WRITE;
/*!40000 ALTER TABLE `theater` DISABLE KEYS */;
INSERT INTO `theater` VALUES (1,'City Base Cinemas San Antonio','https://www.citybasecinema.com/','San Antonio','TX','78223','2623 SE Military Dr',29.354320,-98.451200,'Open','(210) 531-3000'),(2,'Alamo Drafthouse Cinema Stone Oak','https://drafthouse.com/san-antonio/theater/stone-oak','San Antonio','TX','78258','22806 U.S. Hwy 281 N',29.653990,-98.405600,'Open','(210) 729-9422'),(3,'Santikos Galaxy','https://www.santikos.com/san-antonio/galaxy/theater-info','San Antonio','TX','78218','2938 NE Interstate 410 Loop',29.514600,-98.403967,'Open','(877) 691-0734'),(5,'Cinemark San Antonio 16','https://www.cinemark.com/theatres/tx-san-antonio/cinemark-san-antonio-16?utm_medium=organic&utm_source=gmb&utm_campaign=local_listing_theater&utm_content=GMB_listing&y_source=1_MTc0OTMxMzYtNzE1LWxvY2F0aW9uLndlYnNpdGU%3D','San Antonio','TX','78229','The Summit, 5063 Northwest Loop 410 W',29.489400,-98.590700,'Open','(210) 522-9660'),(6,'Santikos Palladium','https://www.santikos.com/san-antonio/palladium/theater-info','San Antonio','TX','78257','17703 W Interstate 10 Frontage Rd',29.608300,-98.598900,'Open','(877) 691-0734'),(7,'Santikos Westlakes','https://www.santikos.com/san-antonio/westlakes/theater-info','San Antonio','TX','78227','1255 SW Loop 410',29.426400,-98.651400,'Open','(877) 691-0734'),(8,'Regal Cielo Vista','https://www.regmovies.com/theatres/regal-cielo-vista-0765?utm_source=google&utm_medium=organic&utm_campaign=gmb-listing','San Antonio','TX','78238','2828 Cinema Ridge',29.463270,-98.619000,'Open','(844) 462-7342'),(9,'AMC Rivercenter 11','https://www.amctheatres.com/movie-theatres/san-antonio/amc-rivercenter-11-with-alamo-imax?utm_medium=organic&utm_source=google&utm_campaign=local','San Antonio','TX','78205','849 E Commerce St suite 800',29.423560,-98.483900,'Open','(210) 228-0351'),(10,'Regal Alamo Quarry','https://www.regmovies.com/theatres/regal-alamo-quarry-0939?utm_source=google&utm_medium=organic&utm_campaign=gmb-listing','San Antonio','TX','78209','255 E Basse Rd Ste. 320',29.495400,-98.480500,'Open','(844) 462-7342'),(11,'Santikos Mayan Palace','https://www.santikos.com/san-antonio/mayan/theater-info','San Antonio','TX','78221','1918 SW Military Dr',29.355200,-98.523600,'Open','(877) 691-0734'),(12,'Flix Brewhouse','https://flixbrewhouse.com/theaters/g000k-flix-brewhouse-san-antonio/','San Antonio','TX','78245','845 TX-1604 Loop',29.424600,-98.712400,'Open','(726) 800-7500'),(13,'Alamo Drafthouse Cinema Park North','https://drafthouse.com/san-antonio/theater/park-north','San Antonio','TX','78216','618 Northwest Loop 410 Suite 307',29.518200,-98.502800,'Open','(210) 729-9293'),(14,'Regal Huebner Oaks','https://www.regmovies.com/theatres/regal-huebner-oaks-0581?utm_source=google&utm_medium=organic&utm_campaign=gmb-listing','San Antonio','TX','78230','11075 I-10 Ste 1H',29.548600,-98.579000,'Open','(844) 462-7342'),(15,'AMC DINE-IN Tech Ridge 10','https://www.amctheatres.com/movie-theatres/austin/amc-dine-in-tech-ridge-10?utm_medium=organic&utm_source=google&utm_campaign=local','Austin','TX','78753','12625 N Interstate Hwy 35',30.408500,-97.671600,'Open','(512) 640-1533'),(16,'Moviehouse & Eatery by Cinepolis SW Austin','https://www.cinepolisusa.com/swaustin/home/?preferred=true','Austin','TX','78735','7415 Southwest Pkwy building 7',30.255500,-97.869100,'Open','(512) 572-0770'),(17,'Alamo Drafthouse Cinema Slaughter Lane','https://drafthouse.com/austin/theater/slaughter-lane','Austin','TX','78749','5701 W Slaughter Ln Suite F',30.199000,-97.868900,'Open','(512) 861-7060'),(18,'Regal Metropolitan','https://www.regmovies.com/theatres/regal-metropolitan-0950?utm_source=google&utm_medium=organic&utm_campaign=gmb-listing','Austin','TX','78745','901 Little Texas Ln',30.198200,-97.769600,'Open','(844) 462-7342'),(19,'Alamo Drafthouse Cinema South Lamar','https://drafthouse.com/austin/theater/south-lamar','Austin','TX','78704','1120 S Lamar Blvd',30.256200,-97.763300,'Open','(512) 861-7040'),(20,'AMC Barton Creek Square 14','https://www.amctheatres.com/movie-theatres/austin/amc-barton-creek-square-14?utm_medium=organic&utm_source=google&utm_campaign=local','Austin','TX','78746','2901 S Capital of Texas Hwy',30.258000,-97.808300,'Open','(512) 306-1991'),(21,'Galaxy Theatres Austin','https://www.galaxytheatres.com/movie-theater/austin','Austin','TX','78752','6700 Middle Fiskville Rd',30.329400,-97.708000,'Open','(888) 407-9874'),(22,'Violet Crown Austin','https://austin.violetcrown.com/cinema/','Austin','TX','78701','434 W 2nd St',30.265900,-97.748300,'Open','(737) 688-0022'),(23,'IPIC Theaters','https://www.ipic.com/austin-tx-the-domain/location?utm_source=google&utm_medium=local_listings&utm_campaign=yext','Austin','TX','78758','3225 Amy Donovan Plaza',30.396800,-97.727900,'Open','(512) 568-3400'),(24,'Regal Arbor',NULL,'Austin','TX','78759','9828 Great Hills Trl',30.394700,-97.747600,'Closed','(844) 462-7342'),(26,'Regal Fiesta 16','None','San Antonio','TX','78230','12631 Vance Jackson Rd',29.561300,-98.585900,'Temporarily Closed','??(844) 462-7342'),(27,'Regal Gateway','https://www.regmovies.com/theatres/regal-gateway-0949?utm_source=google&utm_medium=organic&utm_campaign=gmb-listing','Austin','TX','78759','9700 Stonelake Blvd',30.387900,-97.739600,'Open','??(844) 462-7342'),(28,'Regal Westgate','https://www.regmovies.com/theatres/regal-westgate-0953?utm_source=google&utm_medium=organic&utm_campaign=gmb-listing','Austin','TX','78745','4477 S Lamar Blvd',30.230300,-97.799700,'Open','(844) 462-7342'),(29,'Cinemark Southpark Meadows','https://www.cinemark.com/theatres/tx-austin/cinemark-southpark-meadows?utm_medium=organic&utm_source=gmb&utm_campaign=local_listing_theater&utm_content=GMB_listing&y_source=1_MTc0OTMyMDEtNzE1LWxvY2F0aW9uLndlYnNpdGU%3D','Austin','TX','78748','9900 S IH-35 Service Road SB Unit N',30.154200,-97.794100,'Open','(512) 291-0171');
/*!40000 ALTER TABLE `theater` ENABLE KEYS */;
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
