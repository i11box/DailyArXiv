<template>
  <div class="container">
    <div class="page-header">
      <h1>配置管理</h1>
      <div class="header-actions">
        <el-button type="success" @click="saveConfig" :loading="saving">
          保存配置
        </el-button>
      </div>
    </div>
    
    <el-skeleton :rows="10" animated v-if="loading" />
    
    <div v-else-if="error" class="error-container">
      <el-empty description="加载配置失败">
        <template #description>
          <p>{{ error }}</p>
        </template>
        <el-button type="primary" @click="fetchConfig">重试</el-button>
      </el-empty>
    </div>
    
    <div v-else class="config-form">
      <el-form label-position="top" :model="config">
        <!-- 数据库配置 -->
        <el-divider content-position="left">数据库配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="数据库主机">
              <el-input v-model="config.DB_HOST" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="数据库端口">
              <el-input-number v-model="config.DB_PORT" :min="1" :max="65535" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="数据库名称">
              <el-input v-model="config.DB_NAME" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="数据库用户">
              <el-input v-model="config.DB_USER" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="数据库密码">
          <el-input v-model="config.DB_PASSWORD" show-password />
        </el-form-item>
        
        <!-- Redis配置 -->
        <el-divider content-position="left">Redis配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Redis主机">
              <el-input v-model="config.REDIS_HOST" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Redis端口">
              <el-input-number v-model="config.REDIS_PORT" :min="1" :max="65535" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 爬虫配置 -->
        <el-divider content-position="left">爬虫配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="每个关键词最大结果数">
              <el-input-number v-model="config.max_result" :min="1" :max="100" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Issue中包含的最大论文数">
              <el-input-number v-model="config.issues_result" :min="1" :max="100" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 关键词配置 -->
        <el-divider content-position="left">关键词配置</el-divider>
        <el-form-item>
          <el-tag
            v-for="(keyword, index) in config.keywords"
            :key="index"
            closable
            :disable-transitions="false"
            @close="removeKeyword(index)"
            class="keyword-tag"
          >
            {{ keyword }}
          </el-tag>
          <el-input
            v-if="inputVisible"
            ref="InputRef"
            v-model="inputValue"
            class="keyword-input"
            size="small"
            @keyup.enter="addKeyword"
            @blur="addKeyword"
          />
          <el-button v-else class="button-new-keyword" size="small" @click="showInput">
            + 添加关键词
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';

const config = reactive({
  DB_HOST: '',
  DB_PORT: 3306,
  DB_NAME: '',
  DB_USER: '',
  DB_PASSWORD: '',
  REDIS_HOST: '',
  REDIS_PORT: 6379,
  max_result: 10,
  issues_result: 15,
  keywords: []
});

const loading = ref(true);
const saving = ref(false);
const error = ref(null);
const inputVisible = ref(false);
const inputValue = ref('');
const InputRef = ref(null);

async function fetchConfig() {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await axios.get('/api/config');
    Object.assign(config, response.data);
  } catch (err) {
    console.error('获取配置失败:', err);
    error.value = err.response?.data?.error || '获取配置数据失败，请稍后重试';
  } finally {
    loading.value = false;
  }
}

async function saveConfig() {
  saving.value = true;
  
  try {
    await axios.post('/api/config', config);
    ElMessage.success('配置保存成功');
  } catch (err) {
    console.error('保存配置失败:', err);
    ElMessage.error(err.response?.data?.error || '保存配置失败，请稍后重试');
  } finally {
    saving.value = false;
  }
}

function removeKeyword(index) {
  config.keywords.splice(index, 1);
}

function showInput() {
  inputVisible.value = true;
  nextTick(() => {
    InputRef.value.focus();
  });
}

function addKeyword() {
  if (inputValue.value) {
    if (!config.keywords.includes(inputValue.value)) {
      config.keywords.push(inputValue.value);
    }
    inputVisible.value = false;
    inputValue.value = '';
  }
}

onMounted(() => {
  fetchConfig();
});
</script>

<style scoped>
.keyword-tag {
  margin-right: 10px;
  margin-bottom: 10px;
}

.keyword-input {
  width: 200px;
  display: inline-block;
  vertical-align: bottom;
  margin-right: 10px;
}

.button-new-keyword {
  margin-bottom: 10px;
}

.error-container {
  padding: 60px 0;
  text-align: center;
}
</style>