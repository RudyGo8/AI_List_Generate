-- 创建数据库
CREATE DATABASE IF NOT EXISTS ai_list DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ai_list;

-- 1. 系统配置表
CREATE TABLE IF NOT EXISTS db_sys_conf (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    `key` VARCHAR(256) NOT NULL COMMENT '键',
    `value` VARCHAR(256) NOT NULL COMMENT '值',
    enable INT NOT NULL COMMENT '0停用,1启用',
    remark VARCHAR(512) DEFAULT NULL COMMENT '描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_user VARCHAR(128) NOT NULL DEFAULT 'system' COMMENT '创建人',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    update_user VARCHAR(128) DEFAULT 'system' COMMENT '修改人',
    UNIQUE INDEX uniq_sc_key_enable (`key`, enable)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- 2. AI 提示词表
CREATE TABLE IF NOT EXISTS db_sys_ai_prompt (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    prompt_key VARCHAR(256) NOT NULL COMMENT '提示词标志',
    prompt_value LONGTEXT NOT NULL COMMENT '提示词',
    enable INT NOT NULL COMMENT '0停用,1启用',
    remark VARCHAR(1024) DEFAULT NULL COMMENT '描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_user VARCHAR(128) NOT NULL DEFAULT 'system' COMMENT '创建人',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    update_user VARCHAR(128) DEFAULT 'system' COMMENT '修改人',
    UNIQUE INDEX uniq_sap_prompt_key_enable (prompt_key, enable)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI提示词表';

-- 3. 客户端配置表
CREATE TABLE IF NOT EXISTS db_sys_client_conf (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    client_name VARCHAR(256) NOT NULL COMMENT '客户端名称',
    api_key VARCHAR(128) NOT NULL COMMENT '客户端key',
    api_secret VARCHAR(128) NOT NULL COMMENT '客户端密钥',
    enable INT NOT NULL COMMENT '0停用,1启用',
    remark VARCHAR(512) DEFAULT NULL COMMENT '描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_user VARCHAR(128) NOT NULL DEFAULT 'system' COMMENT '创建人',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    update_user VARCHAR(128) DEFAULT 'system' COMMENT '修改人',
    UNIQUE INDEX uniq_scc_client_name_enable (client_name, enable)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='客户端配置表';

-- 4. 批处理信息表
CREATE TABLE IF NOT EXISTS db_sys_batch_info (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    batch_type VARCHAR(4) NOT NULL COMMENT '批处理类型',
    batch_no VARCHAR(128) NOT NULL COMMENT '批处理编号',
    status VARCHAR(2) NOT NULL COMMENT '批次状态，00:成功，01:失败，03:处理中',
    batch_counts INT DEFAULT 0 COMMENT '批处理条数',
    remark VARCHAR(512) DEFAULT NULL COMMENT '描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_user VARCHAR(128) NOT NULL DEFAULT 'system' COMMENT '创建人',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    update_user VARCHAR(128) DEFAULT 'system' COMMENT '修改人',
    UNIQUE INDEX uniq_sbd_batch_no (batch_no),
    INDEX idx_sbd_status (status),
    INDEX idx_sbd_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='批处理信息表';

-- 5. 商品原始数据表
CREATE TABLE IF NOT EXISTS db_product_src_detail (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键，可以理解为任务ID',
    gid VARCHAR(24) NOT NULL COMMENT '组ID',
    product_title VARCHAR(256) DEFAULT NULL COMMENT '原始商品标题',
    product_url VARCHAR(2048) DEFAULT NULL COMMENT '原始商品链接',
    category_name VARCHAR(128) DEFAULT NULL COMMENT '原始商品类目',
    category_id VARCHAR(24) DEFAULT NULL COMMENT '原始商品类目ID',
    spu_image_url VARCHAR(256) NOT NULL COMMENT '原始spu图片链接',
    sku_image_url_list TEXT DEFAULT NULL COMMENT '原始sku图片链接',
    related_items TEXT DEFAULT NULL COMMENT '原始相关项',
    attributes TEXT DEFAULT NULL COMMENT '原始商品属性',
    supplier_name VARCHAR(256) DEFAULT NULL COMMENT '供应商名称',
    remark VARCHAR(512) DEFAULT NULL COMMENT '描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_user VARCHAR(128) NOT NULL DEFAULT 'system' COMMENT '创建人',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    update_user VARCHAR(128) NOT NULL DEFAULT 'system' COMMENT '修改人',
    INDEX idx_spd_gid (gid),
    INDEX idx_spd_create_time (create_time),
    INDEX idx_spd_update_time (update_time),
    INDEX idx_spd_product_title (product_title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品原始数据表';

-- 6. 商品目标数据表
CREATE TABLE IF NOT EXISTS db_product_des_detail (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    gid VARCHAR(24) NOT NULL COMMENT '组ID',
    platform_id INT DEFAULT NULL COMMENT '平台编号',
    site VARCHAR(12) DEFAULT NULL COMMENT '站点',
    product_src_id BIGINT DEFAULT NULL COMMENT '原商品表主键ID',
    product_title VARCHAR(256) DEFAULT NULL COMMENT '商品标题',
    product_desc TEXT DEFAULT NULL COMMENT '商品描述',
    spu_image_url VARCHAR(256) DEFAULT NULL COMMENT 'spu图片链接',
    sku_image_url_list TEXT DEFAULT NULL COMMENT 'sku图片链接',
    category_name VARCHAR(256) DEFAULT NULL COMMENT '类目名称',
    category_id VARCHAR(128) DEFAULT NULL COMMENT '类目ID',
    sales_attr_value_list TEXT DEFAULT NULL COMMENT '销售属性列表(sku)',
    attr_value_list TEXT DEFAULT NULL COMMENT '属性列表',
    tag_value VARCHAR(256) DEFAULT NULL COMMENT '标签值',
    version VARCHAR(24) DEFAULT NULL COMMENT '版本号',
    remark VARCHAR(512) DEFAULT NULL COMMENT '描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_user VARCHAR(128) NOT NULL DEFAULT 'system' COMMENT '创建人',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    update_user VARCHAR(128) NOT NULL DEFAULT 'system' COMMENT '修改人',
    INDEX idx_dpd_gid (gid),
    INDEX idx_dpd_create_time (create_time),
    INDEX idx_dpd_update_time (update_time),
    INDEX idx_dpd_src_product_src_id (product_src_id),
    INDEX idx_dpd_src_platform_id_site (platform_id, site),
    INDEX idx_dpd_product_title (product_title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品目标数据表';

-- 7. 商品任务详情表
CREATE TABLE IF NOT EXISTS db_product_task_detail (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    gid VARCHAR(24) NOT NULL COMMENT '组ID',
    product_src_id BIGINT DEFAULT NULL COMMENT '原始商品表主键ID',
    product_des_id BIGINT DEFAULT NULL COMMENT '目标商品表主键ID',
    platform_id INT NOT NULL COMMENT '平台ID',
    site VARCHAR(12) DEFAULT NULL COMMENT '站点',
    status VARCHAR(2) NOT NULL COMMENT '数据状态，02:ready,03:处理中,00:成功,01:失败',
    custom_data TEXT DEFAULT NULL COMMENT '用户自定义数据',
    des_lang_type VARCHAR(24) NOT NULL COMMENT '目标语言',
    tag_type VARCHAR(4) DEFAULT NULL COMMENT '标签类型',
    batch_no VARCHAR(128) DEFAULT NULL COMMENT '批处理编号',
    model_name VARCHAR(128) DEFAULT NULL COMMENT '模型名',
    duration FLOAT DEFAULT 0.0 COMMENT '执行时长',
    `usage` VARCHAR(128) DEFAULT NULL COMMENT '消耗',
    notice_url VARCHAR(512) DEFAULT NULL COMMENT '通知地址',
    remark VARCHAR(512) DEFAULT NULL COMMENT '描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_user VARCHAR(128) NOT NULL DEFAULT 'system' COMMENT '创建人',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    update_user VARCHAR(128) DEFAULT 'system' COMMENT '修改人',
    INDEX idx_ptd_product_src_id (product_src_id),
    INDEX idx_ptd_product_des_id (product_des_id),
    INDEX idx_ptd_platform_id (platform_id, site),
    INDEX idx_ptd_gid (gid),
    INDEX idx_ptd_create_time (create_time),
    INDEX idx_ptd_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品任务详情表';

-- 8. 商品类目配置表
CREATE TABLE IF NOT EXISTS db_product_category_conf (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    platform_id INT NOT NULL COMMENT '平台ID,-1代表自有',
    site VARCHAR(12) DEFAULT NULL COMMENT '站点',
    category_id VARCHAR(32) NOT NULL COMMENT '类目ID',
    category_name VARCHAR(128) NOT NULL COMMENT '类目名',
    category_level INT NOT NULL COMMENT '类目层级',
    superior_category_id VARCHAR(32) DEFAULT NULL COMMENT '上级类目id',
    version FLOAT DEFAULT NULL COMMENT '版本',
    remark VARCHAR(512) DEFAULT NULL COMMENT '描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_user VARCHAR(128) NOT NULL DEFAULT 'system' COMMENT '创建人',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    update_user VARCHAR(128) DEFAULT 'system' COMMENT '修改人',
    INDEX idx_pcc_platform_id_site (platform_id, site),
    INDEX idx_pcc_category_id (category_id),
    INDEX idx_pcc_category_name (category_name),
    INDEX idx_pcc_category_level (category_level),
    INDEX idx_pcc_superior_category_id (superior_category_id),
    INDEX idx_pcc_create_time (create_time),
    INDEX idx_pcc_update_time (update_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品类目配置表';

-- 9. 商品类目属性配置表
CREATE TABLE IF NOT EXISTS db_product_category_attribute_conf (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    platform_id INT NOT NULL COMMENT '平台ID,-1代表自有',
    site VARCHAR(12) DEFAULT NULL COMMENT '站点',
    category_id VARCHAR(32) NOT NULL COMMENT '类目ID',
    attribute_type VARCHAR(4) NOT NULL COMMENT '属性类型：0002销售属性，0003商品属性',
    attribute_id VARCHAR(128) NOT NULL COMMENT '属性ID',
    attribute_name VARCHAR(128) NOT NULL COMMENT '属性名',
    required_flag INT NOT NULL COMMENT '必填标志:0非必填，1必填',
    multiple_flag INT NOT NULL COMMENT '多选标志:0单选，1多选',
    customized_flag INT NOT NULL COMMENT '自定义内容标志:0不可自定义，1可自定义',
    value_list TEXT NOT NULL COMMENT '填写内容清单json',
    version FLOAT DEFAULT NULL COMMENT '版本',
    remark VARCHAR(512) DEFAULT NULL COMMENT '描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_user VARCHAR(128) NOT NULL DEFAULT 'system' COMMENT '创建人',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    update_user VARCHAR(128) DEFAULT 'system' COMMENT '修改人',
    UNIQUE INDEX uni_pcac_platform_id_site_category_id_attribute_id (platform_id, site, category_id, attribute_id),
    INDEX idx_pcac_platform_id_site (platform_id, site),
    INDEX idx_pcac_category_id (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品类目属性配置表';

-- 10. 商品标签配置表
CREATE TABLE IF NOT EXISTS db_product_tag_conf (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    gid VARCHAR(24) NOT NULL COMMENT '组ID',
    tag_type VARCHAR(4) NOT NULL COMMENT '标签类别',
    tag_id VARCHAR(256) NOT NULL COMMENT '标签ID',
    tag_value VARCHAR(256) NOT NULL COMMENT '标签值',
    enable INT NOT NULL DEFAULT 0 COMMENT '0停用,1启用',
    remark VARCHAR(512) DEFAULT NULL COMMENT '描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_user VARCHAR(128) NOT NULL DEFAULT 'system' COMMENT '创建人',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    update_user VARCHAR(128) NOT NULL DEFAULT 'system' COMMENT '修改人',
    UNIQUE INDEX uniq_ptc_gid_type_id_value (gid, tag_type, tag_id, tag_value),
    INDEX idx_ptc_gid_tag_value (gid, tag_type, tag_value),
    INDEX idx_ptc_gid_tag_id (gid, tag_type, tag_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品标签配置表';

-- 11. 通知详情表
CREATE TABLE IF NOT EXISTS db_notice_detail (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    gid VARCHAR(24) NOT NULL COMMENT '组ID',
    task_type VARCHAR(4) NOT NULL COMMENT '任务类型',
    biz_id VARCHAR(128) NOT NULL COMMENT '业务ID',
    notice_url VARCHAR(512) DEFAULT NULL COMMENT '通知地址',
    notice_content TEXT DEFAULT NULL COMMENT '通知内容',
    next_notice_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '下次通知时间',
    custom_data TEXT DEFAULT NULL COMMENT '用户自定义数据',
    notice_counts INT DEFAULT 0 COMMENT '通知次数',
    status VARCHAR(2) NOT NULL COMMENT '数据状态，02:ready,03:处理中,00:成功,01:失败',
    batch_no VARCHAR(128) DEFAULT NULL COMMENT '批处理编号',
    remark VARCHAR(512) DEFAULT NULL COMMENT '描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_user VARCHAR(128) NOT NULL DEFAULT 'system' COMMENT '创建人',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    update_user VARCHAR(128) DEFAULT 'system' COMMENT '修改人',
    INDEX idx_nd_gid (gid),
    INDEX idx_nd_status (status),
    INDEX idx_nd_next_notice_time (next_notice_time),
    INDEX idx_nd_task_type_biz_id (task_type, biz_id),
    INDEX idx_nd_update_time (update_time),
    INDEX idx_nd_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='通知详情表';


-- 11.1 站点类目表（用于embedding匹配）
CREATE TABLE IF NOT EXISTS db_category (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    site VARCHAR(64) NOT NULL COMMENT '站点标识，如 shopee_vn, tiktok_id',
    category_path VARCHAR(512) NOT NULL COMMENT '类目路径，如 电子 > 手机',
    category_id VARCHAR(64) NOT NULL COMMENT '平台类目ID',
    parent_id VARCHAR(64) DEFAULT NULL COMMENT '父类目ID',
    level INT NOT NULL DEFAULT 1 COMMENT '类目层级',
    enable INT NOT NULL DEFAULT 1 COMMENT '0停用,1启用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_user VARCHAR(128) NOT NULL DEFAULT 'system' COMMENT '创建人',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    update_user VARCHAR(128) DEFAULT 'system' COMMENT '修改人',
    INDEX idx_site (site),
    UNIQUE INDEX idx_category_id (site, category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='站点类目表';
