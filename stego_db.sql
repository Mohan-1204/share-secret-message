-- phpMyAdmin SQL Dump
-- version 2.11.6
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Apr 16, 2026 at 06:06 AM
-- Server version: 5.0.51
-- PHP Version: 5.2.6

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `stego_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `image_puzzles`
--

CREATE TABLE `image_puzzles` (
  `id` int(11) NOT NULL auto_increment,
  `message_id` int(11) NOT NULL,
  `puzzle_path` varchar(255) NOT NULL,
  `puzzle_order` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `message_id` (`message_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `image_puzzles`
--


-- --------------------------------------------------------

--
-- Table structure for table `shared_files`
--

CREATE TABLE `shared_files` (
  `id` int(11) NOT NULL auto_increment,
  `sender_id` int(11) default NULL,
  `receiver_id` int(11) default NULL,
  `file_name` varchar(255) default NULL,
  `ecc_key` varchar(100) default NULL,
  `lsb_key` varchar(100) default NULL,
  `status` enum('Sent','Received','Extracted') default 'Sent',
  `created_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  `secret_text` varchar(1000) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

--
-- Dumping data for table `shared_files`
--

INSERT INTO `shared_files` (`id`, `sender_id`, `receiver_id`, `file_name`, `ecc_key`, `lsb_key`, `status`, `created_at`, `secret_text`) VALUES
--(1, 1, 2, 'stego_temp_maxresdefault.jpg', '1c8dadc51c644b8b', 'd17de094a68a00ed', 'Sent', '2026-04-15 19:38:16', ''),
--(2, 2, 1, 'stego_temp_VOTE_RIGHT.png', 'e2a7aeed622c9189', '10316a6dbe31186d', 'Sent', '2026-04-16 11:02:05', ''),
--(3, 2, 1, 'stego_temp_gallery_6.jpg', '1c6ee3845013b684', '7108350314a5aa8e', 'Sent', '2026-04-16 11:05:45', ''),
--(4, 2, 1, 'stego_temp_g8.jpg', 'a5ed5c7be8515bdb', 'b010ef91e5684960', 'Sent', '2026-04-16 11:25:13', 'sample test image concept');

-- --------------------------------------------------------

--
-- Table structure for table `shared_messages`
--

CREATE TABLE `shared_messages` (
  `id` int(11) NOT NULL auto_increment,
  `sender_id` int(11) NOT NULL,
  `receiver_email` varchar(100) NOT NULL,
  `original_image` varchar(255) default NULL,
  `stego_image` varchar(255) default NULL,
  `verification_key` varchar(100) default NULL,
  `puzzle_status` enum('Encrypted','Decrypted','Extracted') default 'Encrypted',
  `created_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`),
  KEY `sender_id` (`sender_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `shared_messages`
--


-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(100) NOT NULL,
  `gender` varchar(20) default NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(20) default NULL,
  `address` text,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `gender`, `email`, `phone`, `address`, `username`, `password`, `created_at`) VALUES
(1, 'sundar', 'Male', 'sundarv06@gmail.com', '7904461600', 'trichy', 'sundar', 'sundar', '2026-04-15 14:39:21'),
(2, 'pandiyan', 'Male', 'sundarsamcore@gmail.com', '7904461600', 'trichy', 'pandiyan', 'pandiyan', '2026-04-15 19:16:59');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `image_puzzles`
--
ALTER TABLE `image_puzzles`
  ADD CONSTRAINT `image_puzzles_ibfk_1` FOREIGN KEY (`message_id`) REFERENCES `shared_messages` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `shared_messages`
--
ALTER TABLE `shared_messages`
  ADD CONSTRAINT `shared_messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`);






