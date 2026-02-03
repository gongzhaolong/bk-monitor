-- 创建 metadata_clusterinfo 表
-- 用于存储集群配置信息

USE bk_monitorv3;

-- 如果表已存在，先删除
DROP TABLE IF EXISTS metadata_clusterinfo;

-- 创建表
CREATE TABLE metadata_clusterinfo (
    cluster_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '集群ID',
    bk_tenant_id VARCHAR(64) NOT NULL DEFAULT 'system' COMMENT '租户ID',
    cluster_name VARCHAR(128) NOT NULL COMMENT '集群英文名',
    display_name VARCHAR(128) NOT NULL DEFAULT '' COMMENT '集群显示名称',
    cluster_type VARCHAR(32) NOT NULL COMMENT '集群类型',
    domain_name VARCHAR(128) NOT NULL COMMENT '集群域名',
    port INT NOT NULL COMMENT '端口',
    extranet_domain_name VARCHAR(128) DEFAULT NULL COMMENT '集群外网域名',
    extranet_port INT DEFAULT 0 COMMENT '集群外网端口',
    description VARCHAR(256) NOT NULL COMMENT '集群备注说明信息',
    is_default_cluster TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否默认集群',
    username VARCHAR(64) NOT NULL DEFAULT '' COMMENT '用户名',
    password TEXT COMMENT '密码（加密存储）',
    version VARCHAR(64) DEFAULT NULL COMMENT '存储集群版本',
    custom_option TEXT COMMENT '自定义标签',
    `schema` VARCHAR(32) DEFAULT NULL COMMENT '访问协议',
    is_ssl_verify TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'SSL验证是否强验证',
    ssl_verification_mode VARCHAR(16) DEFAULT 'none' COMMENT 'CA 校验模式',
    ssl_certificate_authorities TEXT DEFAULT NULL COMMENT 'CA 内容',
    ssl_certificate TEXT DEFAULT NULL COMMENT 'SSL/TLS 证书内容',
    ssl_certificate_key TEXT DEFAULT NULL COMMENT 'SSL/TLS 证书私钥内容',
    ssl_insecure_skip_verify TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否跳过服务器校验',
    is_auth TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否开启鉴权',
    sasl_mechanisms VARCHAR(64) DEFAULT NULL COMMENT 'SASL认证机制',
    security_protocol VARCHAR(64) DEFAULT NULL COMMENT '安全协议',
    registered_system VARCHAR(128) NOT NULL DEFAULT '_default' COMMENT '注册来源系统',
    registered_to_bkbase TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已经注册到bkbase平台',
    is_register_to_gse TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否需要往GSE注册',
    gse_stream_to_id INT NOT NULL DEFAULT -1 COMMENT 'GSE接收端配置ID',
    label VARCHAR(32) DEFAULT '' COMMENT '用途标签',
    default_settings TEXT DEFAULT NULL COMMENT '集群的默认配置（JSON格式）',
    creator VARCHAR(255) NOT NULL DEFAULT 'system' COMMENT '创建者',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    last_modify_user VARCHAR(32) NOT NULL DEFAULT 'system' COMMENT '最后更新者',
    last_modify_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    UNIQUE KEY unique_tenant_cluster_type_name (bk_tenant_id, cluster_type, cluster_name),
    KEY idx_cluster_type (cluster_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='集群配置信息';

