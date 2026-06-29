<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { OfficeBuilding, Odometer, Box, Document } from '@element-plus/icons-vue'
import { getDbTest, getStats, getSystemStatus } from '@/api'
import { formatNumber } from '@/utils/format'

const loading = ref(false)
const stats = ref({
  dept_count: 0,
  well_count: 0,
  project_count: 0,
  material_count: 0,
})
const dbInfo = ref(null)
const systemStatus = ref(null)

const cards = [
  { key: 'dept_count', label: '单位数量', icon: OfficeBuilding, color: '#409eff' },
  { key: 'well_count', label: '油水井数量', icon: Odometer, color: '#67c23a' },
  { key: 'project_count', label: '项目数量', icon: Document, color: '#e6a23c' },
  { key: 'material_count', label: '材料数量', icon: Box, color: '#f56c6c' },
]

const backendTagType = computed(() => (systemStatus.value?.backend === 'ok' ? 'success' : 'danger'))

async function loadData() {
  loading.value = true
  try {
    const [statsRes, dbRes, statusRes] = await Promise.all([getStats(), getDbTest(), getSystemStatus()])
    stats.value = statsRes.data.data
    dbInfo.value = dbRes.data
    systemStatus.value = statusRes.data.data
  } catch (error) {
    ElMessage.error(error.userMessage || '加载首页数据失败，请确认后端已启动')
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <div v-loading="loading" class="home">
    <el-card shadow="never" class="hero-card">
      <div class="hero-content">
        <div>
          <el-tag effect="plain" type="primary">数据库实践大作业</el-tag>
          <h2>采油厂油水井作业成本管理系统</h2>
          <p>基于 MySQL 数据库，实现单位查询、成本更新、视图查询及数据库高级特性演示。</p>
        </div>
        <div class="hero-actions">
          <el-tag :type="backendTagType" effect="dark" round>
            后端状态：{{ systemStatus?.backend || 'unknown' }}
          </el-tag>
          <el-button type="primary" size="large" round @click="loadData">刷新数据</el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20" class="stat-row">
      <el-col v-for="card in cards" :key="card.key" :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-inner">
            <div class="stat-icon" :style="{ background: card.color }">
              <el-icon size="24"><component :is="card.icon" /></el-icon>
            </div>
            <div>
              <div class="stat-value">{{ formatNumber(stats[card.key]) }}</div>
              <div class="stat-label">{{ card.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="14">
        <el-card shadow="never">
          <template #header>
            <span>数据库连接状态</span>
          </template>
          <el-descriptions v-if="dbInfo" :column="2" border>
            <el-descriptions-item label="状态">
              <el-tag type="success">{{ dbInfo.message }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="数据库">{{ dbInfo.database }}</el-descriptions-item>
            <el-descriptions-item label="数据表" :span="2">
              <el-space wrap>
                <el-tag v-for="table in dbInfo.tables" :key="table" type="info">{{ table }}</el-tag>
              </el-space>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="10">
        <el-card shadow="never">
          <template #header>
            <span>服务稳定性</span>
          </template>
          <el-descriptions v-if="systemStatus" :column="1" border>
            <el-descriptions-item label="后端健康">
              <el-tag :type="backendTagType">{{ systemStatus.backend }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="数据表数量">{{ systemStatus.table_count }}</el-descriptions-item>
            <el-descriptions-item label="存储过程数量">{{ systemStatus.procedure_count }}</el-descriptions-item>
            <el-descriptions-item label="触发器数量">{{ systemStatus.trigger_count }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hero-card {
  background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 45%, #0ea5e9 100%);
  border: none;
  color: #fff;
}

.hero-card :deep(.el-card__body) {
  padding: 28px 32px;
}

.hero-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.hero-content h2 {
  margin: 12px 0 8px;
  font-size: 28px;
}

.hero-content p {
  margin: 0;
  opacity: 0.88;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.stat-row {
  margin-top: 4px;
}

.stat-card {
  border-radius: 14px;
}

.stat-inner {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-value {
  font-size: 30px;
  font-weight: 700;
  color: #1f2d3d;
}

.stat-label {
  color: #909399;
  margin-top: 4px;
}
</style>
