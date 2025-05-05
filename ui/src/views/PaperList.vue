<template>
  <div class="container">
    <div class="page-header">
      <h1>{{ formattedDate }} 论文推荐</h1>
      <el-button type="primary" @click="refreshPapers">刷新数据</el-button>
    </div>
    
    <el-skeleton :rows="5" animated v-if="loading" />
    
    <div v-else-if="error" class="error-container">
      <el-empty description="加载数据失败">
        <template #description>
          <p>{{ error }}</p>
        </template>
        <el-button type="primary" @click="refreshPapers">重试</el-button>
      </el-empty>
    </div>
    
    <div v-else-if="!papers || Object.keys(papers).length === 0" class="empty-container">
      <el-empty description="暂无论文数据">
        <el-button type="primary" @click="refreshPapers">刷新</el-button>
      </el-empty>
    </div>
    
    <div v-else>
      <div v-for="(paperList, keyword) in papers" :key="keyword">
        <h2 class="keyword-title">{{ keyword }}</h2>
        
        <el-card 
          v-for="paper in paperList" 
          :key="paper.id" 
          class="paper-card"
          shadow="hover"
        >
          <template #header>
            <div class="card-header">
              <h3>{{ paper.title }}</h3>
              <div class="paper-meta">
                <span>{{ formatDate(paper.date) }}</span>
              </div>
            </div>
          </template>
          
          <div class="paper-content">
            <p class="paper-abstract">{{ paper.abstract }}</p>
            
            <div class="paper-actions">
              <div>
                <el-button 
                  v-if="paper.link" 
                  type="primary" 
                  size="small" 
                  @click="openLink(paper.link)"
                >
                  查看原文
                </el-button>
                <el-button 
                  type="success" 
                  size="small" 
                  @click="toggleDifyChatbot(paper)"
                >
                  跟机器人聊聊
                </el-button>
              </div>
              <el-tag size="small" effect="plain">{{ paper.keyword }}</el-tag>
            </div>
            
            <!-- Dify聊天机器人组件 -->
            <DifyChatbot 
              v-if="activePaper === paper.id"
              :paper-title="paper.title"
              :paper-abstract="paper.abstract"
              :visible="true"
            />
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import DifyChatbot from '../components/DifyChatbot.vue';

const papers = ref({});
const loading = ref(true);
const error = ref(null);
const currentDate = ref(null);
const activePaper = ref(null); // 当前激活的论文ID

const formattedDate = computed(() => {
  if (!currentDate.value) return '今日';
  const date = new Date(currentDate.value);
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
});

function formatDate(dateStr) {
  const date = new Date(dateStr);
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
}

function openLink(link) {
  window.open(link, '_blank');
}

function toggleDifyChatbot(paper) {
  // 如果当前论文已经激活，则关闭聊天机器人
  if (activePaper.value === paper.id) {
    activePaper.value = null;
  } else {
    // 否则激活当前论文的聊天机器人
    activePaper.value = paper.id;
    
    // 显示提示消息
    ElMessage({
      message: '聊天机器人已加载，可以开始提问关于这篇论文的问题',
      type: 'success',
      duration: 3000
    });
  }
}

async function fetchPapers() {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await axios.get('/api/papers/latest');
    const papersData = response.data?.papers || {};
    
    // 处理论文数据，添加ID
    Object.keys(papersData).forEach(keyword => {
      papersData[keyword].forEach((paper, index) => {
        // 添加唯一ID
        paper.id = `${keyword}-${index}-${Date.now()}`;
      });
    });
    
    papers.value = papersData;
    currentDate.value = response.data?.date || '';
  } catch (err) {
    console.error('获取论文失败:', err);
    error.value = err.response?.data?.error || '获取论文数据失败，请稍后重试';
    papers.value = {};
  } finally {
    loading.value = false;
  }
}

function refreshPapers() {
  fetchPapers();
}

onMounted(() => {
  fetchPapers();
});
</script>

<style scoped>
.card-header {
  display: flex;
  flex-direction: column;
}

.card-header h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.paper-meta {
  font-size: 14px;
  color: var(--text-color-secondary);
}

.paper-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.paper-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
}

.error-container, .empty-container {
  padding: 60px 0;
  text-align: center;
}

.summary-title {
  font-weight: 500;
  color: var(--primary-color);
}

.summary-content {
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 4px;
  line-height: 1.6;
  text-align: justify;
  white-space: pre-line;
}

.summary-message {
  min-width: 300px;
}
</style>