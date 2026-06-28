import React from 'react';
import './Toast.css';

const ICONS = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };

const Toast = ({ toasts, removeToast }) => (
  <div className="toast-container">
    {toasts.map((t) => (
      <div key={t.id} className={`toast toast-${t.type}`}>
        <span className="toast-icon">{ICONS[t.type] || ICONS.info}</span>
        <span className="toast-message">{t.message}</span>
        <button className="toast-close" onClick={() => removeToast(t.id)}>×</button>
      </div>
    ))}
  </div>
);

export default Toast;
