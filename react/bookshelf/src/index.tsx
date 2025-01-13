import React from "react";
import ReactDOM from "react-dom/client"; // 注意：这里从 'react-dom/client' 导入
import App from "./App";

// 获取根节点
const rootElement = document.getElementById("root");

if (rootElement) {
  // 创建根
  const root = ReactDOM.createRoot(rootElement);
  // 渲染应用
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
} else {
  console.error("Root element not found");
}
