<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'
import { loginByDbUser } from '@/api'
import { saveAuth } from '@/utils/auth'

const route = useRoute()
const router = useRouter()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

async function handleLogin() {
  if (!form.username.trim() || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    const { data } = await loginByDbUser(form.username.trim(), form.password)
    saveAuth({
      username: data.data.username,
      database: data.data.database,
      host: data.data.host,
      port: data.data.port,
      loginAt: new Date().toISOString(),
    })
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/'
    router.replace(redirect)
  } catch (error) {
    ElMessage.error(error.userMessage || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <el-card class="login-card" shadow="hover">
      <template #header>
        <div class="header">
          <h2>采油厂油水井作业成本管理系统</h2>
          <p>请使用数据库用户名和密码登录</p>
        </div>
      </template>

      <el-form @submit.prevent="handleLogin" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" :prefix-icon="User" placeholder="例如 CYGLXT 或 root" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            :prefix-icon="Lock"
            placeholder="数据库密码"
            show-password
            type="password"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button type="primary" :loading="loading" class="login-btn" @click="handleLogin">
          登录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(135deg, #dbeafe 0%, #eff6ff 35%, #f8fafc 100%);
}

.login-card {
  width: 100%;
  max-width: 460px;
  border-radius: 14px;
}

.header h2 {
  margin: 0;
  font-size: 20px;
}

.header p {
  margin: 6px 0 0;
  color: #909399;
  font-size: 13px;
}

.login-btn {
  width: 100%;
  margin-top: 8px;
}
</style>
