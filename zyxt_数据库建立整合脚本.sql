/*
  zyxt 数据库建立整合脚本
  适用环境：MySQL 8.x + Navicat
  说明：本脚本将实验二至实验六中涉及数据库建立、数据准备、索引、视图、存储过程、触发器、事务、游标、用户权限的语句整合为一份可执行脚本。
  注意：本脚本会 DROP DATABASE IF EXISTS zyxt，执行前请确认已经备份原数据库。
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP DATABASE IF EXISTS zyxt;
CREATE DATABASE IF NOT EXISTS zyxt
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_unicode_ci;

USE zyxt;

SET FOREIGN_KEY_CHECKS = 1;

/* =====================================================
   一、基础表建立
   来源：实验二建库建表部分
   ===================================================== */

CREATE TABLE dept (
    DeptCode VARCHAR(50) PRIMARY KEY,
    DeptName VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE well (
    WellNo VARCHAR(50) PRIMARY KEY,
    WellType VARCHAR(20) NOT NULL,
    DeptCode VARCHAR(50) NOT NULL,
    CONSTRAINT chk_well_type CHECK (WellType IN ('油井', '水井')),
    CONSTRAINT fk_well_dept FOREIGN KEY (DeptCode) REFERENCES dept(DeptCode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE construct_unit (
    CompanyName VARCHAR(100) PRIMARY KEY
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE material (
    MaterialCode VARCHAR(50) PRIMARY KEY,
    MaterialName VARCHAR(100) NOT NULL UNIQUE,
    UnitName VARCHAR(20) NOT NULL,
    Price DECIMAL(10, 2) NOT NULL DEFAULT 0,
    CONSTRAINT chk_material_price CHECK (Price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE project (
    BillNo VARCHAR(50) PRIMARY KEY,
    BudgetDept VARCHAR(50),
    WellNo VARCHAR(50),
    BudgetAmount DECIMAL(12, 2),
    BudgetPerson VARCHAR(50),
    BudgetDate DATE,
    StartDate DATE,
    EndDate DATE,
    CompanyName VARCHAR(100),
    WorkContent VARCHAR(200),
    MaterialCost DECIMAL(12, 2) DEFAULT 0,
    LaborCost DECIMAL(12, 2) DEFAULT 0,
    EquipmentCost DECIMAL(12, 2) DEFAULT 0,
    OtherCost DECIMAL(12, 2) DEFAULT 0,
    SettlementAmount DECIMAL(12, 2) DEFAULT 0,
    SettlementPerson VARCHAR(50),
    SettlementDate DATE,
    AccountAmount DECIMAL(12, 2),
    AccountPerson VARCHAR(50),
    AccountDate DATE,
    CONSTRAINT fk_project_dept FOREIGN KEY (BudgetDept) REFERENCES dept(DeptCode),
    CONSTRAINT fk_project_well FOREIGN KEY (WellNo) REFERENCES well(WellNo),
    CONSTRAINT fk_project_company FOREIGN KEY (CompanyName) REFERENCES construct_unit(CompanyName),
    CONSTRAINT chk_project_budget CHECK (BudgetAmount IS NULL OR BudgetAmount >= 0),
    CONSTRAINT chk_project_costs CHECK (
        COALESCE(MaterialCost, 0) >= 0
        AND COALESCE(LaborCost, 0) >= 0
        AND COALESCE(EquipmentCost, 0) >= 0
        AND COALESCE(OtherCost, 0) >= 0
        AND COALESCE(SettlementAmount, 0) >= 0
        AND (AccountAmount IS NULL OR AccountAmount >= 0)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE material_detail (
    DetailID INT AUTO_INCREMENT PRIMARY KEY,
    BillNo VARCHAR(50) NOT NULL,
    MaterialCode VARCHAR(50) NOT NULL,
    Quantity DECIMAL(10, 2) NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    Amount DECIMAL(12, 2),
    CONSTRAINT uk_material_detail_bill_material UNIQUE (BillNo, MaterialCode),
    CONSTRAINT chk_material_detail_amount CHECK (Quantity > 0 AND Price >= 0),
    CONSTRAINT fk_material_detail_project FOREIGN KEY (BillNo) REFERENCES project(BillNo) ON DELETE CASCADE,
    CONSTRAINT fk_material_detail_material FOREIGN KEY (MaterialCode) REFERENCES material(MaterialCode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* =====================================================
   二、基础数据插入
   来源：实验二数据录入部分
   ===================================================== */

INSERT INTO dept VALUES
('1122','采油厂'),
('112201','采油一矿'),
('112202','采油二矿'),
('112201001','采油一矿一队'),
('112201002','采油一矿二队'),
('112201003','采油一矿三队'),
('112202001','采油二矿一队'),
('112202002','采油二矿二队');

INSERT INTO well VALUES
('y001','油井','112201001'),
('y002','油井','112201001'),
('y003','油井','112201002'),
('s001','水井','112201002'),
('y004','油井','112201003'),
('s002','水井','112202001'),
('s003','水井','112202001'),
('y005','油井','112202002');

INSERT INTO construct_unit VALUES
('作业公司作业一队'),
('作业公司作业二队'),
('作业公司作业三队');

INSERT INTO material VALUES
('wm001','材料一','吨',10),
('wm002','材料二','米',10),
('wm003','材料三','桶',10),
('wm004','材料四','袋',10);

/* =====================================================
   三、业务数据插入
   来源：实验二作业项目和材料明细数据
   ===================================================== */

INSERT INTO project VALUES
('zy2018001', '112201001', 'y001', 10000.00, '张三', '2018-05-01', '2018-05-04', '2018-05-25', '作业公司作业一队', '堵漏', 7000.00, 2500.00, 1000.00, 1400.00, 11900.00, '李四', '2018-05-26', 11900.00, '王五', '2018-05-28'),
('zy2018002', '112201002', 'y003', 11000.00, '张三', '2018-05-01', '2018-05-04', '2018-05-23', '作业公司作业二队', '检泵', 6000.00, 1500.00, 1000.00, 2400.00, 10900.00, '李四', '2018-05-26', 10900.00, '王五', '2018-05-28'),
('zy2018003', '112201002', 's001', 10500.00, '张三', '2018-05-01', '2018-05-06', '2018-05-23', '作业公司作业二队', '调剖', 6500.00, 2000.00, 500.00, 1400.00, 10400.00, '李四', '2018-05-26', 10400.00, '王五', '2018-05-28'),
('zy2018004', '112202001', 's002', 12000.00, '张三', '2018-05-01', '2018-05-04', '2018-05-24', '作业公司作业三队', '解堵', 6000.00, 2000.00, 1000.00, 1600.00, 10600.00, '李四', '2018-05-26', 10600.00, '赵六', '2018-05-28'),
('zy2018005', '112202002', 'y005', 12000.00, '张三', '2018-05-01', '2018-05-04', '2018-05-28', '作业公司作业三队', '防砂', 7000.00, 1000.00, 2000.00, 1300.00, 11300.00, '李四', '2018-06-01', NULL, NULL, NULL);

INSERT INTO material_detail (BillNo, MaterialCode, Quantity, Price, Amount) VALUES
('zy2018001', 'wm001', 200, 10, 2000),
('zy2018001', 'wm002', 200, 10, 2000),
('zy2018001', 'wm003', 200, 10, 2000),
('zy2018001', 'wm004', 100, 10, 1000),
('zy2018002', 'wm001', 200, 10, 2000),
('zy2018002', 'wm002', 200, 10, 2000),
('zy2018002', 'wm003', 200, 10, 2000),
('zy2018003', 'wm001', 200, 10, 2000),
('zy2018003', 'wm002', 200, 10, 2000),
('zy2018003', 'wm003', 250, 10, 2500),
('zy2018004', 'wm001', 200, 10, 2000),
('zy2018004', 'wm002', 200, 10, 2000),
('zy2018004', 'wm004', 200, 10, 2000),
('zy2018005', 'wm001', 200, 10, 2000),
('zy2018005', 'wm002', 200, 10, 2000),
('zy2018005', 'wm004', 300, 10, 3000);

/* =====================================================
   四、索引建立
   来源：实验三索引练习，并补充常用连接字段索引
   ===================================================== */

CREATE INDEX idx_BudgetDate ON project(BudgetDate);
CREATE INDEX idx_SettlementDate ON project(SettlementDate);
CREATE INDEX idx_AccountDate ON project(AccountDate);
CREATE INDEX idx_project_budget_dept ON project(BudgetDept);
CREATE INDEX idx_project_well_no ON project(WellNo);
CREATE INDEX idx_well_dept_code ON well(DeptCode);
CREATE INDEX idx_material_detail_bill_no ON material_detail(BillNo);
CREATE INDEX idx_material_detail_material_code ON material_detail(MaterialCode);

/* =====================================================
   五、月度结算汇总表
   来源：实验三 monthly_settlement；实验四增加 Remark 和复合主键
   ===================================================== */

CREATE TABLE monthly_settlement (
    CompanyName VARCHAR(100) COMMENT '施工单位',
    YearMonth VARCHAR(10) COMMENT '年月',
    TotalSettlementAmount DECIMAL(12, 2) COMMENT '结算金额',
    Remark VARCHAR(255) COMMENT '备注',
    PRIMARY KEY (CompanyName, YearMonth)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO monthly_settlement (CompanyName, YearMonth, TotalSettlementAmount)
SELECT CompanyName, DATE_FORMAT(SettlementDate, '%Y-%m'), SUM(SettlementAmount)
FROM project
WHERE SettlementDate IS NOT NULL
GROUP BY CompanyName, DATE_FORMAT(SettlementDate, '%Y-%m');

/* =====================================================
   六、视图建立
   来源：实验四视图练习、实验六安全视图练习
   ===================================================== */

CREATE OR REPLACE VIEW v_project_material AS
SELECT
    p.*,
    md.DetailID,
    md.MaterialCode,
    m.MaterialName,
    m.UnitName,
    md.Quantity,
    md.Price AS DetailPrice,
    md.Amount
FROM project p
JOIN material_detail md ON p.BillNo = md.BillNo
LEFT JOIN material m ON md.MaterialCode = m.MaterialCode;

CREATE OR REPLACE VIEW v_budget_status AS
SELECT
    BillNo,
    BudgetDept,
    WellNo,
    BudgetAmount,
    BudgetPerson,
    BudgetDate
FROM project;

CREATE OR REPLACE VIEW v_mine1_projects AS
SELECT
    p.*
FROM project p
WHERE p.BudgetDept LIKE '112201%';

/* =====================================================
   七、事务存储过程
   来源：实验五 sp_insert_transaction
   ===================================================== */

DROP PROCEDURE IF EXISTS sp_insert_transaction;
DELIMITER //
CREATE PROCEDURE sp_insert_transaction()
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT '插入失败，发生错误，已做回退处理！' AS 处理结果;
    END;

    START TRANSACTION;

    INSERT INTO project VALUES ('zy2018006', '112202002', 'y005', 10000, '张三', '2018-07-01', '2018-07-04', '2018-07-25', '作业公司作业一队', '堵漏', 7000, 2500, 1000, 1400, 11900, '李四', '2018-07-26', 11900, '王五', '2018-07-28');
    INSERT INTO material_detail (BillNo, MaterialCode, Quantity, Price) VALUES ('zy2018006', 'wm001', 200, 10);
    INSERT INTO material_detail (BillNo, MaterialCode, Quantity, Price) VALUES ('zy2018006', 'wm002', 200, 10);
    INSERT INTO material_detail (BillNo, MaterialCode, Quantity, Price) VALUES ('zy2018006', 'wm003', 200, 10);
    INSERT INTO material_detail (BillNo, MaterialCode, Quantity, Price) VALUES ('zy2018006', 'wm004', 100, 10);

    COMMIT;
    SELECT '五条语句全部成功执行，已做提交处理！' AS 处理结果;
END //
DELIMITER ;

/* =====================================================
   八、游标存储过程
   来源：实验五 sp_cursor_print
   ===================================================== */

DROP PROCEDURE IF EXISTS sp_cursor_print;
DELIMITER //
CREATE PROCEDURE sp_cursor_print()
BEGIN
    DECLARE v_BillNo, v_BudgetDept, v_WellNo, v_BudgetPerson, v_CompanyName, v_WorkContent, v_SettlementPerson, v_AccountPerson VARCHAR(50);
    DECLARE v_BudgetAmount, v_MaterialCost, v_LaborCost, v_EquipmentCost, v_OtherCost, v_SettlementAmount, v_AccountAmount DECIMAL(12,2);
    DECLARE v_BudgetDate, v_StartDate, v_EndDate, v_SettlementDate, v_AccountDate DATE;
    DECLARE done INT DEFAULT 0;

    DECLARE cur_project CURSOR FOR SELECT * FROM project;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    DROP TEMPORARY TABLE IF EXISTS temp_print_output;
    CREATE TEMPORARY TABLE temp_print_output (PrintLine VARCHAR(1000));

    INSERT INTO temp_print_output VALUES ('单据号 | 预算单位 | 井号 | 预算金额 | 预算人 | 预算日期 | 开工日期 | 完工日期 | 施工单位 | 施工内容 | 材料费 | 人工费 | 设备费 | 其它费用 | 结算金额 | 结算人 | 结算日期 | 入账金额 | 入账人 | 入账日期');
    INSERT INTO temp_print_output VALUES ('-------------------------------------------------------------------------------------------------------------------------');

    OPEN cur_project;
    read_loop: LOOP
        FETCH cur_project INTO v_BillNo, v_BudgetDept, v_WellNo, v_BudgetAmount, v_BudgetPerson, v_BudgetDate, v_StartDate, v_EndDate, v_CompanyName, v_WorkContent, v_MaterialCost, v_LaborCost, v_EquipmentCost, v_OtherCost, v_SettlementAmount, v_SettlementPerson, v_SettlementDate, v_AccountAmount, v_AccountPerson, v_AccountDate;
        IF done THEN
            LEAVE read_loop;
        END IF;

        INSERT INTO temp_print_output VALUES (
            CONCAT_WS(' | ', v_BillNo, v_BudgetDept, v_WellNo,
                IFNULL(v_BudgetAmount,''), IFNULL(v_BudgetPerson,''), IFNULL(v_BudgetDate,''),
                IFNULL(v_StartDate,''), IFNULL(v_EndDate,''), IFNULL(v_CompanyName,''),
                IFNULL(v_WorkContent,''), IFNULL(v_MaterialCost,''), IFNULL(v_LaborCost,''),
                IFNULL(v_EquipmentCost,''), IFNULL(v_OtherCost,''), IFNULL(v_SettlementAmount,''),
                IFNULL(v_SettlementPerson,''), IFNULL(v_SettlementDate,''), IFNULL(v_AccountAmount,''),
                IFNULL(v_AccountPerson,''), IFNULL(v_AccountDate,'')
            )
        );
    END LOOP;
    CLOSE cur_project;

    SELECT PrintLine AS 游标输出结果 FROM temp_print_output;
END //
DELIMITER ;

/* =====================================================
   九、成本运行情况存储过程
   来源：实验五 sp_cost_report；同时提供后端常用别名 proc_dept_cost_summary
   ===================================================== */

DROP PROCEDURE IF EXISTS sp_cost_report;
DELIMITER //
CREATE PROCEDURE sp_cost_report(IN p_DeptCode VARCHAR(50), IN p_StartDate DATE, IN p_EndDate DATE)
BEGIN
    SELECT CONCAT(p_DeptCode, ' 单位 ', p_StartDate, '---', p_EndDate, ' 成本运行情况') AS 报表标题;

    SELECT
        IFNULL(SUM(BudgetAmount), 0) AS 预算金额,
        IFNULL(SUM(SettlementAmount), 0) AS 结算金额,
        IFNULL(SUM(AccountAmount), 0) AS 入账金额,
        IFNULL(SUM(BudgetAmount), 0) - IFNULL(SUM(SettlementAmount), 0) AS 未结算金额,
        IFNULL(SUM(SettlementAmount), 0) - IFNULL(SUM(AccountAmount), 0) AS 未入账金额
    FROM project
    WHERE BudgetDept LIKE CONCAT(p_DeptCode, '%')
      AND BudgetDate BETWEEN p_StartDate AND p_EndDate;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS proc_dept_cost_summary;
DELIMITER //
CREATE PROCEDURE proc_dept_cost_summary(IN p_dept_code VARCHAR(50))
BEGIN
    SELECT
        p_dept_code AS DeptCode,
        COUNT(p.BillNo) AS ProjectCount,
        COALESCE(SUM(p.BudgetAmount), 0) AS TotalBudgetAmount,
        COALESCE(SUM(p.MaterialCost), 0) AS TotalMaterialCost,
        COALESCE(SUM(p.LaborCost), 0) AS TotalLaborCost,
        COALESCE(SUM(p.EquipmentCost), 0) AS TotalEquipmentCost,
        COALESCE(SUM(p.OtherCost), 0) AS TotalOtherCost,
        COALESCE(SUM(p.SettlementAmount), 0) AS TotalSettlementAmount,
        COALESCE(SUM(p.AccountAmount), 0) AS TotalAccountAmount
    FROM project p
    LEFT JOIN well w ON p.WellNo = w.WellNo
    WHERE p.BudgetDept = p_dept_code
       OR w.DeptCode = p_dept_code
       OR p.BudgetDept LIKE CONCAT(p_dept_code, '%')
       OR w.DeptCode LIKE CONCAT(p_dept_code, '%');
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS proc_cursor_dept_summary;
DELIMITER //
CREATE PROCEDURE proc_cursor_dept_summary()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE v_dept_code VARCHAR(50);
    DECLARE v_dept_name VARCHAR(100);

    DECLARE cur_dept CURSOR FOR
        SELECT DeptCode, DeptName FROM dept ORDER BY DeptCode;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    DROP TEMPORARY TABLE IF EXISTS temp_dept_summary;
    CREATE TEMPORARY TABLE temp_dept_summary (
        DeptCode VARCHAR(50),
        DeptName VARCHAR(100),
        ProjectCount INT,
        TotalBudgetAmount DECIMAL(12,2),
        TotalMaterialCost DECIMAL(12,2),
        TotalLaborCost DECIMAL(12,2),
        TotalEquipmentCost DECIMAL(12,2),
        TotalOtherCost DECIMAL(12,2),
        TotalSettlementAmount DECIMAL(12,2),
        TotalAccountAmount DECIMAL(12,2)
    );

    OPEN cur_dept;
    read_loop: LOOP
        FETCH cur_dept INTO v_dept_code, v_dept_name;
        IF done = 1 THEN
            LEAVE read_loop;
        END IF;

        INSERT INTO temp_dept_summary
        SELECT
            v_dept_code,
            v_dept_name,
            COUNT(p.BillNo),
            COALESCE(SUM(p.BudgetAmount), 0),
            COALESCE(SUM(p.MaterialCost), 0),
            COALESCE(SUM(p.LaborCost), 0),
            COALESCE(SUM(p.EquipmentCost), 0),
            COALESCE(SUM(p.OtherCost), 0),
            COALESCE(SUM(p.SettlementAmount), 0),
            COALESCE(SUM(p.AccountAmount), 0)
        FROM project p
        LEFT JOIN well w ON p.WellNo = w.WellNo
        WHERE p.BudgetDept = v_dept_code
           OR w.DeptCode = v_dept_code
           OR p.BudgetDept LIKE CONCAT(v_dept_code, '%')
           OR w.DeptCode LIKE CONCAT(v_dept_code, '%');
    END LOOP;
    CLOSE cur_dept;

    SELECT * FROM temp_dept_summary ORDER BY DeptCode;
END //
DELIMITER ;

/* =====================================================
   十、触发器建立
   来源：实验五作业项目插入/更新/删除触发器；结合实验二金额计算要求，补充材料明细金额触发器
   ===================================================== */

DROP TRIGGER IF EXISTS trg_material_detail_before_insert_amount;
DROP TRIGGER IF EXISTS trg_material_detail_before_update_amount;
DROP TRIGGER IF EXISTS trg_material_detail_after_insert_project_cost;
DROP TRIGGER IF EXISTS trg_material_detail_after_update_project_cost;
DROP TRIGGER IF EXISTS trg_material_detail_after_delete_project_cost;
DROP TRIGGER IF EXISTS trg_project_insert;
DROP TRIGGER IF EXISTS trg_project_update;
DROP TRIGGER IF EXISTS trg_project_delete;

DELIMITER //
CREATE TRIGGER trg_material_detail_before_insert_amount
BEFORE INSERT ON material_detail
FOR EACH ROW
BEGIN
    SET NEW.Amount = COALESCE(NEW.Quantity, 0) * COALESCE(NEW.Price, 0);
END //

CREATE TRIGGER trg_material_detail_before_update_amount
BEFORE UPDATE ON material_detail
FOR EACH ROW
BEGIN
    SET NEW.Amount = COALESCE(NEW.Quantity, 0) * COALESCE(NEW.Price, 0);
END //

CREATE TRIGGER trg_material_detail_after_insert_project_cost
AFTER INSERT ON material_detail
FOR EACH ROW
BEGIN
    UPDATE project
    SET MaterialCost = (
        SELECT COALESCE(SUM(Amount), 0)
        FROM material_detail
        WHERE BillNo = NEW.BillNo
    )
    WHERE BillNo = NEW.BillNo;
END //

CREATE TRIGGER trg_material_detail_after_update_project_cost
AFTER UPDATE ON material_detail
FOR EACH ROW
BEGIN
    UPDATE project
    SET MaterialCost = (
        SELECT COALESCE(SUM(Amount), 0)
        FROM material_detail
        WHERE BillNo = NEW.BillNo
    )
    WHERE BillNo = NEW.BillNo;
END //

CREATE TRIGGER trg_material_detail_after_delete_project_cost
AFTER DELETE ON material_detail
FOR EACH ROW
BEGIN
    UPDATE project
    SET MaterialCost = (
        SELECT COALESCE(SUM(Amount), 0)
        FROM material_detail
        WHERE BillNo = OLD.BillNo
    )
    WHERE BillNo = OLD.BillNo;
END //

CREATE TRIGGER trg_project_insert
BEFORE INSERT ON project
FOR EACH ROW
BEGIN
    SET NEW.SettlementAmount =
        COALESCE(NEW.MaterialCost, 0)
        + COALESCE(NEW.LaborCost, 0)
        + COALESCE(NEW.EquipmentCost, 0)
        + COALESCE(NEW.OtherCost, 0);
END //

CREATE TRIGGER trg_project_update
BEFORE UPDATE ON project
FOR EACH ROW
BEGIN
    SET NEW.SettlementAmount =
        COALESCE(NEW.MaterialCost, 0)
        + COALESCE(NEW.LaborCost, 0)
        + COALESCE(NEW.EquipmentCost, 0)
        + COALESCE(NEW.OtherCost, 0);
END //

CREATE TRIGGER trg_project_delete
BEFORE DELETE ON project
FOR EACH ROW
BEGIN
    DELETE FROM material_detail WHERE BillNo = OLD.BillNo;
END //
DELIMITER ;

/* =====================================================
   十一、实验六工作时间更新限制触发器（可选）
   说明：该触发器会限制非工作时间更新 project 表。
   如需验证实验六“只能在工作时间更新作业项目表”，取消注释执行。
   注意：启用后，如果当前不是周一至周五 09:00-18:00，后端更新项目费用会被拒绝。
   ===================================================== */

/*
DROP TRIGGER IF EXISTS trg_project_update_time_restrict;
DELIMITER //
CREATE TRIGGER trg_project_update_time_restrict
BEFORE UPDATE ON project
FOR EACH ROW
BEGIN
    DECLARE current_hour INT;
    DECLARE current_day INT;

    SET current_hour = HOUR(NOW());
    SET current_day = DAYOFWEEK(NOW());

    IF (current_hour < 9 OR current_hour >= 18) OR (current_day = 1 OR current_day = 7) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '安全限制：只能在工作时间(周一至周五 09:00-18:00)内更新作业项目表';
    END IF;
END //
DELIMITER ;
*/

/* =====================================================
   十二、数据库安全机制：创建用户并授权
   来源：实验六用户、权限、视图查询授权、存储过程执行授权
   ===================================================== */

CREATE USER IF NOT EXISTS 'CYGLXT'@'localhost' IDENTIFIED BY '2024015937';
CREATE USER IF NOT EXISTS 'CYGLXT'@'127.0.0.1' IDENTIFIED BY '2024015937';

GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE ON zyxt.* TO 'CYGLXT'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE ON zyxt.* TO 'CYGLXT'@'127.0.0.1';

CREATE USER IF NOT EXISTS 'user11'@'localhost' IDENTIFIED BY '123456';
GRANT SELECT ON zyxt.v_mine1_projects TO 'user11'@'localhost';

CREATE USER IF NOT EXISTS 'user12'@'localhost' IDENTIFIED BY '123456';
GRANT EXECUTE ON PROCEDURE zyxt.sp_cost_report TO 'user12'@'localhost';
GRANT EXECUTE ON PROCEDURE zyxt.proc_dept_cost_summary TO 'user12'@'localhost';

FLUSH PRIVILEGES;

/* =====================================================
   十三、创建结果检查语句
   ===================================================== */

SELECT '数据库 zyxt 建立完成' AS 结果;
SHOW TABLES;

SELECT '索引检查' AS 检查项;
SHOW INDEX FROM project;
SHOW INDEX FROM material_detail;

SELECT '视图检查' AS 检查项;
SHOW FULL TABLES WHERE Table_type = 'VIEW';

SELECT '存储过程检查' AS 检查项;
SELECT ROUTINE_NAME, ROUTINE_TYPE, CREATED
FROM information_schema.ROUTINES
WHERE ROUTINE_SCHEMA = 'zyxt'
ORDER BY ROUTINE_NAME;

SELECT '触发器检查' AS 检查项;
SHOW TRIGGERS FROM zyxt;

SELECT '权限检查 CYGLXT' AS 检查项;
SHOW GRANTS FOR 'CYGLXT'@'localhost';

SELECT '调用成本统计过程示例' AS 检查项;
CALL sp_cost_report('112201002', '2018-01-01', '2018-12-31');

SELECT '调用单位成本汇总过程示例' AS 检查项;
CALL proc_dept_cost_summary('112201002');

SELECT '调用游标输出过程示例' AS 检查项;
CALL sp_cursor_print();

