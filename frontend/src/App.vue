<template>
  <div class="container">
    <h1>🤖 内容营销AI助理</h1>
    
    <div class="form-card">
      <div class="form-item">
        <label>📌 主题</label>
        <input v-model="topic" placeholder="例如：AI Agent 开发" />
      </div>
      
      <div class="form-item">
        <label>🎨 风格</label>
        <select v-model="style">
          <option value="专业">专业</option>
          <option value="幽默">幽默</option>
          <option value="极简">极简</option>
        </select>
      </div>
      
      <button @click="generate" :disabled="loading">
        {{ loading ? 'AI 思考中...' : '✨ 生成创意' }}
      </button>
      <div v-if="loading" class="loading-spinner"></div>
    </div>

    <div v-if="result" class="result-card">
      <div class="result-header">
        <h2>💡 AI 创意</h2>
        <button @click="copyResult" class="copy-btn" :title="copySuccess ? '已复制!' : '复制到剪贴板'">
          {{ copySuccess ? '✅ 已复制' : '📋 复制' }}
        </button>
      </div>
      <p>{{ result }}</p>
      <div class="meta">⏱️ 耗时：{{ processingTime }} 秒</div>
    </div>

    <div v-if="error" class="error-card">
      ❌ {{ error }}
    </div>
  </div>
  </template>

<script setup>
import { ref } from 'vue'

// 表单数据
const topic = ref('')
const style = ref('专业')
const loading = ref(false)
const result = ref('')
const processingTime = ref(0)
const error = ref('')
const copySuccess = ref(false)

// 复制结果到剪贴板
async function copyResult() {
  try {
    await navigator.clipboard.writeText(result.value)
    copySuccess.value = true
    setTimeout(() => {
      copySuccess.value = false
    }, 2000)
  } catch (err) {
    error.value = '复制失败，请手动复制'
    console.error('复制失败:', err)
  }
}

// 调用后端接口
async function generate() {
  if (!topic.value.trim()) {
    error.value = '请输入主题'
    return
  }
  
  loading.value = true
  error.value = ''
  result.value = ''
  
  try {
    const response = await fetch('https://delightful-connection-production-4e0a.up.railway.app/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic.value,
        style: style.value
      })
    })
    
    const data = await response.json()
    
    if (data.status === 'success') {
      result.value = data.idea
      processingTime.value = data.processing_time
    } else {
      error.value = data.idea || '生成失败，请稍后重试'
    }
  } catch (err) {
    error.value = '网络错误，请确保后端服务已启动（http://localhost:8000）'
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.loading-spinner {
  margin-top: 10px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.container {
  max-width: 800px;
  margin: 50px auto;
  padding: 20px;
  font-family: system-ui, -apple-system, sans-serif;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
}

.form-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.form-item {
  margin-bottom: 20px;
}

label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #374151;
}

input, select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 16px;
  box-sizing: border-box;
}

input:focus, select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
}

button {
  width: 100%;
  padding: 12px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

button:hover:not(:disabled) {
  background: #2563eb;
}

button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.result-card {
  margin-top: 24px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
}

.result-card h2 {
  margin-top: 0;
  color: #2c3e50;
  font-size: 18px;
}

.result-card p {
  font-size: 16px;
  line-height: 1.6;
  color: #1f2937;
  white-space: pre-wrap;
}

.meta {
  margin-top: 12px;
  color: #6b7280;
  font-size: 14px;
}

.error-card {
  margin-top: 24px;
  background: #fee2e2;
  border: 1px solid #fca5a5;
  border-radius: 8px;
  padding: 12px 16px;
  color: #b91c1c;
}
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.result-header h2 {
  margin: 0;
}

.copy-btn {
  width: auto;
  padding: 6px 12px;
  font-size: 14px;
  font-weight: normal;
  background: #10b981;
}

.copy-btn:hover:not(:disabled) {
  background: #059669;
}
</style>