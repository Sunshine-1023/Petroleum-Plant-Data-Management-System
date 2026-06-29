<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getProjectMaterialView } from '@/api'
import { formatCurrency } from '@/utils/format'

const loading = ref(false)
const tableData = ref([])
const filterBillNo = ref('')
const page = ref(1)
const pageSize = ref(12)

async function loadData() {
  loading.value = true
  try {
    const { data } = await getProjectMaterialView()
    tableData.value = data.data
    page.value = 1
  } catch (error) {
    ElMessage.error(error.userMessage || '视图查询失败')
  } finally {
    loading.value = false
  }
}

const displayData = computed(() => {
  if (!filterBillNo.value.trim()) return tableData.value
  return tableData.value.filter((row) => row.BillNo.includes(filterBillNo.value.trim()))
})

const pagedData = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return displayData.value.slice(start, start + pageSize.value)
})

onMounted(loadData)
</script>

<template>
  <div class="page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <div>
            <span>项目材料综合视图</span>
            <el-tag type="info" class="view-tag">v_project_material</el-tag>
          </div>
          <el-button type="primary" :icon="Refresh" :loading="loading" @click="loadData">
            刷新
          </el-button>
        </div>
      </template>

      <el-alert
        title="本页面查询视图 v_project_material，封装 project、material_detail、material 等表的多表连接结果"
        type="info"
        :closable="false"
        show-icon
        class="tip"
      />

      <div class="toolbar">
        <el-input
          v-model="filterBillNo"
          placeholder="按作业单号筛选"
          clearable
          style="width: 240px"
        />
        <span class="count">共 {{ displayData.length }} 条</span>
      </div>

      <el-table
        v-loading="loading"
        :data="pagedData"
        stripe
        border
        max-height="520"
        style="width: 100%"
      >
        <el-table-column prop="BillNo" label="作业单号" width="130" fixed />
        <el-table-column prop="BudgetDept" label="预算单位" width="120" />
        <el-table-column prop="WellNo" label="井号" width="90" />
        <el-table-column prop="WorkContent" label="施工内容" width="120" />
        <el-table-column prop="BudgetAmount" label="预算金额" width="120">
          <template #default="{ row }">{{ formatCurrency(row.BudgetAmount) }}</template>
        </el-table-column>
        <el-table-column prop="MaterialCost" label="材料费" width="120">
          <template #default="{ row }">{{ formatCurrency(row.MaterialCost) }}</template>
        </el-table-column>
        <el-table-column prop="DetailID" label="明细ID" width="90" />
        <el-table-column prop="MaterialCode" label="材料编码" width="110" />
        <el-table-column prop="Quantity" label="数量" width="90" />
        <el-table-column prop="Price" label="单价" width="90" />
        <el-table-column prop="Amount" label="金额" width="120">
          <template #default="{ row }">{{ formatCurrency(row.Amount) }}</template>
        </el-table-column>
      </el-table>

      <div class="pager">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="displayData.length"
          :page-sizes="[12, 24, 48]"
          background
          layout="total, sizes, prev, pager, next"
        />
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.view-tag {
  margin-left: 10px;
}

.tip {
  margin-bottom: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.count {
  color: #909399;
  font-size: 13px;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}
</style>
