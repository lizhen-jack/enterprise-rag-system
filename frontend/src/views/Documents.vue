<template>
  <div class="documents-page">
    <div class="page-actions">
      <el-button type="primary" @click="showUploadDialog = true">
        <el-icon><Upload /></el-icon>
        上传文档
      </el-button>
      <el-button @click="fetchDocuments">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="documents" v-loading="loading">
        <el-table-column prop="title" label="文档名称" min-width="200">
          <template #default="{ row }">
            <span>{{ row.title }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="file_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getFileTypeColor(row.file_type)" size="small">
              {{ row.file_type.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="file_size" label="大小" width="100">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>

        <el-table-column prop="chunk_count" label="块数" width="80" align="center">
          <template #default="{ row }">
            {{ row.chunk_count }}
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              text
              @click="viewDocument(row)"
            >
              查看
            </el-button>
            <el-button
              type="danger"
              size="small"
              text
              @click="deleteDocument(row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchDocuments"
          @current-change="fetchDocuments"
        />
      </div>
    </el-card>

    <!-- 上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传文档"
      width="500px"
    >
      <el-form :model="uploadForm" label-width="80px">
        <el-form-item label="文档文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :file-list="fileList"
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF, DOCX, TXT, MD, XLSX 格式，最大 50MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item label="标题">
          <el-input v-model="uploadForm.title" placeholder="文档标题" />
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            placeholder="文档描述（可选）"
            :rows="3"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">
          上传并索引
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDocuments, uploadDocument, deleteDocument as deleteDocApi } from '@/api'
import { Upload, Refresh } from '@element-plus/icons-vue'

const loading = ref(false)
const documents = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showUploadDialog = ref(false)
const uploading = ref(false)
const uploadRef = ref(null)
const fileList = ref([])

const uploadForm = reactive({
  title: '',
  description: ''
})

const fetchDocuments = async () => {
  loading.value = true
  try {
    const data = await getDocuments({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    })
    documents.value = data
    total.value = data.length // 简化处理，实际应从后端获取总数
  } catch (error) {
    ElMessage.error('获取文档列表失败')
  } finally {
    loading.value = false
  }
}

const handleFileChange = (file) => {
  uploadForm.title = file.name
}

const handleUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true
  try {
    const file = fileList.value[0].raw
    await uploadDocument(file, uploadForm.title, uploadForm.description)
    ElMessage.success('文档上传成功，正在索引中...')
    showUploadDialog.value = false
    fileList.value = []
    uploadForm.title = ''
    uploadForm.description = ''
    fetchDocuments()
  } catch (error) {
    ElMessage.error('文档上传失败')
  } finally {
    uploading.value = false
  }
}

const viewDocument = (doc) => {
  ElMessage.info('查看功能开发中...')
}

const deleteDocument = async (id) => {
  try {
    await ElMessageBox.confirm(
      '删除后无法恢复，确定要删除该文档吗？',
      '确认删除',
      { type: 'warning' }
    )
    await deleteDocApi(id)
    ElMessage.success('删除成功')
    fetchDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const getFileTypeColor = (type) => {
  const colors = {
    pdf: 'danger',
    docx: 'primary',
    txt: 'info',
    md: 'success',
    xlsx: 'warning'
  }
  return colors[type] || 'info'
}

const getStatusColor = (status) => {
  const colors = {
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return colors[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
.documents-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-actions {
  display: flex;
  gap: 12px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
