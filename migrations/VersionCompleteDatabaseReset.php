<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Complete database reset based on iagent(11).sql
 */
final class VersionCompleteDatabaseReset extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Complete database reset based on iagent(11).sql - Recreates all tables with proper schema';
    }

    public function up(Schema $schema): void
    {
        // DROP ALL EXISTING TABLES FIRST
        $this->addSql('DROP TABLE IF EXISTS `conversation_slots`');
        $this->addSql('DROP TABLE IF EXISTS `message`');
        $this->addSql('DROP TABLE IF EXISTS `conversation`');
        $this->addSql('DROP TABLE IF EXISTS `messenger_messages`');
        $this->addSql('DROP TABLE IF EXISTS `user`');
        $this->addSql('DROP TABLE IF EXISTS `doctrine_migration_versions`');

        // RECREATE ALL TABLES FROM iagent(11).sql
        $this->addSql('CREATE TABLE `conversation` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `session_id` varchar(255) NOT NULL DEFAULT \'\',
            `started_at` datetime NOT NULL DEFAULT current_timestamp(),
            `user_id` int(11) DEFAULT NULL,
            `title` varchar(255) DEFAULT NULL,
            `shown_offers` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`shown_offers`)),
            PRIMARY KEY (`id`),
            KEY `session_id` (`session_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci');

        $this->addSql('CREATE TABLE `conversation_slots` (
            `conversation_id` int(11) NOT NULL,
            `slots_json` longtext DEFAULT NULL,
            PRIMARY KEY (`conversation_id`),
            CONSTRAINT `fk_conversation_slots_conversation` FOREIGN KEY (`conversation_id`) REFERENCES `conversation` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci');

        $this->addSql('CREATE TABLE `doctrine_migration_versions` (
            `version` varchar(191) NOT NULL,
            `executed_at` datetime DEFAULT NULL,
            `execution_time` int(11) DEFAULT NULL,
            PRIMARY KEY (`version`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci');

        $this->addSql('CREATE TABLE `message` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `conversation_id` int(11) NOT NULL,
            `role` varchar(20) NOT NULL DEFAULT \'user\',
            `content` longtext NOT NULL DEFAULT \'\',
            `created_at` datetime NOT NULL DEFAULT current_timestamp(),
            `sender` varchar(20) DEFAULT \'user\',
            `offers` text DEFAULT NULL,
            PRIMARY KEY (`id`),
            KEY `conversation_id` (`conversation_id`),
            CONSTRAINT `fk_message_conversation` FOREIGN KEY (`conversation_id`) REFERENCES `conversation` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci');

        $this->addSql('CREATE TABLE `messenger_messages` (
            `id` bigint(20) NOT NULL AUTO_INCREMENT,
            `body` longtext NOT NULL DEFAULT \'\',
            `headers` longtext NOT NULL DEFAULT \'\',
            `queue_name` varchar(190) NOT NULL DEFAULT \'\',
            `created_at` datetime NOT NULL DEFAULT current_timestamp() COMMENT \'(DC2Type:datetime_immutable)\',
            `available_at` datetime NOT NULL DEFAULT current_timestamp() COMMENT \'(DC2Type:datetime_immutable)\',
            `delivered_at` datetime DEFAULT NULL COMMENT \'(DC2Type:datetime_immutable)\',
            PRIMARY KEY (`id`),
            KEY `IDX_75EA56E0FB7336F0` (`queue_name`),
            KEY `IDX_75EA56E0E3BD61CE` (`available_at`),
            KEY `IDX_75EA56E016BA31DB` (`delivered_at`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci');

        $this->addSql('CREATE TABLE `user` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `email` varchar(180) NOT NULL DEFAULT \'\',
            `roles` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT \'[]\' CHECK (json_valid(`roles`)),
            `password` varchar(255) NOT NULL DEFAULT \'\',
            `first_name` varchar(100) NOT NULL DEFAULT \'\',
            `last_name` varchar(100) NOT NULL DEFAULT \'\',
            `is_verified` tinyint(1) NOT NULL DEFAULT 0,
            PRIMARY KEY (`id`),
            UNIQUE KEY `UNIQ_IDENTIFIER_EMAIL` (`email`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci');

        // Tables are now created with proper schema
        // Sample data can be added separately if needed
    }

    public function down(Schema $schema): void
    {
        // DROP ALL TABLES
        $this->addSql('DROP TABLE IF EXISTS `user`');
        $this->addSql('DROP TABLE IF EXISTS `messenger_messages`');
        $this->addSql('DROP TABLE IF EXISTS `message`');
        $this->addSql('DROP TABLE IF EXISTS `conversation_slots`');
        $this->addSql('DROP TABLE IF EXISTS `conversation`');
        $this->addSql('DROP TABLE IF EXISTS `doctrine_migration_versions`');
    }
} 