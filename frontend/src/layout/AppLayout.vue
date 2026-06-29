<script setup>
import { computed } from 'vue'
import { ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import {
  House, OfficeBuilding, EditPen, View, Cpu, SwitchButton,
} from '@element-plus/icons-vue'
import { clearAuth, getAuth } from '@/utils/auth'

const route = useRoute()
const router = useRouter()

const menuItems = [
  { path: '/', label: '首页', icon: House },
  { path: '/dept-query', label: '单位查询', icon: OfficeBuilding },
  { path: '/cost-update', label: '成本更新', icon: EditPen },
  { path: '/view-query', label: '视图查询', icon: View },
  { path: '/db-demo', label: '数据库技术演示', icon: Cpu },
]

const activeMenu = computed(() => route.path)
const authInfo = computed(() => getAuth())
const currentMenu = computed(() => menuItems.find((item) => item.path === route.path))

function navigate(path) {
  router.push(path)
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确认退出登录吗？', '退出登录', { type: 'warning' })
  } catch {
    return
  }
  clearAuth()
  router.replace('/login')
}
</script>

<template>
  <el-container class="layout">
    <el-aside width="240px" class="aside">
      <div class="brand">
        <div class="brand-icon">油</div>
        <div>
          <div class="brand-title">采油厂管理系统</div>
          <div class="brand-sub">油水井作业成本</div>
        </div>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="side-menu"
        @select="navigate"
      >
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div>
          <h1 class="page-title">{{ route.meta.title }}</h1>
          <p class="page-desc">
            Vue 3 + Element Plus · Django REST · MySQL
            <span v-if="currentMenu"> / {{ currentMenu.label }}</span>
          </p>
        </div>
        <div class="header-actions">
          <el-tag type="info" effect="plain" round>
            登录用户：{{ authInfo?.username || '-' }}
          </el-tag>
          <el-tag type="info" effect="plain" round>
            数据库：{{ authInfo?.database || '-' }}
          </el-tag>
          <el-tag type="success" effect="dark" round>B/S 前后端分离</el-tag>
          <el-button type="danger" plain :icon="SwitchButton" @click="handleLogout">
            退出
          </el-button>
        </div>
      </el-header>

      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout {
  min-height: 100vh;
}

.aside {
  background: linear-gradient(180deg, #0f2744 0%, #16365c 100%);
  color: #fff;
  box-shadow: 4px 0 24px rgba(15, 39, 68, 0.15);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #409eff, #67c23a);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
}

.brand-title {
  font-size: 15px;
  font-weight: 700;
}

.brand-sub {
  font-size: 12px;
  opacity: 0.65;
  margin-top: 2px;
}

.side-menu {
  border-right: none;
  background: transparent;
  padding: 12px 8px;
}

.side-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.78);
  border-radius: 10px;
  margin-bottom: 4px;
  height: 46px;
}

.side-menu :deep(.el-menu-item:hover),
.side-menu :deep(.el-menu-item.is-active) {
  background: rgba(64, 158, 255, 0.18);
  color: #fff;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  height: 72px;
  padding: 0 28px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-title {
  margin: 0;
  font-size: 22px;
  color: #1f2d3d;
}

.page-desc {
  margin: 4px 0 0;
  font-size: 13px;
  color: #909399;
}

.main {
  background: #f4f7fb;
  padding: 24px;
  min-height: calc(100vh - 72px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
