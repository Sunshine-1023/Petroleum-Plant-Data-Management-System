-- 采油厂油水井作业成本管理系统 - 高级数据库对象
-- 包含：索引、存储过程、触发器、用户权限
-- 本脚本可重复执行（幂等）：对象已存在时会先删除再创建，或跳过已存在项

USE zyxt;

-- ============================================================
-- 1. 索引（DROP IF EXISTS + CREATE，可重复执行）
-- ============================================================
DROP INDEX IF EXISTS idx_project_budget_dept ON project;
CREATE INDEX idx_project_budget_dept ON project(BudgetDept);

DROP INDEX IF EXISTS idx_project_well_no ON project;
CREATE INDEX idx_project_well_no ON project(WellNo);

DROP INDEX IF EXISTS idx_well_dept_code ON well;
CREATE INDEX idx_well_dept_code ON well(DeptCode);

DROP INDEX IF EXISTS idx_material_detail_bill_no ON material_detail;
CREATE INDEX idx_material_detail_bill_no ON material_detail(BillNo);

-- ============================================================
-- 2. 修复历史数据：材料明细 Amount 为空时补算
-- ============================================================
UPDATE material_detail
SET Amount = Quantity * Price
WHERE Amount IS NULL;

-- ============================================================
-- 3. 存储过程：按单位代码统计作业成本
-- ============================================================
DROP PROCEDURE IF EXISTS sp_dept_cost_summary;
DELIMITER //
CREATE PROCEDURE sp_dept_cost_summary(IN p_DeptCode VARCHAR(50))
BEGIN
    SELECT
        p_DeptCode AS DeptCode,
        COUNT(*) AS project_count,
        IFNULL(SUM(BudgetAmount), 0) AS total_budget_amount,
        IFNULL(SUM(SettlementAmount), 0) AS total_settlement_amount,
        IFNULL(SUM(AccountAmount), 0) AS total_account_amount
    FROM project
    WHERE BudgetDept = p_DeptCode;
END //
DELIMITER ;

-- ============================================================
-- 4. 存储过程：游标遍历各部门统计
-- ============================================================
DROP PROCEDURE IF EXISTS sp_dept_summary_cursor;
DELIMITER //
CREATE PROCEDURE sp_dept_summary_cursor()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_DeptCode VARCHAR(50);
    DECLARE v_DeptName VARCHAR(100);
    DECLARE v_count INT DEFAULT 0;
    DECLARE v_budget DECIMAL(12, 2) DEFAULT 0;

    DECLARE cur_dept CURSOR FOR
        SELECT DeptCode, DeptName FROM dept ORDER BY DeptCode;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    DROP TEMPORARY TABLE IF EXISTS tmp_dept_summary;
    CREATE TEMPORARY TABLE tmp_dept_summary (
        DeptCode VARCHAR(50),
        DeptName VARCHAR(100),
        project_count INT,
        total_budget_amount DECIMAL(12, 2)
    );

    OPEN cur_dept;
    read_loop: LOOP
        FETCH cur_dept INTO v_DeptCode, v_DeptName;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SELECT COUNT(*), IFNULL(SUM(BudgetAmount), 0)
        INTO v_count, v_budget
        FROM project
        WHERE BudgetDept = v_DeptCode;

        INSERT INTO tmp_dept_summary (DeptCode, DeptName, project_count, total_budget_amount)
        VALUES (v_DeptCode, v_DeptName, v_count, v_budget);
    END LOOP;
    CLOSE cur_dept;

    SELECT * FROM tmp_dept_summary ORDER BY DeptCode;
END //
DELIMITER ;

-- ============================================================
-- 5. 触发器：材料明细自动计算金额
-- ============================================================
DROP TRIGGER IF EXISTS trg_material_detail_calc_amount;
DELIMITER //
CREATE TRIGGER trg_material_detail_calc_amount
BEFORE INSERT ON material_detail
FOR EACH ROW
BEGIN
    SET NEW.Amount = NEW.Quantity * NEW.Price;
END //
DELIMITER ;

DROP TRIGGER IF EXISTS trg_material_detail_calc_amount_upd;
DELIMITER //
CREATE TRIGGER trg_material_detail_calc_amount_upd
BEFORE UPDATE ON material_detail
FOR EACH ROW
BEGIN
    SET NEW.Amount = NEW.Quantity * NEW.Price;
END //
DELIMITER ;

-- ============================================================
-- 6. 触发器：材料明细变化时自动更新项目材料费
-- ============================================================
DROP TRIGGER IF EXISTS trg_material_detail_update_project_cost;
DELIMITER //
CREATE TRIGGER trg_material_detail_update_project_cost
AFTER INSERT ON material_detail
FOR EACH ROW
BEGIN
    UPDATE project
    SET MaterialCost = (
        SELECT IFNULL(SUM(Amount), 0) FROM material_detail WHERE BillNo = NEW.BillNo
    )
    WHERE BillNo = NEW.BillNo;
END //
DELIMITER ;

DROP TRIGGER IF EXISTS trg_material_detail_update_project_cost_upd;
DELIMITER //
CREATE TRIGGER trg_material_detail_update_project_cost_upd
AFTER UPDATE ON material_detail
FOR EACH ROW
BEGIN
    UPDATE project
    SET MaterialCost = (
        SELECT IFNULL(SUM(Amount), 0) FROM material_detail WHERE BillNo = NEW.BillNo
    )
    WHERE BillNo = NEW.BillNo;
END //
DELIMITER ;

DROP TRIGGER IF EXISTS trg_material_detail_update_project_cost_del;
DELIMITER //
CREATE TRIGGER trg_material_detail_update_project_cost_del
AFTER DELETE ON material_detail
FOR EACH ROW
BEGIN
    UPDATE project
    SET MaterialCost = (
        SELECT IFNULL(SUM(Amount), 0) FROM material_detail WHERE BillNo = OLD.BillNo
    )
    WHERE BillNo = OLD.BillNo;
END //
DELIMITER ;

-- ============================================================
-- 7. 用户权限（可重复执行）
-- ============================================================
CREATE USER IF NOT EXISTS 'CYGLXT'@'localhost' IDENTIFIED BY '2024015937';
GRANT SELECT, INSERT, UPDATE, DELETE ON zyxt.* TO 'CYGLXT'@'localhost';
FLUSH PRIVILEGES;
