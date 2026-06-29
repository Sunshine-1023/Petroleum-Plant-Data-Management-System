<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getDeptCostProcedure,
  getCursorDeptSummary,
  createProjectWithMaterials,
} from '@/api'

const loading = reactive({
  procedure: false,
  transaction: false,
  trigger: false,
  cursor: false,
})

const deptCode = ref('112201001')
const procedureResult = ref(null)
const cursorResult = ref(null)
const transactionResult = ref(null)
const triggerResult = ref(null)

async function runProcedure() {
  loading.procedure = true
  procedureResult.value = null
  try {
    const { data } = await getDeptCostProcedure(deptCode.value)
    procedureResult.value = data
    ElMessage.success('存储过程调用成功')
  } catch (error) {
    ElMessage.error(error.userMessage || '存储过程调用失败')
  } finally {
    loading.procedure = false
  }
}

async function runCursor() {
  loading.cursor = true
  cursorResult.value = null
  try {
    const { data } = await getCursorDeptSummary()
    cursorResult.value = data
    ElMessage.success('游标统计完成')
  } catch (error) {
    ElMessage.error(error.userMessage || '游标统计失败')
  } finally {
    loading.cursor = false
  }
}

async function runTransaction() {
  loading.transaction = true
  transactionResult.value = null
  const billNo = `zytest${Date.now().toString().slice(-6)}`
  try {
    const { data } = await createProjectWithMaterials({
      project: {
        BillNo: billNo,
        BudgetDept: '112201001',
        WellNo: 'y001',
        BudgetAmount: 8000,
        BudgetPerson: '前端测试',
        BudgetDate: '2018-06-01',
        StartDate: '2018-06-02',
        EndDate: '2018-06-10',
        CompanyName: '作业公司作业一队',
        WorkContent: '事务演示作业',
        LaborCost: 1200,
        EquipmentCost: 600,
        OtherCost: 300,
      },
      materials: [
        { MaterialCode: 'wm001', Quantity: 20, Price: 15 },
        { MaterialCode: 'wm002', Quantity: 10, Price: 25 },
      ],
    })
    transactionResult.value = data
    ElMessage.success('事务提交成功')
  } catch (error) {
    ElMessage.error(error.userMessage || '事务执行失败')
  } finally {
    loading.transaction = false
  }
}

async function runTriggerDemo() {
  loading.trigger = true
  triggerResult.value = null
  const billNo = `zytrg${Date.now().toString().slice(-6)}`
  try {
    const { data } = await createProjectWithMaterials({
      project: {
        BillNo: billNo,
        BudgetDept: '112201001',
        WellNo: 'y001',
        BudgetAmount: 3000,
        BudgetPerson: '触发器测试',
        BudgetDate: '2018-06-01',
        StartDate: '2018-06-02',
        EndDate: '2018-06-08',
        CompanyName: '作业公司作业一队',
        WorkContent: '触发器演示',
        LaborCost: 500,
        EquipmentCost: 200,
        OtherCost: 100,
      },
      materials: [
        { MaterialCode: 'wm001', Quantity: 8, Price: 50 },
        { MaterialCode: 'wm003', Quantity: 4, Price: 80 },
      ],
    })
    triggerResult.value = {
      message: '触发器效果：material_detail.Amount 自动 = Quantity × Price；project.MaterialCost 自动汇总材料明细',
      data: data.data,
      expectedMaterialCost: data.data.materials.reduce((sum, item) => sum + item.Amount, 0),
    }
    ElMessage.success('触发器演示完成，请查看材料 Amount 与 MaterialCost')
  } catch (error) {
    ElMessage.error(error.userMessage || '触发器演示失败')
  } finally {
    loading.trigger = false
  }
}
</script>

<template>
  <div class="page">
    <el-row :gutter="20">
      <el-col :xs="24" :md="12" :lg="6">
        <el-card shadow="hover" class="demo-card">
          <div class="demo-icon procedure">SP</div>
          <h3>存储过程</h3>
          <p>调用 sp_dept_cost_summary 统计单位作业成本</p>
          <el-input v-model="deptCode" placeholder="单位代码" class="demo-input" />
          <el-button type="primary" :loading="loading.procedure" @click="runProcedure">
            调用存储过程
          </el-button>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12" :lg="6">
        <el-card shadow="hover" class="demo-card">
          <div class="demo-icon transaction">TX</div>
          <h3>事务</h3>
          <p>新增作业项目 + 材料明细，失败则整体回滚</p>
          <el-button type="success" :loading="loading.transaction" @click="runTransaction">
            执行事务新增
          </el-button>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12" :lg="6">
        <el-card shadow="hover" class="demo-card">
          <div class="demo-icon trigger">TR</div>
          <h3>触发器</h3>
          <p>插入材料明细时自动计算 Amount 并更新 MaterialCost</p>
          <el-button type="warning" :loading="loading.trigger" @click="runTriggerDemo">
            查看触发器效果
          </el-button>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12" :lg="6">
        <el-card shadow="hover" class="demo-card">
          <div class="demo-icon cursor">CR</div>
          <h3>游标</h3>
          <p>遍历所有部门，统计各部门项目数与预算总额</p>
          <el-button type="info" :loading="loading.cursor" @click="runCursor">
            执行游标统计
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="result-row">
      <el-col :span="24">
        <el-card shadow="never">
          <template #header>执行结果</template>

          <el-tabs>
            <el-tab-pane label="存储过程">
              <el-table v-if="procedureResult" :data="procedureResult.data" border stripe>
                <el-table-column prop="DeptCode" label="单位代码" />
                <el-table-column prop="project_count" label="项目数" />
                <el-table-column prop="total_budget_amount" label="预算总额" />
                <el-table-column prop="total_settlement_amount" label="结算总额" />
                <el-table-column prop="total_account_amount" label="入账总额" />
              </el-table>
              <el-empty v-else description="点击「调用存储过程」查看结果" />
            </el-tab-pane>

            <el-tab-pane label="事务">
              <pre v-if="transactionResult" class="json-box">{{ JSON.stringify(transactionResult, null, 2) }}</pre>
              <el-empty v-else description="点击「执行事务新增」查看结果" />
            </el-tab-pane>

            <el-tab-pane label="触发器">
              <template v-if="triggerResult">
                <el-alert :title="triggerResult.message" type="success" :closable="false" show-icon />
                <p class="trigger-check">
                  材料明细 Amount 合计：{{ triggerResult.expectedMaterialCost }}，
                  项目 MaterialCost：{{ triggerResult.data.project.MaterialCost }}
                  <el-tag
                    :type="triggerResult.expectedMaterialCost === triggerResult.data.project.MaterialCost ? 'success' : 'warning'"
                    size="small"
                  >
                    {{ triggerResult.expectedMaterialCost === triggerResult.data.project.MaterialCost ? '触发器生效' : '需执行 SQL 补建触发器' }}
                  </el-tag>
                </p>
                <pre class="json-box">{{ JSON.stringify(triggerResult.data, null, 2) }}</pre>
              </template>
              <el-empty v-else description="点击「查看触发器效果」查看结果" />
            </el-tab-pane>

            <el-tab-pane label="游标">
              <el-table v-if="cursorResult" :data="cursorResult.data" border stripe max-height="400">
                <el-table-column prop="DeptCode" label="单位代码" />
                <el-table-column prop="DeptName" label="单位名称" />
                <el-table-column prop="project_count" label="项目数" />
                <el-table-column prop="total_budget_amount" label="预算总额" />
              </el-table>
              <el-empty v-else description="点击「执行游标统计」查看结果" />
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.demo-card {
  text-align: center;
  min-height: 260px;
  border-radius: 14px;
}

.demo-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  margin: 0 auto 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
}

.procedure { background: #409eff; }
.transaction { background: #67c23a; }
.trigger { background: #e6a23c; }
.cursor { background: #909399; }

.demo-card h3 {
  margin: 0 0 8px;
}

.demo-card p {
  color: #909399;
  font-size: 13px;
  min-height: 40px;
  line-height: 1.5;
}

.demo-input {
  margin-bottom: 12px;
}

.result-row {
  margin-top: 4px;
}

.json-box {
  background: #1e293b;
  color: #e2e8f0;
  padding: 16px;
  border-radius: 10px;
  overflow: auto;
  max-height: 360px;
  font-size: 12px;
}

.trigger-check {
  margin: 12px 0;
  color: #606266;
}
</style>
