-- schema.sql

drop database if exists meitu;

create database meitu;

use meitu;

-- grant select, insert, update, delete on awesome.* to 'www-data'@'localhost' identified by 'www-data';

create table meitu_model (
    `id` int not null AUTO_INCREMENT,
    `name` varchar(100) not null,
    `title` varchar(500) not null,
    `summary` varchar(500) null,
    `description` varchar(2048) null,
    `cover` varchar(200) null,
    `view_count` int unsigned not null default 0,
    `created_at` real not null,
    `is_enabled` bool not null default 1,
    unique key `idx_name` (`name`),
    key `idx_title` (`title`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- alter table meitu_model add column `view_count` int unsigned not null default 0 after `cover`;
-- alter table meitu_model add column `cover_backup` varchar(200) null after `cover`;

create table meitu_organize (
    `id` int not null AUTO_INCREMENT,
    `name` varchar(100) not null,
    `title` varchar(500) not null,
    `summary` varchar(500) null,
    `description` varchar(2048) null,
    `cover` varchar(200) null,
    `view_count` int unsigned not null default 0,
    `created_at` real not null,
    `is_enabled` bool not null default 1,
    unique key `idx_name` (`name`),
    key `idx_title` (`title`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- alter table meitu_organize add column `view_count` int unsigned not null default 0 after `cover`;

create table meitu_tag (
    `id` int not null AUTO_INCREMENT,
    `name` varchar(100) not null,
    `title` varchar(500) not null,
    `summary` varchar(500) null,
    `description` varchar(2048) null,
    `cover` varchar(200) null,
    `view_count` int unsigned not null default 0,
    `created_at` real not null,
    `is_enabled` bool not null default 1,
    unique key `idx_name` (`name`),
    key `idx_title` (`title`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- alter table meitu_tag add column `view_count` int unsigned not null default 0 after `cover`;

create table meitu_album (
    `id` int not null AUTO_INCREMENT,
    `model_name` varchar(100),
    `organize_name` varchar(100),
    `category_name` varchar(20) not null,
    `name` varchar(200) not null,
    `title` varchar(500) not null,
    `description` varchar(2048) null,
    `cover` varchar(200) null,
    `view_count` int unsigned not null default 0,
    `origin_link` varchar(500) null,
    `origin_created_at` real not null,
    `created_at` real not null,
    `updated_at` real not null,
    `is_enabled` bool not null default 1,
    unique key `idx_name` (`name`),
    unique key `idx_origin_link` (`origin_link`),
    key `idx_origin_created_at` (`origin_created_at`),
    key `idx_title` (`title`),
    key `idx_model_name` (`model_name`),
    key `idx_organize_name` (`organize_name`),
    key `idx_category_name` (`category_name`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create table meitu_category (
    `id` int not null AUTO_INCREMENT,
    `name` varchar(20) not null,
    `title` varchar(100) not null,
    `created_at` real not null,
    unique key `idx_name` (`name`),
    unique key `idx_title` (`title`),
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;

insert into meitu_category values
(1, 'beauty', '美女图片', UNIX_TIMESTAMP(NOW(4))),
(2, 'handsome', '明星帅哥', UNIX_TIMESTAMP(NOW(4))),
(3, 'news', '娱报', UNIX_TIMESTAMP(NOW(4))),
(4, 'street', '街拍', UNIX_TIMESTAMP(NOW(4)));

create table meitu_image (
    `id` int not null AUTO_INCREMENT,
    `album_id` int not null,
    `image_url` varchar(200) not null,
    `backup_url` varchar(200) null,
    `created_at` real not null,
    `updated_at` real not null,
    `is_enabled` bool not null default 1,
    key `idx_created_at` (`created_at`),
    key `idx_album_id` (`album_id`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create table meitu_album_tag (
    `id` int not null AUTO_INCREMENT,
    `album_id` int not null,
    `tag_id` int not null,
    `created_at` real not null,
    key `idx_album_id` (`album_id`),
    key `idx_tag_id` (`tag_id`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create table meitu_album_model (
    `id` int not null AUTO_INCREMENT,
    `album_id` int not null,
    `model_id` int not null,
    `created_at` real not null,
    key `idx_album_id` (`album_id`),
    key `idx_model_id` (`model_id`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create table meitu_media (
    `id` int not null AUTO_INCREMENT,
    `category_name` varchar(20) not null,
    `keywords` varchar(200),
    `name` varchar(200) not null,
    `title` varchar(500) not null,
    `description` varchar(2048) null,
    `cover` varchar(200) null,
    `view_count` int unsigned not null default 0,
    `origin_link` varchar(500) null,
    `origin_created_at` real not null,
    `created_at` real not null,
    `updated_at` real not null,
    `is_enabled` bool not null default 1,
    unique key `idx_name` (`name`, `category_name`),
    unique key `idx_origin_link` (`origin_link`),
    key `idx_origin_created_at` (`origin_created_at`),
    key `idx_title` (`title`),
    key `idx_keywords` (`keywords`),
    key `idx_category_name` (`category_name`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;


create table meitu_content (
    `id` int not null AUTO_INCREMENT,
    `media_id` int not null,
    `content` mediumtext not null,
    `created_at` real not null,
    `updated_at` real not null,
    `is_enabled` bool not null default 1,
    key `idx_created_at` (`created_at`),
    key `idx_media_id` (`media_id`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;


create table meitu_media_tag (
    `id` int not null AUTO_INCREMENT,
    `media_id` int not null,
    `tag_id` int not null,
    `created_at` real not null,
    key `idx_media_id` (`media_id`),
    key `idx_tag_id` (`tag_id`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;


create table meitu_media_model (
    `id` int not null AUTO_INCREMENT,
    `media_id` int not null,
    `model_id` int not null,
    `created_at` real not null,
    key `idx_media_id` (`media_id`),
    key `idx_model_id` (`model_id`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create table meitu_tmp_model(
    `name` varchar(100),
    `model_url` varchar(200),
    primary key (`name`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create table meitu_search (
    `id` int not null AUTO_INCREMENT,
    `title` varchar(50) not null,
    `count` int unsigned not null default 0,
    `created_at` real not null,
    unique key `idx_title` (`title`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;