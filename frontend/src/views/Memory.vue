<template>
  <div class="memory-page">
    <div class="page-actions">
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        添加记忆
      </el-button>
      <el-button @click="fetchMemories">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>分类筛选</span>
            </div>
          </template>
          <div class="category-list">
            <div
              v-for="cat in categories"
              :key="cat"
              class="category-item"
              :class="{ active: selectedCategory === cat }"
              @click="selectedCategory = cat; fetchMemories()"
            >
              {{ cat || '全部' }}
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="18">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>长期记忆列表</span>
              <el-input
                v-model="searchQuery"
                placeholder="检索记忆"
                style="width: 200px"
                @keydown.enter="handleRetrieve"
              >
                <template #append>
                  <el-button :icon="Search" @click="handleRetrieve" />
                </template>
              </el-input>
            </div>
          </template>

          <div class="memory-list">
            <div
              v-for="memory in memories"
              :key="memory.id"
              class="memory-card"
            >
              <div class="memory-header">
                <el-tag size="small">{{ memory.category || '未分类' }}</el-tag>
                <el-rate
                  v-model="memory.importance"
                  :max="1"
                  :step="0.1"
                  disabled
                  show-score
                />
                <span class="memory-date">{{ formatDate(memory.created_at) }}</span>
              </div>

              <div class="memory-content">
                {{ memory.content }}
              </div>

              <div class="memory-footer">
                <span>访问 {{ memory.access_count }} 次</span>
                <div class="memory-actions">
                  <el-button size="small" @click="editMemory(memory)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteMemory(memory.id)">删除</el-button>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加记忆对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加长期记忆"
      width="500px"
    >
      <el-form :model="memoryForm" label-width="80px">
        <el-form-item label="内容">
          <el-input
            v-model="memoryForm.content"
            type="textarea"
            placeholder="记忆内容"
            :rows="4"
          />
        </el-form-item>

        <el-form-item label="重要性">
          <el-slider v-model="memoryForm.importance" :max="1" :step="0.1" />
        </el-form-item>

        <el-form-item label="分类">
          <el-input v-model="memoryForm.category" placeholder="例如：工作、学习、生活" />
        </el-form-item>

        <el-form-item label="标签">
          <el-input v-model="memoryForm.tags" placeholder="逗号分隔的标签" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddMemory">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import { getMemories, addMemory, deleteMemory as deleteMemApi } from '@/api'

const memories = ref([])
const categories = ref(['全部', '工作', '学习', '生活', '项目'])
const selectedCategory = ref('全部')
const searchQuery = ref('')

const showAddDialog = ref(false)
const memoryForm = reactive({
  content: '',
  importance: 0.5,
  category: '',
  tags: ''
})

const fetchMemories = async () => {
  try {
    const params = {}
    if (selectedCategory.value !== '全部') {
      params.category = selectedCategory.value
    }
    memories.value = await getMemories(params)
  } catch (error) {
    ElMessage.error('获取记忆失败')
  }
}

const handleAddMemory = async () => {
  if (!memoryForm.content) {
    ElMessage.warning('请输入内容')
    return
  }

  try {
    await addMemory(memoryForm)
    ElMessage.success('添加成功')
    showAddDialog.value = false
    Object.assign(memoryForm, {
      content: '',
      importance: 0.5,
      category: '',
      tags: ''
    })
    fetchMemories()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const handleRetrieve = async () => {
  ElMessage.info('语义检索功能开发中...')
}

const editMemory = (memory) => {
  ElMessage.info('编辑功能开发中...')
}

const deleteMemory = async (id) => {
  try {
    await deleteMemApi(id)
    ElMessage.success('删除成功')
    fetchMemories()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchMemories()
})
</script>

<style scoped>
.memory-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-actions {
  display: flex;
  gap: 12px;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-item {
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.category-item:hover {
  background: #f5f5f5;
}

.category-item.active {
  background: #e6f7ff;
  color: #1890ff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.memory-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.memory-card {
  padding: 16px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  transition: all 0.3s;
}

.memory-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.memory-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.memory-date {
  margin-left: auto;
  font-size: 12px;
  color: #999;
}

.memory-content {
  padding: 12px;
  background: #f9f9f9;
  border-radius: 4px;
  line-height: 1.6;
  margin-bottom: 8px;
}

.memory-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #999;
}

.memory-actions {
  display: flex;
  gap: 8px;
}
</style>
