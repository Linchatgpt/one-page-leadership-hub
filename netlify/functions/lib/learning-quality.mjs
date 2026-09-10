const cleanText = (value) => String(value ?? '').replace(/\s+/g, ' ').trim();

export function normalizeQuickScan(value) {
  if (typeof value === 'string') {
    try {
      value = JSON.parse(value);
    } catch {
      return [];
    }
  }
  if (value && !Array.isArray(value) && typeof value === 'object') {
    value = value.quick_scan || value.questions || value.items || value.data;
  }
  if (!Array.isArray(value)) return [];
  return value.map((raw) => {
    const item = Array.isArray(raw)
      ? { question: raw[0], options: raw.slice(1) }
      : typeof raw === 'string'
        ? { question: raw, options: [] }
        : (raw || {});
    const rawOptions = item.options || item.choices || item.answers || [];
    return {
      question: cleanText(item.question || item.prompt || item.prompt_text || item.title || item.text || item.label),
      options: (Array.isArray(rawOptions) ? rawOptions : []).map((rawOption) => {
        const option = typeof rawOption === 'string' ? { text: rawOption } : (rawOption || {});
        return {
          text: cleanText(option.text || option.label || option.value),
          feedback: cleanText(option.feedback || option.explanation || option.reason),
        };
      }),
    };
  });
}

export function validateQuickScan(value) {
  const quickScan = normalizeQuickScan(value);
  const issues = [];
  if (quickScan.length !== 3) issues.push('快問快答需要正好 3 題');
  quickScan.forEach((item, index) => {
    if (!item.question) issues.push(`第 ${index + 1} 題缺少題目`);
    if (item.options.length !== 2) issues.push(`第 ${index + 1} 題需要 2 個選項`);
    item.options.forEach((option, optionIndex) => {
      if (!option.text) issues.push(`第 ${index + 1} 題選項 ${optionIndex + 1} 缺少文字`);
      if (!option.feedback) issues.push(`第 ${index + 1} 題選項 ${optionIndex + 1} 缺少回饋`);
    });
  });
  return { valid: issues.length === 0, issues, quickScan };
}
