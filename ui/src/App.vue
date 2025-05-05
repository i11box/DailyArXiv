<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <el-header height="60px">
        <div class="header-content">
          <div class="logo">
            <router-link to="/">DailyArXiv</router-link>
          </div>
          <el-menu mode="horizontal" router :default-active="activeRoute">
            <el-menu-item index="/">论文列表</el-menu-item>
            <el-menu-item index="/config">配置管理</el-menu-item>
          </el-menu>
        </div>
      </el-header>
      
      <el-main>
        <router-view />
      </el-main>
      
      <el-footer height="60px">
        <div class="footer-content">
          <p> 2025 DailyArXiv - 每日论文推荐</p>
        </div>
      </el-footer>
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import zhCn from 'element-plus/dist/locale/zh-cn.mjs';

const route = useRoute();
const activeRoute = computed(() => route?.path || '/');
</script>

<style>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 10;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.logo {
  font-size: 24px;
  font-weight: bold;
}

.logo a {
  color: var(--primary-color);
  text-decoration: none;
}

.el-main {
  flex: 1;
  padding: 20px;
}

.el-footer {
  background-color: #f5f7fa;
  border-top: 1px solid var(--border-color-light);
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-color-secondary);
}
</style>