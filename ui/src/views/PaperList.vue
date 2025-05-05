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
              <el-button 
                v-if="paper.link" 
                type="primary" 
                size="small" 
                @click="openLink(paper.link)"
              >
                查看原文
              </el-button>
              <el-tag size="small" effect="plain">{{ paper.keyword }}</el-tag>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

const papers = ref({});
const loading = ref(true);
const error = ref(null);
const currentDate = ref(null);

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

async function fetchPapers() {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await axios.get('/api/papers/latest');
    papers.value = response.data?.papers || {};
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
</style>