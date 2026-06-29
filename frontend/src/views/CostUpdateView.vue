<script setup>
import { reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProjectDetail, updateProjectCosts } from '@/api'
import { formatCurrency } from '@/utils/format'

const loading = ref(false)
const result = ref(null)

const form = reactive({
  BillNo: 'zy2018001',
  MaterialCost: 7000,
  LaborCost: 2500,
  EquipmentCost: 1000,
  OtherCost: 1400,
  SettlementAmount: 11900,
  AccountAmount: 11900,
})

function autoCalculate() {
  const sum =
    Number(form.MaterialCost || 0) +
    Number(form.LaborCost || 0) +
    Number(form.EquipmentCost || 0) +
    Number(form.OtherCost || 0)
  form.SettlementAmount = sum
  form.AccountAmount = sum
}

async function loadBillNoData() {
  if (!form.BillNo.trim()) {
    ElMessage.warning('请先输入作业单号')
    return
  }
  loading.value = true
  try {
    const { data } = await getProjectDetail(form.BillNo.trim())
    Object.assign(form, {
      BillNo: data.data.BillNo,
      MaterialCost: data.data.MaterialCost,
      LaborCost: data.data.LaborCost,
      EquipmentCost: data.data.EquipmentCost,
      OtherCost: data.data.OtherCost,
      SettlementAmount: data.data.SettlementAmount,
      AccountAmount: data.data.AccountAmount,
    })
    ElMessage.success('已加载作业单当前成本')
  } catch (error) {
    ElMessage.error(error.userMessage || '加载作业单失败')
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!form.BillNo.trim()) {
    ElMessage.warning('请输入作业单号')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认更新作业单 ${form.BillNo} 的成本数据吗？`,
      '确认更新',
      { type: 'warning' },
    )
  } catch {
    return
  }

  loading.value = true
  result.value = null
  try {
    const { data } = await updateProjectCosts(form.BillNo.trim(), {
      MaterialCost: form.MaterialCost,
      LaborCost: form.LaborCost,
      EquipmentCost: form.EquipmentCost,
      OtherCost: form.OtherCost,
      SettlementAmount: form.SettlementAmount,
      AccountAmount: form.AccountAmount,
    })
    result.value = data.data
    ElMessage.success('更新成功')
  } catch (error) {
    ElMessage.error(error.userMessage || '更新失败')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(form, {
    BillNo: 'zy2018001',
    MaterialCost: 7000,
    LaborCost: 2500,
    EquipmentCost: 1000,
    OtherCost: 1400,
    SettlementAmount: 11900,
    AccountAmount: 11900,
  })
  result.value = null
}
</script>

<template>
  <div class="page">
    <el-row :gutter="20">
      <el-col :xs="24" :lg="14">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>作业项目成本更新</span>
              <el-tag type="danger">PUT /api/projects/&lt;BillNo&gt;/costs/</el-tag>
            </div>
          </template>

          <el-alert
            title="注意：数据库触发器限制仅允许周一至周五 08:00-18:00 更新 project 表"
            type="warning"
            :closable="false"
            show-icon
            class="tip"
          />

          <el-form label-width="100px" class="form">
            <el-form-item label="作业单号">
              <el-input v-model="form.BillNo" placeholder="例如 zy2018001">
                <template #append>
                  <el-button :loading="loading" @click="loadBillNoData">加载当前值</el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="材料费">
                  <el-input-number v-model="form.MaterialCost" :min="0" :step="100" style="width: 100%" @change="autoCalculate" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="人工费">
                  <el-input-number v-model="form.LaborCost" :min="0" :step="100" style="width: 100%" @change="autoCalculate" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="设备费">
                  <el-input-number v-model="form.EquipmentCost" :min="0" :step="100" style="width: 100%" @change="autoCalculate" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="其他费用">
                  <el-input-number v-model="form.OtherCost" :min="0" :step="100" style="width: 100%" @change="autoCalculate" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="结算金额">
                  <el-input-number v-model="form.SettlementAmount" :min="0" :step="100" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="入账金额">
                  <el-input-number v-model="form.AccountAmount" :min="0" :step="100" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item>
              <el-button type="primary" :loading="loading" @click="handleSave">保存更新</el-button>
              <el-button type="success" plain @click="autoCalculate">自动计算结算/入账</el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>

          <el-alert
            type="info"
            :closable="false"
            class="tip"
            show-icon
            :title="`当前结算金额：${formatCurrency(form.SettlementAmount)}；当前入账金额：${formatCurrency(form.AccountAmount)}`"
          />
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card shadow="never">
          <template #header>更新结果对比（报告截图用）</template>

          <template v-if="result">
            <h4 class="compare-title">修改前</h4>
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item v-for="(val, key) in result.before" :key="'b-' + key" :label="key">
                {{ val }}
              </el-descriptions-item>
            </el-descriptions>

            <h4 class="compare-title">修改后</h4>
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item v-for="(val, key) in result.after" :key="'a-' + key" :label="key">
                <span class="changed">{{ val }}</span>
              </el-descriptions-item>
            </el-descriptions>
          </template>

          <el-empty v-else description="保存后将显示修改前后对比" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.page {
  width: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.tip {
  margin-bottom: 20px;
}

.form {
  margin-top: 8px;
}

.compare-title {
  margin: 16px 0 10px;
  color: #606266;
}

.changed {
  color: #67c23a;
  font-weight: 600;
}
</style>
