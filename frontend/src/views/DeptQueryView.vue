<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getDepts, getDeptOverview } from '@/api'
import { formatCurrency } from '@/utils/format'

const loading = ref(false)
const deptCode = ref('')
const deptOptions = ref([])
const overview = ref(null)

async function loadDepts() {
  try {
    const { data } = await getDepts()
    deptOptions.value = data.data
  } catch (error) {
    ElMessage.error(error.userMessage || '加载单位列表失败')
  }
}

async function handleQuery() {
  if (!deptCode.value.trim()) {
    ElMessage.warning('请输入或选择单位代码')
    return
  }

  loading.value = true
  overview.value = null
  try {
    const { data } = await getDeptOverview(deptCode.value.trim())
    overview.value = data.data
    ElMessage.success('查询成功')
  } catch (error) {
    ElMessage.error(error.userMessage || '查询失败')
  } finally {
    loading.value = false
  }
}

function selectDept(code) {
  deptCode.value = code
  handleQuery()
}

onMounted(loadDepts)
</script>

<template>
  <div v-loading="loading" class="page">
    <el-card shadow="never" class="search-card">
      <el-form inline @submit.prevent="handleQuery">
        <el-form-item label="单位代码">
          <el-select
            v-model="deptCode"
            filterable
            allow-create
            default-first-option
            placeholder="输入或选择单位代码"
            style="width: 280px"
          >
            <el-option
              v-for="item in deptOptions"
              :key="item.DeptCode"
              :label="`${item.DeptCode} - ${item.DeptName}`"
              :value="item.DeptCode"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" :loading="loading" @click="handleQuery">
            查询
          </el-button>
        </el-form-item>
      </el-form>

      <div class="quick-tags">
        <span class="quick-label">快速选择：</span>
        <el-tag
          v-for="item in deptOptions.slice(0, 6)"
          :key="item.DeptCode"
          class="quick-tag"
          effect="plain"
          @click="selectDept(item.DeptCode)"
        >
          {{ item.DeptCode }}
        </el-tag>
      </div>
    </el-card>

    <template v-if="overview">
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card shadow="never">
            <template #header>单位基本信息</template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="单位代码">{{ overview.dept.DeptCode }}</el-descriptions-item>
              <el-descriptions-item label="单位名称">{{ overview.dept.DeptName }}</el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="section-row">
        <el-col :span="24">
          <el-card shadow="never">
            <template #header>
              <div class="card-header">
                <span>成本汇总</span>
                <el-tag type="warning">核心查询结果</el-tag>
              </div>
            </template>
            <el-row :gutter="16">
              <el-col :xs="12" :sm="8" :lg="4">
                <div class="summary-item">
                  <div class="summary-value">{{ overview.cost_summary.project_count }}</div>
                  <div class="summary-label">项目数</div>
                </div>
              </el-col>
              <el-col :xs="12" :sm="8" :lg="4">
                <div class="summary-item">
                  <div class="summary-value">{{ formatCurrency(overview.cost_summary.total_budget_amount) }}</div>
                  <div class="summary-label">预算总额</div>
                </div>
              </el-col>
              <el-col :xs="12" :sm="8" :lg="4">
                <div class="summary-item">
                  <div class="summary-value">{{ formatCurrency(overview.cost_summary.total_material_cost) }}</div>
                  <div class="summary-label">材料费</div>
                </div>
              </el-col>
              <el-col :xs="12" :sm="8" :lg="4">
                <div class="summary-item">
                  <div class="summary-value">{{ formatCurrency(overview.cost_summary.total_labor_cost) }}</div>
                  <div class="summary-label">人工费</div>
                </div>
              </el-col>
              <el-col :xs="12" :sm="8" :lg="4">
                <div class="summary-item">
                  <div class="summary-value">{{ formatCurrency(overview.cost_summary.total_equipment_cost) }}</div>
                  <div class="summary-label">设备费</div>
                </div>
              </el-col>
              <el-col :xs="12" :sm="8" :lg="4">
                <div class="summary-item">
                  <div class="summary-value">{{ formatCurrency(overview.cost_summary.total_settlement_amount) }}</div>
                  <div class="summary-label">结算总额</div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="section-row">
        <el-col :span="24">
          <el-card shadow="never">
            <template #header>油水井列表（{{ overview.wells.length }}）</template>
            <el-table :data="overview.wells" stripe border>
              <el-table-column prop="WellNo" label="井号" width="120" />
              <el-table-column prop="WellType" label="井类型" width="120" />
              <el-table-column prop="DeptCode" label="单位代码" />
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="section-row">
        <el-col :span="24">
          <el-card shadow="never">
            <template #header>作业项目列表（{{ overview.projects.length }}）</template>
            <el-table :data="overview.projects" stripe border max-height="420">
              <el-table-column prop="BillNo" label="作业单号" width="130" fixed />
              <el-table-column prop="WellNo" label="井号" width="90" />
              <el-table-column prop="WorkContent" label="施工内容" width="120" />
              <el-table-column prop="BudgetAmount" label="预算金额" width="120">
                <template #default="{ row }">{{ formatCurrency(row.BudgetAmount) }}</template>
              </el-table-column>
              <el-table-column prop="MaterialCost" label="材料费" width="120">
                <template #default="{ row }">{{ formatCurrency(row.MaterialCost) }}</template>
              </el-table-column>
              <el-table-column prop="LaborCost" label="人工费" width="120">
                <template #default="{ row }">{{ formatCurrency(row.LaborCost) }}</template>
              </el-table-column>
              <el-table-column prop="EquipmentCost" label="设备费" width="120">
                <template #default="{ row }">{{ formatCurrency(row.EquipmentCost) }}</template>
              </el-table-column>
              <el-table-column prop="OtherCost" label="其他费用" width="120">
                <template #default="{ row }">{{ formatCurrency(row.OtherCost) }}</template>
              </el-table-column>
              <el-table-column prop="SettlementAmount" label="结算金额" width="120">
                <template #default="{ row }">{{ formatCurrency(row.SettlementAmount) }}</template>
              </el-table-column>
              <el-table-column prop="AccountAmount" label="入账金额" width="120">
                <template #default="{ row }">{{ formatCurrency(row.AccountAmount) }}</template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </template>

    <el-empty v-else description="请输入单位代码后点击查询" />
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.search-card,
.section-row {
  width: 100%;
}

.quick-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.quick-label {
  color: #909399;
  font-size: 13px;
}

.quick-tag {
  cursor: pointer;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.summary-item {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  margin-bottom: 12px;
}

.summary-value {
  font-size: 22px;
  font-weight: 700;
  color: #2563eb;
}

.summary-label {
  margin-top: 6px;
  color: #909399;
  font-size: 13px;
}
</style>
