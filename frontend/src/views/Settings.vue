<template>
  <div class="settings-page">
    <el-card shadow="never">
      <template #header>
        <span>系统设置</span>
      </template>

      <el-form label-width="120px" style="max-width: 600px">
        <el-form-item label="系统名称">
          <el-input v-model="settings.appName" />
        </el-form-item>

        <el-form-item label="AI模型">
          <el-select v-model="settings.aiModel">
            <el-option label="通义千问 Plus" value="qwen-plus" />
            <el-option label="通义千问 Turbo" value="qwen-turbo" />
            <el-option label="文心一言" value="ernie-bot" />
          </el-select>
        </el-form-item>

        <el-form-item label="RAG参数">
          <el-input-number
            v-model="settings.topK"
            :min="3"
            :max="20"
          />
          <span style="margin-left: 8px; color: #666">检索返回结果数量</span>
        </el-form-item>

        <el-form-item label="记忆保留">
          <el-input-number
            v-model="settings.memoryDays"
            :min="7"
            :max="365"
          />
          <span style="margin-left: 8px; color: #666">天</span>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
          <el-button @click="resetSettings">重置为默认</el-button>
        </el-form-item>
      </el-form>

      <el-divider />

      <div class="system-info">
        <h3>系统信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="版本">1.0.0</el-descriptions-item>
          <el-descriptions-item label="状态">运行中</el-descriptions-item>
          <el-descriptions-item label="向量数据库">Milvus</el-descriptions-item>
          <el-descriptions-item label="AI服务">Qwen/Ernie</el-descriptions-item>
          <el-descriptions-item label="数据库">PostgreSQL</el-descriptions-item>
          <el-descriptions-item label="部署方式">Docker</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const settings = ref({
  appName: '企业级RAG系统',
  aiModel: 'qwen-plus',
  topK: 5,
  memoryDays: 90
})

const defaultSettings = {
  appName: '企业级RAG系统',
  aiModel: 'qwen-plus',
  topK: 5,
  memoryDays: 90
}

const loadSettings = () => {
  const saved = localStorage.getItem('rag_settings')
  if (saved) {
    Object.assign(settings.value, JSON.parse(saved))
  }
}

const saveSettings = () => {
  localStorage.setItem('rag_settings', JSON.stringify(settings.value))
  ElMessage.success('设置已保存')
}

const resetSettings = () => {
  Object.assign(settings.value, defaultSettings)
  localStorage.removeItem('rag_settings')
  ElMessage.info('已重置为默认设置')
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-page {
  max-width: 800px;
}

.system-info {
  margin-top: 24px;
}

.system-info h3 {
  margin-bottom: 16px;
  font-size: 16px;
  color: #333;
}
</style>
