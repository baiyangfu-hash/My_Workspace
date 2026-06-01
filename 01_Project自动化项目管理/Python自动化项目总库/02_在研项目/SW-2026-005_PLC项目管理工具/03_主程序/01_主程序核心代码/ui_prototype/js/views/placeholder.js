function renderPlaceholder(title, desc) {
  return `
    <div class="placeholder-view">
      <div class="ph-icon">🚧</div>
      <div class="ph-title">${title}</div>
      <div class="ph-desc">${desc}</div>
    </div>
  `;
}
