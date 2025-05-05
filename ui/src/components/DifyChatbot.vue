<template>
  <div class="dify-chatbot-container" v-if="visible">
    <iframe
      :src="chatbotUrl"
      style="width: 100%; height: 100%; min-height: 700px"
      frameborder="0"
      allow="microphone">
    </iframe>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  paperTitle: {
    type: String,
    default: ''
  },
  paperAbstract: {
    type: String,
    default: ''
  },
  visible: {
    type: Boolean,
    default: false
  }
});

// 构建聊天机器人URL
const chatbotUrl = computed(() => {
  // 基础URL
  const baseUrl = 'https://udify.app/chatbot/ENglxPiWssESIHgj';
  
  // 如果有论文信息，添加作为查询参数
  if (props.paperTitle || props.paperAbstract) {
    // 创建查询参数
    const params = new URLSearchParams();
    
    if (props.paperTitle) {
      params.append('paper_title', props.paperTitle);
    }
    
    if (props.paperAbstract) {
      params.append('paper_abstract', props.paperAbstract);
    }
    
    return `${baseUrl}?${params.toString()}`;
  }
  
  return baseUrl;
});
</script>

<style scoped>
.dify-chatbot-container {
  position: relative;
  z-index: 1000;
  margin-top: 20px;
  width: 100%;
  height: 700px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>
