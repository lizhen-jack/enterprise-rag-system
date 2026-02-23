<template>
  <div class="chat-page">
    <el-row :gutter="20">
      <!-- 左侧：对话列表 -->
      <el-col :span="6">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>对话历史</span>
              <el-button type="primary" size="small" @click="newConversation">
                新建对话
              </el-button>
            </div>
          </template>

          <el-scrollbar height="calc(100vh - 250px)">
            <div
              v-for="conv in conversations"
              :key="conv.id"
              class="conversation-item"
              :class="{ active: currentConversationId === conv.id }"
              @click="selectConversation(conv.id)"
            >
              <div class="conversation-title">{{ conv.title }}</div>
              <div class="conversation-meta">
                {{ conv.message_count }} 条消息
              </div>
            </div>
          </el-scrollbar>
        </el-card>
      </el-col>

      <!-- 右侧：对话主界面 -->
      <el-col :span="18">
        <el-card shadow="never" class="chat-container">
          <el-scrollbar ref="scrollbarRef" height="calc(100vh - 320px)">
            <div class="messages-wrapper">
              <div
                v-for="msg in messages"
                :key="msg.id"
                :class="['message', msg.message_type]"
              >
                <div class="message-avatar">
                  <el-avatar v-if="msg.message_type === 'user'">
                    {{ userStore.user?.fullName?.[0] || 'U' }}
                  </el-avatar>
                  <el-avatar v-else>
                    <el-icon><ChatDotRound /></el-icon>
                  </el-avatar>
                </div>
                <div class="message-content">
                  <div class="message-text" v-html="renderMarkdown(msg.content)"></div>

                  <!-- 来源信息 -->
                  <div v-if="msg.message_type === 'assistant' && lastMessage?.sources?.length" class="message-sources">
                    <div class="sources-title">参考来源</div>
                    <el-tag
                      v-for="source in lastMessage.sources"
                      :key="source.chunk_id"
                      size="small"
                      class="source-tag"
                    >
                      {{ source.document_title }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </el-scrollbar>

          <!-- 输入区域 -->
          <div class="input-area">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="3"
              placeholder="输入你的问题..."
              @keydown.enter.ctrl.exact="handleSend"
            />
            <div class="input-actions">
              <el-switch
                v-model="useRag"
                active-text="启用文档检索"
              />
              <el-switch
                v-model="useMemory"
                active-text="启用长期记忆"
              />
              <el-button
                type="primary"
                :loading="sending"
                @click="handleSend"
              >
                发送 (Ctrl+Enter)
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound } from '@element-plus/icons-vue'
import { chat as chatApi, getConversations, getMessages } from '@/api'
import { useUserStore } from '@/stores/user'
import { marked } from 'marked'

const userStore = useUserStore()

const conversations = ref([])
const messages = ref([])
const currentConversationId = ref(null)
const inputMessage = ref('')
const sending = ref(false)
const lastMessage = ref(null)

const useRag = ref(true)
const useMemory = ref(true)

const fetchConversations = async () => {
  try {
    conversations.value = await getConversations()
    if (conversations.value.length > 0 && !currentConversationId.value) {
      currentConversationId.value = conversations.value[0].id
      fetchMessages(currentConversationId.value)
    }
  } catch (error) {
    ElMessage.error('获取对话列表失败')
  }
}

const fetchMessages = async (conversationId) => {
  currentConversationId.value = conversationId
  try {
    messages.value = await getMessages(conversationId)
  } catch (error) {
    ElMessage.error('获取消息失败')
  }
}

const newConversation = () => {
  currentConversationId.value = null
  messages.value = []
}

const selectConversation = (id) => {
  fetchMessages(id)
}

const handleSend = async () => {
  if (!inputMessage.value.trim()) return

  sending.value = true
  const userMsg = inputMessage.value
  inputMessage.value = ''

  try {
    const response = await chatApi({
      conversation_id: currentConversationId.value,
      message: userMsg,
      use_rag: useRag.value,
      use_memory: useMemory.value
    })

    lastMessage.value = response

    // 添加用户消息和AI回复
    messages.value.push({
      id: response.message_id - 1,
      content: userMsg,
      message_type: 'user',
      created_at: new Date()
    })

    messages.value.push({
      id: response.message_id,
      content: response.reply,
      message_type: 'assistant',
      created_at: new Date()
    })

    // 如果是新对话，更新对话列表
    if (!currentConversationId.value) {
      currentConversationId.value = response.conversation_id
      fetchConversations()
    }

  } catch (error) {
    ElMessage.error('发送失败')
    inputMessage.value = userMsg
  } finally {
    sending.value = false
  }
}

const renderMarkdown = (text) => {
  return marked(text)
}

onMounted(() => {
  fetchConversations()
})
</script>

<style scoped>
.chat-page {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conversation-item {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.conversation-item:hover {
  background: #f5f5f5;
}

.conversation-item.active {
  background: #e6f7ff;
  border: 1px solid #1890ff;
}

.conversation-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.conversation-meta {
  font-size: 12px;
  color: #999;
}

.chat-container {
  height: calc(100vh - 180px);
  display: flex;
  flex-direction: column;
}

.messages-wrapper {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  gap: 12px;
}

.message.assistant {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
}

.message-text {
  padding: 12px 16px;
  border-radius: 8px;
  background: #f5f5f5;
  line-height: 1.6;
}

.message.assistant .message-text {
  background: #e6f7ff;
}

.message-sources {
  margin-top: 8px;
}

.sources-title {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.source-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}

.input-area {
  padding: 16px;
  border-top: 1px solid #f0f0f0;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  gap: 12px;
}

.input-actions .el-switch {
  font-size: 14px;
}
</style>
