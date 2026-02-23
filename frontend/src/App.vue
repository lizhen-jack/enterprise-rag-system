<template>
  <div id="app">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="240px">
        <div class="logo">
          <el-icon size="32"><Document /></el-icon>
          <h2>企业RAG</h2>
        </div>
        <el-menu
          :default-active="activeMenu"
          router
          class="sidebar-menu"
        >
          <el-menu-item index="/documents">
            <el-icon><Folder /></el-icon>
            <span>文档管理</span>
          </el-menu-item>
          <el-menu-item index="/chat">
            <el-icon><ChatDotRound /></el-icon>
            <span>智能问答</span>
          </el-menu-item>
          <el-menu-item index="/memory">
            <el-icon><Clock /></el-icon>
            <span>长期记忆</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航 -->
        <el-header>
          <div class="header-content">
            <span class="page-title">{{ pageTitle }}</span>
            <div class="user-info">
              <el-dropdown>
                <span class="user-name">
                  <el-avatar :size="32" :src="user.avatar || ''">{{ user.fullName?.[0] || 'U' }}</el-avatar>
                  <span>{{ user.fullName || user.username }}</span>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item>个人资料</el-dropdown-item>
                    <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>

        <!-- 内容区域 -->
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const user = computed(() => userStore.user)
const activeMenu = computed(() => route.path)

const pageTitleMap = {
  '/documents': '文档管理',
  '/chat': '智能问答',
  '/memory': '长期记忆',
  '/settings': '系统设置'
}

const pageTitle = computed(() => pageTitleMap[route.path] || '企业级RAG系统')

const logout = () => {
  userStore.logout()
  router.push('/login')
}

onMounted(() => {
  // 检查登录状态
  if (!userStore.token) {
    router.push('/login')
  }
})
</script>

<style scoped>
#app {
  height: 100vh;
  display: flex;
}

.el-container {
  height: 100%;
}

.el-aside {
  background: #001529;
  color: white;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  gap: 10px;
  color: white;
}

.logo h2 {
  margin: 0;
  font-size: 18px;
}

.sidebar-menu {
  border-right: none;
  background: #001529;
}

.sidebar-menu .el-menu-item {
  color: rgba(255,255,255,0.65);
}

.sidebar-menu .el-menu-item:hover {
  background: #1890ff;
  color: white;
}

.sidebar-menu .el-menu-item.is-active {
  background: #1890ff;
  color: white;
}

.el-header {
  background: white;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.user-info {
  cursor: pointer;
}

.user-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.el-main {
  background: #f0f2f5;
  padding: 20px;
}
</style>
