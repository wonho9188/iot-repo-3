-- MySQL dump 10.13  Distrib 8.0.42, for Linux (x86_64)
--
-- Host: localhost    Database: rail_db
-- ------------------------------------------------------
-- Server version	8.0.42-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `barcode_scan_log`
--

DROP TABLE IF EXISTS `barcode_scan_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `barcode_scan_log` (
  `barcode_scan_id` varchar(10) NOT NULL,
  `unit_id` varchar(10) DEFAULT NULL,
  `barcode` varchar(255) DEFAULT NULL,
  `error_code` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`barcode_scan_id`),
  KEY `unit_id` (`unit_id`),
  KEY `error_code` (`error_code`),
  CONSTRAINT `barcode_scan_log_ibfk_1` FOREIGN KEY (`unit_id`) REFERENCES `unit` (`unit_id`),
  CONSTRAINT `barcode_scan_log_ibfk_2` FOREIGN KEY (`error_code`) REFERENCES `error` (`error_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `barcode_scan_log`
--

LOCK TABLES `barcode_scan_log` WRITE;
/*!40000 ALTER TABLE `barcode_scan_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `barcode_scan_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `error`
--

DROP TABLE IF EXISTS `error`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `error` (
  `error_code` varchar(10) NOT NULL,
  `error_range` varchar(255) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `method` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`error_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `error`
--

LOCK TABLES `error` WRITE;
/*!40000 ALTER TABLE `error` DISABLE KEYS */;
/*!40000 ALTER TABLE `error` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `model`
--

DROP TABLE IF EXISTS `model`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `model` (
  `model_id` varchar(10) NOT NULL,
  `model_name` varchar(255) NOT NULL,
  `category` varchar(255) DEFAULT NULL,
  `price` int DEFAULT NULL,
  PRIMARY KEY (`model_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `model`
--

LOCK TABLES `model` WRITE;
/*!40000 ALTER TABLE `model` DISABLE KEYS */;
INSERT INTO `model` VALUES ('01','농심 한입 닭가슴살 150g(5ea)','육류',8000),('02','농심 대패삼겹살 800g','육류',15000),('03','CJ 묵은지 김치 200g','반찬',5000),('04','동서식품 찌개용 두부 300g','반찬',2000),('05','삼양 우유 1L','유제품',2500),('06','삼양 체다 치즈 10개입','유제품',3000),('07','해태 빅 요구르트','유제품',800),('08','롯데 샌드위치용 식빵 (중)','빵',2500),('09','대상 즉석밥 150g(5ea)','즉석밥',4500),('10','농심 신라면(5ea)','라면',3500),('11','대상 쌀과자(10ea)','과자',3000),('12','샘표 진간장(200g)','식재료',2500),('13','정관장 홍삼액(30ea)','건강식품',40000),('14','한성 충전기','생활용품',3000),('15','한성 키보드','전자제품',15000);
/*!40000 ALTER TABLE `model` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `seller`
--

DROP TABLE IF EXISTS `seller`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `seller` (
  `seller_id` varchar(10) NOT NULL,
  `seller_name` varchar(255) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`seller_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `seller`
--

LOCK TABLES `seller` WRITE;
/*!40000 ALTER TABLE `seller` DISABLE KEYS */;
INSERT INTO `seller` VALUES ('01','CJ','서울특별시 강남구','010-1234-5678'),('02','농심','서울특별시 서초구','010-2345-6789'),('03','동서식품','서울특별시 송파구','010-3456-7890'),('04','삼양','서울특별시 강동구','010-4567-8901'),('05','해태','서울특별시 중구','010-5678-9012'),('06','롯데','서울특별시 종로구','010-6789-0123'),('07','대상','서울특별시 용산구','010-7890-1234'),('08','한성','서울특별시 마포구','010-8901-2345'),('09','샘표','서울특별시 은평구','010-9012-3456'),('10','정관장','서울특별시 노원구','010-0123-4567');
/*!40000 ALTER TABLE `seller` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unit`
--

DROP TABLE IF EXISTS `unit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `unit` (
  `unit_id` varchar(10) NOT NULL,
  `model_id` varchar(10) DEFAULT NULL,
  `seller_id` varchar(10) DEFAULT NULL,
  `seller_name` varchar(255) DEFAULT NULL,
  `slot_id` varchar(10) DEFAULT NULL,
  `barcode` varchar(255) NOT NULL,
  `exp` int DEFAULT NULL,
  `disposal_status` tinyint(1) DEFAULT NULL,
  `entry_time` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`unit_id`),
  KEY `model_id` (`model_id`),
  KEY `seller_id` (`seller_id`),
  CONSTRAINT `unit_ibfk_1` FOREIGN KEY (`model_id`) REFERENCES `model` (`model_id`),
  CONSTRAINT `unit_ibfk_2` FOREIGN KEY (`seller_id`) REFERENCES `seller` (`seller_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unit`
--

LOCK TABLES `unit` WRITE;
/*!40000 ALTER TABLE `unit` DISABLE KEYS */;
INSERT INTO `unit` VALUES ('01','01','02','농심','A01','A0102250601',250601,0,'202505010930'),('02','02','02','농심','A02','A0202260901',260901,0,'202505020930'),('03','03','01','CJ','B01','B0301250510',250510,0,'202505030930'),('04','03','01','CJ','B02','B0301250601',250601,0,'202505040930'),('05','05','04','삼양','B03','B0504250501',250501,0,'202505050930'),('06','06','04','삼양','B04','B0604250801',250801,0,'202505060930'),('07','07','05','해태','B05','B0705250610',250610,0,'202505070930'),('08','08','06','롯데','C01','C0806250701',250701,0,'202505080930'),('09','09','07','대상','C02','C0907250601',250601,0,'202505090930'),('10','10','02','농심','C03','C1002260701',260701,0,'202505101030'),('11','11','07','대상','C04','C1107260801',260801,0,'202505111030'),('12','12','09','샘표','C05','C1209260901',260901,0,'202505121030'),('13','13','10','정관장','C06','C1310261001',261001,0,'202505131030'),('14','14','08','한성','D01','D1408991231',991231,0,'202505141030'),('15','15','08','한성','D02','D1508991231',991231,0,'202505151030'),('16','01','02','농심','A03','A0102250601',250601,0,'202505160930'),('17','02','02','농심','A04','A0202260901',260901,0,'202505170930'),('18','03','01','CJ','B06','B0301250510',250510,0,'202505180930'),('19','03','01','CJ','B07','B0301250601',250601,0,'202505190930'),('20','05','04','삼양','B08','B0504250501',250501,0,'202505200930'),('21','06','04','삼양','B09','B0604250801',250801,0,'202505210930'),('22','07','05','해태','B10','B0705250610',250610,0,'202505220930'),('23','08','06','롯데','C06','C0806250701',250701,0,'202505230930'),('24','09','07','대상','C07','C0907250601',250601,0,'202505240930'),('25','10','02','농심','C08','C1002260701',260701,0,'202505251030'),('26','11','07','대상','C09','C1107260801',260801,0,'202505261030'),('27','12','09','샘표','C10','C1209260901',260901,0,'202505271030'),('28','13','10','정관장','C11','C1310261001',261001,0,'202505281030'),('29','14','08','한성','D03','D1408991231',991231,0,'202505291030'),('30','15','08','한성','D04','D1508991231',991231,0,'202505301030'),('31','01','02','농심','A05','A0102250601',250601,0,'202505310930'),('32','02','02','농심','A06','A0202260901',260901,0,'202506010930'),('33','03','01','CJ','B11','B0301250510',250510,0,'202506020930'),('34','03','01','CJ','B12','B0301250601',250601,0,'202506030930'),('35','05','04','삼양','B13','B0504250501',250501,0,'202506040930'),('36','06','04','삼양','B14','B0604250801',250801,0,'202506050930'),('37','07','05','해태','B15','B0705250610',250610,0,'202506060930'),('38','08','06','롯데','C12','C0806250701',250701,0,'202506070930'),('39','09','07','대상','C13','C0907250601',250601,0,'202506080930'),('40','10','02','농심','C14','C1002260701',260701,0,'202506091030');
/*!40000 ALTER TABLE `unit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `warehouse`
--

DROP TABLE IF EXISTS `warehouse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warehouse` (
  `warehouse_id` varchar(10) NOT NULL,
  `warehouse_type` varchar(50) DEFAULT NULL,
  `min_temp` float DEFAULT NULL,
  `max_temp` float DEFAULT NULL,
  `min_hum` float DEFAULT NULL,
  `max_hum` float DEFAULT NULL,
  `capacity` int DEFAULT NULL,
  `used_capacity` int DEFAULT NULL,
  PRIMARY KEY (`warehouse_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warehouse`
--

LOCK TABLES `warehouse` WRITE;
/*!40000 ALTER TABLE `warehouse` DISABLE KEYS */;
/*!40000 ALTER TABLE `warehouse` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `warehouse_slot`
--

DROP TABLE IF EXISTS `warehouse_slot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warehouse_slot` (
  `slot_id` varchar(10) NOT NULL,
  `warehouse_id` varchar(10) DEFAULT NULL,
  `unit_id` varchar(10) DEFAULT NULL,
  `status` int DEFAULT NULL,
  PRIMARY KEY (`slot_id`),
  KEY `warehouse_id` (`warehouse_id`),
  CONSTRAINT `warehouse_slot_ibfk_1` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouse` (`warehouse_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warehouse_slot`
--

LOCK TABLES `warehouse_slot` WRITE;
/*!40000 ALTER TABLE `warehouse_slot` DISABLE KEYS */;
/*!40000 ALTER TABLE `warehouse_slot` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-10 14:43:20
